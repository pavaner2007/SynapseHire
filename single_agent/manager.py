import threading
import time


class InterviewManager:

    def __init__(self):

        self.running = False

        self.start_time = None

        self.end_time = None

        self.transcript = ""

        self.video_data = {}

        self.audio_data = {}

        self.analysis = {}
        
        self.evaluations = []

    # --------------------------

    def add_evaluation(self, evaluation_data):
        self.evaluations.append(evaluation_data)

    # --------------------------

    def start(self):

        self.running = True

        self.start_time = time.time()

    # --------------------------

    def stop(self):

        self.running = False

        self.end_time = time.time()

    # --------------------------

    def duration(self):

        if self.start_time is None:
            return 0

        if self.running:

            return round(
                time.time() - self.start_time,
                1
            )

        return round(
            self.end_time - self.start_time,
            1
        )

    # --------------------------

    def update_video(self, data):

        self.video_data = data

    # --------------------------

    def update_audio(self, data):

        self.audio_data = data

    # --------------------------

    def update_analysis(self, data):

        self.analysis = data