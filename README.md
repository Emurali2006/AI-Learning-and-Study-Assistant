# AI Learning & Study Assistant

An intelligent, local Agentic AI assistant built with **LangGraph**, **LangChain**, **MCP (Model Context Protocol)**, **Ollama (Qwen2.5:3B)**, and **SQLite Memory**.

---

## 1. Problem Statement
Students face challenges in organizing study materials, preparing for exams effectively, creating customized quizzes, and tracking their progress over time. Traditional chatbots often provide generic responses without contextual grounding or session memory, leading to disjointed learning experiences.

## 2. Objectives
- Provide accurate, grounded explanations for Computer Science subjects (Operating Systems, DBMS, C++, Java, Computer Networks, Data Structures).
- Dynamically route student queries using an Agentic workflow to appropriate tools.
- Generate automated multiple-choice quizzes with explanations and real-time scoring.
- Create realistic, time-bounded study plans for exam preparation.
- Persist study activity, quiz performance, and conversations using SQLite memory.
- Operate completely locally without external cloud dependencies or paid APIs.

## 3. Proposed Solution
The **AI Learning & Study Assistant** implements an Agentic AI architecture powered by **LangGraph** and **MCP**. Instead of behaving as a simple chat loop, the agent inspects each user query, routes it to specialized tools exposed over an **MCP Server**, executes the tool, and synthesizes grounded answers using local **Qwen2.5:3B** via Ollama.

---

## 4. Agentic AI Architecture

```
                    STUDENT
                       │
                       ▼
                ┌─────────────┐
                │ LANGGRAPH   │
                │    AGENT    │
                └──────┬──────┘
                       │
                       ▼
                  QUERY ROUTER
                       │
                       ▼
                  TOOL SELECTOR
                       │
                       ▼
                   MCP SERVER
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
 Study Material    Quiz Tool      Study Plan Tool
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                  TOOL RESULT
                       │
                       ▼
                  QWEN2.5:3B
                       │
                       ▼
                 FINAL RESPONSE
                       │
                       ▼
                  SQLITE MEMORY
```

### LangGraph Workflow:
1. **START** -> Entry point receives `AgentState`.
2. **decide_tool** -> Classifies the query (category, subject, topic) and selects the appropriate MCP tool.
3. **call_tool** -> Invokes the selected tool via the MCP Stdio Client session.
4. **synthesize** -> Synthesizes the tool output using Qwen2.5:3B and formats the output.
5. **END** -> Returns final answer and updates SQLite memory.

---

## 5. Technologies Used
- **Python 3.11+**
- **LangGraph** (StateGraph workflow engine)
- **LangChain / LangChain Ollama** (LLM wrapper and core message abstractions)
- **Ollama** (Local LLM runtime)
- **Qwen2.5:3B** (3-billion parameter local language model)
- **MCP (Model Context Protocol)** (Standardized tool server and client architecture)
- **SQLite** (Persistent storage for conversations, study history, and quiz scores)
- **Rich** (Rich CLI user interface and formatting)
- **python-dotenv** (Environment configuration)

---

## 6. Key Features
1. **Query Routing**: Automatic classification of student queries into 8 categories (study question, topic details, quiz, study plan, summary, progress, history, general).
2. **Knowledge Base Search**: Local search over structured CS subjects and topics.
3. **Automated Quiz Generator**: Generates 5-10 question MCQs with options, correct answers, explanations, and CLI scoring.
4. **Custom Study Planner**: Breaks down available study time (e.g. 3 hours) into topic-wise time blocks with revision intervals.
5. **SQLite Session Memory**: Tracks questions, study activity, quiz scores, average percentage, and weak topics.
6. **Robust Fallbacks**: Keyword routing and template fallbacks if LLM output fails or model is slow.

---

## 7. Project Structure

```
ai_learning_assistant/
│
├── agent_client.py       # LangGraph agent & MCP client interface (main CLI entry point)
├── mcp_server.py         # MCP Server exposing study tools via Stdio transport
├── database.py           # SQLite memory management (study_memory.db)
├── knowledge_base.py     # Local JSON search module for study material
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation & setup instructions
├── PROJECT_REPORT.md     # Academic project report
├── .env.example          # Sample environment settings
│
└── data/
    └── study_material.json # Computer Science study material knowledge base
```

---

## 8. Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Ollama installed and running on `http://localhost:11434`

### Windows PowerShell Setup Commands

```powershell
# 1. Navigate to the project directory
cd "d:\my project\AI IT Agent\ai_learning_assistant"

# 2. Create Python Virtual Environment
python -m venv venv

# 3. Activate Virtual Environment
venv\Scripts\activate

# 4. Install Dependencies
pip install -r requirements.txt
```

---

## 9. Ollama Setup

```powershell
# Install Ollama from https://ollama.com if not installed

# Start Ollama service (if not running in background)
ollama serve

# Pull Qwen2.5:3B model
ollama pull qwen2.5:3b
```

---

## 10. MCP Setup
The MCP Server is implemented in `mcp_server.py` using official Model Context Protocol tools.
The agent client (`agent_client.py`) automatically spawns and manages the MCP server process via `stdio` transport. No manual server startup is required!

### Available MCP Tools:
1. `search_study_material`: Search topic explanations, key points, and examples.
2. `get_topic`: Retrieve detailed topic information.
3. `generate_quiz`: Generate custom MCQ quizzes.
4. `create_study_plan`: Generate time-allocated study schedules.
5. `save_quiz_result`: Persist quiz score to SQLite memory.
6. `get_study_history`: Fetch past study activities and queries.
7. `get_progress_summary`: Retrieve quiz averages, performance level, and weak topics.

---

## 11. Running the Application

### Interactive CLI Mode
```powershell
python agent_client.py
```

### Automated Demo Mode
```powershell
python agent_client.py --demo
```

---

## 12. Example Queries

```text
"What is a process in operating systems?"
"Explain inheritance in C++."
"Create a 5-question quiz on DBMS normalization."
"I have 3 hours to prepare for an Operating Systems exam. Create a study plan."
"What topics have I studied recently?"
"How am I performing in my quizzes?"
```

---

## 13. Expected Output

```text
==================================================
       AI LEARNING & STUDY ASSISTANT
 Powered by Qwen2.5:3B + LangGraph + MCP
==================================================

Student: What is a process in operating systems?

[AGENT] Analyzing query...
[ROUTER] Category: study_question
[SUBJECT] Operating Systems
[TOPIC] Process
[TOOL] search_study_material
[TOOL RESULT] Data received
[AGENT] Synthesizing response...

AI Study Assistant:
Process (Operating Systems)

Definition:
A process is a program in execution. It is an active entity that requires system resources such as CPU time, memory, files, and I/O devices.

Key Points:
  - A process is a program in execution (active entity)
  - Each process has its own Process Control Block (PCB)
  - A process can be in states: New, Ready, Running, Waiting, Terminated

Example: A running web browser like Chrome is a process.
```

---

## 14. Limitations
- Knowledge base is currently restricted to pre-populated Computer Science topics in `study_material.json`.
- LLM synthesis speed depends on local hardware GPU/CPU capabilities.
- Memory tracking is scoped per session ID stored in local SQLite database (`study_memory.db`).

---

## 15. Future Enhancements
- Integration of **Vector RAG (ChromaDB/FAISS)** for semantic retrieval over PDF textbooks.
- Graphical User Interface (Streamlit / PySide6 / React frontend).
- Multi-user authentication and cloud sync.
- Adaptive flashcard generation and spaced repetition algorithms.
