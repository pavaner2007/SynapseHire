import cv2
import numpy as np

from utils.math_utils import MathUtils


class BlinkDetector:

    """
    Blink Detection using Eye Aspect Ratio (EAR)

    Returns:
        blink_count
        blink_rate
        eyes_open
    """

    # LEFT EYE
    LEFT = [33, 160, 158, 133, 153, 144]

    # RIGHT EYE
    RIGHT = [362, 385, 387, 263, 373, 380]

    def __init__(self):

        self.blink_count = 0

        self.closed = False

        self.total_frames = 0

        self.closed_frames = 0

        self.EAR_THRESHOLD = 0.20

    def eye_aspect_ratio(self, eye):

        A = MathUtils.distance(eye[1], eye[5])

        B = MathUtils.distance(eye[2], eye[4])

        C = MathUtils.distance(eye[0], eye[3])

        ear = (A + B) / (2.0 * C)

        return ear

    def process(self, frame, face_landmarks):

        h, w = frame.shape[:2]

        landmarks = face_landmarks.landmark

        left = []

        right = []

        for idx in self.LEFT:

            left.append(

                MathUtils.landmark_to_point(

                    landmarks[idx],

                    w,

                    h,

                )

            )

        for idx in self.RIGHT:

            right.append(

                MathUtils.landmark_to_point(

                    landmarks[idx],

                    w,

                    h,

                )

            )

        left = np.array(left)

        right = np.array(right)

        leftEAR = self.eye_aspect_ratio(left)

        rightEAR = self.eye_aspect_ratio(right)

        ear = (leftEAR + rightEAR) / 2

        self.total_frames += 1

        eyes_open = True

        if ear < self.EAR_THRESHOLD:

            self.closed_frames += 1

            eyes_open = False

            if not self.closed:

                self.blink_count += 1

                self.closed = True

        else:

           if self.closed_frames >= 3:
             self.blink_count += 1

           self.closed_frames = 0
           eyes_open = True

        return {

            "ear": ear,

            "blink_count": self.blink_count,

            "eyes_open": eyes_open

        }