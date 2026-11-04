"""
respiratory.py — Layer B: Respiratory Analysis

Extracts:
  1. Breathing Rate (BrPM) — Eulerian Video Magnification (EVM)
     of chest/shoulder micro-movements
  2. SpO₂ (%)             — Red/Green channel absorption ratio

Scientific Basis:
─────────────────
Eulerian Video Magnification (Wu et al., MIT 2012):
  Amplifies tiny, invisible motions in video using a spatial
  Laplacian pyramid decomposed at target temporal frequencies.
  Breathing at 12-20 breaths/min = 0.2-0.33 Hz signal.
  Chest wall movement is < 2mm — invisible normally, visible after 10x EVM.

SpO₂ via RGB Camera:
  Oxygenated hemoglobin (HbO₂) absorbs more IR, reflects more Red.
  Deoxygenated hemoglobin (Hb) absorbs more Red.
  Ratio: R = (AC_red/DC_red) / (AC_green/DC_green)
  SpO₂ ≈ 110 - 25R  (empirical calibration, Verkruysse et al. 2008)
  
  Note: This is LESS accurate than fingertip pulse oximeters.
  Confidence degrades significantly in low light or motion.
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass

from utils.ring_buffer import RingBuffer
from utils.signal_processing import (
    bandpass_filter, estimate_frequency_fft,
    detrend_signal, normalize_signal
)
from config import (
    TARGET_FPS, RING_BUFFER_SIZE,
    RESP_MIN_BPM, RESP_MAX_BPM,
    SPO2_RED_CHANNEL, SPO2_GREEN_CHANNEL,
    CONFIDENCE_THRESHOLD
)


@dataclass
class RespiratoryResult:
    """Structured output for Layer B."""
    breath_rate_bpm: float   # Breaths per minute
    spo2_percent:    float   # Oxygen saturation %
    br_confidence:   float   # 0-1
    spo2_confidence: float   # 0-1


class RespiratoryAnalyzer:
    """
    Breathing rate via EVM and SpO₂ via RGB ratiometry.
    """

    def __init__(self):
        # Breathing signal: stores frame-to-frame motion energy
        self._motion_buffer = RingBuffer(RING_BUFFER_SIZE)
        
        # SpO₂ buffers: separate AC/DC tracking per channel
        self._red_buffer   = RingBuffer(RING_BUFFER_SIZE)
        self._green_buffer = RingBuffer(RING_BUFFER_SIZE)
        
        # Previous frame for motion difference (EVM approximation)
        self._prev_frame_gray: Optional[np.ndarray] = None
        
        # EVM Gaussian pyramid levels
        self._evm_levels = 4
        self._evm_amplification = 15.0

    def process_frame(
        self,
        frame:     np.ndarray,
        landmarks: Optional[object]
    ) -> RespiratoryResult:
        """
        Process one frame for respiratory signals.
        
        EVM is applied to the shoulder/chest region.
        SpO₂ ratio is computed from the facial ROI.
        """
        # ── Motion-based breathing (EVM on full chest ROI) ────────────
        motion_energy = self._extract_chest_motion(frame, landmarks)
        if motion_energy is not None:
            self._motion_buffer.push(motion_energy)

        # ── SpO₂ from facial ROI ──────────────────────────────────────
        if landmarks is not None:
            red_val, green_val = self._extract_spo2_channels(
                frame, landmarks
            )
            if red_val is not None:
                self._red_buffer.push(red_val)
                self._green_buffer.push(green_val)

        # ── Compute outputs ───────────────────────────────────────────
        br_bpm,   br_conf   = self._compute_breathing_rate()
        spo2_pct, spo2_conf = self._compute_spo2()

        return RespiratoryResult(
            breath_rate_bpm = br_bpm,
            spo2_percent    = spo2_pct,
            br_confidence   = br_conf,
            spo2_confidence = spo2_conf,
        )

    def _extract_chest_motion(
        self,
        frame:     np.ndarray,
        landmarks: Optional[object]
    ) -> Optional[float]:
        """
        Compute frame-to-frame motion energy in the chest/shoulder region.
        
        Simplified EVM approach for embedded systems:
          Full EVM (Laplacian pyramid + temporal filter) is too
          compute-intensive for ARM at 25% CPU budget.
          
          Instead: Frame-difference on spatially downsampled ROI,
          bandpass-filtered over the breathing frequency range.
          This captures the gross motion signal without full pyramid.
        
        Returns:
            Scalar motion energy value, or None if no reference frame.
        """
        # Downsample for efficiency (chest motion is low-frequency)
        small = cv2.resize(frame, (160, 120))
        gray  = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32)

        if self._prev_frame_gray is None:
            self._prev_frame_gray = gray
            return None

        # Frame difference = motion signal
        diff  = gray - self._prev_frame_gray
        self._prev_frame_gray = gray

        # Focus on upper body region (top 30-60% of frame = chest)
        h, w  = diff.shape
        chest_region = diff[int(h * 0.3):int(h * 0.7), :]

        # Mean absolute difference = motion energy scalar
        energy = float(np.mean(np.abs(chest_region)))
        return energy

    def _extract_spo2_channels(
        self,
        frame:     np.ndarray,
        landmarks: object
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Extract mean Red and Green channel values from cheek ROI.
        
        SpO₂ Landmark ROI: Cheekbone region
          MediaPipe points: 123, 147, 187, 207 (left cheek)
        
        Returns:
            Tuple of (red_mean, green_mean) or (None, None).
        """
        h, w = frame.shape[:2]
        lm   = landmarks.landmark

        # Cheek region landmarks
        cheek_indices = [36, 47, 123, 147, 187, 205, 207, 214]
        points = []
        for idx in cheek_indices:
            if idx < len(lm):
                x = int(lm[idx].x * w)
                y = int(lm[idx].y * h)
                points.append([x, y])

        if len(points) < 3:
            return None, None

        pts  = np.array(points, dtype=np.int32)
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillConvexPoly(mask, pts, 255)

        # Extract both channels
        red_ch   = frame[:, :, SPO2_RED_CHANNEL]    # Red (BGR index 2)
        green_ch = frame[:, :, SPO2_GREEN_CHANNEL]  # Green (BGR index 1)

        red_pixels   = red_ch[mask > 0]
        green_pixels = green_ch[mask > 0]

        if len(red_pixels) == 0:
            return None, None

        return float(np.mean(red_pixels)), float(np.mean(green_pixels))

    def _compute_breathing_rate(self) -> Tuple[float, float]:
        """
        Extract breathing frequency from motion energy signal.
        
        Pipeline:
          Motion energies → Detrend → Bandpass(0.07-0.67Hz) → FFT
          → Convert dominant frequency to BrPM
        
        Returns:
            Tuple of (breaths_per_minute, confidence)
        """
        # Need at least 30 seconds of data for 4 BrPM resolution
        min_samples = int(TARGET_FPS * 30)
        signal_data = self._motion_buffer.get_latest(min_samples)

        if signal_data is None:
            return np.nan, 0.0

        detrended = detrend_signal(signal_data)
        filtered  = bandpass_filter(
            detrended,
            lowcut  = RESP_MIN_BPM / 60.0,   # 4 BrPM → 0.067 Hz
            highcut = RESP_MAX_BPM / 60.0,   # 40 BrPM → 0.667 Hz
            fs      = TARGET_FPS
        )

        freq_hz, confidence = estimate_frequency_fft(
            normalize_signal(filtered),
            fs       = TARGET_FPS,
            freq_min = RESP_MIN_BPM / 60.0,
            freq_max = RESP_MAX_BPM / 60.0
        )

        return freq_hz * 60.0, confidence

    def _compute_spo2(self) -> Tuple[float, float]:
        """
        Compute SpO₂ from AC/DC ratio of Red and Green channels.
        
        Method (Ratio-of-Ratios):
          AC_red   = std(red_signal)    ← pulsatile component
          DC_red   = mean(red_signal)   ← baseline (DC) component
          R_ratio  = (AC_red/DC_red) / (AC_green/DC_green)
          SpO₂     = 110 - 25 × R_ratio   (empirical constant)
        
        Note: Standard pulse oximeters use RED + INFRARED wavelengths.
        RGB cameras lack true IR. Green channel is used as a proxy.
        This reduces accuracy to ±3-5% vs clinical ±1-2%.
        
        Returns:
            Tuple of (spo2_percent, confidence)
        """
        window = int(TARGET_FPS * RPPG_WINDOW_SEC) if hasattr(
            self, '_rppg_window'
        ) else int(TARGET_FPS * 10)

        red_sig   = self._red_buffer.get_latest(window)
        green_sig = self._green_buffer.get_latest(window)

        if red_sig is None or green_sig is None:
            return np.nan, 0.0

        # AC component = pulsatile (std dev of signal)
        ac_red   = np.std(red_sig)
        ac_green = np.std(green_sig)

        # DC component = baseline (mean of signal)
        dc_red   = np.mean(red_sig)
        dc_green = np.mean(green_sig)

        # Safety checks
        if dc_red < 1.0 or dc_green < 1.0 or ac_green < 1e-6:
            return np.nan, 0.0

        # Ratio of Ratios
        r_ratio = (ac_red / dc_red) / (ac_green / dc_green)

        # Empirical conversion (Verkruysse 2008 calibration)
        spo2 = 110.0 - 25.0 * r_ratio

        # Clamp to physiological range
        spo2 = float(np.clip(spo2, 70.0, 100.0))

        # Confidence based on AC signal strength
        # Weak pulsatile signal → low confidence
        pulsatile_strength = (ac_red / dc_red)  # Should be 0.5-5%
        confidence = float(np.clip(
            pulsatile_strength / 0.02,  # Normalize to ~2% being ideal
            0.0, 1.0
        ))

        return spo2, confidence


# Import needed for typing
RPPG_WINDOW_SEC = 10  # fallback if config not imported
try:
    from config import RPPG_WINDOW_SEC
except ImportError:
    pass