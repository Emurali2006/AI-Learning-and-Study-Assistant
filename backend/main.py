import os
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import MCP and your existing agent
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from agent_client import run_agent

app = FastAPI(
    title="AI Learning & Study Assistant",
    description="AI-powered learning assistant using LangGraph, MCP and Qwen2.5",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def root():
    return {"message": "AI Learning & Study Assistant API is running!", "status": "success"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# NEW ENDPOINT: Fetch study history (past conversations)
@app.get("/api/history")
def get_history():
    try:
        db_path = os.path.join(os.getcwd(), "study_memory.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Safely fetch recent conversations using SQLite's built-in rowid
        cursor.execute("SELECT * FROM conversations ORDER BY rowid DESC LIMIT 10")
        conversations = [dict(row) for row in cursor.fetchall()]
        
        return {"status": "success", "data": conversations}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if 'conn' in locals():
            conn.close()

# NEW ENDPOINT: Fetch study activity (plans, quiz generations, etc.)
@app.get("/api/activity")
def get_activity():
    try:
        db_path = os.path.join(os.getcwd(), "study_memory.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM study_activity ORDER BY rowid DESC LIMIT 10")
        activities = [dict(row) for row in cursor.fetchall()]
        
        return {"status": "success", "data": activities}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if 'conn' in locals():
            conn.close()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    mcp_server_path = os.path.join(os.getcwd(), "mcp_server.py")
    server_params = StdioServerParameters(command="python", args=[mcp_server_path], env=None)

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as mcp_session:
                await mcp_session.initialize()
                ai_response = await run_agent(
                    query=request.message,
                    session_id="web_session_01",
                    mcp_session=mcp_session
                )
        return {"response": ai_response}
    except Exception as e:
        return {"response": f"Error communicating with AI agent: {str(e)}"}