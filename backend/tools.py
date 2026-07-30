# backend/tools.py - RENDER READY (No Ollama)
import os
# FIX: dot wala import
from .config import TWILIO_ACCOUNT_SID, TWILIO_FROM_NUMBER, TWILIO_AUTH_TOKEN, EMERGENCY_CONTACT, GROQ_API_KEY

# MedGemma ka kaam ab Groq se hoga, Render par Ollama nahi chalta
def query_medgemma(prompt: str) -> str:
    """
    Calls Groq with Dr. Emily Hartman personality.
    """
    system_prompt = """You are Dr. Emily Hartman, a warm and experienced clinical psychologist. 
    Respond with: 1. Emotional attunement 2. Gentle normalization 3. Practical guidance 4. Strengths-focused support
    Never use brackets or labels. Always ask open ended questions to dive into root cause.
    """
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7, api_key=GROQ_API_KEY)
        response = llm.invoke(f"{system_prompt}\n\nPatient says: {prompt}")
        return response.content.strip()
    except Exception as e:
        print(f"MedGemma Error: {e}")
        return f"I can sense this is difficult for you. Could you share more about what you're feeling right now?"

# Twilio calling tool
def call_emergency():
    try:
        from twilio.rest import Client
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, EMERGENCY_CONTACT]):
            print("Twilio keys missing, skipping call")
            return
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            to=EMERGENCY_CONTACT,
            from_=TWILIO_FROM_NUMBER,
            url="https://demo.twilio.com/docs/voice.xml"
        )
        print(f"Emergency call placed: {call.sid}")
    except Exception as e:
        print(f"Twilio error: {e}")
