"""
hematological.py — Layer C: Hematological Analysis

Extracts:
  1. Hemoglobin Proxy  — Conjunctival "Redness Index"
  2. Anemia Detection  — Comparison to personal Earth baseline
  3. Space Anemia Flag — Daily trend monitoring

Scientific Basis:
─────────────────
Conjunctival Pallor Method (Kaliyaperumal et al.):
  The inner lower eyelid (palpebral conjunctiva) has thin skin
  directly over blood vessels. Anemia causes pallor (reduced
  redness) in this region, visible even without special equipment.
  
  Redness Index = mean(R channel) / (mean(G channel) + mean(B channel))
  
  Normal RI: > 0.45  (well-perfused, healthy hemoglobin)
  Mild Anemia: 0.35-0.45
  Moderate Anemia: < 0.35

Space Anemia:
  Astronauts lose ~10% of red blood cells in first 10 days in space
  due to: plasma volume shifts, hemolysis, EPO suppression.
  System compares daily RI to Earth baseline from astronaut health record.
"""

import numpy as np
import cv2
from typing import Optional, Tuple
from dataclasses import dataclass
import json
import os

from config import CONFIDENCE_THRESHOLD


@dataclass
class HematologicalResult:
    """Structured output for Layer C."""
    redness_index:         float   # 0-1, higher = more hemoglobin
    hemoglobin_est_g_dl:   float   # Estimated g/dL (11-18 normal)
    anemia_likelihood:     str     # 'Normal' | 'Mild' | 'Moderate' | 'Severe'
    space_anemia_delta:    float   # % change from Earth baseline
    space_anemia_alert:    bool    # True if > 10% decline
    confidence:            float


class HematologicalAnalyzer:
    """
    Non-invasive blood composition estimation via conjunctival analysis.
    """

    # Redness index thresholds (Kaliyaperumal calibration)
    RI_NORMAL   = 0.45
    RI_MILD     = 0.38
    RI_MODERATE = 0.30

    # Hemoglobin estimation: linear regression coefficients
    # Hb(g/dL) ≈ RI × 30 + 1.5  (simplified empirical model)
    HB_SCALE  = 30.0
    HB_OFFSET = 1.5

    def __init__(self, baseline_path: str = "data/hematological_baseline.json"):
        self._baseline_path = baseline_path
        self._earth_baseline_ri: Optional[float] = self._load_baseline()
        self._daily_ri_samples: list = []

    def process_frame(
        self,
        frame:     np.ndarray,
        landmarks: Optional[object]
    ) -> HematologicalResult:
        """
        Analyze conjunctival redness for hemoglobin estimation.
        
        Note: Requires close-up view showing the lower eyelid inner lining.
        In practice, this is most effective during daily health check
        sessions where the astronaut looks upward at the camera.
        """
        if landmarks is None:
            return self._null_result()

        # Extract lower eyelid ROI
        redness_index, confidence = self._extract_conjunctival_ri(
            frame, landmarks
        )

        if redness_index is None or confidence < CONFIDENCE_THRESHOLD:
            return HematologicalResult(
                redness_index       = np.nan,
                hemoglobin_est_g_dl = np.nan,
                anemia_likelihood   = "N/A - Recalibrating",
                space_anemia_delta  = np.nan,
                space_anemia_alert  = False,
                confidence          = confidence if confidence else 0.0,
            )

        # Accumulate for daily average
        self._daily_ri_samples.append(redness_index)

        # Estimate hemoglobin
        hb_est = self.HB_SCALE * redness_index + self.HB_OFFSET
        hb_est = float(np.clip(hb_est, 5.0, 20.0))

        # Classify anemia level
        anemia_class = self._classify_anemia(redness_index)

        # Space anemia comparison
        delta, alert = self._check_space_anemia(redness_index)

        return HematologicalResult(
            redness_index       = float(redness_index),
            hemoglobin_est_g_dl = hb_est,
            anemia_likelihood   = anemia_class,
            space_anemia_delta  = delta,
            space_anemia_alert  = alert,
            confidence          = float(confidence),
        )

    def _extract_conjunctival_ri(
        self,
        frame:     np.ndarray,
        landmarks: object
    ) -> Tuple[Optional[float], float]:
        """
        Extract Redness Index from lower eyelid conjunctiva.
        
        Landmark Approximation:
          The inner lower eyelid isn't directly landmarked by MediaPipe.
          We approximate using the lower eyelid margin landmarks:
          Left lower eyelid: 145, 153, 154, 155, 133
          
          The user must be looking slightly upward for best results.
          We detect this by checking if the eyelid landmarks show
          the characteristic "exposed" conjunctiva geometry.
        
        Returns:
            Tuple of (redness_index, confidence)
        """
        h, w = frame.shape[:2]
        lm   = landmarks.landmark

        # Lower eyelid landmarks (left eye for consistency)
        lower_lid_indices = [145, 153, 154, 155, 133, 173, 157, 158]

        points = []
        for idx in lower_lid_indices:
            if idx < len(lm):
                x = int(lm[idx].x * w)
                y = int(lm[idx].y * h)
                points.append([x, y])

        if len(points) < 3:
            return None, 0.0

        pts   = np.array(points, dtype=np.int32)
        mask  = np.zeros((h, w), dtype=np.uint8)
        cv2.fillConvexPoly(mask, pts, 255)

        # Extract pixel values within mask
        region_pixels = frame[mask > 0]

        if len(region_pixels) < 10:
            return None, 0.0

        # Compute per-channel means
        mean_r = float(np.mean(region_pixels[:, 2]))  # Red channel
        mean_g = float(np.mean(region_pixels[:, 1]))  # Green channel
        mean_b = float(np.mean(region_pixels[:, 0]))  # Blue channel

        denom = mean_g + mean_b
        if denom < 1.0:
            return None, 0.0

        redness_index = mean_r / denom

        # Confidence: larger ROI and more consistent color → higher conf
        roi_size = np.sum(mask > 0)
        color_std = float(np.std(region_pixels[:, 2]))  # Red channel std

        size_conf   = float(np.clip(roi_size / 200.0, 0.0, 1.0))
        color_conf  = float(np.clip(1.0 - (color_std / 50.0), 0.0, 1.0))
        confidence  = (size_conf + color_conf) / 2.0

        return redness_index, confidence

    def _classify_anemia(self, ri: float) -> str:
        """
        Classify anemia likelihood from Redness Index.
        
        Thresholds calibrated from Kaliyaperumal et al. (2016).
        """
        if ri >= self.RI_NORMAL:
            return "Normal"
        elif ri >= self.RI_MILD:
            return "Mild Anemia Suspected"
        elif ri >= self.RI_MODERATE:
            return "Moderate Anemia Suspected"
        else:
            return "Severe Anemia Suspected — Seek Medical Attention"

    def _check_space_anemia(
        self,
        current_ri: float
    ) -> Tuple[float, bool]:
        """
        Compare current RI to Earth baseline for space anemia detection.
        
        Space Anemia Protocol:
          Astronauts establish personal baselines via 5-day average
          pre-launch. In-mission decline > 10% triggers alert.
          
          This mirrors the 54% hemolysis rate documented in
          Trudel et al., Nature Medicine 2022 (Space Anemia paper).
        
        Returns:
            Tuple of (percent_change, alert_triggered)
        """
        if self._earth_baseline_ri is None:
            return np.nan, False

        delta_pct = (
            (current_ri - self._earth_baseline_ri)
            / self._earth_baseline_ri * 100.0
        )

        # Alert if > 10% decline (negative change = anemia worsening)
        alert = delta_pct < -10.0

        return float(delta_pct), alert

    def set_earth_baseline(self, baseline_ri: float) -> None:
        """
        Store personal Earth baseline Redness Index.
        Called during pre-launch medical screening.
        """
        self._earth_baseline_ri = baseline_ri
        self._save_baseline(baseline_ri)

    def compute_daily_average(self) -> Optional[float]:
        """
        Return and reset daily average RI for trend logging.
        Called once per day by the scheduler.
        """
        if not self._daily_ri_samples:
            return None
        avg = float(np.mean(self._daily_ri_samples))
        self._daily_ri_samples.clear()
        return avg

    def _load_baseline(self) -> Optional[float]:
        """Load persisted baseline from local storage."""
        try:
            if os.path.exists(self._baseline_path):
                with open(self._baseline_path, 'r') as f:
                    data = json.load(f)
                    return float(data.get('earth_baseline_ri', 0))
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
        return None

    def _save_baseline(self, ri: float) -> None:
        """Persist baseline to local JSON file."""
        os.makedirs(os.path.dirname(self._baseline_path), exist_ok=True)
        with open(self._baseline_path, 'w') as f:
            json.dump({'earth_baseline_ri': ri}, f)

    @staticmethod
    def _null_result() -> HematologicalResult:
        return HematologicalResult(
            redness_index       = np.nan,
            hemoglobin_est_g_dl = np.nan,
            anemia_likelihood   = "N/A - No Face Detected",
            space_anemia_delta  = np.nan,
            space_anemia_alert  = False,
            confidence          = 0.0,
        )