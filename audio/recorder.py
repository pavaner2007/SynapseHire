import sounddevice as sd
import numpy as np


class AudioRecorder:
    """Kept for compatibility, but AudioWorker now uses sounddevice directly."""

    def __init__(self):
        self.sample_rate = 16000

    def record(self, duration=2):
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        return recording.flatten()