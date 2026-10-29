import time
import speech_recognition as sr


class SpeechRecognizer:

    def __init__(self):

        self.recognizer = sr.Recognizer()

        self.microphone = sr.Microphone()

        with self.microphone as source:
            print("Calibrating microphone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Calibration complete.")

    def listen(self):

        with self.microphone as source:

            try:

                start = time.time()

                audio = self.recognizer.listen(
                    source,
                    timeout=2,
                    phrase_time_limit=5
                )

                end = time.time()

                text = self.recognizer.recognize_google(audio)

                duration = end - start

                return text, duration

            except sr.WaitTimeoutError:

                return "", 0

            except sr.UnknownValueError:

                return "", 0

            except sr.RequestError:

                return "", 0

            except Exception:

                return "", 0