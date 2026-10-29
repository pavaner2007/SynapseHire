import threading
import time
import queue
import cv2

from video.camera import Camera
from video.face_mesh import FaceMeshDetector
from video.head_pose import HeadPoseEstimator
from video.blink import BlinkDetector
from video.iris_tracker import IrisTracker
from video.eye_contact import EyeContact
from video.smile import SmileDetector
from video.pose_detector import PoseDetector
from video.posture import PostureDetector


class VideoWorker(threading.Thread):
    def __init__(self, out_queue):
        super().__init__()
        self.daemon = True
        self.running = False
        self.out_queue = out_queue

        # Delay initialization of heavy models until the thread starts
        self.camera = None
        self.mesh = None
        self.iris = None
        self.head_pose = None
        self.blink = None
        self.eye_contact = None
        self.smile = None
        self.pose_detector = None
        self.posture = None

    def run(self):
        # Initialize Modules here so they don't block the main UI thread
        self.camera = Camera()
        self.mesh = FaceMeshDetector()
        self.iris = IrisTracker()
        self.head_pose = HeadPoseEstimator()
        self.blink = BlinkDetector()
        self.eye_contact = EyeContact()
        self.smile = SmileDetector()
        self.pose_detector = PoseDetector()
        self.posture = PostureDetector()

        self.running = True
        
        # Target FPS to limit CPU usage and keep queue from filling up
        target_fps = 30
        frame_time = 1.0 / target_fps
        
        while self.running:
            start_time = time.time()
            
            frame = self.camera.read()
            if frame is None:
                time.sleep(0.01)
                continue

            # Process Face Mesh
            results = self.mesh.process(frame)
            frame = self.mesh.draw(frame, results)

            # Process Body Pose
            pose_results = self.pose_detector.process(frame)
            frame = self.pose_detector.draw(frame, pose_results)

            # Extract metrics
            pose = None
            eye_data = {}
            blink_data = {}
            iris_data = {}
            smile_data = {}
            posture_data = {}

            if results.multi_face_landmarks:
                face = results.multi_face_landmarks[0]
                pose = self.head_pose.process(frame, face)
                blink_data = self.blink.process(frame, face)
                iris_data = self.iris.process(frame, face)
                eye_data = self.eye_contact.process(pose, iris_data, blink_data)
                smile_data = self.smile.process(frame, face)

            if pose_results.pose_landmarks:
                posture_data = self.posture.process(frame, pose_results.pose_landmarks)
                
            video_data = {
                "head_pose": pose,
                "eye_contact": eye_data,
                "blink": blink_data,
                "iris": iris_data,
                "smile": smile_data,
                "posture": posture_data
            }

            # If queue is full, drop the oldest frame to avoid lag
            try:
                self.out_queue.put_nowait((frame, video_data))
            except queue.Full:
                try:
                    self.out_queue.get_nowait()
                    self.out_queue.put_nowait((frame, video_data))
                except queue.Empty:
                    pass

            # Remove artificial sleep to maximize FPS
            pass

    def stop(self):
        self.running = False
        # wait a bit for thread to finish loop before releasing camera
        time.sleep(0.1)
        self.camera.release()
