import os
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
    return {
        "message": "AI Learning & Study Assistant API is running!",
        "status": "success"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Ensure we use the absolute path to mcp_server.py from the project root
    mcp_server_path = os.path.join(os.getcwd(), "mcp_server.py")
    
    server_params = StdioServerParameters(
        command="python",
        args=[mcp_server_path],
        env=None
    )

    try:
        # Start MCP session
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as mcp_session:
                await mcp_session.initialize()
                
                # Call your existing LangGraph agent
                # Using a hardcoded session_id for web interactions for now
                ai_response = await run_agent(
                    query=request.message,
                    session_id="web_session_01",
                    mcp_session=mcp_session
                )
                
        return {"response": ai_response}
    except Exception as e:
        # Catch and return any errors so the frontend doesn't just crash
        return {"response": f"Error communicating with AI agent: {str(e)}"}