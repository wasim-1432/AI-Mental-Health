# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from ai_agent import graph # SYSTEM_PROMPT ki zarurat nahi, graph me already hai

app = FastAPI(title="SafeSpace AI Backend")

# Frontend (React/Vite) se connect karne ke liye CORS allow karna mandatory hai
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Production me yahan apne frontend ka URL daalna
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "SafeSpace AI Backend Running with Groq"}

@app.post("/ask")
async def ask(query: Query):
    """
    Frontend se message lega, Groq Agent ko bhejega, aur final answer wapas dega
    """
    try:
        print(f"Received from frontend: {query.message}")

        inputs = {"messages": [{"role": "user", "content": query.message}]}

        # Graph ko invoke karo - ye blocking hai isliye ainvoke use kar rahe hain
        # recursion_limit se infinite loop kabhi nahi hoga
        result = await graph.ainvoke(
            inputs,
            config={"recursion_limit": 10}
        )

        messages = result.get("messages", [])
        final_answer = "Sorry, I could not generate a response."
        tool_called = "None"

        # Last se check karo kaunsa tool call hua aur final answer kya hai
        for msg in reversed(messages):
            # Final AI answer
            if msg.type == "ai" and msg.content and final_answer == "Sorry, I could not generate a response.":
                if not getattr(msg, 'tool_calls', None): # tool call wala message khali hota hai
                    final_answer = msg.content

            # Tool ka naam
            if hasattr(msg, 'type') and msg.type == "tool":
                if tool_called == "None":
                    tool_called = getattr(msg, 'name', 'None')

        # Purane messages se bhi tool name nikal lo agar upar na mila ho
        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_called = msg.tool_calls[0]['name']

        print(f"TOOL CALLED: {tool_called}")
        print(f"ANSWER: {final_answer[:100]}...")

        # Frontend ko clean JSON bhejo
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

# last line aise rakho
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port)



# #step 1: Steup FastAPI
# from fastapi import FastAPI
# from pydantic import BaseModel
# import uvicorn
# from ai_agent import graph, SYSTEM_PROMPT

# app=FastAPI()

# #Step 2: Receive and validate request from Frontend
# class Query(BaseModel):
#     message:str



# @app.post("/ask")
# async def ask(query:Query):
#     #AI Agent
#     # response=ai_agent(query)

#     response="This is from backend."
#     #Step 3: Send response to the frontend
#     return response


# if __name__=="__main__":
#     uvicorn.run("main:app", host="0.0.0.0",port=8000, reload=True)
