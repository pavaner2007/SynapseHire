from audio.recorder import AudioRecorder
from audio.whisper_recognizer import WhisperRecognizer

recorder = AudioRecorder()
whisper = WhisperRecognizer()

print("Press Enter to start recording...")
input()

audio_file = recorder.record(duration=5)

text = whisper.transcribe(audio_file)

print("\n----------------------------")
print("Transcript:")
print(text)
print("----------------------------")