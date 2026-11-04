"""
neurological.py — Layer D: Neurological & Cognitive Analysis

Extracts:
  1. Blink Rate & Fatigue (EAR) — Eye Aspect Ratio
  2. Microsleep Detection       — Blinks > 300ms
  3. Pupillometry               — Constriction/dilation speed
  4. Hand Tremor Analysis       — High-frequency landmark jitter

Scientific Basis:
─────────────────
Eye Aspect Ratio (Soukupová & Čech, 2016):
  EAR = (|P2-P6| + |P3-P5|) / (2 × |P1-P4|)
  
  Where P1-P6 are six eye landmark points:
    P1 ── P4  (horizontal axis)
    P2    P6  (upper/lower diagonal)
    P3    P5  (upper/lower diagonal, inner)
  
  Open eye:   EAR ≈ 0.3
  Closed eye: EAR < 0.2
  Blink:      EAR drops below threshold transiently
  Microsleep: EAR stays below threshold > 300ms

Pupillometry:
  Pupil diameter change rate (mm/s) when display brightness changes.
  Fatigue → slower pupil light reflex (PLR).
  Measured via MediaPipe iris landmarks (468-477 = iris ring).

Tremor:
  High-frequency (4-12 Hz) oscillation in wrist/hand landmarks.
  Neuromotor fatigue, microgravity adaptation, or medication effects.
"""

import numpy as np
import time
from typing import Optional, List, Tuple, Deque
from dataclasses import dataclass
from collections import deque

from utils.ring_buffer import RingBuffer
from utils.signal_processing import (
    bandpass_filter, estimate_frequency_fft, normalize_signal
)
from config import (
    TARGET_FPS, RING_BUFFER_SIZE, EAR_THRESHOLD,
    MICROSLEEP_MS, TREMOR_FREQ_MIN_HZ, TREMOR_FREQ_MAX_HZ,
    CONFIDENCE_THRESHOLD
)


@dataclass
class NeurologicalResult:
    """Structured output for Layer D."""
    ear_left:           float   # Eye Aspect Ratio, left eye
    ear_right:          float   # Eye Aspect Ratio, right eye
    blink_rate_per_min: float   # Normal: 15-20 blinks/min
    microsleep_detected: bool   # True if blink > 300ms
    microsleep_duration_ms: float
    pupil_diameter_left:  float  # Relative units
    pupil_diameter_right: float
    pupil_velocity:       float  # Rate of change (px/s)
    tremor_amplitude:     float  # Peak tremor amplitude (pixels)
    tremor_frequency_hz:  float  # Dominant tremor frequency
    fatigue_score:        float  # 0-1 composite fatigue index
    confidence:           float


class NeurologicalAnalyzer:
    """
    Real-time neurological state monitoring from facial and hand landmarks.
    """

    def __init__(self):
        # EAR signal buffers
        self._ear_left_buffer  = RingBuffer(RING_BUFFER_SIZE)
        self._ear_right_buffer = RingBuffer(RING_BUFFER_SIZE)
        
        # Blink detection state machine
        self._blink_state      = 'open'   # 'open' | 'closing' | 'closed'
        self._blink_start_time: Optional[float] = None
        self._blink_log:        Deque[float] = deque(maxlen=100)
        self._microsleep_active = False
        self._microsleep_dur_ms = 0.0
        
        # Pupil buffers
        self._pupil_left_buffer  = RingBuffer(int(TARGET_FPS * 5))
        self._pupil_right_buffer = RingBuffer(int(TARGET_FPS * 5))
        
        # Tremor analysis buffers (X, Y per hand landmark)
        self._hand_x_buffer = RingBuffer(RING_BUFFER_SIZE)
        self._hand_y_buffer = RingBuffer(RING_BUFFER_SIZE)

    def process_frame(
        self,
        face_landmarks:       Optional[object],
        hand_landmarks:       Optional[List],
        timestamp_sec:        float
    ) -> NeurologicalResult:
        """
        Process landmarks for neurological state assessment.
        
        Args:
            face_landmarks: MediaPipe face mesh results.
            hand_landmarks: MediaPipe hand tracking results.
            timestamp_sec:  Current Unix timestamp for blink timing.
        
        Returns:
            NeurologicalResult with all Layer D vitals.
        """
        # ── Eye Analysis ──────────────────────────────────────────────
        ear_l, ear_r = 0.3, 0.3  # Default (open)
        
        if face_landmarks:
            ear_l = self._compute_ear(face_landmarks, eye='left')
            ear_r = self._compute_ear(face_landmarks, eye='right')
            
            self._ear_left_buffer.push(ear_l)
            self._ear_right_buffer.push(ear_r)

        # Blink detection using mean EAR
        mean_ear = (ear_l + ear_r) / 2.0
        microsleep, ms_dur = self._detect_blink(mean_ear, timestamp_sec)

        # ── Pupillometry ──────────────────────────────────────────────
        pupil_l, pupil_r, pupil_vel = 0.0, 0.0, 0.0
        
        if face_landmarks:
            pupil_l, pupil_r = self._measure_pupils(face_landmarks)
            self._pupil_left_buffer.push(pupil_l)
            self._pupil_right_buffer.push(pupil_r)
            pupil_vel = self._compute_pupil_velocity()

        # ── Hand Tremor ───────────────────────────────────────────────
        tremor_amp, tremor_freq = 0.0, 0.0
        
        if hand_landmarks:
            self._extract_hand_motion(hand_landmarks)
            tremor_amp, tremor_freq = self._analyze_tremor()

        # ── Composite Fatigue Score ───────────────────────────────────
        fatigue = self._compute_fatigue_score(
            mean_ear, microsleep, pupil_vel, tremor_amp
        )

        # ── Confidence ────────────────────────────────────────────────
        confidence = 1.0 if face_landmarks else 0.0

        return NeurologicalResult(
            ear_left             = ear_l,
            ear_right            = ear_r,
            blink_rate_per_min   = self._compute_blink_rate(),
            microsleep_detected  = microsleep,
            microsleep_duration_ms = ms_dur,
            pupil_diameter_left  = pupil_l,
            pupil_diameter_right = pupil_r,
            pupil_velocity       = pupil_vel,
            tremor_amplitude     = tremor_amp,
            tremor_frequency_hz  = tremor_freq,
            fatigue_score        = fatigue,
            confidence           = confidence,
        )

    def _compute_ear(self, landmarks: object, eye: str) -> float:
        """
        Compute Eye Aspect Ratio for one eye.
        
        MediaPipe Landmark Indices:
          Left Eye:  [33, 160, 158, 133, 153, 144]
          Right Eye: [362, 385, 387, 263, 373, 380]
          
          Layout:    P2  P3
                  P1      P4
                     P6  P5
          
          EAR = (||P2-P6|| + ||P3-P5||) / (2 × ||P1-P4||)
        
        Returns:
            EAR value (0.0 = closed, ~0.3 = open)
        """
        # Landmark index groups per eye
        indices = {
            'left':  [33,  160, 158, 133, 153, 144],
            'right': [362, 385, 387, 263, 373, 380]
        }

        lm  = landmarks.landmark
        pts = indices[eye]

        def get_point(idx: int) -> np.ndarray:
            p = lm[idx]
            return np.array([p.x, p.y])

        P1, P2, P3, P4, P5, P6 = [get_point(i) for i in pts]

        # Vertical distances
        v1 = np.linalg.norm(P2 - P6)
        v2 = np.linalg.norm(P3 - P5)

        # Horizontal distance
        h  = np.linalg.norm(P1 - P4)

        if h < 1e-6:
            return 0.0

        ear = (v1 + v2) / (2.0 * h)
        return float(ear)

    def _detect_blink(
        self,
        mean_ear:      float,
        timestamp_sec: float
    ) -> Tuple[bool, float]:
        """
        State machine for blink/microsleep detection.
        
        States:
          open    → EAR drops below threshold → transition to 'closing'
          closing → record start time
          closed  → EAR stays low
          closing → EAR rises above threshold → compute duration
          
          If duration > MICROSLEEP_MS → flag microsleep
        
        Returns:
            Tuple of (is_microsleep, duration_ms)
        """
        is_microsleep = False
        duration_ms   = 0.0

        if mean_ear < EAR_THRESHOLD:
            # Eye is closing or closed
            if self._blink_state == 'open':
                self._blink_state      = 'closing'
                self._blink_start_time = timestamp_sec

            elif self._blink_state == 'closing':
                self._blink_state = 'closed'
                duration_ms = (timestamp_sec - self._blink_start_time) * 1000

                if duration_ms > MICROSLEEP_MS:
                    is_microsleep            = True
                    self._microsleep_active  = True
                    self._microsleep_dur_ms  = duration_ms

        else:
            # Eye is open
            if self._blink_state in ('closing', 'closed'):
                # Blink completed — log it
                duration_ms = (
                    (timestamp_sec - self._blink_start_time) * 1000
                    if self._blink_start_time else 0.0
                )
                self._blink_log.append(timestamp_sec)

                if duration_ms > MICROSLEEP_MS:
                    is_microsleep           = True
                    self._microsleep_dur_ms = duration_ms

            self._blink_state      = 'open'
            self._blink_start_time = None

        return is_microsleep, duration_ms

    def _compute_blink_rate(self) -> float:
        """
        Compute blinks per minute from the last 60 seconds.
        
        Uses a sliding window of blink timestamps.
        Normal range: 15-20 blinks/min (fatigue → higher or lower).
        """
        now = time.time()
        one_min_ago = now - 60.0

        recent_blinks = [t for t in self._blink_log if t > one_min_ago]
        return float(len(recent_blinks))

    def _measure_pupils(
        self,
        landmarks: object
    ) -> Tuple[float, float]:
        """
        Estimate pupil diameter from iris landmark ring.
        
        MediaPipe v0.8.10+ provides iris landmarks (indices 468-477):
          468-471: Left iris ring (4 cardinal points)
          473-476: Right iris ring (4 cardinal points)
        
        Diameter estimated as max distance across ring.
        
        Returns:
            Tuple of (left_diameter, right_diameter) in normalized coords.
        """
        lm = landmarks.landmark

        def iris_diameter(indices: List[int]) -> float:
            if max(indices) >= len(lm):
                return 0.0
            pts = np.array([[lm[i].x, lm[i].y] for i in indices])
            # Diameter = max pairwise distance
            max_dist = 0.0
            for i in range(len(pts)):
                for j in range(i + 1, len(pts)):
                    d = np.linalg.norm(pts[i] - pts[j])
                    max_dist = max(max_dist, d)
            return float(max_dist)

        # Left iris: 468-471, Right iris: 473-476
        left_d  = iris_diameter([468, 469, 470, 471])
        right_d = iris_diameter([473, 474, 475, 476])

        return left_d, right_d

    def _compute_pupil_velocity(self) -> float:
        """
        Compute rate of change of pupil diameter (px/s).
        
        Slow pupil response to light → fatigue indicator.
        Measured as derivative of diameter signal over 1 second.
        
        Returns:
            Velocity in normalized units/second.
        """
        n = int(TARGET_FPS * 1)  # 1 second window
        left_sig = self._pupil_left_buffer.get_latest(n)

        if left_sig is None or len(left_sig) < 2:
            return 0.0

        # Simple finite difference for velocity
        velocity = np.abs(np.diff(left_sig)).mean() * TARGET_FPS
        return float(velocity)

    def _extract_hand_motion(self, hand_landmarks_list: List) -> None:
        """
        Extract wrist landmark position for tremor analysis.
        
        Uses MediaPipe Hand landmark index 0 (WRIST).
        Pushes X and Y coordinates to tremor buffers.
        """
        if not hand_landmarks_list:
            return

        # Use first detected hand
        hand = hand_landmarks_list[0]
        wrist = hand.landmark[0]  # WRIST landmark

        self._hand_x_buffer.push(float(wrist.x))
        self._hand_y_buffer.push(float(wrist.y))

    def _analyze_tremor(self) -> Tuple[float, float]:
        """
        Analyze tremor characteristics from wrist position signal.
        
        Tremor frequencies:
          4-6 Hz:   Resting tremor (Parkinson's-like)
          6-12 Hz:  Physiological / intention tremor (fatigue)
          > 12 Hz:  Essential tremor
        
        We bandpass-filter wrist X/Y coordinates to isolate
        the tremor frequency band and measure amplitude and
        dominant frequency.
        
        Returns:
            Tuple of (amplitude_pixels, dominant_freq_hz)
        """
        n = int(TARGET_FPS * 5)  # 5-second window

        x_sig = self._hand_x_buffer.get_latest(n)
        y_sig = self._hand_y_buffer.get_latest(n)

        if x_sig is None or y_sig is None:
            return 0.0, 0.0

        # Filter to tremor frequency band
        x_tremor = bandpass_filter(
            x_sig,
            lowcut  = TREMOR_FREQ_MIN_HZ,
            highcut = TREMOR_FREQ_MAX_HZ,
            fs      = TARGET_FPS
        )
        y_tremor = bandpass_filter(
            y_sig,
            lowcut  = TREMOR_FREQ_MIN_HZ,
            highcut = TREMOR_FREQ_MAX_HZ,
            fs      = TARGET_FPS
        )

        # Tremor amplitude = RMS of filtered signal
        amplitude = float(np.sqrt(
            np.mean(x_tremor ** 2) + np.mean(y_tremor ** 2)
        ))

        # Dominant tremor frequency
        combined = np.sqrt(x_tremor ** 2 + y_tremor ** 2)
        freq_hz, _ = estimate_frequency_fft(
            combined, TARGET_FPS,
            TREMOR_FREQ_MIN_HZ, TREMOR_FREQ_MAX_HZ
        )

        return amplitude, freq_hz

    def _compute_fatigue_score(
        self,
        mean_ear:    float,
        microsleep:  bool,
        pupil_vel:   float,
        tremor_amp:  float
    ) -> float:
        """
        Composite fatigue score (0 = alert, 1 = critically fatigued).
        
        Weighted combination of neurological indicators:
          - EAR droopiness (low EAR = heavy eyelids)
          - Microsleep events
          - Slow pupil response
          - Tremor presence
        
        Weights derived from Karolinska Sleepiness Scale correlation.
        """
        # EAR contribution: lower EAR → more fatigue
        ear_fatigue = float(np.clip(1.0 - (mean_ear / 0.3), 0.0, 1.0))

        # Microsleep contribution
        microsleep_fatigue = 1.0 if microsleep else 0.0

        # Pupil velocity: slow response → fatigue
        # Normal pupil velocity during PLR: > 0.002 units/s
        pupil_fatigue = float(np.clip(1.0 - (pupil_vel / 0.002), 0.0, 1.0))

        # Tremor: high amplitude → neuromotor fatigue
        tremor_fatigue = float(np.clip(tremor_amp / 0.01, 0.0, 1.0))

        # Weighted composite
        fatigue = (
            0.35 * ear_fatigue      +
            0.30 * microsleep_fatigue +
            0.20 * pupil_fatigue    +
            0.15 * tremor_fatigue
        )

        return float(np.clip(fatigue, 0.0, 1.0))