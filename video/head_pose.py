import cv2
import numpy as np
from collections import deque

from utils.math_utils import MathUtils


class HeadPoseEstimator:
    """
    Head Pose Estimation using

    - MediaPipe FaceMesh
    - OpenCV solvePnP
    - Rodrigues
    - Euler Angles
    - Moving Average Smoothing

    Returns

    yaw
    pitch
    roll
    direction
    """

    # MediaPipe landmark ids
    NOSE = 1
    CHIN = 199

    LEFT_EYE = 33
    RIGHT_EYE = 263

    LEFT_MOUTH = 61
    RIGHT_MOUTH = 291

    def __init__(self):

        # ----------------------------
        # Generic 3D Face Model
        # ----------------------------
        self.yaw_offset = None

        self.model_points = np.array(
            [
                (0.0, 0.0, 0.0),          # Nose tip
                (0.0, -63.6, -12.5),      # Chin
                (-43.3, 32.7, -26.0),     # Left eye corner
                (43.3, 32.7, -26.0),      # Right eye corner
                (-28.9, -28.9, -24.1),    # Left mouth
                (28.9, -28.9, -24.1),     # Right mouth
            ],
            dtype=np.float64,
        )

        # Moving average buffers

        self.yaw_history = deque(maxlen=10)
        self.pitch_history = deque(maxlen=10)
        self.roll_history = deque(maxlen=10)

    # ----------------------------------------------------

    def get_image_points(self, landmarks, width, height):

        image_points = np.array(
            [
                MathUtils.landmark_to_point(
                    landmarks[self.NOSE],
                    width,
                    height,
                ),

                MathUtils.landmark_to_point(
                    landmarks[self.CHIN],
                    width,
                    height,
                ),

                MathUtils.landmark_to_point(
                    landmarks[self.LEFT_EYE],
                    width,
                    height,
                ),

                MathUtils.landmark_to_point(
                    landmarks[self.RIGHT_EYE],
                    width,
                    height,
                ),

                MathUtils.landmark_to_point(
                    landmarks[self.LEFT_MOUTH],
                    width,
                    height,
                ),

                MathUtils.landmark_to_point(
                    landmarks[self.RIGHT_MOUTH],
                    width,
                    height,
                ),
            ],
            dtype=np.float64,
        )

        return image_points

    # ----------------------------------------------------

    def smooth(self, yaw, pitch, roll):

        self.yaw_history.append(yaw)
        self.pitch_history.append(pitch)
        self.roll_history.append(roll)

        yaw = np.mean(self.yaw_history)
        pitch = np.mean(self.pitch_history)
        roll = np.mean(self.roll_history)

        return yaw, pitch, roll

    # ----------------------------------------------------

    def get_direction(self, yaw, pitch):

        direction = "Facing Forward"

        if yaw < -20:
            direction = "Looking Left"

        elif yaw > 20:
            direction = "Looking Right"

        elif pitch < -20:
            direction = "Looking Down"

        elif pitch > 20:
            direction = "Looking Up"

        return direction

        # ----------------------------------------------------

    def estimate_pose(self, frame, face_landmarks):
        
        height, width = frame.shape[:2]
        landmarks = face_landmarks.landmark
        image_points = self.get_image_points(
        landmarks,
        width,
        height, )
        camera_matrix = np.array(
        [
            [width, 0, width / 2],
            [0, width, height / 2],
            [0, 0, 1],
        ],
        dtype=np.float64,
        )
        
        dist_coeffs = np.zeros((4, 1))
        success, rotation_vector, translation_vector = cv2.solvePnP(
        self.model_points,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_EPNP, )
        if not success:
            return None

        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_matrix)

        pitch = float(angles[0])
        yaw = float(angles[1])
        if self.yaw_offset is None:
             self.yaw_offset = yaw

        yaw = yaw - self.yaw_offset
        roll = float(angles[2])  
        
        if pitch > 90:
            pitch -= 180
        elif pitch < -90:
            pitch += 180

        if yaw > 90:
            yaw -= 180
        elif yaw < -90:
            yaw += 180
        

    # Smooth values
        yaw, pitch, roll = self.smooth(
            yaw,
            pitch,
            roll,
        )
        
        direction = self.get_direction(
            yaw,
            pitch,
        )
        
        return {
        "yaw": yaw,
        "pitch": pitch,
        "roll": roll,
        "direction": direction,
        "rotation_vector": rotation_vector,
        "translation_vector": translation_vector,
        "camera_matrix": camera_matrix,
        "dist_coeffs": dist_coeffs,
        "nose_point": image_points[0],
    }
    # ----------------------------------------------------

    def draw(self, frame, pose):

        """
        Draw pose information on the frame.
        """

        if pose is None:
            return frame

        yaw = pose["yaw"]
        pitch = pose["pitch"]
        roll = pose["roll"]

        direction = pose["direction"]

        nose = tuple(
            pose["nose_point"].astype(int)
        )

        axis = np.float32([
    (0.0, 0.0, 80.0)
])

        nose_end, _ = cv2.projectPoints(
            axis,
            pose["rotation_vector"],
            pose["translation_vector"],
            pose["camera_matrix"],
            pose["dist_coeffs"],
        )

        end = tuple(
    map(
        int,
        nose_end.reshape(-1, 2)[0]
    )
)

        cv2.line(
            frame,
            nose,
            end,
            (255, 0, 0),
            3,
        )

        return frame

    # ----------------------------------------------------

    def process(self, frame, face_landmarks):

        pose = self.estimate_pose(
            frame,
            face_landmarks,
        )

        frame = self.draw(
            frame,
            pose,
        )

        return pose 