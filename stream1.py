# stream.py (Windows Compatible)
import threading
import numpy as np
import sounddevice as sd

class AudioStreamWorker:
    def __init__(self, sample_rate=44100, chunk_size=2048):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.stream = None
        self.is_running = False
        self.audio_callback = None

    def start(self, callback):
        self.audio_callback = callback
        self.is_running = True
        
        try:
            # Open input stream using Windows default microphone
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.chunk_size,
                callback=self._sd_callback
            )
            self.stream.start()
            return True
        except Exception as e:
            print(f"[Stream Error] Failed to start sounddevice stream on Windows: {e}")
            return False

    def _sd_callback(self, indata, frames, time_info, status):
        if not self.is_running:
            return
        # Extract mono channel and convert float32 audio to int16 PCM format
        audio_chunk = (indata[:, 0] * 32767).astype(np.int16)
        if len(audio_chunk) > 0 and self.audio_callback:
            self.audio_callback(audio_chunk)

    def stop(self):
        self.is_running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
