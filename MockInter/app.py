import streamlit as st
import time
import os
import io
import json
import requests
import speech_recognition as sr
import av
import cv2
from datetime import datetime
from dotenv import load_dotenv
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

# ---------------------------
# Storage: JSON file
# ---------------------------
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd(), "interview_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_response(response_data):
    data = load_data()
    clean = {k: v for k, v in response_data.items() if isinstance(v, (str, int, float, bool, type(None)))}
    data.append(clean)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------------------
# Ollama
# ---------------------------
def ask_ollama(prompt):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }, timeout=120)
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"Error contacting LLaMA 3: {e}"

# ---------------------------
# Resume Text Extraction
# ---------------------------
def extract_resume_text(uploaded_file):
    try:
        import pypdf
        uploaded_file.seek(0)
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"(Could not extract resume text: {e})"

# ---------------------------
# Audio Transcription
# ---------------------------
def transcribe_audio_bytes(audio_bytes):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        return ""

# ---------------------------
# Video Processor (recv)
# ---------------------------
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.no_face_warning_count = 0
        self.multiple_face_warning_count = 0
        self.last_no_face_time = time.time()
        self.last_multiple_time = time.time()
        self.no_face_frames = 0
        self.multiple_face_frames = 0
        self.frame_threshold = 5
        self.warning_interval = 2
        self.proctoring_enabled = False
        self.current_question = ""
        self.question_number = 0
        self.total_questions = 3

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        current_time = time.time()
        violation_message = None

        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if self.proctoring_enabled:
            if len(faces) == 0:
                self.no_face_frames += 1
                if self.no_face_frames >= self.frame_threshold:
                    if current_time - self.last_no_face_time > self.warning_interval:
                        self.no_face_warning_count += 1
                        self.last_no_face_time = current_time
                    violation_message = "No Face Detected!"
            else:
                self.no_face_frames = 0

            if len(faces) > 1:
                self.multiple_face_frames += 1
                if self.multiple_face_frames >= self.frame_threshold:
                    if current_time - self.last_multiple_time > self.warning_interval:
                        self.multiple_face_warning_count += 1
                        self.last_multiple_time = current_time
                    violation_message = "Multiple Faces Detected!"
            else:
                self.multiple_face_frames = 0

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if violation_message:
            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (img.shape[1], img.shape[0]), (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = img.shape[1] / 800
            thickness = max(2, int(img.shape[1] / 400))
            text_size, _ = cv2.getTextSize(violation_message, font, font_scale, thickness)
            tx = (img.shape[1] - text_size[0]) // 2
            ty = (img.shape[0] + text_size[1]) // 2
            cv2.putText(img, violation_message, (tx, ty), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        # Question banner on top
        if self.current_question:
            h_img = img.shape[0]
            w_img = img.shape[1]
            banner_h = 75
            overlay2 = img.copy()
            cv2.rectangle(overlay2, (0, 0), (w_img, banner_h), (15, 15, 50), -1)
            cv2.addWeighted(overlay2, 0.8, img, 0.2, 0, img)

            # Progress indicator
            prog_text = f"Q{self.question_number}/{self.total_questions}"
            cv2.putText(img, prog_text, (w_img - 70, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)

            # Question text (wrap if needed)
            max_chars = max(35, w_img // 11)
            q_text = self.current_question
            if len(q_text) > max_chars:
                # Try to split at a word boundary
                split_idx = q_text[:max_chars].rfind(" ")
                if split_idx == -1:
                    split_idx = max_chars
                line1 = q_text[:split_idx]
                line2 = q_text[split_idx:split_idx + max_chars]
                cv2.putText(img, line1, (8, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(img, line2 + ("..." if len(q_text) > split_idx + max_chars else ""), (8, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)
            else:
                cv2.putText(img, q_text, (8, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

# ---------------------------
# Interview Logic
# ---------------------------
def get_interview_questions(job_role, resume_text, experience, interview_type):
    if interview_type == "Technical Interview":
        focus = """Generate TECHNICAL questions only — programming, data structures, algorithms,
system design, frameworks based on candidate's resume skills and job role.
Do NOT ask behavioral or HR questions."""
    else:
        focus = """Generate BEHAVIORAL/HR questions only — teamwork, leadership, communication,
conflict resolution, strengths, weaknesses, career goals.
Do NOT ask technical coding questions."""

    prompt = f"""Generate exactly 3 interview questions for a {job_role} role.
Candidate has {experience} years of experience.
{focus}

Resume Content:
{resume_text[:2500]}

Return ONLY 3 numbered questions. One per line. No extra text."""

    response = ask_ollama(prompt)
    lines = [l.strip() for l in response.split("\n") if l.strip()]
    questions = [l for l in lines if l and l[0].isdigit()]
    if len(questions) < 2:
        questions = lines
    return questions[:3]

def evaluate_answer(question, answer):
    """Evaluate answer only if answer is provided. Return score 0 if empty."""
    if not answer or not answer.strip():
        return "Score: 0\nVerdict: Incorrect\nFeedback: No answer was provided for this question.\nSuggestion: Try to attempt every question, even a partial answer earns more credit than silence."

    prompt = f"""You are a strict interviewer. Evaluate this interview answer.
If the answer is vague, off-topic, or irrelevant to the question, give a low score.
Only give a high score if the answer is accurate, detailed, and relevant.

Question: {question}
Candidate's Answer: {answer}

Respond in EXACTLY this format (nothing else, no markdown, no extra lines):
Score: <integer 0 to 10>
Verdict: <one of: Correct, Partially Correct, Incorrect>
Feedback: <2-3 sentences of specific, honest feedback based on the actual answer given>
Suggestion: <1-2 sentences with a concrete, actionable tip on how to improve this specific answer>"""
    return ask_ollama(prompt)

def extract_score(text):
    import re
    match = re.search(r"Score:\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
    if match:
        try:
            return min(10.0, float(match.group(1)))
        except ValueError:
            pass
    return 0.0

def extract_field(text, field):
    """Generic extractor for a 'Field: value' line. Returns '' if not found."""
    import re
    match = re.search(rf"{field}:\s*(.+)", text, re.IGNORECASE)
    if match:
        # Stop at the next "Label:" pattern if the model didn't newline properly
        value = match.group(1).strip()
        value = re.split(r"\n?[A-Za-z ]+:\s", value)[0].strip()
        return value
    return ""

def extract_verdict(text, score):
    """Get verdict from model output, falling back to a score-based verdict."""
    verdict = extract_field(text, "Verdict")
    if verdict:
        return verdict
    if score >= 7:
        return "Correct"
    elif score >= 4:
        return "Partially Correct"
    else:
        return "Incorrect"

def extract_suggestion(text):
    return extract_field(text, "Suggestion") or "Try to add more specific examples and structure your answer clearly (situation, action, result)."

def verdict_badge(verdict):
    v = verdict.lower()
    if "partial" in v:
        return "⚠️", "#f0ad4e"
    elif "incorrect" in v or "wrong" in v:
        return "❌", "#d9534f"
    else:
        return "✅", "#28a745"

# ---------------------------
# Session State Init
# ---------------------------
for key, default in [
    ("interviews", []),
    ("current_interview", None),
    ("question_index", 0),
    ("show_form", False),
    ("responses", []),
    ("awaiting_next", False),
    ("last_feedback", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.markdown("### Interview Type")
interview_type = st.sidebar.radio(
    "Choose type:",
    ["Technical Interview", "Mock Interview"],
    key="interview_type_select"
)

# ---------------------------
# Main Layout
# ---------------------------
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%);
        color: #f3f4f6;
    }
    .stCard {
        background: rgba(31, 41, 55, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎤 AI Mock Interview")
st.caption(f"Mode: **{interview_type}**")

cam_col, content_col = st.columns([1, 1.5])

with cam_col:
    st.subheader("📷 Live Camera")

    # Auto-start camera when interview is in progress
    auto_start = st.session_state.current_interview is not None

    camera = webrtc_streamer(
        key="mock_camera",
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTC_CONFIGURATION,
        async_processing=True,
        media_stream_constraints={"video": True, "audio": True},  # audio:True for mic access
        desired_playing_state=True if auto_start else None,
    )
    if camera and hasattr(camera, "video_processor") and camera.video_processor:
        vp = camera.video_processor
        st.caption(f"⚠️ No Face: {vp.no_face_warning_count} | 👥 Multiple: {vp.multiple_face_warning_count}")

# ---------------------------
# Content Column
# ---------------------------
with content_col:

    # ---- FORM ----
    if st.session_state.current_interview is None:
        st.subheader("Start a New Interview")
        if st.button("➕ Add New Interview"):
            st.session_state.show_form = True

        if st.session_state.show_form:
            with st.form("interview_form", clear_on_submit=False):
                username = st.text_input("Your Name")
                job_role = st.text_input("Job Role", placeholder="Ex. Full Stack Developer")
                resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
                experience = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
                col_start, col_cancel = st.columns(2)
                start_btn = col_start.form_submit_button("▶️ Start Interview", use_container_width=True)
                cancel_btn = col_cancel.form_submit_button("✖️ Cancel", use_container_width=True)

            if cancel_btn:
                st.session_state.show_form = False
                st.rerun()

            if start_btn:
                if not username or not job_role or resume_file is None:
                    st.warning("Please fill all fields and upload your resume.")
                else:
                    with st.spinner("📄 Reading resume..."):
                        resume_text = extract_resume_text(resume_file)
                    with st.spinner(f"🤖 Generating 3 {interview_type} questions..."):
                        questions = get_interview_questions(job_role, resume_text, experience, interview_type)

                    st.session_state.current_interview = {
                        "username": username,
                        "role": job_role,
                        "experience": experience,
                        "interview_type": interview_type,
                        "questions": questions,
                    }
                    st.session_state.question_index = 0
                    st.session_state.responses = []
                    st.session_state.show_form = False

                    # Enable proctoring + set first question
                    if camera and hasattr(camera, "video_processor") and camera.video_processor:
                        vp = camera.video_processor
                        vp.proctoring_enabled = True
                        vp.total_questions = len(questions)
                        vp.question_number = 1
                        if questions:
                            vp.current_question = questions[0]
                    st.rerun()

        # Previous interviews
        if st.session_state.interviews:
            st.markdown("---")
            st.subheader("📋 Previous Interviews")
            for inv in reversed(st.session_state.interviews):
                scores = [r.get("score") for r in inv.get("responses", []) if r.get("score") is not None]
                avg_str = f"{sum(scores)/len(scores):.1f}/10" if scores else "N/A"
                with st.expander(f"{inv['role']} | {inv['interview_type']} | Score: {avg_str}"):
                    for r in inv.get("responses", []):
                        st.markdown(f"**Q:** {r['question']}")
                        st.markdown(f"**A:** {r['answer'] or '_No answer provided_'}")
                        st.markdown(f"**Feedback:** {r['feedback']}")
                        st.markdown(f"**Score:** {r.get('score', 0)}/10")
                        st.markdown("---")

    # ---- INTERVIEW IN PROGRESS ----
    elif st.session_state.current_interview is not None:
        interview = st.session_state.current_interview
        questions = interview["questions"]
        index = st.session_state.question_index

        if index < len(questions):
            # Sync camera overlay
            if camera and hasattr(camera, "video_processor") and camera.video_processor:
                vp = camera.video_processor
                vp.proctoring_enabled = True
                vp.current_question = questions[index]
                vp.question_number = index + 1
                vp.total_questions = len(questions)

            st.markdown(f"**{interview['role']}** | {interview['interview_type']} | {interview['experience']} yrs")
            st.progress((index) / len(questions), text=f"Question {index + 1} of {len(questions)}")

            st.markdown(f"### ❓ Question {index + 1}")
            st.info(questions[index])

            # ---- STEP 1: answer not yet submitted for this question ----
            if not st.session_state.awaiting_next:

                # Mic recorder
                st.markdown("🎙️ **Record your answer** (or type below):")
                try:
                    from streamlit_mic_recorder import mic_recorder
                    audio = mic_recorder(
                        start_prompt="🎙️ Start Recording",
                        stop_prompt="⏹️ Stop Recording",
                        just_once=True,
                        use_container_width=True,
                        key=f"mic_{index}"
                    )
                    if audio and audio.get("bytes"):
                        with st.spinner("Transcribing your spoken answer..."):
                            transcribed = transcribe_audio_bytes(audio["bytes"])
                        if transcribed:
                            # IMPORTANT: write straight into the text_area's own key.
                            # (Passing a separate `value=` on every rerun does NOT work
                            # once the widget key already exists in session_state — that
                            # was why a spoken answer never reached the box and got
                            # submitted as blank / treated as "Skipped".)
                            st.session_state[f"answer_area_{index}"] = transcribed
                            st.success("✅ Recorded! Transcribed text added below — review and submit.")
                            st.rerun()
                        else:
                            st.warning("Couldn't understand the audio. Please try again or type your answer.")
                except ImportError:
                    st.info("Install streamlit-mic-recorder for voice input.")

                answer = st.text_area(
                    "Your Answer:",
                    height=130,
                    placeholder="Type your answer here, or use the mic recorder above...",
                    key=f"answer_area_{index}"
                )

                col1, col2 = st.columns([1, 1])
                with col1:
                    skip = st.button("⏭️ Skip (No Answer)", key=f"skip_{index}", use_container_width=True)
                with col2:
                    submit = st.button("✅ Submit Answer", key=f"next_{index}", use_container_width=True, type="primary")

                if skip or submit:
                    # Use ONLY what's currently in the answer box — ignore stale session state
                    final_answer = "" if skip else answer.strip()

                    # Block LLaMA if no answer given
                    if not final_answer:
                        feedback = "Score: 0\nVerdict: Incorrect\nFeedback: No answer was provided for this question.\nSuggestion: Attempt every question, even a partial answer earns more credit than silence."
                        score = 0.0
                    else:
                        with st.spinner("🤖 Analyzing your answer..."):
                            feedback = evaluate_answer(questions[index], final_answer)
                        score = extract_score(feedback)
                        # Cap score if answer too short (less than 3 words)
                        if len(final_answer.split()) < 3:
                            score = min(score, 2.0)
                            feedback += "\nSuggestion: Try to give a fuller, more detailed answer instead of a one-word response."

                    verdict = extract_verdict(feedback, score)
                    suggestion = extract_suggestion(feedback)

                    response_entry = {
                        "username": interview["username"],
                        "question": questions[index],
                        "answer": final_answer,
                        "feedback": feedback,
                        "verdict": verdict,
                        "suggestion": suggestion,
                        "score": score,
                        "interview_type": interview["interview_type"],
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.responses.append(response_entry)
                    save_response(response_entry)

                    # Show this answer's analysis immediately instead of jumping straight
                    # to the next question.
                    st.session_state.last_feedback = response_entry
                    st.session_state.awaiting_next = True
                    st.rerun()

            # ---- STEP 2: show right/wrong + suggestion for the answer just given ----
            else:
                fb = st.session_state.last_feedback
                icon, color = verdict_badge(fb["verdict"])

                st.markdown(f"""
<div style='background:{color}22;border:1px solid {color};padding:16px;border-radius:10px;margin:10px 0;'>
<h4 style='margin:0;color:{color};'>{icon} {fb['verdict']} — Score: {fb['score']}/10</h4>
</div>""", unsafe_allow_html=True)

                if fb["answer"]:
                    st.markdown(f"**Your Answer:** {fb['answer']}")
                else:
                    st.warning("No answer was provided for this question.")

                # Pull just the "Feedback:" line out of the raw model text for a clean display
                clean_feedback = extract_field(fb["feedback"], "Feedback") or fb["feedback"]
                st.markdown(f"**📋 Feedback:** {clean_feedback}")
                st.markdown(f"**💡 Suggestion:** {fb['suggestion']}")

                is_last = (index + 1) >= len(questions)
                btn_label = "🏁 See Final Results" if is_last else "➡️ Next Question"
                if st.button(btn_label, use_container_width=True, type="primary"):
                    st.session_state.question_index += 1
                    st.session_state.awaiting_next = False
                    st.session_state.last_feedback = None
                    next_idx = st.session_state.question_index

                    if camera and hasattr(camera, "video_processor") and camera.video_processor:
                        vp = camera.video_processor
                        if next_idx < len(questions):
                            vp.current_question = questions[next_idx]
                            vp.question_number = next_idx + 1
                        else:
                            vp.current_question = ""
                            vp.proctoring_enabled = False
                    st.rerun()

        # ---- RESULTS ----
        else:
            if camera and hasattr(camera, "video_processor") and camera.video_processor:
                camera.video_processor.proctoring_enabled = False
                camera.video_processor.current_question = ""

            responses = st.session_state.responses
            scores = [r["score"] for r in responses if r.get("score") is not None]

            st.success("🎉 Interview Completed!")

            if scores:
                overall = sum(scores) / len(scores)
                st.markdown(f"""
<div style='background:linear-gradient(135deg,#1e3c72,#2a5298);padding:20px;
border-radius:12px;text-align:center;margin:10px 0;'>
<h2 style='color:white;margin:0;'>🏆 Overall Score</h2>
<h1 style='color:#FFD700;margin:5px 0;font-size:3em;'>{overall:.1f}
<span style='font-size:0.5em;color:white;'>/10</span></h1>
<p style='color:#ccc;margin:0;'>{interview['role']} | {interview['interview_type']}</p>
</div>""", unsafe_allow_html=True)

                st.markdown("#### 📊 Score Breakdown")
                for i, r in enumerate(responses):
                    sc = r.get("score", 0)
                    answered = "✅" if r["answer"].strip() else "⏭️ Skipped"
                    st.markdown(f"Q{i+1} {answered}: **{sc}/10**")
                    st.progress(sc / 10)

            st.markdown("---")
            st.markdown("#### 📝 Detailed Feedback")
            for i, r in enumerate(responses):
                answered_label = "✅ Answered" if r["answer"].strip() else "⏭️ Skipped"
                with st.expander(f"Q{i+1} [{answered_label}]: {r['question']}", expanded=False):
                    if r["answer"].strip():
                        st.markdown(f"**Your Answer:** {r['answer']}")
                    else:
                        st.warning("No answer was provided for this question.")
                    verdict = r.get("verdict") or extract_verdict(r.get("feedback", ""), r.get("score", 0))
                    icon, _ = verdict_badge(verdict)
                    st.markdown(f"**Verdict:** {icon} {verdict}")
                    clean_feedback = extract_field(r.get("feedback", ""), "Feedback") or r.get("feedback", "")
                    st.markdown(f"**Feedback:** {clean_feedback}")
                    suggestion = r.get("suggestion") or extract_suggestion(r.get("feedback", ""))
                    st.markdown(f"**💡 Suggestion:** {suggestion}")
                    st.markdown(f"**Score:** {r.get('score', 0)}/10")

            st.markdown("---")
            if st.button("🔁 Start New Interview", use_container_width=True, type="primary"):
                interview_record = dict(interview)
                interview_record["responses"] = responses
                st.session_state.interviews.append(interview_record)
                st.session_state.current_interview = None
                st.session_state.question_index = 0
                st.session_state.responses = []
                st.rerun()
