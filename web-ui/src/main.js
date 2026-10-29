import { marked } from 'marked';
import confetti from 'canvas-confetti';

// State Management
const state = {
  ws: null,
  wsConnected: false,
  webcamStream: null,
  audioStream: null,
  mediaRecorder: null,
  recordedAudioChunks: [],
  isRecording: false,
  isGDRecording: false,
  gdRecorder: null,
  videoInterval: null,
  ttsEnabled: true,
  currentMode: 'all',
  lastRecruiterVerdict: ''
};

// DOM Elements
const wsStatus = document.getElementById('wsStatus');
const camStatus = document.getElementById('camStatus');
const micStatus = document.getElementById('micStatus');
const webcam = document.getElementById('webcam');
const captureCanvas = document.getElementById('captureCanvas');

// Vision HUD Elements
const hudEyeFill = document.getElementById('hudEyeFill');
const hudEyeVal = document.getElementById('hudEyeVal');
const hudSmileVal = document.getElementById('hudSmileVal');
const hudPoseVal = document.getElementById('hudPoseVal');
const metricEye = document.getElementById('metricEye');
const metricPosture = document.getElementById('metricPosture');
const metricSmile = document.getElementById('metricSmile');
const metricConfidenceRating = document.getElementById('metricConfidenceRating');
const postureBadge = document.getElementById('postureBadge');
const smileBadge = document.getElementById('smileBadge');
const coachingAlert = document.getElementById('coachingAlert');
const coachingText = document.getElementById('coachingText');

// Session & Audio Elements
const currentQuestionText = document.getElementById('currentQuestionText');
const aiReplyText = document.getElementById('aiReplyText');
const transcriptText = document.getElementById('transcriptText');
const statWpm = document.getElementById('statWpm');
const statFillers = document.getElementById('statFillers');
const statPauses = document.getElementById('statPauses');
const statConfidenceScore = document.getElementById('statConfidenceScore');
const btnRecord = document.getElementById('btnRecord');
const recordBtnText = document.getElementById('recordBtnText');
const btnNextQuestion = document.getElementById('btnNextQuestion');
const btnEndSession = document.getElementById('btnEndSession');
const ttsToggle = document.getElementById('ttsToggle');

// Resume Elements
const btnUploadResume = document.getElementById('btnUploadResume');
const resumeInput = document.getElementById('resumeInput');
const resumeFileName = document.getElementById('resumeFileName');

// Group Discussion Elements
const gdTopicBanner = document.getElementById('gdTopicBanner');
const gdTranscriptFeed = document.getElementById('gdTranscriptFeed');
const btnStartGD = document.getElementById('btnStartGD');
const btnRecordGDTurn = document.getElementById('btnRecordGDTurn');
const btnEndGD = document.getElementById('btnEndGD');
const speakerCards = {
  'Judge AI': document.getElementById('speakerJudge'),
  'AI Alex': document.getElementById('speakerAlex'),
  'AI Jordan': document.getElementById('speakerJordan'),
  'AI Taylor': document.getElementById('speakerTaylor'),
  'User': document.getElementById('speakerUser')
};

// Recruiter & Planner Elements
const pipelineJD = document.getElementById('pipelineJD');
const pipelineResume = document.getElementById('pipelineResume');
const inputTechScore = document.getElementById('inputTechScore');
const inputHRScore = document.getElementById('inputHRScore');
const inputGDScore = document.getElementById('inputGDScore');
const btnRunRecruiter = document.getElementById('btnRunRecruiter');
const verdictContainer = document.getElementById('verdictContainer');
const verdictMarkdown = document.getElementById('verdictMarkdown');
const btnTransferToPlanner = document.getElementById('btnTransferToPlanner');

const plannerRoleInput = document.getElementById('plannerRoleInput');
const plannerVerdictInput = document.getElementById('plannerVerdictInput');
const btnGenerateRoadmap = document.getElementById('btnGenerateRoadmap');
const roadmapContainer = document.getElementById('roadmapContainer');
const roadmapMarkdown = document.getElementById('roadmapMarkdown');

// Report Modal
const reportModal = document.getElementById('reportModal');
const reportContent = document.getElementById('reportContent');
const btnCloseReportModal = document.getElementById('btnCloseReportModal');
const btnCloseReport = document.getElementById('btnCloseReport');
const btnPrintReport = document.getElementById('btnPrintReport');

// 1. WEBSOCKET SETUP
function initWebSocket() {
  const wsUrl = `ws://${window.location.hostname || '127.0.0.1'}:8000/ws`;
  console.log(`Connecting to WebSocket: ${wsUrl}`);
  
  state.ws = new WebSocket(wsUrl);

  state.ws.onopen = () => {
    state.wsConnected = true;
    wsStatus.innerHTML = '<span class="dot dot-connected"></span> Connected';
    console.log('Connected to AI Interviewer Server!');
  };

  state.ws.onclose = () => {
    state.wsConnected = false;
    wsStatus.innerHTML = '<span class="dot dot-disconnected"></span> Disconnected';
    console.warn('Disconnected. Reconnecting in 3s...');
    setTimeout(initWebSocket, 3000);
  };

  state.ws.onerror = (err) => {
    console.error('WebSocket Error:', err);
  };

  state.ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleServerMessage(data);
    } catch (e) {
      console.error('Error parsing WS message:', e);
    }
  };
}

function sendWs(payload) {
  if (state.ws && state.ws.readyState === WebSocket.OPEN) {
    state.ws.send(JSON.stringify(payload));
  }
}

// 2. SERVER MESSAGE ROUTING
function handleServerMessage(data) {
  switch (data.type) {
    case 'control':
      if (data.action === 'start' || data.action === 'next') {
        currentQuestionText.textContent = data.question || 'No question available.';
        speakText(data.question);
      }
      break;

    case 'metrics_update':
      updateVisionHUD(data.video, data.confidence);
      break;

    case 'audio_update':
      if (data.transcript) {
        transcriptText.textContent = data.transcript;
      }
      if (data.metrics) {
        statWpm.textContent = Math.round(data.metrics.wpm || 0);
        statFillers.textContent = data.metrics.fillers?.length || data.metrics.filler_count || 0;
        statPauses.textContent = data.metrics.long_pauses || 0;
      }
      break;

    case 'ai_reply':
      aiReplyText.textContent = data.reply;
      speakText(data.reply);
      // If it looks like coaching feedback
      if (data.reply.toLowerCase().includes('sit up') || data.reply.toLowerCase().includes('straight') || data.reply.toLowerCase().includes('eye contact')) {
        showCoachingAlert(data.reply);
      }
      break;

    case 'report':
      showReportModal(data.report_text);
      break;

    case 'resume_processed':
      alert('📄 ' + (data.message || 'Resume processed successfully! Dynamic questions generated.'));
      resumeFileName.textContent = '✓ Ready with dynamic questions';
      break;

    case 'gd_reply':
      handleGDSpeaker(data.speaker, data.reply);
      if (data.topic) {
        gdTopicBanner.innerHTML = `Topic: <strong>${data.topic}</strong>`;
      }
      break;

    case 'gd_report':
      handleGDSpeaker(data.speaker || 'Judge AI', data.reply);
      confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
      break;

    case 'recruitment_verdict':
      btnRunRecruiter.disabled = false;
      btnRunRecruiter.innerHTML = '🔍 Run Recruiter Agent Verdict';
      state.lastRecruiterVerdict = data.verdict;
      verdictContainer.style.display = 'block';
      verdictMarkdown.innerHTML = marked.parse(data.verdict);
      verdictContainer.scrollIntoView({ behavior: 'smooth' });
      break;

    case 'planner_roadmap':
      btnGenerateRoadmap.disabled = false;
      btnGenerateRoadmap.innerHTML = '✨ Generate Personalized Roadmap';
      roadmapContainer.style.display = 'block';
      roadmapMarkdown.innerHTML = marked.parse(data.roadmap);
      roadmapContainer.scrollIntoView({ behavior: 'smooth' });
      break;

    default:
      console.log('Unhandled message:', data);
  }
}

// 3. VISION HUD UPDATES
function updateVisionHUD(videoData, confidenceData) {
  if (!videoData) return;

  // Eye contact
  const eye = videoData.eye_contact || {};
  const eyeScore = eye.score !== undefined ? Math.round(eye.score * 100) : (eye.eye_contact ? 90 : 30);
  hudEyeFill.style.width = `${eyeScore}%`;
  hudEyeVal.textContent = `${eyeScore}%`;
  metricEye.textContent = `${eyeScore}%`;

  // Posture
  const posture = videoData.posture || {};
  const postureStatus = posture.posture || 'Good';
  metricPosture.textContent = postureStatus;
  postureBadge.textContent = postureStatus;
  if (postureStatus === 'Good') {
    postureBadge.style.color = '#10b981';
    metricPosture.className = 'box-value text-emerald';
  } else {
    postureBadge.style.color = '#f59e0b';
    metricPosture.className = 'box-value text-amber';
  }

  // Smile
  const smile = videoData.smile || {};
  const isSmiling = smile.smile || false;
  hudSmileVal.textContent = isSmiling ? 'Yes 😊' : 'Neutral';
  smileBadge.textContent = isSmiling ? 'Smiling' : 'Neutral';
  metricSmile.textContent = smile.score ? smile.score.toFixed(2) : (isSmiling ? '1.0' : '0.0');

  // Head pose
  const headPose = eye.gaze_direction || 'Center';
  hudPoseVal.textContent = headPose;

  // Confidence
  if (confidenceData) {
    statConfidenceScore.textContent = `${Math.round(confidenceData.score || 0)}%`;
    metricConfidenceRating.textContent = confidenceData.rating || 'Moderate';
  }
}

function showCoachingAlert(msg) {
  coachingText.textContent = msg;
  coachingAlert.style.display = 'flex';
  setTimeout(() => {
    coachingAlert.style.display = 'none';
  }, 7000);
}

// 4. WEBCAM & VIDEO STREAMING
async function initMedia() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 360, frameRate: { ideal: 15 } },
      audio: true
    });

    state.webcamStream = stream;
    webcam.srcObject = stream;
    camStatus.innerHTML = '<span class="dot dot-active"></span> Camera';
    micStatus.innerHTML = '<span class="dot dot-active"></span> Mic';

    // Start sending video frames every 180ms
    const ctx = captureCanvas.getContext('2d');
    captureCanvas.width = 320;
    captureCanvas.height = 180;

    state.videoInterval = setInterval(() => {
      if (!state.wsConnected || webcam.readyState !== 4) return;

      ctx.drawImage(webcam, 0, 0, captureCanvas.width, captureCanvas.height);
      const dataUrl = captureCanvas.toDataURL('image/jpeg', 0.5);

      sendWs({
        type: 'video',
        data: dataUrl
      });
    }, 200);

    // Setup Audio Recorder
    initAudioRecorder(stream);

  } catch (err) {
    console.warn('Camera/Mic permission failed:', err);
    camStatus.innerHTML = '<span class="dot dot-inactive"></span> Cam Blocked';
    micStatus.innerHTML = '<span class="dot dot-inactive"></span> Mic Blocked';
  }
}

// 5. AUDIO RECORDING & SPEECH-TO-TEXT
function initAudioRecorder(stream) {
  let mimeType = 'audio/webm';
  if (!MediaRecorder.isTypeSupported('audio/webm')) {
    mimeType = 'audio/mp4';
  }

  const audioTrack = stream.getAudioTracks()[0];
  const audioOnlyStream = new MediaStream([audioTrack]);

  state.mediaRecorder = new MediaRecorder(audioOnlyStream, { mimeType });

  state.mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) {
      state.recordedAudioChunks.push(e.data);
    }
  };

  state.mediaRecorder.onstop = async () => {
    const blob = new Blob(state.recordedAudioChunks, { type: mimeType });
    state.recordedAudioChunks = [];

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64Data = reader.result;
      sendWs({
        type: 'audio_chunk',
        data: base64Data
      });
    };
    reader.readAsDataURL(blob);
  };
}

function toggleRecording() {
  if (!state.mediaRecorder) return;

  if (!state.isRecording) {
    state.recordedAudioChunks = [];
    state.mediaRecorder.start();
    state.isRecording = true;
    btnRecord.classList.add('btn-danger');
    btnRecord.classList.remove('btn-primary');
    recordBtnText.textContent = 'Stop & Evaluate';
    transcriptText.textContent = 'Listening to your answer...';
  } else {
    state.mediaRecorder.stop();
    state.isRecording = false;
    btnRecord.classList.remove('btn-danger');
    btnRecord.classList.add('btn-primary');
    recordBtnText.textContent = 'Record Answer';
    transcriptText.textContent = 'Transcribing speech with Groq Whisper...';
  }
}

// 6. MULTI-AGENT GD LOGIC
function handleGDSpeaker(speaker, text) {
  // Clear active highlights
  Object.values(speakerCards).forEach(card => card?.classList.remove('speaking'));

  // Highlight current speaker
  const card = speakerCards[speaker] || speakerCards['AI Alex'];
  if (card) {
    card.classList.add('speaking');
  }

  // Append to transcript feed
  const msgDiv = document.createElement('div');
  const isJudge = speaker === 'Judge AI';
  const isUser = speaker === 'User';
  msgDiv.className = `debate-msg ${isJudge ? 'speaker-judge' : (isUser ? 'speaker-user' : 'speaker-ai')}`;
  msgDiv.innerHTML = `<strong>${speaker}:</strong> ${text}`;
  gdTranscriptFeed.appendChild(msgDiv);
  gdTranscriptFeed.scrollTop = gdTranscriptFeed.scrollHeight;

  // Speak aloud
  if (!isUser) {
    speakText(text);
  }
}

function setupGDAudio() {
  if (!state.webcamStream) return;
  const audioTrack = state.webcamStream.getAudioTracks()[0];
  const audioStream = new MediaStream([audioTrack]);

  state.gdRecorder = new MediaRecorder(audioStream);
  let gdChunks = [];

  state.gdRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) gdChunks.push(e.data);
  };

  state.gdRecorder.onstop = () => {
    const blob = new Blob(gdChunks, { type: 'audio/webm' });
    gdChunks = [];
    const reader = new FileReader();
    reader.onloadend = () => {
      sendWs({
        type: 'gd_audio_chunk',
        data: reader.result
      });
    };
    reader.readAsDataURL(blob);
  };
}

function toggleGDTurnRecord() {
  if (!state.gdRecorder) setupGDAudio();
  if (!state.gdRecorder) return;

  if (!state.isGDRecording) {
    state.gdRecorder.start();
    state.isGDRecording = true;
    btnRecordGDTurn.classList.add('btn-danger');
    btnRecordGDTurn.innerHTML = '⏹️ Stop Speaking';
    handleGDSpeaker('User', 'Speaking...');
  } else {
    state.gdRecorder.stop();
    state.isGDRecording = false;
    btnRecordGDTurn.classList.remove('btn-danger');
    btnRecordGDTurn.innerHTML = '🎙️ Speak Argument (Turn)';
  }
}

// 7. BROWSER TEXT-TO-SPEECH (TTS)
function speakText(text) {
  if (!state.ttsEnabled || !window.speechSynthesis) return;

  window.speechSynthesis.cancel(); // Stop current speech
  const cleanText = text.replace(/[*#_~`]/g, '');
  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.rate = 1.05;
  utterance.pitch = 1.0;
  window.speechSynthesis.speak(utterance);
}

// 8. REPORT MODAL
function showReportModal(reportMarkdown) {
  reportContent.innerHTML = marked.parse(reportMarkdown || 'No report generated.');
  reportModal.style.display = 'flex';
  confetti({ particleCount: 120, spread: 80, origin: { y: 0.5 } });
}

// 9. EVENT LISTENERS SETUP
function setupEventListeners() {
  // Navigation Tabs
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      const targetPane = document.getElementById(`pane-${tab.dataset.tab}`);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  // Record Answer Button
  btnRecord.addEventListener('click', toggleRecording);

  // Next Question Button
  btnNextQuestion.addEventListener('click', () => {
    sendWs({ type: 'next_question' });
  });

  // End Session Button
  btnEndSession.addEventListener('click', () => {
    sendWs({ type: 'end_session' });
  });

  // TTS Toggle
  ttsToggle.addEventListener('click', () => {
    state.ttsEnabled = !state.ttsEnabled;
    ttsToggle.textContent = state.ttsEnabled ? '🔊 TTS ON' : '🔇 TTS OFF';
    ttsToggle.classList.toggle('active', state.ttsEnabled);
    if (!state.ttsEnabled) window.speechSynthesis.cancel();
  });

  // Mode Switchers
  const modeButtons = [
    { btn: document.getElementById('btnModeTech'), mode: 'technical' },
    { btn: document.getElementById('btnModeHR'), mode: 'hr' },
    { btn: document.getElementById('btnModeResume'), mode: 'all' }
  ];

  modeButtons.forEach(({ btn, mode }) => {
    btn?.addEventListener('click', () => {
      modeButtons.forEach(m => m.btn.classList.remove('active'));
      btn.classList.add('active');
      state.currentMode = mode;
      sendWs({ type: 'start_interview', mode });
    });
  });

  // Resume Upload
  btnUploadResume.addEventListener('click', () => resumeInput.click());
  resumeInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      resumeFileName.textContent = `Uploading ${file.name}...`;
      const reader = new FileReader();
      reader.onload = () => {
        sendWs({
          type: 'resume_upload',
          data: reader.result
        });
      };
      reader.readAsDataURL(file);
    }
  });

  // GD Buttons
  btnStartGD.addEventListener('click', () => {
    btnRecordGDTurn.disabled = false;
    btnEndGD.disabled = false;
    sendWs({ type: 'start_gd' });
  });

  btnRecordGDTurn.addEventListener('click', toggleGDTurnRecord);

  btnEndGD.addEventListener('click', () => {
    btnRecordGDTurn.disabled = true;
    btnEndGD.disabled = true;
    sendWs({ type: 'end_gd' });
  });

  // Recruiter Pipeline Button
  btnRunRecruiter.addEventListener('click', () => {
    const jd = pipelineJD.value.trim();
    const resume = pipelineResume.value.trim();
    const techScore = parseFloat(inputTechScore.value) || 85;
    const hrScore = parseFloat(inputHRScore.value) || 88;
    const gdScore = parseFloat(inputGDScore.value) || 80;

    if (!jd) {
      alert('Please provide a Job Description.');
      return;
    }

    btnRunRecruiter.disabled = true;
    btnRunRecruiter.innerHTML = '⏳ Recruiter Agent Evaluating...';

    sendWs({
      type: 'evaluate_recruitment',
      jd,
      resume,
      tech_score: techScore,
      hr_score: hrScore,
      gd_score: gdScore
    });
  });

  // Transfer Recruiter Verdict to Planner
  btnTransferToPlanner.addEventListener('click', () => {
    plannerVerdictInput.value = state.lastRecruiterVerdict;
    document.querySelector('.nav-tab[data-tab="planner"]').click();
  });

  // Planner Generate Roadmap Button
  btnGenerateRoadmap.addEventListener('click', () => {
    const role = plannerRoleInput.value.trim();
    const verdict = plannerVerdictInput.value.trim();

    if (!verdict) {
      alert('Please enter or transfer a recruiter verdict first.');
      return;
    }

    btnGenerateRoadmap.disabled = true;
    btnGenerateRoadmap.innerHTML = '⏳ Coach Designing Roadmap...';

    sendWs({
      type: 'get_planner_roadmap',
      jd: role,
      verdict: verdict
    });
  });

  // Modal Close
  btnCloseReportModal.addEventListener('click', () => reportModal.style.display = 'none');
  btnCloseReport.addEventListener('click', () => reportModal.style.display = 'none');
  btnPrintReport.addEventListener('click', () => window.print());
}

// 10. INITIALIZATION
window.addEventListener('DOMContentLoaded', () => {
  initWebSocket();
  initMedia();
  setupEventListeners();
});

