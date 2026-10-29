import re
from collections import Counter


class FillerWordDetector:

    def __init__(self):

        self.fillers = [
            "um",
            "uh",
            "like",
            "basically",
            "actually",
            "you know",
            "i think",
            "i mean",
            "sort of",
            "kind of",
            "so yeah"
        ]

    def process(self, transcript):

        text = transcript.lower()

        counts = Counter()

        total = 0

        for filler in self.fillers:

            matches = re.findall(r"\b" + re.escape(filler) + r"\b", text)

            if matches:

                counts[filler] = len(matches)

                total += len(matches)

        if total == 0:

            rating = "Excellent"

        elif total <= 3:

            rating = "Good"

        elif total <= 7:

            rating = "Average"

        else:

            rating = "Needs Improvement"

        return {

            "counts": dict(counts),

            "total": total,

            "rating": rating

        }