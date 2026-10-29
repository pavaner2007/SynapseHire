import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from dotenv import load_dotenv
load_dotenv()

import asyncio
import cv2
import numpy as np
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import tempfile
import time
import fitz  # PyMuPDF

# Import existing core modules
from video.camera import Camera
from video.face_mesh import FaceMeshDetector
from video.head_pose import HeadPoseEstimator
from video.blink import BlinkDetector
from video.iris_tracker import IrisTracker
from video.eye_contact import EyeContact
from video.smile import SmileDetector
from video.pose_detector import PoseDetector
from video.posture import PostureDetector

from audio.whisper_recognizer import WhisperRecognizer
from single_agent.transcript import TranscriptManager
from single_agent.filler_detector import FillerWordDetector
from audio.speech_analyzer import SpeechAnalyzer
from single_agent.answer_evaluator import AnswerEvaluator
from multi_agent.gd_manager import GDManager
from multi_agent.recruiter_manager import RecruiterManager
from multi_agent.planner_manager import PlannerManager

from single_agent.manager import InterviewManager
from single_agent.questions import QuestionManager
from single_agent.confidence_engine import ConfidenceEngine

app = FastAPI()

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def make_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(make_serializable(v) for v in obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def decode_base64(data_url):
    import re
    b64_string = data_url.split(",")[1]
    b64_string = re.sub(r'\s+', '', b64_string)
    missing_padding = len(b64_string) % 4
    if missing_padding:
        b64_string += '=' * (4 - missing_padding)
    return base64.b64decode(b64_string)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_json(self, message: dict, websocket: WebSocket):
        message = make_serializable(message)
        await websocket.send_json(message)

manager = ConnectionManager()

# Global initialization for heavy models
print("Initializing models...")
mesh = FaceMeshDetector()
iris = IrisTracker()
head_pose = HeadPoseEstimator()
blink = BlinkDetector()
eye_contact = EyeContact()
smile = SmileDetector()
pose_detector = PoseDetector()
posture = PostureDetector()

whisper_recognizer = WhisperRecognizer()
filler_detector = FillerWordDetector()
speech_analyzer = SpeechAnalyzer()
conf_engine = ConfidenceEngine()
evaluator = AnswerEvaluator()

print("Models loaded.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("Client connected!")
    
    interview_manager = InterviewManager()
    question_manager = QuestionManager(mode="sequential")
    transcript = TranscriptManager()
    gd_manager = GDManager()
    recruiter_manager = RecruiterManager()
    planner_manager = PlannerManager()
    
    interview_manager.start()
    current_q = question_manager.current_question()
    
    await manager.send_json({
        "type": "control",
        "action": "start",
        "question": current_q
    }, websocket)

    bad_eye_contact_frames = 0
    bad_posture_frames = 0
    cooldown_timer = 0

    try:
        while True:
            # We expect text JSON or binary data from frontend
            # The frontend can send {"type": "audio", "data": "base64..."} 
            # or {"type": "video", "data": "base64..."}
            
            message = await websocket.receive_text()
            payload = json.loads(message)
            
            msg_type = payload.get("type")
            
            if msg_type == "video":
                # Process base64 frame
                try:
                    img_data = decode_base64(payload["data"])
                    np_arr = np.frombuffer(img_data, np.uint8)
                    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(f"Video decode error: {e}")
                    frame = None
                
                if frame is not None:
                    # Process Video
                    results = mesh.process(frame)
                    pose_results = pose_detector.process(frame)
                    
                    eye_data = {}
                    smile_data = {}
                    posture_data = {}
                    
                    if results.multi_face_landmarks:
                        face = results.multi_face_landmarks[0]
                        pose_est = head_pose.process(frame, face)
                        blink_data = blink.process(frame, face)
                        iris_data = iris.process(frame, face)
                        eye_data = eye_contact.process(pose_est, iris_data, blink_data)
                        smile_data = smile.process(frame, face)

                    if pose_results.pose_landmarks:
                        posture_data = posture.process(frame, pose_results.pose_landmarks)
                        
                    video_data = {
                        "eye_contact": eye_data,
                        "smile": smile_data,
                        "posture": posture_data
                    }
                    interview_manager.update_video(video_data)
                    
                    # Compute confidence
                    audio_data = interview_manager.audio_data or {}
                    fillers = audio_data.get("fillers")
                    filler_count = fillers["total"] if fillers and "total" in fillers else 0
                    sp_metrics = audio_data.get("speech_metrics", {})
                    s_data = {
                        "wpm": sp_metrics.get("wpm", 0),
                        "fillers": filler_count,
                        "long_pauses": sp_metrics.get("long_pauses", 0)
                    }
                    latest_eval = interview_manager.evaluations[-1].get("evaluation", {}) if interview_manager.evaluations else {}
                    
                    conf_score, conf_rating = conf_engine.calculate(video_data, s_data, latest_eval)
                    
                    # Send update back
                    await manager.send_json({
                        "type": "metrics_update",
                        "video": video_data,
                        "confidence": {"score": conf_score, "rating": conf_rating}
                    }, websocket)
                    
                    # Proactive Coaching Logic
                    if cooldown_timer > 0:
                        cooldown_timer -= 1
                    else:
                        posture_status = posture_data.get("posture", "Good")
                        
                        if posture_status in ["Leaning Too Left", "Leaning Too Right"]:
                            bad_posture_frames += 1
                        else:
                            bad_posture_frames = 0
                            
                        if bad_posture_frames >= 15:
                            await manager.send_json({
                                "type": "ai_reply",
                                "reply": f"Try to sit up straight and avoid {posture_status.lower()}."
                            }, websocket)
                            bad_posture_frames = 0
                            cooldown_timer = 60
            
            elif msg_type == "audio_chunk":
                audio_b64 = payload.get("data", "")
                text = ""
                if audio_b64:
                    try:
                        audio_bytes = decode_base64(audio_b64)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
                            temp_audio.write(audio_bytes)
                            temp_audio_path = temp_audio.name
                        
                        text = whisper_recognizer.transcribe(temp_audio_path)
                        os.remove(temp_audio_path)
                    except Exception as e:
                        print(f"Audio processing error: {e}")
                
                if text:
                    transcript.add(text)
                    fillers = filler_detector.process(transcript.get_transcript())
                    total_fillers = fillers.get("total", 0) if fillers else 0
                    metrics = speech_analyzer.process_chunk(text, total_fillers)
                    
                    audio_data = {
                        "text": text,
                        "fillers": fillers,
                        "speech_metrics": metrics
                    }
                    interview_manager.update_audio(audio_data)
                    
                    await manager.send_json({
                        "type": "audio_update",
                        "transcript": text,
                        "metrics": metrics
                    }, websocket)
                    
                    # Trigger conversational AI response if sentence is long enough
                    if len(text.strip()) > 2:
                        curr_q = question_manager.current_question()
                        metrics_for_llm = {
                            "video_metrics": interview_manager.video_data,
                            "speech_metrics": audio_data.get("speech_metrics"),
                            "fillers": audio_data.get("fillers", {}).get("total", 0)
                        }
                        metrics_for_llm = make_serializable(metrics_for_llm)
                        
                        try:
                            eval_res = evaluator.evaluate(curr_q, text, metrics=metrics_for_llm)
                            
                            # Add to manager for final report
                            eval_res["question"] = curr_q
                            eval_res["answer"] = text
                            interview_manager.add_evaluation(eval_res)
                            
                            reply_text = eval_res.get("conversational_reply", "That's an interesting point.")
                            follow_up = eval_res.get("follow_up_question", "")
                            
                            if follow_up:
                                question_manager.add_follow_up(follow_up)
                                
                        except Exception as e:
                            reply_text = f"LLM Error: {str(e)}"
                        
                        await manager.send_json({
                            "type": "ai_reply",
                            "reply": reply_text
                        }, websocket)
                        
                        # Proceed to next question automatically
                        next_q = question_manager.next_question()
                        if next_q == "Interview Complete.":
                            report = evaluator.generate_report(interview_manager.evaluations)
                            await manager.send_json({
                                "type": "report",
                                "report_text": report
                            }, websocket)
                        else:
                            await manager.send_json({
                                "type": "control",
                                "action": "next",
                                "question": next_q
                            }, websocket)
            
            elif msg_type == "resume_upload":
                resume_b64 = payload.get("data", "")
                if resume_b64:
                    try:
                        # DataURL format: data:application/pdf;base64,....
                        if "," in resume_b64:
                            resume_b64 = resume_b64.split(",")[1]
                        
                        resume_bytes = base64.b64decode(resume_b64)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                            temp_pdf.write(resume_bytes)
                            temp_pdf_path = temp_pdf.name
                        
                        # Extract text with PyMuPDF
                        doc = fitz.open(temp_pdf_path)
                        text = ""
                        for page in doc:
                            text += page.get_text()
                        doc.close()
                        os.remove(temp_pdf_path)
                        
                        # Generate dynamic questions
                        questions = evaluator.generate_resume_questions(text, num_questions=5)
                        
                        # Replace default questions
                        question_manager.active_questions = questions
                        question_manager.current_index = 0
                        
                        await manager.send_json({
                            "type": "resume_processed",
                            "message": "Questions generated successfully."
                        }, websocket)
                        
                    except Exception as e:
                        print(f"Resume processing error: {e}")
                        await manager.send_json({
                            "type": "ai_reply",
                            "reply": "I couldn't read your resume properly, but we can start anyway."
                        }, websocket)
                        # We trigger resume_processed anyway so it unblocks
                        await manager.send_json({
                            "type": "resume_processed"
                        }, websocket)

            elif msg_type == "next_question":
                prev_q = question_manager.current_question()
                next_q = question_manager.next_question()
                await manager.send_json({
                    "type": "control",
                    "action": "next",
                    "question": next_q
                }, websocket)
                
            elif msg_type == "start_interview":
                mode = payload.get("mode", "all")
                question_manager.reset(category=mode)
                first_q = question_manager.current_question()
                await manager.send_json({
                    "type": "control",
                    "action": "next",
                    "question": first_q
                }, websocket)
                
            elif msg_type == "end_session":
                report = evaluator.generate_report(interview_manager.evaluations)
                
                avg_score = 0
                if interview_manager.evaluations:
                    avg_score = sum(e.get("overall_score", 0) for e in interview_manager.evaluations) / len(interview_manager.evaluations)
                
                await manager.send_json({
                    "type": "report",
                    "report_text": report,
                    "overall_score": avg_score
                }, websocket)

            elif msg_type == "start_gd":
                gd_manager.reset()
                opening, topic = gd_manager.start_discussion()
                await manager.send_json({
                    "type": "gd_reply",
                    "speaker": gd_manager.judge,
                    "reply": opening,
                    "topic": topic
                }, websocket)

            elif msg_type == "gd_audio_chunk":
                audio_b64 = payload.get("data", "")
                if audio_b64:
                    if "base64," in audio_b64:
                        audio_b64 = audio_b64.split("base64,")[1]
                    audio_bytes = base64.b64decode(audio_b64)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
                        temp_audio.write(audio_bytes)
                        temp_audio_path = temp_audio.name
                        
                    transcription = whisper_recognizer.transcribe(temp_audio_path)
                    os.remove(temp_audio_path)
                    
                    if transcription and transcription.strip():
                        await manager.send_json({
                            "type": "audio_update",
                            "transcript": transcription,
                            "metrics": {"wpm": 0, "fillers": []}
                        }, websocket)
                        
                        # Get AI response
                        reply_data = gd_manager.process_turn("User", transcription)
                        await manager.send_json({
                            "type": "gd_reply",
                            "speaker": reply_data["speaker"],
                            "reply": reply_data["reply"]
                        }, websocket)

            elif msg_type == "end_gd":
                verdict, user_score = gd_manager.conclude_discussion()
                await manager.send_json({
                    "type": "gd_report",
                    "speaker": gd_manager.judge,
                    "reply": verdict,
                    "report_text": verdict,
                    "overall_score": user_score
                }, websocket)

            elif msg_type == "evaluate_recruitment":
                jd = payload.get("jd", "")
                resume = payload.get("resume", "")
                tech_score = payload.get("tech_score", 0.0)
                hr_score = payload.get("hr_score", 0.0)
                gd_score = payload.get("gd_score", 0.0)
                
                verdict = recruiter_manager.evaluate_candidate(jd, resume, tech_score, hr_score, gd_score)
                await manager.send_json({
                    "type": "recruitment_verdict",
                    "verdict": verdict
                }, websocket)

            elif msg_type == "get_planner_roadmap":
                jd = payload.get("jd", "")
                verdict = payload.get("verdict", "")
                
                roadmap = planner_manager.generate_roadmap(jd, verdict)
                await manager.send_json({
                    "type": "planner_roadmap",
                    "roadmap": roadmap
                }, websocket)

    except WebSocketDisconnect:
        print("Client disconnected.")
        manager.disconnect(websocket)
        interview_manager.stop()

from fastapi.staticfiles import StaticFiles

dist_path = os.path.join(os.path.dirname(__file__), "web-ui", "dist")
if os.path.exists(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
