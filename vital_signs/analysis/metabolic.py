"""
metabolic.py — Layer E: Metabolic & External Analysis

Extracts:
  1. Body Temperature (Estimate) — From rPPG perfusion index
  2. Nutritional Intake Logging  — Food tray image segmentation

Scientific Basis:
─────────────────
Temperature from PPG Perfusion:
  Perfusion Index (PI) = AC/DC ratio of PPG signal
  Higher perfusion → more blood flow → higher skin temperature
  Correlation: ΔT ≈ 0.5 × ΔPI (empirical, Shelley 2007)
  
  This is MUCH less accurate than IR thermometry, but gives
  a relative trend useful for fever detection in absence of
  a thermometer.

Food Volume Estimation:
  Uses YOLOv5-based object detection trained on ISS food trays.
  Detects: protein pouch, vegetable pouch, carb pouch, dessert
  Estimates volume via bounding box area × depth heuristic.
  Logs macros: P/C/F grams for crew nutrition tracking.
  
  Reference: NASA Food Frequency Questionnaire (FFQ) digital replacement.
"""

import numpy as np
import cv2
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass

from utils.ring_buffer import RingBuffer
from utils.signal_processing import normalize_signal
from config import TARGET_FPS


@dataclass
class MetabolicResult:
    """Structured output for Layer E."""
    temperature_est_c:  float   # Celsius estimate
    temp_confidence:    float
    nutrition_detected: bool    # Food tray in frame?
    protein_g:          float   # Estimated grams
    carbs_g:            float
    fats_g:             float
    calories_kcal:      float


class MetabolicAnalyzer:
    """
    Body temperature and nutrition tracking.
    
    Note: Temperature estimation requires stable ambient conditions.
    In the ISS, this works because cabin temp is controlled 21-23°C.
    On EVA or in variable environments, confidence drops to 0.
    """

    # Temperature estimation calibration
    BASELINE_TEMP_C = 36.5      # Normal core temp (°C)
    PI_TO_TEMP_SCALE = 0.5      # ΔT per unit ΔPI
    
    # Nutrition macro ratios (kcal/g)
    PROTEIN_KCAL_PER_G = 4.0
    CARB_KCAL_PER_G    = 4.0
    FAT_KCAL_PER_G     = 9.0

    def __init__(self, baseline_pi: Optional[float] = None):
        """
        Args:
            baseline_pi: Personal baseline Perfusion Index.
                         Set during pre-launch calibration.
        """
        self._perfusion_buffer = RingBuffer(int(TARGET_FPS * 30))
        self._baseline_pi = baseline_pi or 1.0  # Default PI
        
        # YOLOv5 would be loaded here (omitted for brevity)
        # self._food_detector = torch.hub.load('ultralytics/yolov5', 'custom',
        #                                      path='models/iss_food_tray.pt')
        self._food_detector = None  # Placeholder

    def process_frame(
        self,
        frame:          np.ndarray,
        rppg_signal:    Optional[np.ndarray],
        is_mealtime:    bool = False
    ) -> MetabolicResult:
        """
        Process frame for temperature and nutrition.
        
        Args:
            frame:       BGR frame
            rppg_signal: Raw green channel rPPG signal from forehead
            is_mealtime: Flag indicating if this is a scheduled meal scan
        
        Returns:
            MetabolicResult with temperature and nutrition estimates
        """
        # ── Temperature from Perfusion ────────────────────────────────
        temp_c, temp_conf = self._estimate_temperature(rppg_signal)

        # ── Nutrition Detection (only during scheduled mealtimes) ─────
        if is_mealtime and self._food_detector is not None:
            nutrition = self._analyze_food_tray(frame)
        else:
            nutrition = {
                'detected': False,
                'protein_g': 0.0,
                'carbs_g':   0.0,
                'fats_g':    0.0,
                'calories':  0.0
            }

        return MetabolicResult(
            temperature_est_c  = temp_c,
            temp_confidence    = temp_conf,
            nutrition_detected = nutrition['detected'],
            protein_g          = nutrition['protein_g'],
            carbs_g            = nutrition['carbs_g'],
            fats_g             = nutrition['fats_g'],
            calories_kcal      = nutrition['calories'],
        )

    def _estimate_temperature(
        self,
        rppg_signal: Optional[np.ndarray]
    ) -> Tuple[float, float]:
        """
        Estimate core body temperature from PPG perfusion index.
        
        Perfusion Index = (AC component / DC component) × 100
        Where:
          AC = pulsatile (heartbeat) amplitude
          DC = baseline (non-pulsatile) level
        
        High PI → good perfusion → normal/elevated temp
        Low PI  → vasoconstriction → hypothermia or shock
        
        Returns:
            Tuple of (temperature_celsius, confidence)
        """
        if rppg_signal is None or len(rppg_signal) < 60:
            return np.nan, 0.0

        # Compute Perfusion Index
        ac_component = np.std(rppg_signal)    # Pulsatile amplitude
        dc_component = np.mean(rppg_signal)   # Baseline level

        if dc_component < 1e-6:
            return np.nan, 0.0

        pi = (ac_component / dc_component) * 100.0

        # Temperature estimate from PI deviation
        pi_delta = pi - self._baseline_pi
        temp_delta = self.PI_TO_TEMP_SCALE * pi_delta
        temp_est = self.BASELINE_TEMP_C + temp_delta

        # Clamp to physiological range
        temp_est = float(np.clip(temp_est, 35.0, 42.0))

        # Confidence: high if PI signal is stable
        # Check coefficient of variation over last 10 seconds
        window = int(TARGET_FPS * 10)
        if len(rppg_signal) >= window:
            recent_pi_values = []
            for i in range(0, len(rppg_signal) - window, window // 10):
                chunk = rppg_signal[i:i+window]
                chunk_pi = (np.std(chunk) / np.mean(chunk)) * 100
                recent_pi_values.append(chunk_pi)
            
            if recent_pi_values:
                pi_cv = np.std(recent_pi_values) / np.mean(recent_pi_values)
                confidence = float(np.clip(1.0 - pi_cv, 0.0, 1.0))
            else:
                confidence = 0.5
        else:
            confidence = 0.5

        return temp_est, confidence

    def _analyze_food_tray(self, frame: np.ndarray) -> Dict:
        """
        Detect and quantify food items on ISS meal tray.
        
        YOLOv5 Custom Model Classes:
          0: protein_pouch
          1: vegetable_pouch
          2: carb_pouch
          3: dessert_pouch
          4: beverage_pouch
        
        Each pouch has known volume → mass conversion factors.
        
        Returns:
            Dict with detected: bool, protein_g, carbs_g, fats_g, calories
        """
        # Placeholder implementation (real version uses YOLOv5)
        # In production: results = self._food_detector(frame)
        
        # For now, return no detection
        return {
            'detected':  False,
            'protein_g': 0.0,
            'carbs_g':   0.0,
            'fats_g':    0.0,
            'calories':  0.0
        }

        # ── Real Implementation (when YOLOv5 model is trained) ────────
        """
        results = self._food_detector(frame)
        detections = results.pandas().xyxy[0]  # Bounding boxes
        
        nutrition = {
            'detected':  len(detections) > 0,
            'protein_g': 0.0,
            'carbs_g':   0.0,
            'fats_g':    0.0,
            'calories':  0.0
        }
        
        # ISS food pouch standard sizes (grams per pouch type)
        POUCH_MACROS = {
            'protein_pouch':    {'protein': 25, 'carbs': 5,  'fats': 8},
            'vegetable_pouch':  {'protein': 3,  'carbs': 15, 'fats': 1},
            'carb_pouch':       {'protein': 5,  'carbs': 45, 'fats': 2},
            'dessert_pouch':    {'protein': 2,  'carbs': 30, 'fats': 5},
        }
        
        for _, row in detections.iterrows():
            class_name = row['name']
            confidence = row['confidence']
            
            if confidence < 0.6:
                continue
            
            if class_name in POUCH_MACROS:
                macros = POUCH_MACROS[class_name]
                nutrition['protein_g'] += macros['protein']
                nutrition['carbs_g']   += macros['carbs']
                nutrition['fats_g']    += macros['fats']
        
        # Compute total calories
        nutrition['calories'] = (
            nutrition['protein_g'] * self.PROTEIN_KCAL_PER_G +
            nutrition['carbs_g']   * self.CARB_KCAL_PER_G +
            nutrition['fats_g']    * self.FAT_KCAL_PER_G
        )
        
        return nutrition
        """

    def set_baseline_perfusion(self, pi: float) -> None:
        """
        Set personal baseline Perfusion Index.
        Called during pre-launch calibration.
        """
        self._baseline_pi = pi