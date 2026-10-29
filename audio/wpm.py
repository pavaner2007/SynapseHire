class WPMCalculator:

    def process(self, text, duration):

        words = len(text.split())

        if duration <= 0:
            return 0

        wpm = (words / duration) * 60

        return round(wpm, 1)

    def get_status(self, wpm):

        if wpm == 0:
            return "Calculating..."

        if wpm < 100:
            return "Too Slow"

        elif wpm < 160:
            return "Good"

        elif wpm < 190:
            return "Fast"

        else:
            return "Too Fast"