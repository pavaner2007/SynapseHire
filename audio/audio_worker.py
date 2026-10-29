import threading
import time
import queue
import tempfile
import os
import speech_recognition as sr

from audio.whisper_recognizer import WhisperRecognizer
from analysis.transcript import TranscriptManager
from analysis.filler_detector import FillerWordDetector
from audio.speech_analyzer import SpeechAnalyzer


class AudioWorker(threading.Thread):

    def __init__(self, out_queue):
        super().__init__()
        self.daemon = True
        self.running = False
        self.out_queue = out_queue

        self.whisper = None
        self.transcript = None
        self.filler = None
        self.analyzer = None
        self.recognizer = sr.Recognizer()
        
        # Optimize recognizer for conversational speech
        self.recognizer.energy_threshold = 300 
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0 # 1 second of silence to end sentence

    def run(self):
        self.whisper = WhisperRecognizer()
        self.transcript = TranscriptManager()
        self.filler = FillerWordDetector()
        self.analyzer = SpeechAnalyzer()

        self.running = True

        with sr.Microphone() as source:
            print("\n[VAD] Calibrating microphone for ambient noise... Please stay quiet for 2 seconds.")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"[VAD] Calibration complete. Energy threshold set to: {self.recognizer.energy_threshold}")
            
            while self.running:
                try:
                    # Listen for a phrase (blocks until speech starts, then records until silence)
                    audio_data = self.recognizer.listen(source, timeout=1, phrase_time_limit=20)
                    
                    # Once a phrase is finished, process it
                    self._process_audio(audio_data)

                except sr.WaitTimeoutError:
                    # No speech detected within the 1-second timeout, loop back and listen again
                    continue
                except Exception as e:
                    print(f"[AudioWorker] Error: {e}")
                    time.sleep(0.5)

    def _process_audio(self, audio_data: sr.AudioData):
        """Save the AudioData to a wav file and transcribe with Whisper."""
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
                f.write(audio_data.get_wav_data())

            text = self.whisper.transcribe(tmp_path)
        finally:
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        if not text:
            return

        print(f"[VAD] Transcribed: {text}")
        
        self.transcript.add(text)
        fillers = self.filler.process(self.transcript.get_transcript())
        total_fillers = fillers.get("total", 0) if fillers else 0
        metrics = self.analyzer.process_chunk(text, total_fillers)

        out_data = {
            "text": text,
            "is_final": True,
            "fillers": fillers,
            "speech_metrics": metrics
        }
        self._put_queue(out_data)

    def _put_queue(self, audio_data):
        try:
            self.out_queue.put_nowait(audio_data)
        except queue.Full:
            try:
                self.out_queue.get_nowait()
                self.out_queue.put_nowait(audio_data)
            except queue.Empty:
                pass

    def stop(self):
        self.running = False