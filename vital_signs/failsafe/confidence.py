"""
confidence.py — Confidence Scoring & Failsafe Output

This module enforces the core safety rule:
  IF confidence < 0.60 → output "N/A - Recalibrating"
  NEVER output a low-confidence number as if it were accurate.

In clinical settings, a wrong number is worse than no number.
An astronaut acting on a falsely-low SpO₂ reading could
unnecessarily trigger an emergency response.

Architecture: ConfidenceGate wraps every vital sign output.
  The gate either passes the value through or replaces it with
  the safe "N/A" sentinel, plus a human-readable reason.
"""

from dataclasses import dataclass
from typing import Union, Optional, Any
import numpy as np
from config import CONFIDENCE_THRESHOLD


# Sentinel type: either a float or an explanation string
VitalOutput = Union[float, str]


@dataclass
class GatedVital:
    """
    A vital sign that has passed through the confidence gate.
    
    Fields:
        value:       The actual float value, or "N/A - <reason>" string.
        confidence:  Raw confidence score (0-1) for logging.
        is_valid:    True if the value is a real measurement.
        reason:      Human-readable explanation if invalid.
    """
    value:      VitalOutput
    confidence: float
    is_valid:   bool
    reason:     str = ""


class ConfidenceGate:
    """
    Wraps vital sign outputs with confidence-based validation.
    
    Usage:
        gate = ConfidenceGate()
        hr_output = gate.check(
            value=72.5,
            confidence=0.45,
            label="Heart Rate"
        )
        # Returns GatedVital(value="N/A - Recalibrating: Heart Rate",
        #                    confidence=0.45, is_valid=False)
    """

    # Specific reasons for low confidence (for diagnostic logging)
    REASONS = {
        'low_light':    "Low light conditions",
        'motion':       "Excessive motion artifact",
        'occlusion':    "Face/ROI occluded",
        'insufficient': "Insufficient signal samples",
        'default':      "Recalibrating",
    }

    def __init__(self, threshold: float = CONFIDENCE_THRESHOLD):
        self._threshold = threshold
        self._recal_count = 0  # Track consecutive failures for escalation

    def check(
        self,
        value:      float,
        confidence: float,
        label:      str,
        reason_key: str = 'default'
    ) -> GatedVital:
        """
        Gate a single vital sign measurement.
        
        Args:
            value:      Computed vital sign value.
            confidence: Quality score (0.0 - 1.0).
            label:      Human-readable vital name (for log message).
            reason_key: Key into REASONS dict for specific explanation.
        
        Returns:
            GatedVital with either the real value or "N/A" message.
        """
        # NaN values always fail the gate
        if np.isnan(value) if isinstance(value, float) else False:
            confidence = 0.0

        if confidence >= self._threshold:
            self._recal_count = 0
            return GatedVital(
                value      = float(value),
                confidence = confidence,
                is_valid   = True,
                reason     = ""
            )
        else:
            self._recal_count += 1
            reason_str = self.REASONS.get(reason_key, self.REASONS['default'])
            na_message = f"N/A - {reason_str}: {label}"

            return GatedVital(
                value      = na_message,
                confidence = confidence,
                is_valid   = False,
                reason     = reason_str
            )

    def check_all(
        self,
        vitals_dict: dict,
        confidence:  float,
        reason_key:  str = 'default'
    ) -> dict:
        """
        Gate an entire dictionary of vitals with a single confidence score.
        
        Used when one quality metric (e.g., face detection confidence)
        applies to multiple derived measurements.
        """
        return {
            key: self.check(val, confidence, key, reason_key)
            for key, val in vitals_dict.items()
        }

    @property
    def consecutive_failures(self) -> int:
        """Number of consecutive confidence failures. Escalate if > 10."""
        return self._recal_count

    def should_escalate(self) -> bool:
        """
        True if the system has been recalibrating for too long.
        Triggers sensor fusion fallback (WiFi-CSI).
        """
        return self._recal_count > 30  # ~30 seconds at 1Hz