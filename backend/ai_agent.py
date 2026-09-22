from langchain_core.tools import tool

# Render deployment ke liye relative imports
from .tools import query_medgemma, call_emergency
from .config import GROQ_API_KEY

from langchain.agents import create_agent
from langchain_groq import ChatGroq


# =========================================================
# 1. MENTAL HEALTH SPECIALIST TOOL
# =========================================================

@tool
def ask_mental_health_specialist(query: str) -> str:
    """
    Generate a supportive mental-health response using MedGemma.
    Use this tool for normal emotional or mental-health conversations.
    Do not use this tool for emergency calling.
    """

    print(f"\n[DEBUG] -> MedGemma calling with: {query[:150]}")

    try:
        result = query_medgemma(query)

        if result is None:
            return (
                "I'm here to listen and support you. "
                "Please tell me a little more about what you're going through."
            )

        result = str(result)

        print(f"[DEBUG] <- MedGemma returned {len(result)} chars")

        return result

    except Exception as e:
        print(f"[ERROR] MedGemma Error: {e}")

        return (
            "I'm here with you. It sounds like you're going through "
            "a difficult moment. Please tell me what is happening."
        )


# =========================================================
# 2. EMERGENCY CALL TOOL
# =========================================================

@tool
def emergency_call_tool() -> str:
    """
    Place an emergency/safety call.

    This tool should be used when the user:
    - explicitly asks to call emergency contact/help
    - expresses suicidal thoughts
    - expresses intention to self-harm
    """

    print("\n[DEBUG] -> EMERGENCY CALL TOOL EXECUTING")

    try:
        result = call_emergency()

        print(f"[DEBUG] <- Emergency function returned: {result}")

        return (
            "The emergency contact call has been initiated. "
            "Please stay connected and, if possible, stay with a trusted "
            "person or emergency professional."
        )

    except Exception as e:

        print(f"[ERROR] Emergency call failed: {e}")

        return (
            "I could not complete the emergency call automatically. "
            "Please contact your local emergency service immediately "
            "or ask someone nearby to call for you."
        )


# =========================================================
# 3. THERAPIST SEARCH TOOL
# =========================================================

@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Find therapists near the provided location.

    IMPORTANT:
    Actual therapist/location API should be implemented here or
    connected from tools.py. Do not return fake therapist data.
    """

    print(f"\n[DEBUG] -> Therapist search requested for: {location}")

    # We intentionally DO NOT return fake 555 numbers.
    #
    # Connect your real LocationIQ / Google Places / therapist
    # search implementation here.

    return (
        f"Therapist search was requested for {location}, "
        "but the real therapist-location service is not configured yet. "
        "Please connect the location/places API to return actual nearby therapists."
    )


# =========================================================
# 4. TOOLS
# =========================================================

tools = [
    ask_mental_health_specialist,
    emergency_call_tool,
    find_nearby_therapists_by_location,
]


# =========================================================
# 5. GROQ / GPT-OSS 120B
# =========================================================

if not GROQ_API_KEY:
    print("[WARNING] GROQ_API_KEY not found in environment variables!")


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    api_key=GROQ_API_KEY,
)


# =========================================================
# 6. SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are SafeSpace AI, a warm, supportive mental-health assistant.

AVAILABLE TOOLS:

1. ask_mental_health_specialist
   - Use for normal emotional and mental-health conversations.
   - Call at most ONCE per user turn.

2. emergency_call_tool
   - Use for explicit requests to call emergency help/contact.
   - Use when the user expresses suicidal thoughts or intent to self-harm.

3. find_nearby_therapists_by_location
   - Use when the user asks for a nearby therapist.
   - If the user's location is missing, ask for their city/location.

IMPORTANT RULES:

- Never invent therapist names, addresses, phone numbers, or locations.
- Never claim that an emergency call was completed unless the emergency
  tool actually returned successfully.
- After a tool returns a result, use that result in the final response.
- Do not repeatedly call the same tool.
- Keep responses supportive, concise, and clear.
"""


# =========================================================
# 7. CREATE LANGCHAIN AGENT
# =========================================================

graph = create_agent(
    llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)


# =========================================================
# 8. EMERGENCY DETECTION
# =========================================================

def is_emergency_request(text: str) -> bool:

    text = text.lower().strip()

    emergency_phrases = [

        # Explicit suicidal statements
        "i want to kill myself",
        "i wanna kill myself",
        "i want to die",
        "i want to end my life",
        "i'm going to kill myself",
        "im going to kill myself",
        "i am going to kill myself",

        # Self-harm
        "i want to hurt myself",
        "i want to harm myself",
        "i am going to hurt myself",
        "i am going to harm myself",

        # Emergency help requests
        "call emergency",
        "call emergency contact",
        "call my emergency contact",
        "contact emergency",
        "contact my emergency contact",
        "call for help",
        "send emergency help",
        "get emergency help",
    ]

    return any(
        phrase in text
        for phrase in emergency_phrases
    )


# =========================================================
# 9. THERAPIST REQUEST DETECTION
# =========================================================

def is_therapist_request(text: str) -> bool:

    text = text.lower()

    therapist_words = [
        "therapist",
        "psychologist",
        "counsellor",
        "counselor",
        "mental health doctor",
        "psychiatrist",
    ]

    location_words = [
        "near me",
        "nearby",
        "nearest",
        "near",
        "location",
    ]

    has_therapist_word = any(
        word in text
        for word in therapist_words
    )

    has_location_word = any(
        word in text
        for word in location_words
    )

    return has_therapist_word and (
        has_location_word or "find" in text or "give" in text
    )


# =========================================================
# 10. EXTRACT LOCATION
# =========================================================

def extract_location(text: str) -> str | None:

    text_lower = text.lower()

    patterns = [
        "near ",
        "in ",
        "at ",
    ]

    for pattern in patterns:

        if pattern in text_lower:

            index = text_lower.find(pattern)

            location = text[index + len(pattern):].strip()

            if location:
                return location

    return None


# =========================================================
# 11. MAIN RESPONSE FUNCTION
# =========================================================

def get_response(user_input: str) -> str:

    user_input = user_input.strip()

    if not user_input:
        return "Please tell me what you're feeling or what you need help with."


    # -----------------------------------------------------
    # EMERGENCY ROUTE
    # -----------------------------------------------------

    if is_emergency_request(user_input):

        print("\n========================================")
        print("[DEBUG] EMERGENCY REQUEST DETECTED")
        print("========================================")

        try:

            result = emergency_call_tool.invoke({})

            print(
                f"[DEBUG] Emergency tool result: {result}"
            )

            return (
                "I'm glad you reached out. "
                "I've initiated the emergency safety call. "
                "Please stay connected and, if possible, move to a safe "
                "place and stay with someone you trust."
            )

        except Exception as e:

            print(
                f"[ERROR] Emergency tool execution failed: {e}"
            )

            return (
                "I couldn't complete the emergency call automatically. "
                "Please call your local emergency service immediately "
                "or ask someone nearby to call for you."
            )


    # -----------------------------------------------------
    # THERAPIST ROUTE
    # -----------------------------------------------------

    if is_therapist_request(user_input):

        location = extract_location(user_input)

        if not location:

            return (
                "Sure. I can help you find a nearby therapist. "
                "Please tell me your city or area, for example: "
                "\"therapists near Pune\"."
            )

        try:

            result = find_nearby_therapists_by_location.invoke(
                {
                    "location": location
                }
            )

            print(
                f"[DEBUG] Therapist tool result: {result}"
            )

            return result

        except Exception as e:

            print(
                f"[ERROR] Therapist search failed: {e}"
            )

            return (
                "I couldn't search for therapists right now. "
                "Please try again with your city or area."
            )


    # -----------------------------------------------------
    # NORMAL AI AGENT ROUTE
    # -----------------------------------------------------

    print(
        f"\n[DEBUG] -> Sending normal query to GPT-OSS 120B: "
        f"{user_input[:150]}"
    )

    try:

        inputs = {
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }

        result = graph.invoke(inputs)

        messages = result.get("messages", [])

        if not messages:
            return (
                "I'm here to listen. "
                "Could you tell me a little more?"
            )

        # Find the final AI response
        for message in reversed(messages):

            if getattr(message, "type", None) == "ai":

                content = getattr(
                    message,
                    "content",
                    None
                )

                if content:

                    print(
                        f"[DEBUG] <- Final AI response received"
                    )

                    return content


        return (
            "I'm here to listen and support you. "
            "Could you tell me a little more about what you're experiencing?"
        )

    except Exception as e:

        print(
            f"[ERROR] Agent execution failed: {e}"
        )

        import traceback

        traceback.print_exc()

        return (
            "I'm having trouble processing that right now. "
            "Please try again."
        )


# =========================================================
# 12. LOCAL TEST
# =========================================================

if __name__ == "__main__":

    print("==============================================")
    print("       SafeSpace AI - GPT-OSS 120B")
    print("==============================================")

    print("Available tools:")
    print(" - ask_mental_health_specialist")
    print(" - emergency_call_tool")
    print(" - find_nearby_therapists_by_location")
    print("----------------------------------------------")

    while True:

        user_input = input("\nUser: ")

        if user_input.lower().strip() in [
            "exit",
            "quit",
            "q",
        ]:
            print("SafeSpace AI stopped.")
            break

        try:

            answer = get_response(user_input)

            print("\nSafeSpace AI:")
            print(answer)

        except Exception as e:

            print(
                f"\n[ERROR] {e}"
            )

            import traceback

            traceback.print_exc()
