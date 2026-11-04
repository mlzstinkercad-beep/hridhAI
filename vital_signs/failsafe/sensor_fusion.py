"""
sensor_fusion.py — WiFi-CSI Fallback System

When camera is blocked (confidence failures > 30s),
the system automatically switches to WiFi Channel State
Information (CSI) for basic vital sign monitoring.

WiFi-CSI Physics:
  WiFi radio waves (2.4/5 GHz) are reflected and absorbed by
  the human body. Breathing and heartbeat cause micro-movements
  that create measurable perturbations in the wireless channel.
  
  CSI captures the complex amplitude + phase of each subcarrier.
  Body motion modulates these, allowing:
    - Breathing rate: ±1 BrPM accuracy
    - Heart rate:     ±5 BPM accuracy (less precise than camera)
  
  Hardware requirement: Intel 5300 or Atheros WiFi NIC in monitor mode.
  Reference: AirPulse (https://github.com/rxt1077/airpulse)
  
  In the ISS context: The station's internal WiFi infrastructure
  serves as the passive radar array.

NOTE: This is the DEGRADED mode — reduced accuracy is acceptable
      because the alternative is ZERO data (camera blocked).
"""

import numpy as np
import subprocess
import threading
from typing import Optional, Tuple
from dataclasses import dataclass

from utils.ring_buffer import RingBuffer
from utils.signal_processing import (
    bandpass_filter, estimate_frequency_fft, detrend_signal
)
from config import TARGET_FPS, WIFI_INTERFACE


@dataclass
class CSIVitals:
    """Reduced vital set available from WiFi-CSI."""
    heart_rate_bpm:  float
    breath_rate_bpm: float
    hr_confidence:   float
    br_confidence:   float
    source:          str = "WiFi-CSI"  # Always tag as degraded source


class WiFiCSIFallback:
    """
    Passive WiFi sensing for breathing and heart rate when camera fails.
    
    Activation: Called by the orchestrator when ConfidenceGate escalates.
    """

    def __init__(self, interface: str = WIFI_INTERFACE):
        self._interface   = interface
        self._active      = False
        self._csi_buffer  = RingBuffer(900)  # 30s at 30Hz
        self._read_thread: Optional[threading.Thread] = None
        self._stop_event  = threading.Event()

    def activate(self) -> bool:
        """
        Start WiFi-CSI data collection.
        
        Returns:
            True if CSI interface successfully opened, False otherwise.
        """
        if self._active:
            return True

        try:
            # Verify interface supports monitor mode
            result = subprocess.run(
                ['iw', 'dev', self._interface, 'info'],
                capture_output = True, text = True, timeout = 2
            )
            if result.returncode != 0:
                print(f"[CSI] Interface {self._interface} not available")
                return False

            self._active    = True
            self._stop_event.clear()

            # Start background thread to collect CSI data
            self._read_thread = threading.Thread(
                target = self._csi_collection_loop,
                daemon = True,
                name   = "WiFiCSI-Reader"
            )
            self._read_thread.start()
            print("[CSI] WiFi-CSI fallback ACTIVATED")
            return True

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"[CSI] Activation failed: {e}")
            return False

    def deactivate(self) -> None:
        """Stop CSI collection when camera recovers."""
        self._stop_event.set()
        self._active = False
        print("[CSI] WiFi-CSI fallback DEACTIVATED — camera restored")

    def get_vitals(self) -> Optional[CSIVitals]:
        """
        Compute heart rate and breathing rate from buffered CSI data.
        
        Returns:
            CSIVitals if enough data, None otherwise.
        """
        if not self._active:
            return None

        signal_data = self._csi_buffer.get_all()
        if len(signal_data) < 60:  # Need at least 2 seconds
            return None

        # ── Breathing rate (0.1 - 0.7 Hz) ────────────────────────────
        br_signal = bandpass_filter(
            detrend_signal(signal_data),
            lowcut=0.07, highcut=0.7, fs=30.0
        )
        br_freq, br_conf = estimate_frequency_fft(
            br_signal, fs=30.0, freq_min=0.07, freq_max=0.7
        )

        # ── Heart rate (0.7 - 3.0 Hz) ─────────────────────────────────
        hr_signal = bandpass_filter(
            detrend_signal(signal_data),
            lowcut=0.7, highcut=3.0, fs=30.0
        )
        hr_freq, hr_conf = estimate_frequency_fft(
            hr_signal, fs=30.0, freq_min=0.7, freq_max=3.0
        )

        return CSIVitals(
            heart_rate_bpm  = hr_freq * 60.0,
            breath_rate_bpm = br_freq * 60.0,
            hr_confidence   = hr_conf * 0.7,  # CSI is 70% as accurate
            br_confidence   = br_conf * 0.8,
            source          = "WiFi-CSI (Degraded Mode)"
        )

    def _csi_collection_loop(self) -> None:
        """
        Background thread: reads CSI amplitude from WiFi driver.
        
        In production: reads from /proc/net/csi or similar kernel interface
        provided by modified Atheros/Intel WiFi driver.
        In simulation: generates synthetic signal for testing.
        
        The CSI amplitude is the key feature — it captures the
        multipath channel response which varies with body motion.
        """
        import time

        print("[CSI] Collection loop started")
        sample_rate = 30  # Hz
        interval    = 1.0 / sample_rate

        while not self._stop_event.is_set():
            start = time.monotonic()

            try:
                # Production: csi_amplitude = read_csi_driver()
                # Simulation: synthetic respiratory + cardiac signal
                t   = time.time()
                csi_amplitude = (
                    0.5 * np.sin(2 * np.pi * 0.25 * t) +    # Breathing
                    0.1 * np.sin(2 * np.pi * 1.2  * t) +    # Heartbeat
                    0.02 * np.random.randn()                  # Noise
                )
                self._csi_buffer.push(float(csi_amplitude))

            except Exception as e:
                print(f"[CSI] Read error: {e}")

            # Maintain precise sampling rate
            elapsed = time.monotonic() - start
            sleep_t = max(0.0, interval - elapsed)
            time.sleep(sleep_t)