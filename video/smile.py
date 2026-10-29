import numpy as np

from utils.math_utils import MathUtils


class SmileDetector:

    """
    Smile Detection using Mouth Aspect Ratio (MAR)

    Returns:
        mar
        smiling
        intensity
        expression
    """

    LEFT = 61
    RIGHT = 291

    TOP = 13
    BOTTOM = 14

    def __init__(self):

        self.history = []

    def mouth_ratio(
        self,
        left,
        right,
        top,
        bottom,
    ):

        width = MathUtils.distance(
            left,
            right
        )

        height = MathUtils.distance(
            top,
            bottom
        )

        if width == 0:
            return 0

        return height / width

    def process(
        self,
        frame,
        face_landmarks,
    ):

        h, w = frame.shape[:2]

        landmarks = face_landmarks.landmark

        left = MathUtils.landmark_to_point(
            landmarks[self.LEFT],
            w,
            h,
        )

        right = MathUtils.landmark_to_point(
            landmarks[self.RIGHT],
            w,
            h,
        )

        top = MathUtils.landmark_to_point(
            landmarks[self.TOP],
            w,
            h,
        )

        bottom = MathUtils.landmark_to_point(
            landmarks[self.BOTTOM],
            w,
            h,
        )

        mar = self.mouth_ratio(
            left,
            right,
            top,
            bottom,
        )

        intensity = min(
            100,
            max(
                0,
                (mar - 0.03) * 700
            )
        )

        smiling = intensity > 30

        if intensity > 80:
            expression = "Big Smile"

        elif intensity > 45:
            expression = "Natural Smile"

        else:
            expression = "Neutral"

        return {

            "mar": mar,

            "intensity": intensity,

            "smiling": smiling,

            "expression": expression

        }