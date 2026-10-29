import datetime


class TranscriptManager:

    def __init__(self):

        self.sentences = []

    def add(self, text):

        if text.strip() == "":
            return

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        self.sentences.append({

            "time": timestamp,

            "text": text

        })

    def get_transcript(self):

        transcript = ""

        for sentence in self.sentences:

            transcript += f"[{sentence['time']}] "

            transcript += sentence["text"]

            transcript += "\n"

        return transcript

    def total_words(self):

        total = 0

        for sentence in self.sentences:

            total += len(sentence["text"].split())

        return total