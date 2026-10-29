from collections import deque


class EyeContact:

    """
    Eye Contact Engine

    Uses:
        - Head Pose
        - Iris Tracking
        - Blink Detection

    Returns:
        looking
        score
        rating
    """

    def __init__(self):

        self.total_frames = 0
        self.contact_frames = 0

        # Smooth last 15 predictions
        self.history = deque(maxlen=15)
        self.contact_history = deque(maxlen=120)

    def process(self, pose, iris, blink):

        score = 100

        # -------------------------
        # Head Direction
        # -------------------------
        if abs(pose["yaw"]) > 20:
            score -= 35

        if abs(pose["pitch"]) > 20:
            score -= 20

        # -------------------------
        # Iris
        # -------------------------
        if iris["gaze"] != "CENTER":
            score -= 45

        # -------------------------
        # Blink
        # -------------------------
        if not blink["eyes_open"]:
            score -= 10

        score = max(0, min(100, score))

        looking = (
        abs(pose["yaw"]) < 20
        and abs(pose["pitch"]) < 20
        and iris["gaze"] == "CENTER"
        and blink["eyes_open"]
        )

        score = 100

        if abs(pose["yaw"]) > 20:
            score -= 30

        if abs(pose["pitch"]) > 20:
            score -= 20

        if iris["gaze"] != "CENTER":
            score -= 40

        if not blink["eyes_open"]:
            score -= 10

        score = max(0, score)

        self.history.append(score)

        smooth_score = sum(self.history) / len(self.history)

        self.contact_history.append(1 if looking else 0)

        percentage = (
            sum(self.contact_history) /
            len(self.contact_history)
        ) * 100 

        if percentage >= 90:
            rating = "Excellent"

        elif percentage >= 75:
            rating = "Good"

        elif percentage >= 60:
            rating = "Fair"

        else:
            rating = "Poor"

        return {

            "looking": looking,

            "score": smooth_score,

            "percentage": percentage,

            "rating": rating

        }