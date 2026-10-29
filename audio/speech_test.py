from audio.speech import SpeechRecognizer
from audio.wpm import WPMCalculator

speech = SpeechRecognizer()
wpm = WPMCalculator()

print("Start speaking...")

while True:

    text, duration = speech.listen()

    if text == "":
        continue

    current_wpm = wpm.process(text, duration)

    status = wpm.get_status(current_wpm)

    print("-" * 40)
    print("Transcript :", text)
    print("Duration   :", round(duration, 2), "sec")
    print("WPM        :", current_wpm)
    print("Status     :", status)