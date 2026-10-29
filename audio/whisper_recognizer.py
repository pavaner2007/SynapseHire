import os
from groq import Groq
from dotenv import load_dotenv


class WhisperRecognizer:

    def __init__(self):
        print("Initializing Groq Whisper API...")
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("WARNING: GROQ_API_KEY not found! Whisper disabled.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            print("Groq Whisper client ready.")

    def transcribe(self, audio_path: str) -> str:
        """Transcribe an audio file. Returns clean text, empty string if silent or error."""
        if not self.client:
            return ""

        try:
            with open(audio_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                  file=(os.path.basename(audio_path), file.read()),
                  model="whisper-large-v3",
                  response_format="text",
                  language="en"
                )
            result = transcription.strip()
            print(f"Groq Whisper final: '{result}'")
            return result
        except Exception as e:
            print(f"Groq Whisper Error: {e}")
            return ""