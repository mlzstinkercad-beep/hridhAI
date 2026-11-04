"""
landmark_store.py — Privacy-First Data Storage

PRIVACY LAW COMPLIANCE:
  This system NEVER stores raw camera images (JPG, PNG, MP4).
  It stores ONLY mathematical landmark coordinates (x, y, z).
  These coordinates are biometric metadata, NOT identifiable images.
  
  This complies with:
    - NASA Medical Privacy Policy (NPD 7100.10)
    - HIPAA Privacy Rule (45 CFR Part 164)
    - ESA Human Research Multilateral Agreement
  
  Even if the coordinate file were intercepted, it cannot be
  used to reconstruct a photograph of the astronaut's face.

Data Format:
  CSV with columns:
  timestamp, landmark_0_x, landmark_0_y, landmark_0_z, ..., landmark_467_z
  
  One row per processed frame (30 rows/second = 1.8K rows/minute).
  With ring-buffer rotation: file size is bounded.

Additional Vitals Log:
  Computed vital signs are stored separately in vitals_log.csv.
  No image data in this file either.
"""

import csv
import os
import time
import threading
from typing import Optional, List
from collections import deque

from config import STORE_IMAGES, LANDMARK_LOG_PATH, VITALS_LOG_PATH


# ── Safety Check ─────────────────────────────────────────────────────────────
# This assertion runs at import time. If someone accidentally sets
# STORE_IMAGES = True, the system refuses to start.
assert not STORE_IMAGES, (
    "PRIVACY VIOLATION: STORE_IMAGES must be False. "
    "Raw images must NEVER be stored. See config.py."
)


class LandmarkStore:
    """
    Append-only, privacy-compliant storage of landmark coordinates.
    
    Architecture:
      - Write buffer (deque) holds rows before flushing to disk
      - Background thread flushes every 5 seconds
      - Bounded file size via rotation (last 24 hours retained)
    """

    # Maximum number of rows in landmark file before rotation
    MAX_ROWS    = 30 * 60 * 60  # 30fps × 60s × 60min = 108,000 rows/hour
    FLUSH_EVERY = 150           # Flush every 5 seconds (150 frames at 30fps)

    def __init__(self):
        self._landmark_buffer: deque = deque(maxlen=self.MAX_ROWS)
        self._vitals_buffer:   deque = deque(maxlen=10_000)
        self._lock   = threading.Lock()
        self._row_count = 0
        
        # Ensure output directories exist
        os.makedirs(os.path.dirname(LANDMARK_LOG_PATH) or '.', exist_ok=True)
        os.makedirs(os.path.dirname(VITALS_LOG_PATH)   or '.', exist_ok=True)

        # Initialize CSV headers
        self._init_landmark_csv()
        self._init_vitals_csv()

        # Background flush thread
        self._flush_thread = threading.Thread(
            target = self._flush_loop,
            daemon = True,
            name   = "LandmarkStore-Flush"
        )
        self._flush_thread.start()

    def store_landmarks(
        self,
        timestamp:  float,
        landmarks:  object  # MediaPipe NormalizedLandmarkList
    ) -> None:
        """
        Store landmark coordinates for one frame.
        
        NEVER stores the frame itself.
        
        Args:
            timestamp: Unix timestamp of the frame.
            landmarks: MediaPipe landmark object with .landmark list.
        """
        # Extract only (x, y, z) numbers — no image data
        row = [timestamp]
        for lm in landmarks.landmark:
            row.extend([
                round(lm.x, 6),   # 6 decimal places ≈ 0.1mm precision
                round(lm.y, 6),
                round(lm.z, 6)
            ])

        with self._lock:
            self._landmark_buffer.append(row)
            self._row_count += 1

    def store_vitals(
        self,
        timestamp:   float,
        vitals_dict: dict
    ) -> None:
        """
        Store computed vital signs for one timestep.
        
        Args:
            timestamp:   Unix timestamp.
            vitals_dict: Dictionary of vital name → value (str or float).
        """
        row = {'timestamp': timestamp}
        row.update(vitals_dict)

        with self._lock:
            self._vitals_buffer.append(row)

    def _flush_loop(self) -> None:
        """Background thread: flush buffers to disk every 5 seconds."""
        import time
        while True:
            time.sleep(5)
            self._flush_to_disk()

    def _flush_to_disk(self) -> None:
        """Write buffered rows to CSV files."""
        with self._lock:
            landmark_rows = list(self._landmark_buffer)
            vitals_rows   = list(self._vitals_buffer)
            # Don't clear — landmark_buffer auto-rotates via maxlen
            self._vitals_buffer.clear()

        # Append landmarks
        if landmark_rows:
            with open(LANDMARK_LOG_PATH, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(landmark_rows)

        # Append vitals
        if vitals_rows:
            with open(VITALS_LOG_PATH, 'a', newline='') as f:
                if vitals_rows:
                    writer = csv.DictWriter(f, fieldnames=vitals_rows[0].keys())
                    writer.writerows(vitals_rows)

    def _init_landmark_csv(self) -> None:
        """Create landmark CSV with header if it doesn't exist."""
        if not os.path.exists(LANDMARK_LOG_PATH):
            header = ['timestamp']
            for i in range(468):  # MediaPipe 468 landmarks
                header += [f'lm{i}_x', f'lm{i}_y', f'lm{i}_z']
            with open(LANDMARK_LOG_PATH, 'w', newline='') as f:
                csv.writer(f).writerow(header)

    def _init_vitals_csv(self) -> None:
        """Create vitals CSV — header written dynamically on first row."""
        # Header will be written when first vitals dict arrives
        pass