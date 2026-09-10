# AI Learning & Study Assistant - Project Report

## 1. Project Overview

### Project Title
**AI Learning & Study Assistant**

### Problem Statement
Modern students often struggle with fragmented study materials, lack of personalized learning schedules, difficulty assessing their understanding through practice quizzes, and absent tracking of past learning interactions. Standard AI chatbots provide generic, un-grounded answers without state persistence or structured tool execution.

### Brief Description
The **AI Learning & Study Assistant** is a local, privacy-focused Agentic AI application. Built using **LangGraph**, **Model Context Protocol (MCP)**, **LangChain**, **Ollama (Qwen2.5:3B)**, and **SQLite**, it acts as an autonomous tutor. It interprets student intent, dynamically routes requests to local MCP tools (searching knowledge bases, generating custom quizzes, building study plans, tracking activity), and synthesizes clear, structured answers with full session memory.

---

## 2. Objectives & Proposed Solution

### Project Objectives
1. Build an autonomous Agentic AI system for student study support without relying on cloud APIs.
2. Implement dynamic query routing to specialized MCP tools based on student intent.
3. Provide automated multiple-choice quiz generation with interactive CLI evaluation.
4. Generate practical, time-allocated study schedules for exam preparation.
5. Maintain long-term session memory using SQLite for performance tracking and study history retrieval.

### How the Agentic AI Solution Works

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

The system operates via a stateful **LangGraph StateGraph** graph:
- **START Node**: Ingests `AgentState` containing the query and session context.
- **decide_tool Node**: Utilizes hybrid keyword matching and Qwen2.5:3B LLM intent classification to map queries to 8 functional categories.
- **call_tool Node**: Invokes the corresponding tool exposed by the local **MCP Server** via `stdio` transport.
- **synthesize Node**: Combines structured tool results with Qwen2.5:3B to generate student-friendly explanations formatted with Definitions, Key Points, and Examples.
- **SQLite Checkpoint**: Automatically logs conversation history, activity types, and quiz performance scores into `study_memory.db`.

### Key Features
- **6 Computer Science Subjects Covered**: Operating Systems, DBMS, C++, Java, Computer Networks, Data Structures.
- **Automated Quiz Generator**: Multi-choice question creation with instant scoring and explanation feedback.
- **Time-Bounded Study Planner**: Hour-by-hour exam preparation breakdowns.
- **Progress Tracking & Analytics**: Calculates quiz averages, weak topics, and recently studied material.
- **100% Offline Local Execution**: Zero cloud API dependencies, zero subscription costs.

---

## 3. Implementation & Results

### Technologies/Tools Used
- **Language**: Python 3.11+
- **Agent Orchestration**: LangGraph, LangChain Core, LangChain Ollama
- **Local LLM**: Ollama running Qwen2.5:3B
- **Protocol**: MCP (Model Context Protocol) via Stdio Server/Client
- **Database**: SQLite3 (`study_memory.db`)
- **CLI Interface**: Rich (console panels, progress rules, tables)

### Working Process
1. **Knowledge Base Creation**: Designed a structured JSON dataset (`data/study_material.json`) containing subject entries, explanations, key points, examples, and difficulty levels.
2. **MCP Server Construction**: Created `mcp_server.py` exposing 7 distinct tools (`search_study_material`, `get_topic`, `generate_quiz`, `create_study_plan`, `save_quiz_result`, `get_study_history`, `get_progress_summary`).
3. **LangGraph Pipeline**: Formulated `agent_client.py` using `StateGraph` linking intent routing, MCP execution, and LLM synthesis.
4. **SQLite Memory Engine**: Built `database.py` with relational schema storing conversation logs, quiz scores, and activity logs.

### Screenshots / Output Placeholders

```
+-----------------------------------------------------------------------+
| [SCREENSHOT PLACEHOLDER 1: CLI Startup & MCP Tool Discovery]          |
| Shows Rich banner, Ollama connection, and 7 MCP tools discovered.     |
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
| [SCREENSHOT PLACEHOLDER 2: Study Question Routing & LLM Synthesis]   |
| Shows query "What is a process in operating systems?" routing to       |
| search_study_material and presenting structured output.               |
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
| [SCREENSHOT PLACEHOLDER 3: Interactive MCQ Quiz & Scoring]            |
| Shows 5-question quiz generation, interactive user input, and result  |
| score saved to SQLite.                                                |
+-----------------------------------------------------------------------+
```

### Results Achieved
- Successfully demonstrated a fully autonomous agentic loop over local MCP architecture.
- Verified accurate query classification across all 8 intent categories.
- Demonstrated end-to-end quiz generation, execution, and memory logging.
- Verified robust error handling and fallback routing when LLM parsing is delayed or incomplete.

---

## 4. Conclusion & Future Scope

### Project Conclusion
The **AI Learning & Study Assistant** demonstrates the practical power of Agentic AI using local open-source models. By decoupling decision-making (LangGraph), tool execution (MCP Server), LLM reasoning (Qwen2.5:3B), and memory (SQLite), the application provides a modular, reliable, and privacy-focused educational assistant suitable for academic demonstrations, viva presentations, and self-directed student learning.

### Challenges Faced
1. **Parsing Free-Form LLM Outputs**: Small 3B parameter models can produce slightly variable JSON outputs for quizzes. Resolved using regex-based JSON extraction with deterministic fallback question builders.
2. **Local Transport Reliability**: Ensured robust Stdio IPC stream handling between `agent_client.py` and `mcp_server.py`.

### Future Enhancements
- **Vector RAG Integration**: Replace keypoint search with ChromaDB vector embeddings over textbook PDFs.
- **Spaced Repetition Flashcards**: Implement Leitner box flashcard schedules.
- **Web User Interface**: Deploy a lightweight UI using Streamlit or React.

---

## 5. References
1. LangGraph Documentation: https://langchain-ai.github.io/langgraph/
2. Model Context Protocol (MCP) Specification: https://modelcontextprotocol.io/
3. Ollama Documentation: https://ollama.com/
4. Qwen2.5 Model Card: https://huggingface.co/Qwen/Qwen2.5-3B
