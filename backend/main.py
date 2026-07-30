# backend/main.py - RENDER READY FINAL
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
# FIX: Relative import - Render ke liye mandatory
from.ai_agent import graph

app = FastAPI(title="SafeSpace AI Backend")

# Frontend se connect karne ke liye CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "SafeSpace AI Backend Running with Groq", "port": os.environ.get("PORT", "8000")}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
async def ask(query: Query):
    try:
        print(f"Received from frontend: {query.message}")
        inputs = {"messages": [{"role": "user", "content": query.message}]}

        # ainvoke - async version
        result = await graph.ainvoke(
            inputs,
            config={"recursion_limit": 10}
        )

        messages = result.get("messages", [])
        final_answer = "Sorry, I could not generate a response."
        tool_called = "None"

        # Tool name nikalo
        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_called = msg.tool_calls[0].get('name', 'None')

        # Final answer nikalo - last AI message jisme tool_calls na ho
        for msg in reversed(messages):
            if getattr(msg, 'type', None) == "ai" and getattr(msg, 'content', None):
                if not getattr(msg, 'tool_calls', None):
                    final_answer = msg.content
                    break

        print(f"TOOL CALLED: {tool_called}")
        print(f"ANSWER: {final_answer[:200]}")

        return {
            "tool_called": tool_called,
            "answer": final_answer
        }

    except Exception as e:
        print(f"ERROR in /ask: {e}")
        import traceback
        traceback.print_exc()
        return {
            "tool_called": "error",
            "answer": f"Backend error: {str(e)}"
        }

# Render ke liye ye block chahiye hi nahi, par local test ke liye rakha hai
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # yahan "main:app" likho, "backend.main:app" nahi, kyuki file already backend ke andar hai
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
