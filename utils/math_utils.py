import math

class MathUtils:
    @staticmethod
    def landmark_to_point(landmark, width, height):
        """
        Converts a normalized MediaPipe landmark to absolute pixel coordinates.
        Returns a tuple (x, y).
        """
        return (int(landmark.x * width), int(landmark.y * height))

    @staticmethod
    def distance(p1, p2):
        """
        Calculates the Euclidean distance between two points p1 and p2.
        Each point is a tuple (x, y).
        """
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
