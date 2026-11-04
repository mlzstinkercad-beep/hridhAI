"""
pose_normalizer.py — Microgravity Orientation Correction

In microgravity, there is no "up". Crew members can be:
  - Upside-down relative to the camera
  - Sideways (90° or 270°)
  - Tilted at arbitrary angles

This module detects face orientation and rotates frames
to a canonical upright pose before landmark detection.

Algorithm:
  1. Try face detection at 0°, 90°, 180°, 270° rotations
  2. Accept first rotation where face is detected
  3. Smooth rotation decisions over 10 frames to avoid jitter
  4. Use MediaPipe face mesh confidence as quality metric

Why this matters:
  MediaPipe is trained on upright faces. Upside-down faces
  produce low-quality landmarks or fail entirely.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, List
from collections import Counter


class PoseNormalizer:
    """
    Detects and corrects arbitrary face orientations.
    
    Uses a sliding window vote to smooth rotation decisions
    and prevent flickering when orientation is ambiguous.
    """

    def __init__(self, smoothing_window: int = 10):
        """
        Args:
            smoothing_window: Number of frames to average rotation over
        """
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode        = False,
            max_num_faces            = 1,
            refine_landmarks         = False,  # Faster for orientation check
            min_detection_confidence = 0.3,    # Lower threshold for detection
            min_tracking_confidence  = 0.3,
        )
        
        self._rotation_history: List[int] = []
        self._smoothing_window = smoothing_window
        self._last_valid_rotation = 0  # Fallback

    def normalize(self, frame: np.ndarray) -> np.ndarray:
        """
        Detect face orientation and rotate to canonical upright.
        
        Args:
            frame: Input BGR frame (any orientation)
        
        Returns:
            Frame rotated to upright position
        """
        # Test all cardinal rotations
        rotations_to_test = [0, 90, 180, 270]
        best_rotation = None
        best_confidence = 0.0

        for angle in rotations_to_test:
            rotated = self._rotate_image(frame, angle)
            rgb = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
            
            results = self._face_mesh.process(rgb)

            if results.multi_face_landmarks:
                # Face detected at this rotation
                # Estimate confidence from landmark count and positions
                landmarks = results.multi_face_landmarks[0].landmark
                
                # Confidence heuristic: how centered is the face?
                face_center_x = np.mean([lm.x for lm in landmarks])
                face_center_y = np.mean([lm.y for lm in landmarks])
                
                # Penalize off-center faces (person might be partially rotated)
                center_score = 1.0 - (
                    abs(face_center_x - 0.5) + abs(face_center_y - 0.5)
                )
                
                confidence = center_score

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_rotation = angle

        if best_rotation is not None:
            # Add to smoothing history
            self._rotation_history.append(best_rotation)
            if len(self._rotation_history) > self._smoothing_window:
                self._rotation_history.pop(0)
            
            # Use majority vote from history
            rotation_vote = Counter(self._rotation_history).most_common(1)[0][0]
            self._last_valid_rotation = rotation_vote
        else:
            # No face detected in any rotation — use last known good
            rotation_vote = self._last_valid_rotation

        # Apply final rotation
        return self._rotate_image(frame, rotation_vote)

    @staticmethod
    def _rotate_image(image: np.ndarray, angle: int) -> np.ndarray:
        """
        Rotate image by angle (0, 90, 180, 270 only).
        
        Uses OpenCV's optimized rotate functions (no interpolation artifacts).
        """
        if angle == 0:
            return image
        elif angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            # Arbitrary angle (shouldn't happen with cardinal-only testing)
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            return cv2.warpAffine(image, M, (w, h))