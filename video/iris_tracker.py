import cv2
import numpy as np

from utils.math_utils import MathUtils


class IrisTracker:

    """
    Iris Tracking using MediaPipe Face Mesh

    Returns
    -------
    left_ratio
    right_ratio
    average_ratio

    gaze

    LEFT
    RIGHT
    CENTER
    """

    # Iris landmarks
    LEFT_IRIS = [474, 475, 476, 477]
    RIGHT_IRIS = [469, 470, 471, 472]

    # Eye corners
    LEFT_LEFT = 33
    LEFT_RIGHT = 133

    RIGHT_LEFT = 362
    RIGHT_RIGHT = 263

    def __init__(self):

        self.history = []

    def iris_center(self, landmarks, ids, w, h):

        pts = []

        for idx in ids:

            pts.append(
                MathUtils.landmark_to_point(
                    landmarks[idx],
                    w,
                    h,
                )
            )

        pts = np.array(pts)

        return np.mean(pts, axis=0)

    def horizontal_ratio(self, iris, left_corner, right_corner):
        eye_width = right_corner[0] - left_corner[0]

        if abs(eye_width) < 1:
            return 0.5

        return (iris[0] - left_corner[0]) / eye_width

    def process(self, frame, face_landmarks):

        h, w = frame.shape[:2]

        landmarks = face_landmarks.landmark

        left_center = self.iris_center(
            landmarks,
            self.LEFT_IRIS,
            w,
            h,
        )

        right_center = self.iris_center(
            landmarks,
            self.RIGHT_IRIS,
            w,
            h,
        )

        left_corner = MathUtils.landmark_to_point(
            landmarks[self.LEFT_LEFT],
            w,
            h,
        )

        left_outer = MathUtils.landmark_to_point(
            landmarks[self.LEFT_RIGHT],
            w,
            h,
        )

        right_corner = MathUtils.landmark_to_point(
            landmarks[self.RIGHT_LEFT],
            w,
            h,
        )

        right_outer = MathUtils.landmark_to_point(
            landmarks[self.RIGHT_RIGHT],
            w,
            h,
        )

        left_ratio = self.horizontal_ratio(
            left_center,
            left_corner,
            left_outer,
        )

        right_ratio = self.horizontal_ratio(
            right_center,
            right_corner,
            right_outer,
        )

        average = (left_ratio + right_ratio) / 2

        if average < 0.42:
            gaze = "LEFT"

        elif average > 0.58:
            gaze = "RIGHT"

        else:
            gaze = "CENTER"

        cv2.circle(
            frame,
            tuple(left_center.astype(int)),
            3,
            (0,255,0),
            -1,
        )

        cv2.circle(
            frame,
            tuple(right_center.astype(int)),
            3,
            (0,255,0),
            -1,
        )

        return {

            "left_ratio": left_ratio,

            "right_ratio": right_ratio,

            "average_ratio": average,

            "gaze": gaze,

        }