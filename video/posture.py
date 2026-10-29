import math


class PostureDetector:

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    NOSE = 0

    def __init__(self):

        pass

    def process(self, frame, pose_landmarks):

        if pose_landmarks is None:

            return None

        h, w = frame.shape[:2]

        landmarks = pose_landmarks.landmark

        left = landmarks[self.LEFT_SHOULDER]
        right = landmarks[self.RIGHT_SHOULDER]
        nose = landmarks[self.NOSE]

        lx = left.x * w
        ly = left.y * h

        rx = right.x * w
        ry = right.y * h

        nx = nose.x * w

        angle = math.degrees(
            math.atan2(
                ry - ly,
                rx - lx,
            )
        )

        shoulder_center = (lx + rx) / 2

        if abs(angle) < 15:
            posture = "Good"
        elif angle > 15:
            posture = "Leaning Too Right"
        else:
            posture = "Leaning Too Left"

        return {

            "posture": posture,

            "shoulder_angle": angle,

            "nose_x": nx,

            "center_x": shoulder_center,

        }