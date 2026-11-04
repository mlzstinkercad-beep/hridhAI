"""
config.py
All system-wide constants for SpaceMedVision.
Centralized here so changing one value propagates everywhere.
"""

# ─── Camera ──────────────────────────────────────────────────────
CAMERA_INDEX        = 0
FRAME_WIDTH         = 640
FRAME_HEIGHT        = 480
TARGET_FPS          = 30          # Capture FPS
VITALS_UPDATE_HZ    = 1           # Minimum output rate (Hz)
MAX_LAG_MS          = 200         # Maximum processing lag

# ─── Ring Buffer ─────────────────────────────────────────────────
RING_BUFFER_SECONDS = 30          # Store last 30 seconds of signal
RING_BUFFER_SIZE    = TARGET_FPS * RING_BUFFER_SECONDS  # 900 frames
MAX_RAM_MB          = 512

# ─── Lighting ────────────────────────────────────────────────────
MIN_LUX             = 10
MAX_LUX             = 10_000
CLAHE_CLIP_LIMIT    = 2.0
CLAHE_TILE_GRID     = (8, 8)

# ─── CPU ─────────────────────────────────────────────────────────
MAX_CPU_PERCENT     = 25.0

# ─── Confidence ──────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.60       # Below this → "N/A - Recalibrating"

# ─── rPPG / Hemodynamic ──────────────────────────────────────────
RPPG_WINDOW_SEC     = 10          # Seconds of signal for FFT
HR_MIN_BPM          = 40
HR_MAX_BPM          = 200
HRV_WINDOW_SEC      = 30

# ─── Respiratory ─────────────────────────────────────────────────
RESP_MIN_BPM        = 4
RESP_MAX_BPM        = 40
SPO2_RED_CHANNEL    = 2           # BGR index
SPO2_GREEN_CHANNEL  = 1

# ─── Neurological ────────────────────────────────────────────────
EAR_THRESHOLD       = 0.25        # Eye Aspect Ratio blink threshold
MICROSLEEP_MS       = 300         # Blink > 300ms = microsleep
TREMOR_FREQ_MIN_HZ  = 4.0         # Parkinsonian/fatigue tremor range
TREMOR_FREQ_MAX_HZ  = 12.0

# ─── Hematological ───────────────────────────────────────────────
ANEMIA_REDNESS_BASELINE = None    # Set during calibration

# ─── MediaPipe ───────────────────────────────────────────────────
MEDIAPIPE_MAX_FACES = 1
MEDIAPIPE_CONFIDENCE = 0.5

# ─── Privacy ─────────────────────────────────────────────────────
STORE_IMAGES        = False       # NEVER store raw frames
LANDMARK_LOG_PATH   = "data/landmarks.csv"
VITALS_LOG_PATH     = "data/vitals_log.csv"

# ─── Sensor Fusion Fallback ───────────────────────────────────────
WIFI_CSI_ENABLED    = True
WIFI_INTERFACE      = "wlan0"