# stream.py
import subprocess
import threading
import numpy as np

class AudioStreamWorker:
    def __init__(self, sample_rate=44100, chunk_size=2048):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.process = None
        self.is_running = False
        self.audio_callback = None
        self._thread = None

    def start(self, callback):
        self.audio_callback = callback
        self.is_running = True
        
        cmd = [
            "pw-record",
            "--format=s16",
            "--rate", str(self.sample_rate),
            "--channels=1",
            "-"
        ]
        
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"[Stream Error] Failed to start pw-record: {e}")
            return False

        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        return True

    def _read_loop(self):
        bytes_per_sample = 2  # s16 LE
        while self.is_running and self.process and self.process.poll() is None:
            raw_data = self.process.stdout.read(self.chunk_size * bytes_per_sample)
            if not raw_data:
                break
            audio_chunk = np.frombuffer(raw_data, dtype=np.int16)
            if len(audio_chunk) > 0 and self.audio_callback:
                self.audio_callback(audio_chunk)

    def stop(self):
        self.is_running = False
        if self.process:
            self.process.terminate()
            self.process = None