import streamlit as st
import time
import os
import json
import requests
import speech_recognition as sr
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from deepface import DeepFace
import cv2
from PIL import Image
import threading

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def ask_ollama(prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    return response.json().get("response", "").strip()

# MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["mock_interviews"]
feedback_collection = db["feedbacks"]

def get_interview_questions(job_role, tech_stack, experience):
    prompt = f"""Generate exactly 5 interview questions for a {job_role} role with {tech_stack} skills.
The candidate has {experience} years of experience.
Return only 5 numbered questions, one per line. No extra text."""
    response = ask_ollama(prompt)
    questions = [q.strip() for q in response.split("\n") if q.strip() and q.strip()[0].isdigit()]
    if len(questions) < 5:
        questions = [q.strip() for q in response.split("\n") if q.strip()]
    return questions[:5]

def process_answer(question, answer, avg_emotion):
    prompt = f"""Evaluate this interview answer. Give a score out of 10 and detailed feedback.
Also consider the candidate's detected emotion: {avg_emotion}

Question: {question}
Answer: {answer}

Score and Feedback:"""
    return ask_ollama(prompt)

def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Recording... Speak now!")
        audio = recognizer.listen(source, timeout=5)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Could not request results"

# Emotion tracking
emotion_list = []
emotion_lock = threading.Lock()
stop_emotion_flag = threading.Event()

def track_emotions_background():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return
    while not stop_emotion_flag.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            dominant_emotion = result[0]['dominant_emotion']
            with emotion_lock:
                emotion_list.append(dominant_emotion)
        except Exception:
            pass
        time.sleep(1)
    cap.release()

def get_avg_emotion():
    with emotion_lock:
        if emotion_list:
            return max(set(emotion_list), key=emotion_list.count)
        return "neutral"

# Session state
if "interviews" not in st.session_state:
    st.session_state.interviews = []
if "emotion_thread_started" not in st.session_state:
    st.session_state.emotion_thread_started = False

# ---------------------------
# Main App
# ---------------------------
st.title("AI Mock Interview (with Emotion Tracking)")
st.subheader("Create and start your AI Mock Interview")

if st.button("+ Add New"):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.form("interview_form"):
        username = st.text_input("Username")
        job_role = st.text_input("Job Role", placeholder="Ex. Full Stack Developer")
        tech_stack = st.text_input("Tech Stack", placeholder="Ex. React, Node.js")
        experience = st.number_input("Years of Experience", min_value=0, step=1)
        start_btn = st.form_submit_button("Start Interview")
        cancel_btn = st.form_submit_button("Cancel")

        if cancel_btn:
            st.session_state.show_form = False
            st.rerun()

        if start_btn and username and job_role and tech_stack:
            with st.spinner("Generating questions with LLaMA 3..."):
                questions = get_interview_questions(job_role, tech_stack, experience)
            interview_data = {
                "username": username,
                "role": job_role,
                "stack": tech_stack,
                "experience": experience,
                "questions": questions,
                "responses": []
            }
            st.session_state.current_interview = interview_data
            st.session_state.interviews.append(interview_data)
            st.session_state.show_form = False
            st.session_state.question_index = 0
            # Start emotion tracking thread
            if not st.session_state.emotion_thread_started:
                stop_emotion_flag.clear()
                t = threading.Thread(target=track_emotions_background, daemon=True)
                t.start()
                st.session_state.emotion_thread_started = True
            st.rerun()

if "current_interview" in st.session_state:
    interview = st.session_state.current_interview
    st.subheader(f"Job Role: {interview['role']}")
    st.text(f"Tech Stack: {interview['stack']}")
    st.text(f"Years of Experience: {interview['experience']}")

    # Show current detected emotion
    current_emotion = get_avg_emotion()
    st.info(f"Current Detected Emotion: **{current_emotion}**")

    index = st.session_state.question_index
    if index < len(interview["questions"]):
        st.subheader(f"Question #{index + 1}")
        st.write(interview["questions"][index])

        if "answer_text" not in st.session_state:
            st.session_state.answer_text = ""

        answer = st.text_area("Your Answer", key=f"answer_{index}", value=st.session_state.answer_text)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Record Answer"):
                st.session_state.answer_text = record_audio()
                st.rerun()
        with col2:
            if st.button("Next Question"):
                answer = st.session_state.answer_text
                st.session_state.answer_text = ""
                avg_emotion = get_avg_emotion()
                with st.spinner("Evaluating answer..."):
                    feedback = process_answer(interview["questions"][index], answer, avg_emotion)
                response_data = {
                    "username": interview["username"],
                    "question": interview["questions"][index],
                    "answer": answer,
                    "feedback": feedback,
                    "emotion": avg_emotion
                }
                feedback_collection.insert_one(response_data)
                interview["responses"].append(response_data)
                st.session_state.question_index += 1
                st.rerun()
    else:
        stop_emotion_flag.set()
        st.session_state.emotion_thread_started = False
        st.success("Interview Completed!")
        st.markdown("## Interview Summary")
        for idx, response in enumerate(interview["responses"]):
            with st.expander(f"Question {idx + 1}: {response['question']}"):
                st.markdown(f"**Your Answer:** {response['answer']}")
                st.markdown(f"**Feedback:** {response['feedback']}")
                st.markdown(f"**Emotion:** {response['emotion']}")
        if st.button("Close Interview"):
            del st.session_state["current_interview"]
            del st.session_state["question_index"]
            st.rerun()

if "current_interview" not in st.session_state and st.session_state.interviews:
    st.subheader("Previous Mock Interviews")
    for i, interview in enumerate(st.session_state.interviews):
        with st.expander(f"{interview['role']} - {interview['experience']} Years"):
            st.write(f"Tech Stack: {interview['stack']}")
            for response in interview["responses"]:
                st.write(f"**Q:** {response['question']}")
                st.write(f"**Answer:** {response['answer']}")
                st.write(f"**Feedback:** {response['feedback']}")
                st.write(f"**Emotion:** {response['emotion']}")
