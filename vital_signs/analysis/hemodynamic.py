"""
hemodynamic.py — Layer A: Hemodynamic Analysis

Extracts from RGB camera:
  1. Heart Rate (BPM)     — Green channel rPPG
  2. HRV (RMSSD)          — RR interval analysis
  3. Blood Pressure       — Pulse Transit Time (PTT)
  4. Blood Glucose (Est.) — PPG waveform morphology

Scientific Basis:
─────────────────
rPPG (Remote Photoplethysmography):
  Blood absorbs green light (530-570nm) most strongly.
  As the heart beats, blood volume in facial capillaries
  oscillates → green channel pixel values oscillate subtly.
  This ΔG / G signal (AC/DC component) IS the pulse.

PTT (Pulse Transit Time) for Blood Pressure:
  BP ∝ 1/PTT² (Moens-Korteweg equation approximation)
  PTT = time for pulse wave to travel from heart → forehead
  We estimate this as the delay between carotid region peak
  and forehead peak in the same rPPG signal.
  Reference: Poon & Zhang, 2005.

Blood Glucose via PPG Morphology:
  High blood sugar → increased blood viscosity
  → Increased vascular resistance
  → Changes the "Dicrotic notch" timing and amplitude
  → Measured via Augmentation Index (AIx) of PPG waveform
  This is ESTIMATIVE — not a replacement for glucometry.
  Reference: Hina & Maciejewski, 2022.
"""

import numpy as np
import cv2
import mediapipe as mp
from scipy import signal as scipy_signal
from typing import Optional, Tuple, Dict
from dataclasses import dataclass

from utils.ring_buffer import RingBuffer
from utils.signal_processing import (
    bandpass_filter, estimate_frequency_fft,
    detrend_signal, normalize_signal,
    find_peaks_robust, compute_hrv_rmssd
)
from config import (
    TARGET_FPS, RING_BUFFER_SIZE, RPPG_WINDOW_SEC,
    HR_MIN_BPM, HR_MAX_BPM, HRV_WINDOW_SEC,
    CONFIDENCE_THRESHOLD
)


@dataclass
class HemodynamicResult:
    """Structured output for Layer A."""
    heart_rate_bpm:    float           # BPM or NaN
    hrv_rmssd_ms:      float           # HRV in ms or NaN
    bp_systolic_est:   float           # mmHg estimate or NaN
    bp_diastolic_est:  float           # mmHg estimate or NaN
    glucose_index:     float           # Augmentation Index (0-1) or NaN
    hr_confidence:     float           # 0.0 – 1.0
    bp_confidence:     float           # 0.0 – 1.0
    glucose_confidence: float          # 0.0 – 1.0


class HemodynamicAnalyzer:
    """
    Continuous heart rate, HRV, blood pressure, and glucose estimation
    from facial ROI using rPPG and PPG morphology analysis.
    """

    def __init__(self):
        # Separate ring buffers per ROI for PTT measurement
        self._forehead_buffer = RingBuffer(RING_BUFFER_SIZE)
        self._carotid_buffer  = RingBuffer(RING_BUFFER_SIZE)  # Neck ROI
        self._hrv_buffer      = RingBuffer(
            int(TARGET_FPS * HRV_WINDOW_SEC)
        )
        
        # MediaPipe for landmark-based ROI extraction
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode        = False,
            max_num_faces            = 1,
            refine_landmarks         = True,
            min_detection_confidence = 0.5,
            min_tracking_confidence  = 0.5
        )
        
        # Calibration baselines (set during onboarding)
        self._baseline_ptt_ms: Optional[float] = None
        self._baseline_bp_systolic:  float = 120.0  # mmHg Earth-normal
        self._baseline_bp_diastolic: float = 80.0

    def process_frame(
        self,
        frame: np.ndarray,
        landmarks: Optional[object]
    ) -> HemodynamicResult:
        """
        Process one frame and update ring buffers.
        Returns current hemodynamic estimates.
        
        Args:
            frame:     Preprocessed BGR frame.
            landmarks: MediaPipe face landmarks (may be None if occluded).
        
        Returns:
            HemodynamicResult with all Layer A vitals.
        """
        if landmarks is None:
            return self._null_result()

        # ── Extract ROI mean green channel values ─────────────────────
        forehead_val = self._extract_roi_green(
            frame, landmarks, roi_type='forehead'
        )
        carotid_val  = self._extract_roi_green(
            frame, landmarks, roi_type='carotid'
        )

        if forehead_val is None:
            return self._null_result()

        # Push to ring buffers (old data auto-discarded)
        self._forehead_buffer.push(forehead_val)
        if carotid_val is not None:
            self._carotid_buffer.push(carotid_val)

        # ── Compute Heart Rate ────────────────────────────────────────
        hr_bpm, hr_confidence, rr_intervals = self._compute_heart_rate()

        # ── Compute HRV ───────────────────────────────────────────────
        hrv_rmssd = self._compute_hrv(rr_intervals)

        # ── Compute Blood Pressure via PTT ────────────────────────────
        bp_sys, bp_dia, bp_conf = self._compute_blood_pressure()

        # ── Estimate Blood Glucose via PPG Morphology ─────────────────
        glucose_idx, gluc_conf = self._compute_glucose_index()

        return HemodynamicResult(
            heart_rate_bpm     = hr_bpm,
            hrv_rmssd_ms       = hrv_rmssd,
            bp_systolic_est    = bp_sys,
            bp_diastolic_est   = bp_dia,
            glucose_index      = glucose_idx,
            hr_confidence      = hr_confidence,
            bp_confidence      = bp_conf,
            glucose_confidence = gluc_conf,
        )

    def _extract_roi_green(
        self,
        frame:     np.ndarray,
        landmarks: object,
        roi_type:  str
    ) -> Optional[float]:
        """
        Extract mean green channel from a facial ROI.
        
        ROI Landmark Groups (MediaPipe 468-point mesh):
          Forehead: Points 10, 338, 297, 332, 284, 251, 389
          Carotid:  Approximated from chin/jaw region
        
        Returns:
            Mean green channel value (0-255), or None if ROI invalid.
        """
        h, w = frame.shape[:2]
        lm   = landmarks.landmark

        # Landmark index groups per ROI type
        roi_indices = {
            'forehead': [10, 338, 297, 332, 284, 251, 389, 109, 67, 103],
            'carotid':  [152, 148, 176, 149, 150, 136, 172, 58, 132]
        }

        indices = roi_indices.get(roi_type, [])
        if not indices:
            return None

        # Build polygon mask from landmark points
        points = []
        for idx in indices:
            if idx < len(lm):
                x = int(lm[idx].x * w)
                y = int(lm[idx].y * h)
                points.append([x, y])

        if len(points) < 3:
            return None

        pts    = np.array(points, dtype=np.int32)
        mask   = np.zeros((h, w), dtype=np.uint8)
        cv2.fillConvexPoly(mask, pts, 255)

        # Extract green channel mean within mask
        green_channel = frame[:, :, 1]  # BGR → index 1 = Green
        roi_pixels    = green_channel[mask > 0]

        if len(roi_pixels) == 0:
            return None

        return float(np.mean(roi_pixels))

    def _compute_heart_rate(
        self
    ) -> Tuple[float, float, np.ndarray]:
        """
        Extract heart rate from forehead rPPG signal via FFT.
        
        Processing pipeline:
          Raw green signal → Detrend → Bandpass(0.67-3.33Hz) → FFT
          → Find dominant frequency → Convert to BPM
        
        Returns:
            Tuple of (bpm, confidence, rr_intervals_ms)
        """
        window_samples = int(TARGET_FPS * RPPG_WINDOW_SEC)
        raw_signal = self._forehead_buffer.get_latest(window_samples)

        if raw_signal is None:
            return np.nan, 0.0, np.array([])

        # Signal conditioning
        detrended  = detrend_signal(raw_signal)
        filtered   = bandpass_filter(
            detrended,
            lowcut  = HR_MIN_BPM / 60.0,   # 40 BPM → 0.67 Hz
            highcut = HR_MAX_BPM / 60.0,   # 200 BPM → 3.33 Hz
            fs      = TARGET_FPS
        )
        normalized = normalize_signal(filtered)

        # FFT-based frequency estimation
        freq_hz, confidence = estimate_frequency_fft(
            normalized,
            fs       = TARGET_FPS,
            freq_min = HR_MIN_BPM / 60.0,
            freq_max = HR_MAX_BPM / 60.0
        )

        bpm = freq_hz * 60.0

        # Extract RR intervals for HRV
        peaks = find_peaks_robust(
            normalized, TARGET_FPS,
            min_freq_hz = HR_MIN_BPM / 60.0,
            max_freq_hz = HR_MAX_BPM / 60.0
        )
        rr_intervals = np.diff(peaks) / TARGET_FPS * 1000  # ms

        return bpm, confidence, rr_intervals

    def _compute_hrv(self, rr_intervals: np.ndarray) -> float:
        """Compute RMSSD from current RR intervals."""
        if len(rr_intervals) < 2:
            return np.nan
        return compute_hrv_rmssd(rr_intervals)

    def _compute_blood_pressure(self) -> Tuple[float, float, float]:
        """
        Estimate BP via Pulse Transit Time (PTT).
        
        PTT = cross-correlation delay between forehead and carotid signals.
        Shorter PTT → Stiffer arteries → Higher BP.
        
        Formula (Bramwell-Hill approximation):
          BP ∝ 1 / PTT²
        
        Calibration:
          At onboarding, PTT_baseline maps to known BP_baseline.
          Subsequent deviations scale proportionally.
        
        Returns:
            Tuple of (systolic_mmHg, diastolic_mmHg, confidence)
        """
        n_samples = int(TARGET_FPS * RPPG_WINDOW_SEC)
        fore_sig  = self._forehead_buffer.get_latest(n_samples)
        car_sig   = self._carotid_buffer.get_latest(n_samples)

        if fore_sig is None or car_sig is None:
            return np.nan, np.nan, 0.0

        # Filter both signals to cardiac band
        fore_f = bandpass_filter(
            detrend_signal(fore_sig),
            0.67, 3.33, TARGET_FPS
        )
        car_f  = bandpass_filter(
            detrend_signal(car_sig),
            0.67, 3.33, TARGET_FPS
        )

        # Cross-correlation to find time delay
        correlation = scipy_signal.correlate(fore_f, car_f, mode='full')
        lags        = scipy_signal.correlation_lags(
            len(fore_f), len(car_f), mode='full'
        )
        lag_samples = lags[np.argmax(correlation)]
        ptt_ms      = abs(lag_samples) / TARGET_FPS * 1000  # ms

        # Confidence: quality of cross-correlation peak
        max_corr   = np.max(np.abs(correlation))
        mean_corr  = np.mean(np.abs(correlation))
        bp_conf    = float(np.clip(max_corr / (mean_corr + 1e-6) / 10, 0, 1))

        if bp_conf < CONFIDENCE_THRESHOLD:
            return np.nan, np.nan, bp_conf

        # Set baseline on first successful measurement
        if self._baseline_ptt_ms is None:
            self._baseline_ptt_ms = ptt_ms
            return (
                self._baseline_bp_systolic,
                self._baseline_bp_diastolic,
                bp_conf
            )

        # Scale BP estimate from PTT ratio
        # PTT_ratio > 1 (longer PTT) → lower BP
        # PTT_ratio < 1 (shorter PTT) → higher BP
        ptt_ratio  = self._baseline_ptt_ms / (ptt_ms + 1e-6)
        bp_sys_est = self._baseline_bp_systolic  * (ptt_ratio ** 2)
        bp_dia_est = self._baseline_bp_diastolic * (ptt_ratio ** 2)

        # Clamp to physiological limits
        bp_sys_est = np.clip(bp_sys_est, 60, 200)
        bp_dia_est = np.clip(bp_dia_est, 40, 130)

        return float(bp_sys_est), float(bp_dia_est), float(bp_conf)

    def _compute_glucose_index(self) -> Tuple[float, float]:
        """
        Estimate blood glucose proxy via PPG Augmentation Index (AIx).
        
        PPG Waveform Anatomy:
          ┌─ Peak 1 (Systolic peak) — direct cardiac ejection
          │         ┌─ Dicrotic notch — aortic valve closure
          │         │    ┌─ Peak 2 (Dicrotic peak) — reflected wave
          ▼         ▼    ▼
         ╱╲        ╱╲
        ╱  ╲______╱  ╲___
        
        Augmentation Index = (P2 - P1) / Pulse Pressure
        
        High glucose → increased viscosity → reflected wave arrives
        earlier and with higher amplitude → AIx increases.
        
        This is a BIOMARKER PROXY, not a clinical glucose reading.
        
        Returns:
            Tuple of (augmentation_index 0-1, confidence 0-1)
        """
        n_samples = int(TARGET_FPS * RPPG_WINDOW_SEC)
        raw = self._forehead_buffer.get_latest(n_samples)

        if raw is None:
            return np.nan, 0.0

        filtered = bandpass_filter(
            detrend_signal(raw),
            0.5, 5.0, TARGET_FPS
        )
        normalized = normalize_signal(filtered)

        # Find all peaks (systolic peaks)
        peaks = find_peaks_robust(
            normalized, TARGET_FPS,
            min_freq_hz = 0.5,
            max_freq_hz = 3.33
        )

        if len(peaks) < 3:
            return np.nan, 0.0

        # Analyze waveform shape between consecutive peaks
        aix_values = []

        for i in range(len(peaks) - 1):
            beat_segment = normalized[peaks[i]:peaks[i + 1]]
            if len(beat_segment) < 5:
                continue

            systolic_peak = beat_segment[0]  # First point = P1

            # Find dicrotic notch (local minimum after peak)
            # Search in second half of beat
            second_half = beat_segment[len(beat_segment) // 4:]
            if len(second_half) < 3:
                continue

            notch_idx = np.argmin(second_half) + len(beat_segment) // 4

            # Find dicrotic peak (local max after notch)
            post_notch = beat_segment[notch_idx:]
            if len(post_notch) < 2:
                continue

            dicrotic_peak = np.max(post_notch)

            # Augmentation Index calculation
            pulse_pressure = systolic_peak - np.min(beat_segment)
            if pulse_pressure < 1e-6:
                continue

            aix = (dicrotic_peak - systolic_peak) / pulse_pressure
            aix_values.append(float(aix))

        if not aix_values:
            return np.nan, 0.0

        mean_aix = float(np.mean(aix_values))
        # Confidence from consistency of measurements
        confidence = 1.0 - float(np.std(aix_values)) if len(aix_values) > 1 else 0.5
        confidence = float(np.clip(confidence, 0.0, 1.0))

        return mean_aix, confidence

    def set_baseline(
        self,
        systolic:  float,
        diastolic: float,
        ptt_ms:    Optional[float] = None
    ) -> None:
        """
        Set personalized calibration baseline for blood pressure.
        Called during astronaut onboarding on Earth.
        """
        self._baseline_bp_systolic  = systolic
        self._baseline_bp_diastolic = diastolic
        if ptt_ms is not None:
            self._baseline_ptt_ms = ptt_ms

    @staticmethod
    def _null_result() -> HemodynamicResult:
        """Return all-NaN result when face is not detected."""
        return HemodynamicResult(
            heart_rate_bpm     = np.nan,
            hrv_rmssd_ms       = np.nan,
            bp_systolic_est    = np.nan,
            bp_diastolic_est   = np.nan,
            glucose_index      = np.nan,
            hr_confidence      = 0.0,
            bp_confidence      = 0.0,
            glucose_confidence = 0.0,
        )