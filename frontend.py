# step1: Setup streamlit
import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="AI Mental Health Therapist", layout="wide")
st.title("🧠 SafeSpace - AI Mental Health Therapist")

# Initialise chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# step2: User is able to ask question
user_input = st.chat_input("What's on your mind today?")

if user_input:
    # 1. Append user input to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    try:
        # 2. Call backend
        res = requests.post(BACKEND_URL, json={"message": user_input}, timeout=30)
        res.raise_for_status()
        data = res.json()  # {'tool_called': 'None', 'answer': '...'}

        # FIX: Sirf answer nikalo, poora JSON nahi
        bot_answer = data.get("answer", "Sorry, I couldn't get a response.")
        tool_used = data.get("tool_called", "None")

        # Optional: tool name ko console me dekh sakte ho
        print(f"Tool called: {tool_used}")

        # 3. Append ONLY answer to history
        st.session_state.chat_history.append({"role": "assistant", "content": bot_answer})

    except requests.exceptions.ConnectionError:
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": "⚠️ Backend is not running. Please run `uv run backend/main.py` first."
        })
    except Exception as e:
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"Error: {e}"
        })

# step3: Show response from backend
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])