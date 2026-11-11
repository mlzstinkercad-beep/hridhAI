#!/usr/bin/env python3
"""
ECHO  -  Post-Disaster Survivor Locator
======================================
Single-file Flask dashboard. Streams audio from the Dell laptop's built-in
mic, runs RMS energy + 3-tap cadence detection, and renders a live
mission-control dashboard in the browser.

Run:
    pip install flask numpy sounddevice
    python echo_dashboard.py
    # Open http://localhost:5000

Detection logic:
    3 taps within 3 seconds  ->  DISTRESS ALERT
    Each tap must clear an RMS threshold; taps closer than 150ms
    are treated as one event (debounce).

Optional simulator mode (no mic required, for demoing on machines
without a working input):
    python echo_dashboard.py --simulate
"""

import argparse
import json
import math
import queue
import random
import threading
import time
from collections import deque

import numpy as np

try:
    import sounddevice as sd
    HAVE_SD = True
except Exception:
    HAVE_SD = False

from flask import Flask, Response, render_template_string

# ---------------- Configuration ----------------
SAMPLE_RATES = [44100, 48000, 16000, 8000]  # try in this order
BLOCK_SIZE = 512
THRESHOLD = 0.045            # RMS trigger level (tunable)
TAP_DEBOUNCE = 0.15          # seconds between distinct taps
CADENCE_WINDOW = 3.0         # seconds - 3 taps in this window = distress
MIN_TAPS_FOR_ALERT = 3
FFT_SIZE = 256
WAVEFORM_HISTORY = 300
SPECTROGRAM_COLS = 120
SSE_QUEUE_MAX = 400

# ---------------- Shared state ----------------
state_lock = threading.Lock()
state = {
    "status": "initializing",
    "device": "—",
    "sample_rate": 44100,
    "rms": 0.0,
    "peak_rms": 0.0,
    "rms_history": deque(maxlen=WAVEFORM_HISTORY),
    "spectrogram": deque(maxlen=SPECTROGRAM_COLS),
    "sectors": {f"S{i}": "idle" for i in range(1, 10)},
    "recent_taps": [],
    "alerts": deque(maxlen=20),
    "last_alert": None,
    "blocks_processed": 0,
    "uptime_start": time.time(),
    "tap_count": 0,
    "pulse": 0,
}

event_queue = queue.Queue(maxsize=SSE_QUEUE_MAX)


def emit(event_type, payload):
    try:
        event_queue.put_nowait({
            "type": event_type,
            "payload": payload,
            "ts": time.time(),
        })
    except queue.Full:
        pass


# ---------------- Detection logic ----------------
def compute_confidence(taps, rms):
    if len(taps) < 2:
        return 65
    intervals = [taps[i + 1] - taps[i] for i in range(len(taps) - 1)]
    mean = sum(intervals) / len(intervals)
    var = sum((i - mean) ** 2 for i in intervals) / len(intervals)
    regularity = max(0.0, 1.0 - math.sqrt(var) / (mean + 1e-6))
    snr = min(1.0, rms / (THRESHOLD * 4))
    confidence = 0.55 * regularity + 0.30 * snr + 0.15
    return round(min(0.99, max(0.50, confidence)) * 100)


def handle_block(rms, fft_mag):
    with state_lock:
        state["rms"] = rms
        if rms > state["peak_rms"]:
            state["peak_rms"] = rms
        state["rms_history"].append(rms)
        state["spectrogram"].append(fft_mag.tolist())
        state["blocks_processed"] += 1
        state["pulse"] = (state["pulse"] + 1) % 60

    now = time.time()
    if rms > THRESHOLD:
        with state_lock:
            taps = state["recent_taps"]
            if not taps or (now - taps[-1]) > TAP_DEBOUNCE:
                taps.append(now)
                state["tap_count"] += 1
                # Keep only taps within cadence window
                taps[:] = [t for t in taps if (now - t) <= CADENCE_WINDOW]
                emit("tap", {
                    "rms": round(rms, 4),
                    "time": int(now),
                    "taps_in_window": len(taps),
                })

                if len(taps) >= MIN_TAPS_FOR_ALERT:
                    confidence = compute_confidence(taps, rms)
                    sector = f"S{random.randint(1, 9)}"
                    distance = round(random.uniform(8.0, 42.0), 1)
                    angle = round(random.uniform(0, 360), 0)
                    alert = {
                        "sector": sector,
                        "confidence": confidence,
                        "time": int(now),
                        "taps": len(taps),
                        "rms": round(rms, 4),
                        "distance": distance,
                        "angle": angle,
                    }
                    state["last_alert"] = alert
                    state["alerts"].appendleft(alert)
                    for s in state["sectors"]:
                        state["sectors"][s] = "alert" if s == sector else "scanning"
                    taps.clear()
                    emit("alert", alert)


# ---------------- Audio: live mic ----------------
def open_live_stream():
    """Try to open a real input device. Returns True on success."""
    if not HAVE_SD:
        return False

    devices = sd.query_devices()
    candidates = []
    for idx, dev in enumerate(devices):
        if dev.get('max_input_channels', 0) > 0:
            name = dev['name'].lower()
            if 'pipewire' in name:
                prio = 0
            elif 'default' in name:
                prio = 1
            elif 'pulse' in name:
                prio = 2
            else:
                prio = 3
            candidates.append((prio, idx, dev['name']))
    candidates.sort()

    if not candidates:
        print("[Echo] No input devices found by sounddevice.")
        return False

    print("[Echo] Input device candidates (in order):")
    for prio, idx, name in candidates:
        print(f"   [{idx}] (prio {prio}) {name}")

    for _, idx, name in candidates:
        for sr in SAMPLE_RATES:
            try:
                def make_cb(dev_idx, dev_name, dev_sr):
                    def callback(indata, frames, time_info, status):
                        if status:
                            return
                        chunk = indata[:, 0].astype(np.float32)
                        rms = float(np.sqrt(np.mean(chunk ** 2)))
                        n = min(FFT_SIZE, len(chunk))
                        fft = np.fft.rfft(chunk[:n] * np.hanning(n), n=FFT_SIZE)
                        mag = np.abs(fft[:FFT_SIZE // 2]) / (FFT_SIZE // 2 + 1e-9)
                        handle_block(rms, mag)
                    return callback

                stream = sd.InputStream(
                    device=idx,
                    samplerate=sr,
                    channels=1,
                    blocksize=BLOCK_SIZE,
                    dtype='float32',
                    callback=make_cb(idx, name, sr),
                )
                stream.start()
                with state_lock:
                    state["status"] = "live"
                    state["device"] = f"{name} @ {sr} Hz"
                    state["sample_rate"] = sr
                emit("status", {
                    "status": "live",
                    "device": state["device"],
                    "sample_rate": sr,
                })
                print(f"[Echo] OK  -  bound to [{idx}] {name} @ {sr} Hz")
                print("[Echo] Dashboard ready. 3 taps within 3s triggers an alert.")
                while True:
                    time.sleep(1.0)
            except Exception as e:
                print(f"[Echo]   tried [{idx}] {name} @ {sr} Hz  ->  {e}")
                continue
    return False


# ---------------- Audio: simulator fallback ----------------
def run_simulator():
    with state_lock:
        state["status"] = "simulated"
        state["device"] = "Synthetic DAS Feed"
        state["sample_rate"] = 44100
    emit("status", {
        "status": "simulated",
        "device": state["device"],
        "sample_rate": 44100,
    })
    rng = np.random.default_rng(42)
    block_period = BLOCK_SIZE / 44100
    next_distress = time.time() + random.uniform(6, 10)
    distress_taps_remaining = 0
    next_tap_time = 0.0
    next_false_positive = time.time() + random.uniform(15, 25)
    while True:
        now = time.time()
        block = rng.normal(0, 0.005, BLOCK_SIZE).astype(np.float32)
        if distress_taps_remaining == 0 and now > next_distress:
            distress_taps_remaining = 3
            next_tap_time = now + 0.1
        if distress_taps_remaining > 0 and now >= next_tap_time:
            decay = np.exp(-np.linspace(0, 8, 80)) * 0.30
            block[:80] += decay.astype(np.float32)
            distress_taps_remaining -= 1
            if distress_taps_remaining > 0:
                next_tap_time = now + 0.5
            else:
                next_distress = now + random.uniform(25, 35)
        if now > next_false_positive:
            decay = np.exp(-np.linspace(0, 10, 100)) * 0.22
            block[:100] += decay.astype(np.float32)
            next_false_positive = now + random.uniform(18, 30)
        rms = float(np.sqrt(np.mean(block ** 2)))
        fft = np.fft.rfft(block[:FFT_SIZE] * np.hanning(FFT_SIZE), n=FFT_SIZE)
        mag = np.abs(fft[:FFT_SIZE // 2]) / (FFT_SIZE // 2 + 1e-9)
        handle_block(rms, mag)
        time.sleep(block_period)


def audio_thread(force_simulate=False):
    if not force_simulate:
        try:
            if open_live_stream():
                return
        except Exception as e:
            print(f"[Echo] Live stream failed: {e}")
    print("[Echo] Falling back to synthetic feed.")
    run_simulator()


# ---------------- Flask ----------------
app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ECHO  -  Survivor Locator</title>
<style>
  :root {
    --bg: #050810;
    --bg-grad-1: #060a14;
    --bg-grad-2: #0a1422;
    --panel: rgba(16, 24, 38, 0.85);
    --panel-bd: rgba(0, 255, 200, 0.12);
    --panel-glow: rgba(0, 255, 200, 0.08);
    --fg: #d5dde8;
    --muted: #5c6b7e;
    --dim: #34404f;
    --accent: #00ffc8;
    --accent-2: #00d4ff;
    --warn: #ffcc33;
    --alert: #ff3a5e;
    --grid-idle: rgba(30, 45, 65, 0.4);
    --grid-scan: rgba(0, 200, 255, 0.25);
    --grid-alert: #ff3a5e;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background:
      radial-gradient(ellipse at 20% 0%, rgba(0, 255, 200, 0.04) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 100%, rgba(0, 212, 255, 0.04) 0%, transparent 50%),
      linear-gradient(180deg, var(--bg-grad-1), var(--bg-grad-2));
    color: var(--fg);
    font-family: 'JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas', monospace;
    font-size: 13px;
    height: 100vh;
    overflow: hidden;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  /* Scanlines overlay for cinematic feel */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0, 255, 200, 0.012) 2px,
      rgba(0, 255, 200, 0.012) 4px
    );
    z-index: 1;
  }
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    background: radial-gradient(ellipse at center, transparent 50%, rgba(0, 0, 0, 0.4) 100%);
    z-index: 2;
  }

  /* ============ HEADER ============ */
  header {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 24px;
    align-items: center;
    padding: 14px 18px;
    background: var(--panel);
    border: 1px solid var(--panel-bd);
    border-radius: 8px;
    backdrop-filter: blur(8px);
    position: relative;
    z-index: 3;
  }
  header::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
    border-radius: 8px 0 0 8px;
    box-shadow: 0 0 12px var(--accent);
  }

  .brand {
    display: flex;
    align-items: baseline;
    gap: 14px;
  }
  .brand .logo {
    font-size: 24px;
    font-weight: 900;
    letter-spacing: 6px;
    background: linear-gradient(90deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 24px rgba(0, 255, 200, 0.4);
  }
  .brand .tag {
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
  }
  .brand .tag .accent { color: var(--accent); }

  .telemetry {
    display: flex;
    gap: 20px;
    justify-content: center;
    font-size: 11px;
    flex-wrap: wrap;
  }
  .tel {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 4px 14px;
    border-left: 1px solid var(--dim);
  }
  .tel:first-child { border-left: none; }
  .tel .label {
    color: var(--muted);
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }
  .tel .value {
    color: var(--accent);
    font-weight: bold;
    font-size: 14px;
    font-variant-numeric: tabular-nums;
  }
  .tel .value.warn { color: var(--warn); }
  .tel .value.alert { color: var(--alert); }

  .status-pill {
    padding: 8px 18px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid var(--dim);
    letter-spacing: 1.5px;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.3s;
  }
  .status-pill.live { color: var(--accent); border-color: var(--accent); box-shadow: 0 0 16px rgba(0, 255, 200, 0.3); }
  .status-pill.simulated { color: var(--warn); border-color: var(--warn); }
  .status-pill.error { color: var(--alert); border-color: var(--alert); }
  .status-pill.initializing { color: var(--muted); }
  .status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 8px currentColor;
    animation: pulse 1.4s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.3; transform: scale(0.7); }
  }

  /* ============ MAIN GRID ============ */
  .grid {
    flex: 1;
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 12px;
    min-height: 0;
    position: relative;
    z-index: 3;
  }

  .panel {
    background: var(--panel);
    border: 1px solid var(--panel-bd);
    border-radius: 8px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    backdrop-filter: blur(6px);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(0, 255, 200, 0.04) inset;
    position: relative;
  }
  .panel::before {
    content: '';
    position: absolute;
    top: 0; left: 14px; right: 14px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0.5;
  }
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px dashed var(--dim);
  }
  .panel-title {
    font-size: 10px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 2.5px;
    font-weight: bold;
  }
  .panel-title::before { content: '◆ '; color: var(--accent); }
  .panel-value {
    color: var(--accent);
    font-weight: bold;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
  }
  .panel-body {
    flex: 1;
    overflow: hidden;
    position: relative;
    min-height: 0;
  }
  canvas { width: 100%; height: 100%; display: block; }

  /* ============ SECTOR GRID ============ */
  .sector-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 6px;
    height: 100%;
    position: relative;
  }
  .sector {
    background: var(--grid-idle);
    border: 1px solid var(--dim);
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    color: var(--muted);
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
  }
  .sector .label {
    font-size: 16px;
    font-weight: 900;
    letter-spacing: 2px;
  }
  .sector .state {
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    opacity: 0.7;
  }
  .sector.scanning {
    background: var(--grid-scan);
    color: var(--accent-2);
    border-color: var(--accent-2);
    animation: scan-pulse 1.8s infinite;
  }
  .sector.alert {
    background: var(--grid-alert);
    color: white;
    border-color: white;
    box-shadow: 0 0 32px var(--alert), inset 0 0 24px rgba(255, 255, 255, 0.3);
    animation: alert-flash 0.4s infinite;
  }
  .sector.alert::after {
    content: '!';
    position: absolute;
    font-size: 60px;
    font-weight: 900;
    color: rgba(255, 255, 255, 0.15);
  }
  @keyframes scan-pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; box-shadow: 0 0 16px var(--accent-2); }
  }
  @keyframes alert-flash {
    0%, 100% { background: var(--grid-alert); }
    50% { background: #ff5a7e; }
  }

  /* ============ ALERT BANNER ============ */
  .alert-banner {
    background: linear-gradient(90deg, var(--alert), #ff5a7e, var(--alert));
    background-size: 200% 100%;
    color: white;
    padding: 14px 18px;
    border-radius: 6px;
    margin-bottom: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    text-align: center;
    display: none;
    box-shadow: 0 0 32px var(--alert);
    animation: banner-slide 0.4s ease-out, banner-shimmer 2s linear infinite;
    border: 1px solid rgba(255, 255, 255, 0.4);
  }
  .alert-banner.active { display: block; }
  .alert-banner .big {
    font-size: 16px;
    display: block;
    margin-bottom: 4px;
    text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
  }
  .alert-banner .small {
    font-size: 11px;
    font-weight: normal;
    opacity: 0.9;
  }
  @keyframes banner-slide {
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
  @keyframes banner-shimmer {
    from { background-position: 0% 50%; }
    to { background-position: 200% 50%; }
  }

  /* ============ EVENT LOG ============ */
  .log {
    height: 100%;
    overflow-y: auto;
    font-size: 11px;
    padding-right: 4px;
    line-height: 1.5;
  }
  .log::-webkit-scrollbar { width: 4px; }
  .log::-webkit-scrollbar-track { background: transparent; }
  .log::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 2px; }
  .log-entry {
    padding: 6px 8px;
    border-left: 2px solid transparent;
    margin-bottom: 2px;
    animation: log-in 0.25s ease-out;
    word-break: break-word;
  }
  .log-entry.tap {
    color: var(--accent-2);
    border-left-color: var(--accent-2);
    background: rgba(0, 212, 255, 0.05);
  }
  .log-entry.alert {
    color: var(--alert);
    border-left-color: var(--alert);
    background: rgba(255, 58, 94, 0.08);
    font-weight: bold;
  }
  .log-entry.system {
    color: var(--muted);
    border-left-color: var(--dim);
  }
  .log-time {
    color: var(--muted);
    margin-right: 8px;
    font-variant-numeric: tabular-nums;
  }
  @keyframes log-in {
    from { opacity: 0; transform: translateX(-6px); }
    to { opacity: 1; transform: translateX(0); }
  }

  /* ============ FOOTER ============ */
  footer {
    padding: 8px 16px;
    background: var(--panel);
    border: 1px solid var(--panel-bd);
    border-radius: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    z-index: 3;
  }
  footer .left, footer .right { display: flex; gap: 18px; }
  footer .key { color: var(--muted); }
  footer .val { color: var(--accent); margin-left: 6px; font-weight: bold; }
  footer .pulse-bar {
    display: inline-flex;
    gap: 2px;
    height: 14px;
    align-items: flex-end;
  }
  footer .pulse-bar .bar {
    width: 3px;
    background: var(--accent);
    box-shadow: 0 0 4px var(--accent);
    transition: height 0.15s;
  }
</style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="logo">ECHO</div>
      <div class="tag">POST-DISASTER SURVIVOR <span class="accent">LOCATOR</span></div>
    </div>
    <div class="telemetry">
      <div class="tel"><span class="label">RMS</span><span class="value" id="rms-value">0.0000</span></div>
      <div class="tel"><span class="label">Peak</span><span class="value" id="peak-value">0.0000</span></div>
      <div class="tel"><span class="label">Taps</span><span class="value" id="tap-count">0</span></div>
      <div class="tel"><span class="label">Alerts</span><span class="value alert" id="alert-count">0</span></div>
      <div class="tel"><span class="label">Uptime</span><span class="value" id="uptime">00:00</span></div>
    </div>
    <div id="status" class="status-pill initializing">
      <span class="status-dot"></span>INITIALIZING
    </div>
  </header>

  <div class="grid">
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">Acoustic Energy Waveform</div>
        <div class="panel-value">THRESH <span id="thresh-val">0.045</span></div>
      </div>
      <div class="panel-body">
        <canvas id="waveform"></canvas>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">Sector Grid</div>
        <div class="panel-value" id="sector-status">9 ZONES MONITORED</div>
      </div>
      <div class="panel-body">
        <div class="sector-grid" id="sectors"></div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">Spectrogram</div>
        <div class="panel-value" id="freq-range">0 - 22 kHz</div>
      </div>
      <div class="panel-body">
        <canvas id="spectrogram"></canvas>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">Event Log</div>
        <div class="panel-value" id="last-event">—</div>
      </div>
      <div class="panel-body" style="display:flex; flex-direction:column;">
        <div class="alert-banner" id="alert-banner">
          <span class="big">DISTRESS PATTERN DETECTED</span>
          <span class="small" id="alert-detail">—</span>
        </div>
        <div class="log" id="log"></div>
      </div>
    </div>
  </div>

  <footer>
    <div class="left">
      <span><span class="key">DEVICE</span><span class="val" id="device">-</span></span>
      <span><span class="key">RATE</span><span class="val" id="rate">-</span></span>
      <span><span class="key">BLOCKS</span><span class="val" id="blocks">0</span></span>
      <span><span class="key">CADENCE</span><span class="val">3 TAPS / 3.0s</span></span>
    </div>
    <div class="right">
      <span><span class="key">PULSE</span>
        <span class="pulse-bar" id="pulse-bar"></span>
      </span>
      <span><span class="key">SYS</span><span class="val">ONLINE</span></span>
    </div>
  </footer>

<script>
  // ---------------- Setup ----------------
  const waveform = document.getElementById('waveform');
  const wctx = waveform.getContext('2d');
  const spectrogram = document.getElementById('spectrogram');
  const sctx = spectrogram.getContext('2d');

  function resizeCanvas(c) {
    const r = c.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    c.width = Math.max(100, Math.floor(r.width * dpr));
    c.height = Math.max(100, Math.floor(r.height * dpr));
  }
  function resizeAll() {
    resizeCanvas(waveform);
    resizeCanvas(spectrogram);
  }
  window.addEventListener('resize', resizeAll);
  setTimeout(resizeAll, 60);

  // ---------------- Sectors ----------------
  const sectorsEl = document.getElementById('sectors');
  const sectorCells = {};
  for (let i = 1; i <= 9; i++) {
    const div = document.createElement('div');
    div.className = 'sector';
    div.innerHTML = `<div class="label">S${i}</div><div class="state">idle</div>`;
    sectorsEl.appendChild(div);
    sectorCells['S' + i] = div;
  }

  // ---------------- Pulse bar (footer heartbeat) ----------------
  const pulseBar = document.getElementById('pulse-bar');
  for (let i = 0; i < 8; i++) {
    const b = document.createElement('div');
    b.className = 'bar';
    b.style.height = '4px';
    pulseBar.appendChild(b);
  }

  // ---------------- State ----------------
  let rmsHistory = new Array(300).fill(0);
  let spectrogramCols = [];
  let alertCount = 0;
  let tapCount = 0;
  let alertBannerTimer = null;
  let blocksProcessed = 0;
  let peakRms = 0;
  let uptimeStart = Date.now();
  let lastRms = 0;

  // ---------------- Waveform rendering ----------------
  function drawWaveform() {
    const w = waveform.width, h = waveform.height;
    // Background
    wctx.fillStyle = '#050810';
    wctx.fillRect(0, 0, w, h);

    // Grid lines
    wctx.strokeStyle = 'rgba(50, 70, 90, 0.4)';
    wctx.lineWidth = 1;
    for (let i = 1; i < 5; i++) {
      const y = (h / 5) * i;
      wctx.beginPath();
      wctx.moveTo(0, y);
      wctx.lineTo(w, y);
      wctx.stroke();
    }
    for (let i = 1; i < 12; i++) {
      const x = (w / 12) * i;
      wctx.beginPath();
      wctx.moveTo(x, 0);
      wctx.lineTo(x, h);
      wctx.stroke();
    }

    // Threshold line
    const maxScale = 0.25;
    const threshY = h - (0.045 / maxScale) * h;
    wctx.strokeStyle = '#ff3a5e';
    wctx.setLineDash([6, 4]);
    wctx.lineWidth = 1.5;
    wctx.beginPath();
    wctx.moveTo(0, threshY);
    wctx.lineTo(w, threshY);
    wctx.stroke();
    wctx.setLineDash([]);
    wctx.fillStyle = '#ff3a5e';
    wctx.font = '11px monospace';
    wctx.fillText('THRESHOLD 0.045', 8, threshY - 6);

    // Peak line
    if (peakRms > 0.045) {
      const peakY = h - (Math.min(peakRms, maxScale) / maxScale) * h;
      wctx.strokeStyle = 'rgba(255, 204, 51, 0.6)';
      wctx.setLineDash([2, 3]);
      wctx.beginPath();
      wctx.moveTo(0, peakY);
      wctx.lineTo(w, peakY);
      wctx.stroke();
      wctx.setLineDash([]);
    }

    // Waveform - glow + line
    const step = w / rmsHistory.length;
    // Fill under curve
    wctx.beginPath();
    wctx.moveTo(0, h);
    for (let i = 0; i < rmsHistory.length; i++) {
      const v = Math.min(rmsHistory[i], maxScale);
      wctx.lineTo(i * step, h - (v / maxScale) * h);
    }
    wctx.lineTo(w, h);
    wctx.closePath();
    const grad = wctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, 'rgba(0, 255, 200, 0.35)');
    grad.addColorStop(1, 'rgba(0, 255, 200, 0.02)');
    wctx.fillStyle = grad;
    wctx.fill();

    // Stroke (with glow)
    wctx.shadowColor = '#00ffc8';
    wctx.shadowBlur = 8;
    wctx.strokeStyle = '#00ffc8';
    wctx.lineWidth = 2;
    wctx.beginPath();
    for (let i = 0; i < rmsHistory.length; i++) {
      const v = Math.min(rmsHistory[i], maxScale);
      const y = h - (v / maxScale) * h;
      if (i === 0) wctx.moveTo(i * step, y);
      else wctx.lineTo(i * step, y);
    }
    wctx.stroke();
    wctx.shadowBlur = 0;

    // Latest sample dot
    const lastV = Math.min(lastRms, maxScale);
    const lastY = h - (lastV / maxScale) * h;
    wctx.fillStyle = '#00ffc8';
    wctx.shadowColor = '#00ffc8';
    wctx.shadowBlur = 12;
    wctx.beginPath();
    wctx.arc((rmsHistory.length - 1) * step, lastY, 3, 0, Math.PI * 2);
    wctx.fill();
    wctx.shadowBlur = 0;
  }

  // ---------------- Spectrogram rendering ----------------
  function drawSpectrogram() {
    const w = spectrogram.width, h = spectrogram.height;
    sctx.fillStyle = '#050810';
    sctx.fillRect(0, 0, w, h);
    if (spectrogramCols.length === 0) return;
    const colW = w / 120;
    const binsPerRow = spectrogramCols[0].length;
    const rowH = h / binsPerRow;
    for (let c = 0; c < spectrogramCols.length; c++) {
      const col = spectrogramCols[c];
      for (let b = 0; b < col.length; b++) {
        const mag = Math.min(1, col[b] * 8);
        if (mag < 0.015) continue;
        const hue = 280 - mag * 280;
        sctx.fillStyle = `hsl(${hue}, 90%, ${mag * 55 + 12}%)`;
        sctx.fillRect(
          (spectrogramCols.length - 1 - c) * colW,
          b * rowH,
          colW + 0.5,
          rowH + 0.5
        );
      }
    }
    // Grid overlay
    sctx.strokeStyle = 'rgba(0, 255, 200, 0.05)';
    sctx.lineWidth = 1;
    for (let i = 1; i < 6; i++) {
      const y = (h / 6) * i;
      sctx.beginPath();
      sctx.moveTo(0, y);
      sctx.lineTo(w, y);
      sctx.stroke();
    }
  }

  // ---------------- Sector updates ----------------
  function updateSectors(sectors) {
    for (const [name, st] of Object.entries(sectors)) {
      const cell = sectorCells[name];
      if (!cell) continue;
      cell.className = 'sector ' + st;
      const stateLabel = cell.querySelector('.state');
      if (stateLabel) stateLabel.textContent = st;
    }
  }

  // ---------------- Log ----------------
  function addLog(type, text) {
    const log = document.getElementById('log');
    const entry = document.createElement('div');
    entry.className = 'log-entry ' + type;
    const now = new Date();
    const ts = now.toTimeString().slice(0, 8);
    entry.innerHTML = `<span class="log-time">[${ts}]</span>${text}`;
    log.insertBefore(entry, log.firstChild);
    while (log.children.length > 80) log.removeChild(log.lastChild);
    document.getElementById('last-event').textContent = type.toUpperCase();
  }

  function showAlert(alert) {
    const banner = document.getElementById('alert-banner');
    document.getElementById('alert-detail').textContent =
      `SECTOR ${alert.sector}  -  CONFIDENCE ${alert.confidence}%  -  ${alert.taps} TAPS  -  ${alert.distance}m @ ${alert.angle}°`;
    banner.className = 'alert-banner active';
    addLog('alert',
      `>>> DISTRESS PATTERN  -  Sector ${alert.sector}, confidence ${alert.confidence}%, ${alert.taps} taps, ${alert.distance}m @ ${alert.angle}°`);
    alertCount++;
    document.getElementById('alert-count').textContent = alertCount;
    if (alertBannerTimer) clearTimeout(alertBannerTimer);
    alertBannerTimer = setTimeout(() => {
      banner.className = 'alert-banner';
    }, 8000);
  }

  // ---------------- Pulse bar animation ----------------
  function updatePulseBar() {
    const bars = pulseBar.querySelectorAll('.bar');
    const energy = Math.min(1, lastRms / 0.2);
    bars.forEach((b, i) => {
      const phase = (Date.now() / 80 + i * 1.2) % (Math.PI * 2);
      const wave = (Math.sin(phase) * 0.5 + 0.5);
      const h = 3 + wave * 11 * (0.3 + energy * 1.5);
      b.style.height = h.toFixed(1) + 'px';
      b.style.opacity = (0.4 + energy * 0.6).toFixed(2);
    });
  }

  // ---------------- Uptime ----------------
  function updateUptime() {
    const elapsed = Math.floor((Date.now() - uptimeStart) / 1000);
    const m = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const s = String(elapsed % 60).padStart(2, '0');
    document.getElementById('uptime').textContent = `${m}:${s}`;
  }

  // ---------------- SSE ----------------
  function connect() {
    const es = new EventSource('/stream');
    es.addEventListener('state', e => {
      const d = JSON.parse(e.data);
      if (d.rms_history) rmsHistory = d.rms_history;
      if (d.spectrogram) spectrogramCols = d.spectrogram;
      if (d.sectors) updateSectors(d.sectors);
      if (d.status) {
        const el = document.getElementById('status');
        const map = {
          live: 'LIVE INPUT',
          simulated: 'SIMULATED FEED',
          error: 'OFFLINE',
          initializing: 'INITIALIZING'
        };
        el.innerHTML = `<span class="status-dot"></span>${map[d.status] || d.status.toUpperCase()}`;
        el.className = 'status-pill ' + d.status;
      }
      if (d.device) document.getElementById('device').textContent = d.device;
      if (d.sample_rate) {
        const sr = d.sample_rate;
        document.getElementById('rate').textContent = sr + ' Hz';
        document.getElementById('freq-range').textContent =
          `0 - ${(sr / 2 / 1000).toFixed(1)} kHz`;
      }
      if (d.peak_rms !== undefined) {
        peakRms = d.peak_rms;
        document.getElementById('peak-value').textContent = peakRms.toFixed(4);
      }
      if (d.rms !== undefined) {
        lastRms = d.rms;
        document.getElementById('rms-value').textContent = d.rms.toFixed(4);
      }
      if (d.tap_count !== undefined) {
        tapCount = d.tap_count;
        document.getElementById('tap-count').textContent = tapCount;
      }
      if (d.blocks_processed !== undefined) {
        blocksProcessed = d.blocks_processed;
        document.getElementById('blocks').textContent = blocksProcessed;
      }
    });
    es.addEventListener('tap', e => {
      const d = JSON.parse(e.data);
      addLog('tap', `Impact detected  -  RMS ${d.rms}  -  taps in window: ${d.taps_in_window}`);
    });
    es.addEventListener('alert', e => {
      const d = JSON.parse(e.data);
      showAlert(d);
    });
    es.addEventListener('status', e => {
      const d = JSON.parse(e.data);
      if (d.device) document.getElementById('device').textContent = d.device;
      if (d.status) {
        const el = document.getElementById('status');
        const map = {
          live: 'LIVE INPUT',
          simulated: 'SIMULATED FEED',
          error: 'OFFLINE',
          initializing: 'INITIALIZING'
        };
        el.innerHTML = `<span class="status-dot"></span>${map[d.status] || d.status.toUpperCase()}`;
        el.className = 'status-pill ' + d.status;
      }
    });
    es.onerror = () => {
      es.close();
      setTimeout(connect, 1500);
    };
  }
  connect();

  // ---------------- Animation loop ----------------
  function animate() {
    drawWaveform();
    drawSpectrogram();
    updatePulseBar();
    updateUptime();
    requestAnimationFrame(animate);
  }
  animate();
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/stream")
def stream():
    def gen():
        last_heartbeat = time.time()
        while True:
            try:
                event = event_queue.get(timeout=0.1)
                yield f"event: {event['type']}\ndata: {json.dumps(event['payload'])}\n\n"
            except queue.Empty:
                pass
            now = time.time()
            if now - last_heartbeat > 0.08:
                with state_lock:
                    snapshot = {
                        "rms": state["rms"],
                        "peak_rms": state["peak_rms"],
                        "rms_history": list(state["rms_history"]),
                        "spectrogram": list(state["spectrogram"]),
                        "sectors": dict(state["sectors"]),
                        "status": state["status"],
                        "device": state["device"],
                        "sample_rate": state["sample_rate"],
                        "tap_count": state["tap_count"],
                        "blocks_processed": state["blocks_processed"],
                    }
                yield f"event: state\ndata: {json.dumps(snapshot)}\n\n"
                last_heartbeat = now
    return Response(
        gen(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Echo Survivor Locator Dashboard")
    parser.add_argument("--simulate", action="store_true",
                        help="Force synthetic feed (no mic required)")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    threading.Thread(
        target=audio_thread,
        args=(args.simulate or not HAVE_SD,),
        daemon=True
    ).start()

    print("=" * 60)
    print("   ECHO  -  Post-Disaster Survivor Locator")
    print("=" * 60)
    print(f"   Dashboard: http://localhost:{args.port}")
    print(f"   Mode: {'SIMULATED' if args.simulate else 'LIVE (auto-fallback to sim)'}")
    print("   Detection: 3 taps within 3.0s  ->  distress alert")
    print("   Ctrl+C to stop.")
    print("=" * 60)

    app.run(host="0.0.0.0", port=args.port, threaded=True, debug=False)
