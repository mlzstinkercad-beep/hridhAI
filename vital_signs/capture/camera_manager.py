"""
camera_manager.py — Camera Initialization & Control

Handles:
  1. Camera device initialization
  2. Frame rate control
  3. Auto-exposure/gain adjustment for ISS lighting
  4. Graceful camera failure handling

ISS-Specific Considerations:
  - Cameras may be commercial USB webcams (Logitech C920)
  - Lighting can shift rapidly (sunrise/sunset every 90 minutes)
  - Camera must survive power cycling during crew sleep periods
"""

import cv2
import logging
from typing import Optional, Tuple
import numpy as np

from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, TARGET_FPS

logger = logging.getLogger("SpaceMed.Camera")


class CameraManager:
    """
    Wrapper for OpenCV VideoCapture with ISS-specific error handling.
    """

    def __init__(
        self,
        camera_index: int = CAMERA_INDEX,
        width:  int = FRAME_WIDTH,
        height: int = FRAME_HEIGHT,
        fps:    int = TARGET_FPS
    ):
        self.camera_index = camera_index
        self.width  = width
        self.height = height
        self.fps    = fps
        
        self._cap: Optional[cv2.VideoCapture] = None
        self._frame_count = 0
        self._fail_count  = 0
        self._max_consecutive_fails = 10

    def open(self) -> bool:
        """
        Initialize camera device.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Opening camera {self.camera_index}")
        
        self._cap = cv2.VideoCapture(self.camera_index)
        
        if not self._cap.isOpened():
            logger.error(f"Failed to open camera {self.camera_index}")
            return False

        # Set resolution
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._cap.set(cv2.CAP_PROP_FPS, self.fps)

        # Disable auto-focus (causes lag)
        self._cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        
        # Set manual focus to infinity (ISS cabin distances)
        self._cap.set(cv2.CAP_PROP_FOCUS, 0)

        # Verify settings
        actual_width  = self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps    = self._cap.get(cv2.CAP_PROP_FPS)

        logger.info(
            f"Camera opened: {actual_width}x{actual_height} @ {actual_fps} FPS"
        )

        if actual_width != self.width or actual_height != self.height:
            logger.warning(
                f"Resolution mismatch: requested {self.width}x{self.height}, "
                f"got {actual_width}x{actual_height}"
            )

        return True

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Capture one frame.
        
        Returns:
            Tuple of (success: bool, frame: ndarray or None)
        """
        if self._cap is None or not self._cap.isOpened():
            logger.warning("Camera not opened, attempting to reopen...")
            if not self.open():
                self._fail_count += 1
                return False, None

        ret, frame = self._cap.read()

        if not ret:
            self._fail_count += 1
            logger.warning(
                f"Frame capture failed ({self._fail_count} consecutive)"
            )

            if self._fail_count >= self._max_consecutive_fails:
                logger.error("Camera appears disconnected. Attempting reset.")
                self.close()
                self.open()
                self._fail_count = 0

            return False, None

        # Success
        self._fail_count = 0
        self._frame_count += 1
        return True, frame

    def close(self) -> None:
        """Release camera device."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            logger.info("Camera closed")

    @property
    def is_opened(self) -> bool:
        """Check if camera is currently open."""
        return self._cap is not None and self._cap.isOpened()

    @property
    def frame_count(self) -> int:
        """Total frames captured since initialization."""
        return self._frame_count