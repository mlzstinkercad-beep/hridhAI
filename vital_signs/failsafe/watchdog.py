"""
watchdog.py — System Watchdog & Resource Monitor

Enforces the "Space-Hardened" computational constraints:
  - CPU usage ≤ 25%
  - RAM usage ≤ 512 MB
  - Vitals update rate ≥ 1 Hz with ≤ 200ms lag

The watchdog runs as a separate thread and can:
  1. Throttle processing (skip frames) if CPU exceeds limit
  2. Force garbage collection if RAM approaches limit
  3. Log violations for ground team review
  4. Trigger emergency shutdown if resources critically exceed limits

Design: Separate thread with 1-second monitoring interval.
        Uses psutil for cross-platform resource measurement.
"""

import threading
import time
import gc
import os
import psutil
import logging
from typing import Callable, Optional
from dataclasses import dataclass, field

from config import MAX_CPU_PERCENT, MAX_RAM_MB, VITALS_UPDATE_HZ, MAX_LAG_MS


logger = logging.getLogger("SpaceMed.Watchdog")


@dataclass
class SystemHealth:
    """Snapshot of current system resource usage."""
    cpu_percent:     float = 0.0
    ram_mb:          float = 0.0
    last_vitals_lag_ms: float = 0.0
    frame_skip_count:   int   = 0
    gc_trigger_count:   int   = 0
    violations:         list  = field(default_factory=list)


class SystemWatchdog(threading.Thread):
    """
    Background thread monitoring CPU, RAM, and timing constraints.
    Implements adaptive frame skipping to stay within CPU budget.
    """

    def __init__(
        self,
        throttle_callback: Optional[Callable[[int], None]] = None
    ):
        """
        Args:
            throttle_callback: Called with skip_count when CPU > limit.
                               The orchestrator uses this to skip N frames.
        """
        super().__init__(daemon=True, name="WatchdogThread")
        self._process          = psutil.Process(os.getpid())
        self._health           = SystemHealth()
        self._throttle_cb      = throttle_callback
        self._stop_event       = threading.Event()
        self._lock             = threading.Lock()
        self._last_vital_time  = time.monotonic()
        
        # Adaptive frame skip: 0 = process every frame, N = skip N frames
        self._frame_skip = 0

    def run(self) -> None:
        """Main watchdog loop — runs every second."""
        logger.info("Watchdog started")
        
        while not self._stop_event.is_set():
            loop_start = time.monotonic()
            
            self._check_cpu()
            self._check_ram()
            self._check_timing()
            self._log_health()
            
            # Run exactly every 1 second
            elapsed = time.monotonic() - loop_start
            time.sleep(max(0.0, 1.0 - elapsed))

    def _check_cpu(self) -> None:
        """
        Monitor CPU and throttle if over budget.
        
        Adaptive throttling strategy:
          CPU 25-30%: Skip every other frame (process 15 FPS instead of 30)
          CPU 30-40%: Skip 2 of 3 frames (10 FPS)
          CPU > 40%:  Skip 3 of 4 frames (7.5 FPS) + log critical warning
        
        This maintains vitals updates at ≥1 Hz even at 7.5 FPS.
        """
        cpu = self._process.cpu_percent(interval=None)

        with self._lock:
            self._health.cpu_percent = cpu

        if cpu > MAX_CPU_PERCENT * 1.6:  # > 40%
            new_skip = 3
            severity = "CRITICAL"
        elif cpu > MAX_CPU_PERCENT * 1.2:  # > 30%
            new_skip = 2
            severity = "WARNING"
        elif cpu > MAX_CPU_PERCENT:  # > 25%
            new_skip = 1
            severity = "INFO"
        else:
            new_skip = 0
            severity = None

        if new_skip != self._frame_skip:
            self._frame_skip = new_skip
            if severity:
                logger.warning(
                    f"[{severity}] CPU: {cpu:.1f}% > {MAX_CPU_PERCENT}% "
                    f"limit. Frame skip → {new_skip}"
                )
            if self._throttle_cb and new_skip >= 0:
                self._throttle_cb(new_skip)

    def _check_ram(self) -> None:
        """
        Monitor RAM and force garbage collection before limit.
        
        Strategy:
          RAM > 400 MB (80% of 512 limit): Trigger gc.collect()
          RAM > 500 MB (97.5% of limit):   Force full GC + log critical
          RAM > 512 MB: Emergency → would crash anyway, log + alert crew
        """
        ram_bytes = self._process.memory_info().rss
        ram_mb    = ram_bytes / (1024 * 1024)

        with self._lock:
            self._health.ram_mb = ram_mb

        if ram_mb > MAX_RAM_MB:
            logger.critical(
                f"RAM LIMIT EXCEEDED: {ram_mb:.1f}MB > {MAX_RAM_MB}MB! "
                f"System may crash."
            )
        elif ram_mb > MAX_RAM_MB * 0.975:
            logger.error(
                f"RAM CRITICAL: {ram_mb:.1f}MB. Forcing full GC."
            )
            gc.collect(generation=2)
            with self._lock:
                self._health.gc_trigger_count += 1
        elif ram_mb > MAX_RAM_MB * 0.80:
            logger.warning(
                f"RAM HIGH: {ram_mb:.1f}MB. Triggering GC."
            )
            gc.collect(generation=0)

    def _check_timing(self) -> None:
        """
        Verify vitals are being updated within the 200ms lag requirement.
        
        The orchestrator calls report_vital_update() after each output.
        If more than 1.2 seconds pass without an update, log the violation.
        """
        now = time.monotonic()
        lag_ms = (now - self._last_vital_time) * 1000

        with self._lock:
            self._health.last_vitals_lag_ms = lag_ms

        if lag_ms > (1000 / VITALS_UPDATE_HZ + MAX_LAG_MS):
            logger.warning(
                f"TIMING VIOLATION: {lag_ms:.0f}ms since last vitals update "
                f"(limit: {1000/VITALS_UPDATE_HZ + MAX_LAG_MS:.0f}ms)"
            )

    def report_vital_update(self) -> None:
        """Called by orchestrator after each successful vitals output."""
        self._last_vital_time = time.monotonic()

    def _log_health(self) -> None:
        """Periodic health summary to log file."""
        with self._lock:
            h = self._health
        logger.debug(
            f"Health: CPU={h.cpu_percent:.1f}% RAM={h.ram_mb:.0f}MB "
            f"Lag={h.last_vitals_lag_ms:.0f}ms Skip={self._frame_skip}"
        )

    def get_frame_skip(self) -> int:
        """Current frame skip setting (used by capture loop)."""
        return self._frame_skip

    def get_health(self) -> SystemHealth:
        """Thread-safe snapshot of current system health."""
        with self._lock:
            return SystemHealth(**self._health.__dict__)

    def stop(self) -> None:
        """Graceful shutdown."""
        self._stop_event.set()