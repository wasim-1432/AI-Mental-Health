from langchain_core.tools import tool
# FIX:.tools aur.config - dot lagana zaruri hai Render ke liye
from.tools import query_medgemma, call_emergency
from.config import GROQ_API_KEY
from langchain.agents import create_agent
from langchain_groq import ChatGroq

@tool
def ask_mental_health_specialist(query: str) -> str:
    """Generate a therapeutic response using MedGemma. Use for emotional queries. Call MAX 1 time per turn."""
    print(f"\n[DEBUG] -> MedGemma calling with: {query[:100]}")
    try:
        result = query_medgemma(query)
        print(f"[DEBUG] <- MedGemma returned {len(result)} chars")
        return result
    except Exception as e:
        print(f"[DEBUG] MedGemma Error: {e}")
        return f"I understand you're going through a tough time. I'm here to listen. Could you tell me more? (System note: {e})"

@tool
def emergency_call_tool() -> str:
    """Place emergency call ONLY if user expresses suicidal ideation or self-harm."""
    try:
        call_emergency()
        return "Emergency call placed to safety helpline. Please stay on the line, help is coming."
    except Exception as e:
        return f"Failed to place call but alert triggered: {e}"

@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """Find therapists near a location."""
    return (
        f"Here are some therapists near {location}:\n"
        "- Dr. Ayesha Kapoor - +1 (555) 123-4567\n"
        "- Dr. James Patel - +1 (555) 987-6543\n"
        "- MindCare Counseling Center - +1 (555) 222-3333"
    )

# --- GROQ SETUP ---
tools = [ask_mental_health_specialist, emergency_call_tool, find_nearby_therapists_by_location]

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in env!")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=GROQ_API_KEY
)

SYSTEM_PROMPT = """You are SafeSpace AI - warm and supportive.
TOOLS:
1. ask_mental_health_specialist: Use for emotional queries. Call it ONCE.
2. find_nearby_therapists_by_location: Use for therapist search.
3. emergency_call_tool: Use ONLY for suicide/self-harm.

CRITICAL RULE: After you call a tool and get its result, you MUST NOT call any tool again. You MUST use that result to generate your final answer to the user. Do not loop.
"""

graph = create_agent(llm, tools=tools, system_prompt=SYSTEM_PROMPT)

if __name__ == "__main__":
    print("SafeSpace AI (Groq - Fixed) Started...")
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        inputs = {"messages": [{"role": "user", "content": user_input}]}
        try:
            final_answer = None
            tool_called = "None"
            for event in graph.stream(inputs, stream_mode="values", config={"recursion_limit": 10}):
                messages = event.get("messages", [])
                if not messages: continue
                last_msg = messages[-1]
                if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                    tool_called = last_msg.tool_calls[0]['name']
                    print(f"TOOL CALLED: {tool_called}")
                if last_msg.type == "ai" and last_msg.content:
                    if not getattr(last_msg, 'tool_calls', None):
                        final_answer = last_msg.content
            print(f"ANSWER: {final_answer}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
