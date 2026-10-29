import time


class Calibration:

    """
    5 Second Calibration

    Learns user's natural eye position.
    """

    def __init__(self, duration=5):

        self.duration = duration

        self.start_time = None

        self.finished = False

        self.values = []

        self.baseline = None

    def start(self):

        if self.start_time is None:
            self.start_time = time.time()

    def process(self, value):

        if self.finished:
            return

        self.start()

        self.values.append(value)

        elapsed = time.time() - self.start_time

        if elapsed >= self.duration:

            self.baseline = sum(self.values) / len(self.values)

            self.finished = True

    def remaining(self):

        if self.finished:
            return 0

        return max(
            0,
            self.duration - (time.time() - self.start_time)
        )

    def is_finished(self):

        return self.finished