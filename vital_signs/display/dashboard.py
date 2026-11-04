"""
dashboard.py — Real-Time Vitals Dashboard

Renders a heads-up display (HUD) overlay showing all vital signs
in a color-coded, easy-to-read format for quick astronaut assessment.

Display Zones:
  ┌─────────────────────────────────────────────┐
  │ LAYER A: HEMODYNAMIC        [Green/Yellow/Red]│
  │ HR: 72 BPM | HRV: 45ms | BP: 120/80         │
  ├─────────────────────────────────────────────┤
  │ LAYER B: RESPIRATORY                        │
  │ BR: 16 BrPM | SpO₂: 98%                     │
  ├─────────────────────────────────────────────┤
  │ LAYER C: HEMATOLOGICAL                      │
  │ Hb Est: 14.2 g/dL | Status: Normal          │
  ├─────────────────────────────────────────────┤
  │ LAYER D: NEUROLOGICAL                       │
  │ Fatigue: 0.23 | Blinks: 18/min              │
  ├─────────────────────────────────────────────┤
  │ SYSTEM STATUS                               │
  │ Source: RGB Camera | CPU: 22% | RAM: 384MB  │
  └─────────────────────────────────────────────┘

Color Coding:
  Green:  Normal range, high confidence
  Yellow: Borderline or medium confidence
  Red:    Out of range or low confidence
  Gray:   N/A / Recalibrating

Output Modes:
  1. OpenCV window (for ground testing)
  2. Terminal/SSH text output (for headless ISS deployment)
  3. JSON log file (for Mission Control downlink)
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple
import json
import os
from datetime import datetime

from config import CONFIDENCE_THRESHOLD


class Dashboard:
    """
    Multi-modal vital signs display system.
    
    Supports three simultaneous output modes for redundancy.
    """

    # Color scheme (BGR format for OpenCV)
    COLOR_BG       = (20, 20, 20)      # Dark gray background
    COLOR_NORMAL   = (0, 255, 0)       # Green
    COLOR_WARNING  = (0, 215, 255)     # Yellow
    COLOR_CRITICAL = (0, 0, 255)       # Red
    COLOR_NA       = (128, 128, 128)   # Gray
    COLOR_TEXT     = (255, 255, 255)   # White

    # Vital sign normal ranges (for color coding)
    RANGES = {
        'heart_rate_bpm':   (60, 100),
        'breath_rate':      (12, 20),
        'spo2_percent':     (95, 100),
        'bp_systolic':      (90, 140),
        'bp_diastolic':     (60, 90),
        'hrv_rmssd_ms':     (20, 100),
        'hemoglobin_est':   (12, 18),
        'fatigue_score':    (0, 0.5),
        'ear_mean':         (0.25, 0.35),
    }

    def __init__(
        self,
        window_width:  int = 800,
        window_height: int = 600,
        font_scale:    float = 0.6,
        enable_window: bool = True,
        enable_terminal: bool = True,
        json_log_path: str = "data/dashboard_log.json"
    ):
        self.width  = window_width
        self.height = window_height
        self.font   = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = font_scale
        self.thickness  = 1
        
        self.enable_window   = enable_window
        self.enable_terminal = enable_terminal
        self.json_log_path   = json_log_path

        if self.enable_window:
            cv2.namedWindow('SpaceMedVision Dashboard', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('SpaceMedVision Dashboard', window_width, window_height)

    def render(self, vitals: Dict[str, Any]) -> None:
        """
        Render vitals to all enabled output modes.
        
        Args:
            vitals: Dictionary from main.py containing gated vital signs.
        """
        # Extract values (handle GatedVital objects)
        processed = self._extract_values(vitals)

        # Render each output mode
        if self.enable_window:
            self._render_opencv(processed)
        
        if self.enable_terminal:
            self._render_terminal(processed)
        
        self._render_json_log(processed)

    def _extract_values(self, vitals: Dict) -> Dict:
        """
        Extract numeric values from GatedVital objects.
        
        GatedVital.value can be either:
          - float (valid measurement)
          - str "N/A - <reason>" (failed confidence gate)
        """
        processed = {}
        for key, val in vitals.items():
            # Check if it's a GatedVital object
            if hasattr(val, 'value'):
                processed[key] = {
                    'value':      val.value,
                    'confidence': val.confidence,
                    'is_valid':   val.is_valid
                }
            else:
                # Direct value (e.g., strings like anemia_status)
                processed[key] = {
                    'value':      val,
                    'confidence': 1.0,
                    'is_valid':   True
                }
        return processed

    def _render_opencv(self, vitals: Dict) -> None:
        """
        Render graphical dashboard in OpenCV window.
        
        Layout: 5 horizontal bands for the 5 health layers + system status.
        """
        # Create blank canvas
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        canvas[:] = self.COLOR_BG

        y_offset = 30  # Starting Y position
        line_height = 35

        # ── Header ──────────────────────────────────────────────────
        self._draw_text(
            canvas, "SPACEMEDVISION - ASTRONAUT HEALTH MONITOR",
            10, y_offset, self.COLOR_TEXT, scale=0.8, bold=True
        )
        self._draw_line(canvas, y_offset + 10)
        y_offset += line_height + 10

        # ── Layer A: Hemodynamic ────────────────────────────────────
        y_offset = self._draw_layer(
            canvas, y_offset, "LAYER A: HEMODYNAMIC",
            [
                ('HR',       vitals.get('heart_rate_bpm'),  'BPM'),
                ('HRV',      vitals.get('hrv_rmssd_ms'),    'ms'),
                ('BP Sys',   vitals.get('bp_systolic'),     'mmHg'),
                ('BP Dia',   vitals.get('bp_diastolic'),    'mmHg'),
                ('Glucose',  vitals.get('glucose_index'),   'Index'),
            ]
        )

        # ── Layer B: Respiratory ────────────────────────────────────
        y_offset = self._draw_layer(
            canvas, y_offset, "LAYER B: RESPIRATORY",
            [
                ('Breaths',  vitals.get('breath_rate'),     'BrPM'),
                ('SpO₂',     vitals.get('spo2_percent'),    '%'),
            ]
        )

        # ── Layer C: Hematological ──────────────────────────────────
        y_offset = self._draw_layer(
            canvas, y_offset, "LAYER C: HEMATOLOGICAL",
            [
                ('Hb Est',   vitals.get('hemoglobin_est'),  'g/dL'),
                ('RI',       vitals.get('redness_index'),   ''),
                ('Anemia',   vitals.get('anemia_status'),   ''),
            ],
            extra_alerts=[
                ('Space Anemia Alert', vitals.get('space_anemia_alert'))
            ]
        )

        # ── Layer D: Neurological ───────────────────────────────────
        y_offset = self._draw_layer(
            canvas, y_offset, "LAYER D: NEUROLOGICAL",
            [
                ('Fatigue',  vitals.get('fatigue_score'),   'Score'),
                ('EAR',      vitals.get('ear_mean'),        ''),
                ('Blinks',   vitals.get('blink_rate'),      '/min'),
                ('Tremor',   vitals.get('tremor_amplitude'),'px'),
            ],
            extra_alerts=[
                ('Microsleep Detected', vitals.get('microsleep'))
            ]
        )

        # ── System Status ───────────────────────────────────────────
        self._draw_line(canvas, y_offset)
        y_offset += 20
        
        data_source = vitals.get('data_source', {}).get('value', 'Unknown')
        source_color = (
            self.COLOR_NORMAL if 'Camera' in str(data_source)
            else self.COLOR_WARNING
        )
        
        self._draw_text(
            canvas, f"Data Source: {data_source}",
            10, y_offset, source_color
        )
        
        y_offset += 25
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        self._draw_text(
            canvas, f"Time: {timestamp}",
            10, y_offset, self.COLOR_TEXT
        )

        # Display
        cv2.imshow('SpaceMedVision Dashboard', canvas)
        cv2.waitKey(1)  # Non-blocking

    def _draw_layer(
        self,
        canvas: np.ndarray,
        y_start: int,
        title: str,
        vitals_list: list,
        extra_alerts: list = None
    ) -> int:
        """
        Draw one health layer section.
        
        Args:
            canvas:       Image to draw on
            y_start:      Starting Y coordinate
            title:        Layer name
            vitals_list:  List of (label, vital_dict, unit) tuples
            extra_alerts: List of (label, bool_value) for alert flags
        
        Returns:
            New Y offset after this section
        """
        # Section title
        self._draw_text(
            canvas, title, 10, y_start,
            self.COLOR_TEXT, scale=0.7, bold=True
        )
        y_start += 25

        # Vitals in this layer
        x_offset = 20
        for label, vital_data, unit in vitals_list:
            if vital_data is None:
                continue

            value = vital_data.get('value')
            confidence = vital_data.get('confidence', 0.0)
            is_valid = vital_data.get('is_valid', False)

            # Determine color based on range and confidence
            if isinstance(value, str):  # N/A message
                color = self.COLOR_NA
                display_text = f"{label}: {value}"
            elif not is_valid or confidence < CONFIDENCE_THRESHOLD:
                color = self.COLOR_WARNING
                display_text = f"{label}: {value:.1f} {unit} (Low Conf)"
            else:
                # Check if in normal range
                range_key = self._find_range_key(label)
                if range_key and range_key in self.RANGES:
                    low, high = self.RANGES[range_key]
                    if low <= value <= high:
                        color = self.COLOR_NORMAL
                    else:
                        color = self.COLOR_CRITICAL
                else:
                    color = self.COLOR_NORMAL
                
                display_text = f"{label}: {value:.1f} {unit}"

            self._draw_text(canvas, display_text, x_offset, y_start, color)
            x_offset += 200  # Horizontal spacing

            # Wrap to next line if too wide
            if x_offset > self.width - 200:
                x_offset = 20
                y_start += 25

        # Alert flags (e.g., Space Anemia Alert)
        if extra_alerts:
            y_start += 25
            for alert_label, alert_value in extra_alerts:
                if alert_value and alert_value.get('value'):
                    self._draw_text(
                        canvas, f"⚠ {alert_label}",
                        20, y_start, self.COLOR_CRITICAL, bold=True
                    )
                    y_start += 25

        y_start += 10
        self._draw_line(canvas, y_start)
        return y_start + 15

    def _draw_text(
        self,
        canvas: np.ndarray,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        scale: float = None,
        bold: bool = False
    ) -> None:
        """Draw text on canvas with optional bold."""
        scale = scale or self.font_scale
        thickness = 2 if bold else self.thickness
        
        cv2.putText(
            canvas, str(text), (x, y),
            self.font, scale, color, thickness, cv2.LINE_AA
        )

    def _draw_line(self, canvas: np.ndarray, y: int) -> None:
        """Draw horizontal separator line."""
        cv2.line(
            canvas, (10, y), (self.width - 10, y),
            self.COLOR_TEXT, 1
        )

    def _find_range_key(self, label: str) -> str:
        """Map display label to range key."""
        mapping = {
            'HR':       'heart_rate_bpm',
            'Breaths':  'breath_rate',
            'SpO₂':     'spo2_percent',
            'BP Sys':   'bp_systolic',
            'BP Dia':   'bp_diastolic',
            'HRV':      'hrv_rmssd_ms',
            'Hb Est':   'hemoglobin_est',
            'Fatigue':  'fatigue_score',
            'EAR':      'ear_mean',
        }
        return mapping.get(label, '')

    def _render_terminal(self, vitals: Dict) -> None:
        """
        Render text-based dashboard to stdout/SSH terminal.
        
        Uses ANSI color codes for color-coding in terminal.
        """
        # ANSI color codes
        GREEN  = '\033[92m'
        YELLOW = '\033[93m'
        RED    = '\033[91m'
        GRAY   = '\033[90m'
        RESET  = '\033[0m'
        BOLD   = '\033[1m'

        print("\n" + "="*70)
        print(f"{BOLD}SPACEMEDVISION - ASTRONAUT HEALTH MONITOR{RESET}")
        print("="*70)

        def format_vital(label: str, vital_data: dict, unit: str = '') -> str:
            if vital_data is None:
                return f"{label}: N/A"
            
            value = vital_data.get('value')
            conf = vital_data.get('confidence', 0.0)
            
            if isinstance(value, str):
                return f"{GRAY}{label}: {value}{RESET}"
            elif conf < CONFIDENCE_THRESHOLD:
                return f"{YELLOW}{label}: {value:.1f} {unit} (Low Conf){RESET}"
            else:
                # Check range
                range_key = self._find_range_key(label)
                if range_key in self.RANGES:
                    low, high = self.RANGES[range_key]
                    if low <= value <= high:
                        color = GREEN
                    else:
                        color = RED
                else:
                    color = GREEN
                return f"{color}{label}: {value:.1f} {unit}{RESET}"

        # Layer A
        print(f"\n{BOLD}[LAYER A: HEMODYNAMIC]{RESET}")
        print(f"  {format_vital('HR', vitals.get('heart_rate_bpm'), 'BPM')}")
        print(f"  {format_vital('HRV', vitals.get('hrv_rmssd_ms'), 'ms')}")
        print(f"  {format_vital('BP', vitals.get('bp_systolic'), 'mmHg')}/"
              f"{vitals.get('bp_diastolic', {}).get('value', 'N/A')}")

        # Layer B
        print(f"\n{BOLD}[LAYER B: RESPIRATORY]{RESET}")
        print(f"  {format_vital('Breathing', vitals.get('breath_rate'), 'BrPM')}")
        print(f"  {format_vital('SpO₂', vitals.get('spo2_percent'), '%')}")

        # Layer C
        print(f"\n{BOLD}[LAYER C: HEMATOLOGICAL]{RESET}")
        print(f"  {format_vital('Hemoglobin', vitals.get('hemoglobin_est'), 'g/dL')}")
        anemia_status = vitals.get('anemia_status', {}).get('value', 'Unknown')
        print(f"  Anemia Status: {anemia_status}")

        # Layer D
        print(f"\n{BOLD}[LAYER D: NEUROLOGICAL]{RESET}")
        print(f"  {format_vital('Fatigue', vitals.get('fatigue_score'), 'Score')}")
        print(f"  {format_vital('Blink Rate', vitals.get('blink_rate'), '/min')}")
        
        microsleep = vitals.get('microsleep', {}).get('value')
        if microsleep:
            print(f"  {RED}{BOLD}⚠ MICROSLEEP DETECTED{RESET}")

        # System Status
        print(f"\n{BOLD}[SYSTEM STATUS]{RESET}")
        source = vitals.get('data_source', {}).get('value', 'Unknown')
        print(f"  Data Source: {source}")
        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("="*70 + "\n")

    def _render_json_log(self, vitals: Dict) -> None:
        """
        Append vitals snapshot to JSON log file.
        
        Format: One JSON object per line (newline-delimited JSON).
        This allows streaming/tail analysis by Mission Control.
        """
        # Flatten vitals dict for JSON serialization
        flat = {'timestamp': datetime.utcnow().isoformat()}
        
        for key, data in vitals.items():
            if isinstance(data, dict):
                value = data.get('value')
                # Convert numpy types to Python native
                if hasattr(value, 'item'):
                    value = value.item()
                flat[key] = value
                flat[f"{key}_confidence"] = data.get('confidence', 0.0)
            else:
                flat[key] = data

        # Append to log file (newline-delimited JSON)
        os.makedirs(os.path.dirname(self.json_log_path) or '.', exist_ok=True)
        with open(self.json_log_path, 'a') as f:
            f.write(json.dumps(flat) + '\n')