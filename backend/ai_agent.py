from langchain_core.tools import tool
from tools import query_medgemma, call_emergency

@tool
def ask_mental_health_specialist(query: str) -> str:
    """Generate a therapeutic response using MedGemma. Use for emotional queries. Call MAX 1 time per turn."""
    print(f"\n[DEBUG] -> MedGemma calling with: {query[:100]}")
    result = query_medgemma(query)
    print(f"[DEBUG] <- MedGemma returned {len(result)} chars")
    return result

@tool
def emergency_call_tool() -> str:
    """Place emergency call ONLY if user expresses suicidal ideation or self-harm."""
    call_emergency()
    return "Emergency call placed to safety helpline."

@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """Find therapists near a location."""
    return (
        f"Here are some therapists near {location}:\n"
        "- Dr. Ayesha Kapoor - +1 (555) 123-4567\n"
        "- Dr. James Patel - +1 (555) 987-6543\n"
        "- MindCare Counseling Center - +1 (555) 222-3333"
    )

# --- FIXED GROQ SETUP ---
from langchain.agents import create_agent # <-- NAYA IMPORT, purana wala hata diya
from langchain_groq import ChatGroq
from config import GROQ_API_KEY

tools = [ask_mental_health_specialist, emergency_call_tool, find_nearby_therapists_by_location]

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

# Naye API me system_prompt argument hai, prompt nahi
graph = create_agent(llm, tools=tools, system_prompt=SYSTEM_PROMPT)

if __name__ == "__main__":
    print("SafeSpace AI (Groq - Fixed) Started...")

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        print(f"Received: {user_input}")
        inputs = {"messages": [{"role": "user", "content": user_input}]}

        # recursion_limit se infinite loop force stop hoga
        try:
            final_answer = None
            tool_called = "None"

            # stream_mode="values" zyada stable hai
            for event in graph.stream(inputs, stream_mode="values", config={"recursion_limit": 10}):
                messages = event.get("messages", [])
                if not messages:
                    continue
                last_msg = messages[-1]

                # Tool call detect
                if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                    tool_called = last_msg.tool_calls[0]['name']
                    print(f"TOOL CALLED: {tool_called}")

                # Final AI answer detect
                if last_msg.type == "ai" and last_msg.content:
                    # Agar is message me tool_calls nahi hai, to ye final answer hai
                    if not getattr(last_msg, 'tool_calls', None):
                        final_answer = last_msg.content

            print(f"ANSWER: {final_answer}")

        except Exception as e:
            print(f"ERROR in graph: {e}")
            import traceback
            traceback.print_exc()