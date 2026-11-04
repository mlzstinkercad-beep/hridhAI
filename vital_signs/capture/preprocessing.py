"""
preprocessing.py

Handles all frame preprocessing before biological analysis.
This is the FIRST pipeline stage — every frame passes through here.

Key Challenges Solved:
  1. Lighting range 10-10,000 lux → must normalize to consistent range
  2. Microgravity: face can be upside-down or sideways
  3. Motion blur from floating at 1.5 m/s

Algorithm: CLAHE (Contrast Limited Adaptive Histogram Equalization)
  - Better than standard HE: limits over-amplification in bright regions
  - Adaptive: operates on local tiles, handles uneven ISS lighting
  - Critical for rPPG: inconsistent brightness → inconsistent green channel
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Optional
from config import CLAHE_CLIP_LIMIT, CLAHE_TILE_GRID


class FramePreprocessor:
    """
    Preprocessing pipeline: normalize → denoise → detect orientation.
    
    Thread Safety: Each camera thread gets its own preprocessor instance.
    """

    def __init__(self):
        # CLAHE object — reuse to avoid repeated initialization overhead
        self._clahe = cv2.createCLAHE(
            clipLimit    = CLAHE_CLIP_LIMIT,
            tileGridSize = CLAHE_TILE_GRID
        )
        
        # MediaPipe Face Mesh for orientation detection
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode        = False,
            max_num_faces            = 1,
            refine_landmarks         = True,  # Iris landmarks for pupillometry
            min_detection_confidence = 0.5,
            min_tracking_confidence  = 0.5
        )
        
        # Orientation history for smoothing (avoids flip-flop jitter)
        self._orientation_buffer = []
        self._orientation_window = 10

    def process(self, frame: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Full preprocessing pipeline for one frame.
        
        Args:
            frame: Raw BGR frame from camera.
        
        Returns:
            Tuple of:
              - normalized_frame: Lighting-corrected BGR frame
              - lux_estimate:     Estimated scene brightness (lux proxy)
        """
        # ── Step 1: Estimate and log lighting conditions ──────────────
        lux_estimate = self._estimate_lux(frame)

        # ── Step 2: CLAHE normalization (per-channel for color fidelity) 
        normalized = self._apply_clahe(frame)

        # ── Step 3: Mild Gaussian blur to reduce sensor noise ─────────
        # Kernel (3,3) — small enough to preserve pulse signal detail
        denoised = cv2.GaussianBlur(normalized, (3, 3), 0)

        # ── Step 4: Orientation correction for microgravity ───────────
        corrected = self._correct_orientation(denoised)

        return corrected, lux_estimate

    def _apply_clahe(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE independently to each BGR channel.
        
        Why per-channel?
          rPPG uses the Green channel specifically. If we convert to
          grayscale for CLAHE we lose the R/G/B ratio information
          needed for SpO2 calculation.
        """
        b, g, r = cv2.split(frame)
        b_eq = self._clahe.apply(b)
        g_eq = self._clahe.apply(g)
        r_eq = self._clahe.apply(r)
        return cv2.merge([b_eq, g_eq, r_eq])

    def _estimate_lux(self, frame: np.ndarray) -> float:
        """
        Estimate scene luminance as a proxy for lux.
        
        True lux requires a dedicated sensor. This proxy uses the
        mean luminance of the Y channel (YCrCb color space) as a
        confidence modifier: very dark or very bright scenes reduce
        rPPG signal confidence.
        
        Returns:
            Proxy value in range [0, 255], loosely correlating to lux.
        """
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        y_channel = ycrcb[:, :, 0]
        return float(np.mean(y_channel))

    def _correct_orientation(self, frame: np.ndarray) -> np.ndarray:
        """
        Detect and correct for microgravity face orientations.
        
        In the ISS, crew float in arbitrary orientations. Standard
        facial detection fails on upside-down faces. We detect the
        face in all 4 orientations and rotate to upright canonical form.
        
        Strategy:
          - Try 0°, 90°, 180°, 270° rotations
          - Accept first rotation where face mesh is detected
          - Smooth over 10 frames to avoid jitter
        
        Returns:
            Frame rotated to canonical upright orientation.
        """
        rotations = [0, 90, 180, 270]
        
        for angle in rotations:
            rotated = self._rotate_frame(frame, angle)
            rgb     = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
            results = self._face_mesh.process(rgb)
            
            if results.multi_face_landmarks:
                # Smooth orientation decisions
                self._orientation_buffer.append(angle)
                if len(self._orientation_buffer) > self._orientation_window:
                    self._orientation_buffer.pop(0)
                
                # Use majority vote over window to avoid flickering
                from collections import Counter
                best_angle = Counter(self._orientation_buffer).most_common(1)[0][0]
                return self._rotate_frame(frame, best_angle)
        
        # No face detected in any orientation — return original
        return frame

    @staticmethod
    def _rotate_frame(frame: np.ndarray, angle: int) -> np.ndarray:
        """Rotate frame by angle degrees (0, 90, 180, 270 only)."""
        if angle == 0:
            return frame
        elif angle == 90:
            return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(frame, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return frame