"""
ring_buffer.py

A fixed-size, thread-safe ring buffer using numpy arrays.
Once full, oldest data is overwritten. No dynamic allocation.
This is the CORE memory-safety mechanism — prevents RAM growth
during the 24/7 continuous operation requirement.

Design Rationale:
  - Pre-allocates all memory at startup (no runtime malloc)
  - Old frames are overwritten (never accumulate)
  - Lock-free reads via atomic index (single producer/consumer)
"""

import numpy as np
import threading
from typing import Optional


class RingBuffer:
    """
    Pre-allocated circular buffer for time-series signal data.
    
    Memory footprint: fixed at (capacity × dtype_size) bytes.
    Example: 900 floats × 4 bytes = 3,600 bytes per signal channel.
    """

    def __init__(self, capacity: int, dtype=np.float32):
        """
        Args:
            capacity: Maximum number of samples to store.
                      Older samples are silently overwritten.
            dtype:    NumPy data type for storage efficiency.
        """
        self._capacity = capacity
        self._buffer   = np.zeros(capacity, dtype=dtype)
        self._head     = 0          # Next write position
        self._count    = 0          # Valid samples currently stored
        self._lock     = threading.Lock()

    def push(self, value: float) -> None:
        """
        Add one sample. O(1) time, O(1) memory — no allocation.
        Thread-safe via mutex.
        """
        with self._lock:
            self._buffer[self._head] = value
            self._head  = (self._head + 1) % self._capacity
            self._count = min(self._count + 1, self._capacity)

    def get_latest(self, n: int) -> Optional[np.ndarray]:
        """
        Retrieve the most recent `n` samples in chronological order.
        
        Returns:
            numpy array of shape (n,), or None if not enough data.
        
        Why copy? The caller may hold the array while new data arrives;
        without copy, a race condition could corrupt the signal mid-FFT.
        """
        with self._lock:
            if self._count < n:
                return None  # Not enough data yet

            # Reconstruct chronological order from circular indices
            end   = self._head
            start = (end - n) % self._capacity

            if start < end:
                return self._buffer[start:end].copy()
            else:
                # Buffer has wrapped around — stitch two slices
                return np.concatenate([
                    self._buffer[start:],
                    self._buffer[:end]
                ])

    def get_all(self) -> np.ndarray:
        """Return all valid samples in chronological order."""
        with self._lock:
            n = self._count
            if n == 0:
                return np.array([], dtype=self._buffer.dtype)
            return self.get_latest(n)

    @property
    def count(self) -> int:
        """Number of valid samples currently stored."""
        with self._lock:
            return self._count

    @property
    def is_full(self) -> bool:
        with self._lock:
            return self._count == self._capacity

    def clear(self) -> None:
        """Reset without deallocating — keeps memory footprint fixed."""
        with self._lock:
            self._buffer[:] = 0.0
            self._head  = 0
            self._count = 0