# frontend.py - FINAL
import streamlit as st
import requests
import os

st.set_page_config(page_title="AI Mental Health Therapist", layout="wide")
st.title("🧠 SafeSpace - AI Mental Health Therapist")

# Render par Environment Variable se lega, local par localhost
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/ask")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("What's on your mind today?")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    try:
        res = requests.post(BACKEND_URL, json={"message": user_input}, timeout=60)
        res.raise_for_status()
        data = res.json()
        bot_answer = data.get("answer", "Sorry, I couldn't get a response.")
        st.session_state.chat_history.append({"role": "assistant", "content": bot_answer})
    except requests.exceptions.ConnectionError:
        st.session_state.chat_history.append({"role": "assistant", "content": f"⚠ Backend not running at {BACKEND_URL}. Check Render logs."})
    except Exception as e:
        st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {e}"})

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
