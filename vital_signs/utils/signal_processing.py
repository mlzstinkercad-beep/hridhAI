"""
signal_processing.py

Shared Digital Signal Processing utilities used across all
biological layers. Centralized here to avoid duplication and
ensure consistent filter parameters throughout the system.

Key Algorithms:
  - Bandpass Butterworth filter  (used by rPPG, respiratory)
  - FFT-based frequency estimation (heart rate, breath rate)
  - Peak detection with noise tolerance
  - Detrending for baseline wander removal
"""

import numpy as np
from scipy import signal as scipy_signal
from typing import Tuple, Optional


def bandpass_filter(
    data:       np.ndarray,
    lowcut:     float,
    highcut:    float,
    fs:         float,
    order:      int = 4
) -> np.ndarray:
    """
    Apply a zero-phase Butterworth bandpass filter.
    
    'Zero-phase' (via filtfilt) means no time delay — critical for
    accurate PTT (Pulse Transit Time) measurement between body sites.
    
    Args:
        data:    Input signal array.
        lowcut:  Lower frequency bound (Hz).
        highcut: Upper frequency bound (Hz).
        fs:      Sampling frequency (Hz) = camera FPS.
        order:   Filter order (higher = steeper rolloff, more compute).
    
    Returns:
        Filtered signal of same length as input.
    """
    if len(data) < order * 3:
        # Not enough samples for filtfilt — return raw data
        return data

    nyq  = 0.5 * fs
    low  = lowcut  / nyq
    high = highcut / nyq

    # Clamp to valid range (0, 1) exclusive
    low  = np.clip(low,  1e-6, 0.999)
    high = np.clip(high, 1e-6, 0.999)

    if low >= high:
        return data

    b, a = scipy_signal.butter(order, [low, high], btype='band')
    
    # filtfilt: forward + backward pass = zero phase shift
    return scipy_signal.filtfilt(b, a, data)


def estimate_frequency_fft(
    signal_data: np.ndarray,
    fs:          float,
    freq_min:    float,
    freq_max:    float
) -> Tuple[float, float]:
    """
    Estimate dominant frequency in a signal via FFT.
    
    Returns:
        Tuple of (dominant_frequency_hz, confidence_score 0-1).
    
    Confidence is derived from the Signal-to-Noise Ratio of the
    dominant peak relative to surrounding frequencies. A clean
    heartbeat signal produces a sharp spike → high confidence.
    A noisy/motion-artifact signal → broad spectrum → low confidence.
    """
    n   = len(signal_data)
    if n < 2:
        return 0.0, 0.0

    # Hanning window reduces spectral leakage at signal boundaries
    windowed = signal_data * np.hanning(n)

    # Real FFT (symmetric output, half the bins)
    fft_vals  = np.abs(np.fft.rfft(windowed))
    fft_freqs = np.fft.rfftfreq(n, d=1.0 / fs)

    # Mask to physiological range
    mask = (fft_freqs >= freq_min) & (fft_freqs <= freq_max)

    if not np.any(mask):
        return 0.0, 0.0

    masked_vals  = fft_vals[mask]
    masked_freqs = fft_freqs[mask]

    peak_idx  = np.argmax(masked_vals)
    peak_freq = masked_freqs[peak_idx]
    peak_amp  = masked_vals[peak_idx]

    # Confidence = peak power / (total power in band)
    # → 1.0 if all energy is at one frequency (pure sine)
    # → 0.0 if energy is uniformly spread (pure noise)
    total_power = np.sum(masked_vals ** 2)
    if total_power < 1e-10:
        return peak_freq, 0.0

    peak_power  = peak_amp ** 2
    confidence  = float(np.sqrt(peak_power / total_power))
    confidence  = np.clip(confidence, 0.0, 1.0)

    return float(peak_freq), confidence


def detrend_signal(data: np.ndarray) -> np.ndarray:
    """
    Remove linear baseline drift from a signal.
    
    In rPPG, slow illumination changes (e.g., astronaut drifting
    through a shadow) create low-frequency baseline wander that
    would otherwise corrupt heart rate estimation.
    """
    return scipy_signal.detrend(data, type='linear')


def normalize_signal(data: np.ndarray) -> np.ndarray:
    """
    Z-score normalization. Mean=0, Std=1.
    Allows comparison of signals captured under different
    lighting conditions without scaling artifacts.
    """
    std = np.std(data)
    if std < 1e-10:
        return np.zeros_like(data)
    return (data - np.mean(data)) / std


def find_peaks_robust(
    data:        np.ndarray,
    fs:          float,
    min_freq_hz: float,
    max_freq_hz: float
) -> np.ndarray:
    """
    Find signal peaks within a physiological frequency range.
    
    Returns:
        Array of peak indices.
    """
    # Convert frequency range to sample distance constraints
    min_distance = int(fs / max_freq_hz) if max_freq_hz > 0 else 1
    
    peaks, properties = scipy_signal.find_peaks(
        data,
        distance  = max(1, min_distance),
        prominence = 0.1 * np.ptp(data)  # Must be 10% of signal range
    )
    return peaks


def compute_hrv_rmssd(rr_intervals_ms: np.ndarray) -> float:
    """
    Compute Heart Rate Variability via RMSSD method.
    (Root Mean Square of Successive Differences)
    
    RMSSD is the gold-standard short-term HRV metric.
    Low RMSSD in space can indicate cardiovascular deconditioning.
    
    Args:
        rr_intervals_ms: Array of R-R intervals in milliseconds.
    
    Returns:
        RMSSD value in milliseconds.
    """
    if len(rr_intervals_ms) < 2:
        return 0.0
    
    successive_diffs = np.diff(rr_intervals_ms)
    rmssd = np.sqrt(np.mean(successive_diffs ** 2))
    return float(rmssd)