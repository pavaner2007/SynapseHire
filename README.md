# 🤖 AgentVerse | Multimodal AI Interview & Behavioral Simulator

An advanced, real-time interview preparation platform powered by multi-agent orchestration, computer vision, and high-throughput LLM reasoning. **AgentVerse** evaluates candidates not just on *what* they say, but *how* they say it—tracking body language, vocal delivery, and debate agility in real time.

---

## 🌟 Key Highlights & Modes

- 📹 **Live Vision Telemetry (MediaPipe & OpenCV)**: Real-time tracking of eye-contact percentage, posture stability (detects slouching or leaning), blink rates, and smile intensity.
- 🎙️ **Speech & Vocal Intelligence (Groq Whisper)**: Sub-second audio transcription measuring Words-Per-Minute (WPM), filler word frequency (`um`, `uh`, `like`), and conversational pauses.
- 📄 **Dynamic Resume Ingestion (PyMuPDF)**: Automatically extracts skills and experience from uploaded PDF resumes to dynamically generate targeted questions.
- 👥 **Multi-Agent Group Discussion Arena**: Simulates high-stakes competitive debates against 3 distinct AI personas (*Aggressive Counter-arguer*, *Technical Specialist*, *Pragmatic Realist*) moderated and scored by an AI Judge.
- 👔 **The Recruiter Pipeline**: Synthesizes a target Job Description (JD), Resume, Technical score, HR score, and GD score into an actionable hiring verdict (**RECRUITED** / **NOT RECRUITED**).
- 📅 **Planner Agent Coaching**: Generates a personalized, week-by-week soft-skills and communication improvement timeline based on performance gaps.

---

## 🏗️ Architecture & How It Works

```
Candidate (Webcam + Mic)
       │
       ▼
 [Browser Web UI] ──(WebSockets: /ws)──► [FastAPI Backend]
       │                                         │
       ├── Video Frames (5 FPS) ─────────────► [MediaPipe + OpenCV]
       │                                         • Face Mesh & Iris Tracking
       │                                         • Posture & Pose Estimation
       │
       └── Audio Chunks (WebM) ──────────────► [Groq Whisper-large-v3]
                                                 • Real-time Transcription
                                                 • WPM & Filler Detector
                                                 │
                                                 ▼
                                        [Groq LLM Reasoning]
                                         • Answer Evaluation
                                         • Multi-Agent GD Debate
                                         • Recruiter & Planner Pipeline
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Vanilla JS, HTML5 Canvas, CSS3 Glassmorphism, Vite Dev Server |
| **Backend** | Python 3.12, FastAPI, WebSockets (`/ws`), Uvicorn |
| **Computer Vision** | OpenCV, MediaPipe (Face Mesh, Iris Tracker, Pose Estimation) |
| **Speech Processing** | Groq Whisper (`whisper-large-v3`), Web Audio API, MediaRecorder |
| **AI Orchestration** | Groq Cloud SDK (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`) |
| **Document Processing** | PyMuPDF (`fitz`) |

---

## 📂 Project Directory Structure

```text
├── audio/                      # Audio processing, speech metrics, and Whisper STT
│   ├── audio_worker.py
│   ├── filler_words.py
│   ├── speech_analyzer.py
│   ├── whisper_recognizer.py   # Groq Whisper integration
│   └── wpm.py
├── video/                      # Computer vision and telemetry pipeline
│   ├── blink.py
│   ├── eye_contact.py
│   ├── face_mesh.py            # MediaPipe face mesh
│   ├── head_pose.py
│   ├── iris_tracker.py
│   ├── pose_detector.py        # MediaPipe pose estimation
│   ├── posture.py              # Slouching / leaning detection
│   └── smile.py
├── single_agent/               # 1-on-1 interview orchestration
│   ├── answer_evaluator.py     # LLM grading & conversational replies
│   ├── confidence_engine.py    # Multimodal confidence scoring
│   ├── filler_detector.py
│   ├── manager.py
│   ├── questions.py            # Question bank & dynamic resume questions
│   └── transcript.py
├── multi_agent/                # Multi-agent simulation workflows
│   ├── gd_manager.py           # Competitive Group Discussion arena
│   ├── recruiter_manager.py    # End-to-end recruitment pipeline
│   └── planner_manager.py      # Soft-skills improvement roadmap coach
├── web-ui/                     # Modern Vite web application
│   ├── index.html              # Dashboard, debate stage, and telemetry HUD
│   ├── src/
│   │   ├── main.js             # WebSocket client & real-time streaming
│   │   └── style.css           # Glassmorphism dark UI design
│   ├── package.json
│   └── vite.config.js
├── server.py                   # FastAPI WebSocket server & static host
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment variables
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** (Python 3.12 recommended)
- **Node.js 18+** & npm
- A free **Groq API Key** from [console.groq.com](https://console.groq.com)

### 2. Backend Setup
1. Clone the repository and navigate into the project directory:
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment variables:
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. Start the FastAPI server:
   ```bash
   python server.py
   ```
   *The server will start at `http://127.0.0.1:8000` with WebSocket endpoint at `ws://127.0.0.1:8000/ws`.*

### 3. Frontend Setup (Vite Dev Server)
In a second terminal window:
1. Navigate to the `web-ui` directory:
   ```bash
   cd web-ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open the displayed URL (typically `http://localhost:5173`) in your browser.
   *(Alternatively, opening `http://127.0.0.1:8000` directly serves the production-built UI).*

---

## 🎯 How to Use

1. **Camera & Microphone Permissions**: Grant access when the browser prompts.
2. **Technical / HR Mode**: Click **Record Answer** to respond to questions. Receive real-time speech telemetry, posture coaching, and conversational AI feedback.
3. **Resume Mode**: Upload your PDF resume to have the AI dynamically generate targeted interview questions based on your background.
4. **Group Discussion**: Enter the **Multi-Agent GD** tab. Click **Start Group Discussion** to receive a topic from the Judge AI and debate live against three AI competitors.
5. **Recruiter Pipeline**: Paste a Job Description, input stage scores, and run the Recruiter Agent to get an immediate **RECRUITED** or **NOT RECRUITED** hiring report.
6. **Planner Coach**: Convert your recruiter verdict into a personalized week-by-week soft-skills roadmap.

---

## 📜 License
Distributed under the MIT License. Feel free to use, modify, and distribute.
