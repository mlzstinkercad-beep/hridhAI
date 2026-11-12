# processor.py
import time
import numpy as np

class SignalProcessor:
    def __init__(self, tap_threshold=2200, window_seconds=0.8):
        self.tap_threshold = tap_threshold
        self.window_seconds = window_seconds
        self.sample_rate = 44100
        self.recent_taps = []
        self.last_tap_time = 0

    def process_chunk(self, audio_chunk):
        # 1. High-Pass Filter: Remove DC offset and electrical hum
        float_chunk = audio_chunk.astype(np.float32)
        filtered_chunk = float_chunk - np.mean(float_chunk)
        
        # 2. Extract peak transient amplitude
        peak_val = np.max(np.abs(filtered_chunk))
        
        tap_detected = False
        current_time = time.time()

        # 3. Amplitude + Spectral Pitch Validation
        if peak_val > self.tap_threshold:
            # Perform Fast Fourier Transform (FFT) to analyze the pitch/dominant frequency
            fft_vals = np.fft.rfft(filtered_chunk)
            fft_freqs = np.fft.rfftfreq(len(filtered_chunk), 1.0 / self.sample_rate)
            magnitude = np.abs(fft_vals)
            
            if len(magnitude) > 0:
                dominant_freq = fft_freqs[np.argmax(magnitude)]
                
                # Desk taps/surface impacts resonate cleanly in the low-to-mid frequency band (80Hz - 1800Hz).
                # This automatically filters out high-pitched room noise, voice consonants, and sharp clatter.
                is_valid_tap_pitch = (80.0 <= dominant_freq <= 1800.0)
                
                if is_valid_tap_pitch and (current_time - self.last_tap_time) > 0.12:  # Debounce window
                    self.recent_taps.append(current_time)
                    self.last_tap_time = current_time
                    tap_detected = True

        # 4. Clean up taps outside the rolling time window (0.8s for triple-tap cadence)
        self.recent_taps = [t for t in self.recent_taps if (current_time - t) <= self.window_seconds]

        # 5. Strict Triple-Tap Pattern Matcher
        alert_triggered = False
        if len(self.recent_taps) >= 3:
            alert_triggered = True
            self.recent_taps.clear()  # Reset buffer after alert

        return filtered_chunk, peak_val, tap_detected, alert_triggered