
# ==============================================================================
# agent_client.py - AI Learning and Study Assistant
# LangGraph Agent + MCP Client
# ==============================================================================

import asyncio
import sys
import json
import re
import argparse
import uuid
from typing import Optional, TypedDict
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule

from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import database as db

console = Console()
MODEL_NAME = "qwen2.5:3b"
OLLAMA_BASE_URL = "http://localhost:11434"
MCP_SERVER_PATH = str(Path(__file__).parent / "mcp_server.py")


# ==============================================================================
# Agent State
# ==============================================================================

class AgentState(TypedDict):
    query: str
    category: str
    subject: str
    topic: str
    tool_name: str
    tool_args: dict
    tool_result: str
    response: str
    session_id: str
    tools_description: str


def get_llm():
    return ChatOllama(model=MODEL_NAME, temperature=0.3, base_url=OLLAMA_BASE_URL)


def check_ollama():
    try:
        import urllib.request
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return True
    except Exception:
        return False


# ==============================================================================
# Classification / Routing
# ==============================================================================

CATEGORY_KEYWORDS = {
    "quiz": ["quiz", "quizz", "test me", "questions", "mcq", "multiple choice"],
    "study_plan": ["study plan", "plan", "schedule", "exam tomorrow", "prepare for",
                   "hours to study", "hour to study", "hours to prepare", "revision plan"],
    "progress": ["progress", "performance", "score", "result", "how am i doing",
                 "my performance", "my result", "how have i been"],
    "study_history": ["history", "studied recently", "recently studied", "what did i study",
                      "what have i studied", "topics i studied", "what topics"],
    "topic_details": ["explain", "what is", "what are", "describe", "define",
                      "tell me about", "elaborate", "detail"],
    "summary": ["summarize", "summary", "summarise", "brief", "overview", "gist"],
    "study_question": ["how does", "how do", "why is", "why does", "difference between",
                       "compare", "vs", "versus"]
}

TOOL_MAP = {
    "study_question": "search_study_material",
    "topic_details": "get_topic",
    "quiz": "generate_quiz",
    "study_plan": "create_study_plan",
    "summary": "search_study_material",
    "progress": "get_progress_summary",
    "study_history": "get_study_history",
    "general": "search_study_material"
}

SUBJECT_KEYWORDS = {
    "Operating Systems": ["operating system", " os ", "process", "thread", "cpu scheduling",
                          "deadlock", "paging", "virtual memory", "memory management"],
    "DBMS": ["dbms", "database", " sql ", "normalization", "primary key", "foreign key",
              "transaction", "acid", "relational"],
    "C++": ["c++", "cpp", "constructor", "destructor", "inheritance", "polymorphism",
             "overloading", "overriding", "pointer"],
    "Java": ["java", "jvm", "interface", "exception handling", "collections",
              "extends", "implements", "arraylist", "hashmap"],
    "Computer Networks": ["computer network", " tcp", " udp", " ip ", "http", "https",
                          "osi model", "protocol", "routing", "subnet", "network"],
    "Data Structures": ["data structure", "linked list", " stack", " queue",
                        " tree", " graph", "sorting algorithm", "bst", "binary search"]
}

TOPIC_KEYWORDS = {
    "process": "Process",
    "thread": "Thread",
    "deadlock": "Deadlock",
    "paging": "Paging",
    "virtual memory": "Virtual Memory",
    "cpu scheduling": "CPU Scheduling",
    "scheduling": "CPU Scheduling",
    "normalization": "Normalization",
    "normal form": "Normalization",
    "primary key": "Primary Key",
    "foreign key": "Foreign Key",
    " sql ": "SQL",
    "transaction": "Transactions",
    "acid": "Transactions",
    "inheritance": "Inheritance",
    "polymorphism": "Polymorphism",
    "constructor": "Constructor",
    "function overloading": "Function Overloading",
    "overloading": "Function Overloading",
    "exception handling": "Exception Handling",
    "exception": "Exception Handling",
    "interface": "Interfaces",
    "collections": "Collections",
    "osi model": "OSI Model",
    "osi": "OSI Model",
    "tcp vs udp": "TCP vs UDP",
    "tcp": "TCP vs UDP",
    "http": "HTTP and HTTPS",
    "https": "HTTP and HTTPS",
    "ip address": "IP Addressing",
    "ip addressing": "IP Addressing",
    "subnet": "IP Addressing",
    "linked list": "Linked List",
    " stack": "Stack",
    " queue": "Queue",
    "binary search tree": "Binary Search Tree",
    "bst": "Binary Search Tree",
    "sorting algorithm": "Sorting Algorithms",
    "sorting": "Sorting Algorithms",
    "database": "Database",
    "class and object": "Class and Object",
    " array": "Array"
}


def classify_query(query: str):
    """Classify query with keyword matching."""
    query_lower = " " + query.lower() + " "
    
    # Detect category
    category = "general"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in query_lower or kw in query.lower() for kw in keywords):
            category = cat
            break
    
    # Detect subject
    subject = ""
    for subj, keywords in SUBJECT_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            subject = subj
            break
    
    # Also check plain subject names
    if not subject:
        for subj in SUBJECT_KEYWORDS:
            if subj.lower() in query.lower():
                subject = subj
                break
    
    # Detect topic
    topic = ""
    for kw, tp in TOPIC_KEYWORDS.items():
        if kw in query_lower:
            topic = tp
            break
    
    return category, subject, topic


def classify_llm(query: str, llm):
    """Use LLM to classify query category."""
    try:
        prompt = (
            "Classify this student query. Reply with ONLY these 3 lines:\n"
            "CATEGORY: <one of: study_question, topic_details, quiz, study_plan, summary, progress, study_history, general>\n"
            "SUBJECT: <one of: Operating Systems, DBMS, C++, Java, Computer Networks, Data Structures, or empty>\n"
            f"TOPIC: <specific topic name or empty>\n\nQuery: {query}"
        )
        r = llm.invoke([HumanMessage(content=prompt)])
        text = r.content.strip()
        cat = sub = top = ""
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("CATEGORY:"):
                cat = line.replace("CATEGORY:", "").strip().lower()
            elif line.startswith("SUBJECT:"):
                sub = line.replace("SUBJECT:", "").strip()
            elif line.startswith("TOPIC:"):
                top = line.replace("TOPIC:", "").strip()
        valid = list(TOOL_MAP.keys())
        if cat not in valid:
            cat = "general"
        return cat, sub, top
    except Exception:
        return "", "", ""


def build_tool_args(state: dict) -> dict:
    """Build tool arguments from agent state."""
    cat = state["category"]
    query = state["query"]
    subject = state["subject"]
    topic = state["topic"]
    session_id = state["session_id"]
    q_lower = query.lower()
    
    if cat in ("study_question", "summary", "general"):
        return {
            "query": query,
            "subject": subject or None,
            "topic": topic or None
        }
    elif cat == "topic_details":
        return {
            "subject": subject or "Operating Systems",
            "topic": topic or query[:50]
        }
    elif cat == "quiz":
        n_match = re.search(r"(\d+)\s*(?:question|mcq|q)", q_lower)
        n = min(int(n_match.group(1)) if n_match else 5, 10)
        diff = ("advanced" if "advanced" in q_lower
                else "intermediate" if "intermediate" in q_lower
                else "beginner")
        return {
            "subject": subject or "Operating Systems",
            "topic": topic or "general",
            "number_of_questions": n,
            "difficulty": diff
        }
    elif cat == "study_plan":
        tm = re.search(r"(\d+)\s*(hour|day|minute)", q_lower)
        avail = f"{tm.group(1)} {tm.group(2)}s" if tm else "3 hours"
        return {
            "subject": subject or "Operating Systems",
            "available_time": avail,
            "goal": "exam preparation"
        }
    elif cat in ("progress", "study_history"):
        return {"session_id": session_id}
    
    return {"query": query}


# ==============================================================================
# LangGraph Nodes
# ==============================================================================

def make_decide_tool(llm):
    """Create the decide_tool node."""
    def decide_tool(state: AgentState) -> AgentState:
        query = state["query"]
        console.print("[dim][[AGENT] Analyzing query...][/dim]")
        
        cat, sub, top = classify_query(query)
        
        # Use LLM for better classification if keyword gives general
        if cat == "general" and len(query) > 10:
            try:
                lcat, lsub, ltop = classify_llm(query, llm)
                if lcat and lcat != "general":
                    cat = lcat
                if lsub and not sub:
                    sub = lsub
                if ltop and not top:
                    top = ltop
            except Exception:
                pass
        
        tool = TOOL_MAP.get(cat, "search_study_material")
        
        console.print(f"[cyan][[ROUTER] Category: {cat}][/cyan]")
        if sub:
            console.print(f"[cyan][[SUBJECT] {sub}][/cyan]")
        if top:
            console.print(f"[cyan][[TOPIC] {top}][/cyan]")
        console.print(f"[green][[TOOL] {tool}][/green]")
        
        new_state = {**state, "category": cat, "subject": sub, "topic": top}
        args = build_tool_args(new_state)
        return {**new_state, "tool_name": tool, "tool_args": args}
    
    return decide_tool


def make_call_tool(mcp_session):
    """Create the call_tool node."""
    async def call_tool_node(state: AgentState) -> AgentState:
        tool_name = state["tool_name"]
        tool_args = {k: v for k, v in state["tool_args"].items() if v is not None}
        
        # Ensure session_id for memory tools
        if tool_name in ("get_study_history", "get_progress_summary", "save_quiz_result"):
            tool_args["session_id"] = state["session_id"]
        
        result = await mcp_session.call_tool(tool_name, tool_args)
        
        tool_result = ""
        if result and result.content:
            for c in result.content:
                if hasattr(c, "text"):
                    tool_result += c.text
        
        console.print("[yellow][[TOOL RESULT] Data received][/yellow]")
        return {**state, "tool_result": tool_result}
    
    return call_tool_node



def synthesize(state: AgentState) -> AgentState:
    """Synthesize final response using LLM."""
    console.print("[dim][[AGENT] Synthesizing response...][/dim]")
    
    query = state["query"]
    tool_result = state["tool_result"]
    category = state["category"]
    
    try:
        tool_data = json.loads(tool_result) if tool_result else {}
    except json.JSONDecodeError:
        tool_data = {"raw": tool_result}
    
    # Quiz - return marker for interactive handling
    if category == "quiz" and "quiz" in tool_data:
        return {**state, "response": f"__QUIZ__:{json.dumps(tool_data)}"}
    
    # Study Plan
    if category == "study_plan" and "study_plan" in tool_data:
        d = tool_data
        resp = f"===== STUDY PLAN FOR {d.get('subject', '').upper()} =====\n"
        resp += f"Available Time: {d.get('available_time', '')}\n"
        topics = d.get("topics_covered", [])
        if topics:
            resp += f"Topics: {', '.join(topics[:6])}\n"
        resp += f"\n{d.get('study_plan', '')}"
        return {**state, "response": resp}
    
    # Progress
    if category == "progress" and "total_quizzes_attempted" in tool_data:
        d = tool_data
        resp = "===== YOUR PROGRESS SUMMARY =====\n\n"
        resp += f"Total Quizzes Attempted: {d.get('total_quizzes_attempted', 0)}\n"
        resp += f"Average Score: {d.get('average_score_percentage', 0)}%\n"
        resp += f"Performance Level: {d.get('performance_level', 'N/A')}\n"
        weak = d.get("weak_topics", [])
        if weak:
            resp += "\nTopics to Improve:\n"
            for t in weak[:3]:
                resp += f"  - {t.get('subject', '')} > {t.get('topic', '')}\n"
        recent = d.get("recently_studied_topics", [])
        if recent:
            resp += "\nRecently Studied:\n"
            for r in recent[:5]:
                resp += f"  - {r.get('subject', '')} > {r.get('topic', '')}\n"
        if d.get("total_quizzes_attempted", 0) == 0:
            resp += "\nNo quizzes yet. Try: 'Create a quiz on Operating Systems'\n"
        return {**state, "response": resp}
    
    # Study History
    if category == "study_history":
        d = tool_data
        if not d.get("found"):
            return {**state, "response": "No history found yet. Start asking questions to build your study history!"}
        resp = "===== YOUR STUDY HISTORY =====\n"
        act = d.get("recent_activity", [])
        if act:
            resp += "\nRecent Topics:\n"
            for a in act[:7]:
                resp += f"  - [{a.get('activity_type', '').upper()}] {a.get('subject', '')} > {a.get('topic', '')} ({a.get('timestamp', '')[:10]})\n"
        queries = d.get("recent_queries", [])
        if queries:
            resp += "\nRecent Questions:\n"
            for q in queries[:5]:
                resp += f"  - {q}\n"
        quiz_h = d.get("quiz_history", [])
        if quiz_h:
            resp += "\nRecent Quiz Results:\n"
            for qh in quiz_h[:3]:
                pct = round(qh.get('score', 0) / max(qh.get('total_questions', 1), 1) * 100, 1)
                resp += f"  - {qh.get('subject', '')} - {qh.get('topic', '')}: {qh.get('score', 0)}/{qh.get('total_questions', 0)} ({pct}%)\n"
        return {**state, "response": resp}
    
    # For knowledge questions - use LLM synthesis
    try:
        llm = get_llm()
        results = tool_data.get("results", [])
        data = tool_data.get("data", {})
        
        ctx = ""
        if results:
            for r in results[:2]:
                ctx += f"\nTopic: {r.get('topic', '')}\n"
                ctx += f"Subject: {r.get('subject', '')}\n"
                ctx += f"Explanation: {r.get('explanation', '')}\n"
                ctx += f"Key Points: {', '.join(r.get('key_points', []))}\n"
                ctx += f"Examples: {', '.join(r.get('examples', []))}\n"
        elif data:
            entry = data
            ctx = f"\nTopic: {entry.get('topic', '')}\n"
            ctx += f"Subject: {entry.get('subject', '')}\n"
            ctx += f"Explanation: {entry.get('explanation', '')}\n"
            ctx += f"Key Points: {', '.join(entry.get('key_points', []))}\n"
            ctx += f"Examples: {', '.join(entry.get('examples', []))}\n"
        elif not tool_data.get("found", True):
            avail = tool_data.get("available_subjects", [])
            return {**state, "response": (
                f"I could not find specific information about your query.\n\n"
                f"Available subjects: {', '.join(avail)}\n\n"
                f"Try asking about topics in: Operating Systems, DBMS, C++, Java, Computer Networks, or Data Structures"
            )}
        else:
            ctx = json.dumps(tool_data, indent=2)
        
        prompt = (
            f"You are an AI Study Assistant helping a student.\n"
            f"Student's question: \"{query}\"\n\n"
            f"Relevant knowledge base content:\n{ctx}\n\n"
            f"Provide a clear, well-structured answer that:\n"
            f"1. Directly answers the question\n"
            f"2. Uses the knowledge base information above\n"
            f"3. Is organized with: Definition, Key Points, and Example (where applicable)\n"
            f"4. Uses simple, student-friendly language\n"
            f"5. Does NOT invent facts not in the knowledge base\n\n"
            f"Keep it concise but complete:"
        )
        
        r = llm.invoke([HumanMessage(content=prompt)])
        return {**state, "response": r.content.strip()}
    
    except Exception as e:
        # Fallback from tool data
        results = tool_data.get("results", [])
        if results:
            r = results[0]
            resp = f"**{r.get('topic', '')}** ({r.get('subject', '')})\n\n"
            resp += f"{r.get('explanation', '')}\n\n"
            kps = r.get("key_points", [])
            if kps:
                resp += "Key Points:\n"
                for kp in kps:
                    resp += f"  - {kp}\n"
            examples = r.get("examples", [])
            if examples:
                resp += f"\nExample: {examples[0]}"
            return {**state, "response": resp}
        return {**state, "response": f"Error generating response. Please try again. ({e})"}


# ==============================================================================
# Interactive Quiz
# ==============================================================================

def run_interactive_quiz(quiz_data: dict, session_id: str):
    """Run an interactive quiz session."""
    subject = quiz_data.get("subject", "")
    topic = quiz_data.get("topic", "")
    questions = quiz_data.get("quiz", [])
    
    if not questions:
        console.print("[red]No quiz questions could be generated. Please try again.[/red]")
        return
    
    console.print()
    console.print(Panel(
        f"[bold yellow]===== {subject.upper()} - {topic.upper()} QUIZ =====\n"
        f"Total: {len(questions)} questions | Difficulty: {quiz_data.get('difficulty', 'beginner')}[/bold yellow]",
        border_style="yellow"
    ))
    
    score = 0
    for i, q in enumerate(questions, 1):
        console.print()
        console.print(f"[bold cyan]Question {i}/{len(questions)}:[/bold cyan]")
        console.print(f"[white]{q.get('question', '')}[/white]")
        console.print()
        opts = q.get("options", {})
        for opt, txt in opts.items():
            console.print(f"  [yellow]{opt}.[/yellow] {txt}")
        console.print()
        
        while True:
            ans = console.input("[bold green]Your answer (A/B/C/D): [/bold green]").strip().upper()
            if ans in ["A", "B", "C", "D"]:
                break
            console.print("[red]Please enter A, B, C, or D[/red]")
        
        correct = q.get("correct", "A").upper()
        if ans == correct:
            score += 1
            console.print("[bold green][OK] Correct![/bold green]")
        else:
            console.print(f"[bold red][X] Incorrect. Correct answer: {correct}[/bold red]")
        
        exp = q.get("explanation", "")
        if exp:
            console.print(f"[dim]Explanation: {exp}[/dim]")
    
    console.print()
    pct = round((score / len(questions)) * 100, 1)
    col = "green" if pct >= 70 else "yellow" if pct >= 50 else "red"
    console.print(Panel(
        f"[bold {col}]Quiz Complete!\n\nScore: {score}/{len(questions)} ({pct}%)\n"
        f"{'Excellent! Keep it up!' if pct >= 80 else 'Good job!' if pct >= 60 else 'Keep practicing - you can do it!'}[/bold {col}]",
        border_style=col
    ))
    
    # Save result
    db.save_quiz_result(session_id, subject, topic, score, len(questions))
    db.save_study_activity(session_id, subject, topic, "quiz")
    console.print("[dim]Quiz result saved to memory.[/dim]")


# ==============================================================================
# UI Functions
# ==============================================================================

def show_banner():
    console.print()
    console.print(Panel(
        "[bold cyan]       AI LEARNING AND STUDY ASSISTANT[/bold cyan]\n"
        "[dim] Powered by Qwen2.5:3B + LangGraph + MCP [/dim]",
        border_style="cyan",
        padding=(1, 4)
    ))
    console.print()


def show_help():
    t = Table(title="Commands", border_style="dim")
    t.add_column("Command", style="cyan")
    t.add_column("Description")
    t.add_row("history", "Show recent study history")
    t.add_row("progress", "Show quiz performance and progress")
    t.add_row("help", "Show this help message")
    t.add_row("exit / quit", "Exit the application")
    console.print(t)
    console.print()
    console.print("[dim]Example queries:[/dim]")
    console.print('  "What is a process in operating systems?"')
    console.print('  "Create a 5-question quiz on DBMS normalization."')
    console.print('  "I have 3 hours to prepare for an OS exam. Create a study plan."')
    console.print('  "Explain inheritance in C++."')
    console.print()


def display_response(response: str, session_id: str):
    """Display the agent response - handles quiz specially."""
    if response.startswith("__QUIZ__:"):
        try:
            quiz_data = json.loads(response.replace("__QUIZ__:", ""))
            run_interactive_quiz(quiz_data, session_id)
        except json.JSONDecodeError:
            console.print("[red]Error displaying quiz. Please try again.[/red]")
    else:
        console.print()
        console.print(Panel(
            response,
            title="[bold green]AI Study Assistant[/bold green]",
            border_style="green",
            padding=(1, 2)
        ))
    console.print()


# ==============================================================================
# Agent Runner
# ==============================================================================

async def run_agent(query: str, session_id: str, mcp_session: ClientSession) -> str:
    """Run the LangGraph agent for a single query."""
    llm = get_llm()
    
    builder = StateGraph(AgentState)
    builder.add_node("decide_tool", make_decide_tool(llm))
    builder.add_node("call_tool", make_call_tool(mcp_session))
    builder.add_node("synthesize", synthesize)
    builder.add_edge(START, "decide_tool")
    builder.add_edge("decide_tool", "call_tool")
    builder.add_edge("call_tool", "synthesize")
    builder.add_edge("synthesize", END)
    
    graph = builder.compile()
    
    result = await graph.ainvoke({
        "query": query,
        "category": "",
        "subject": "",
        "topic": "",
        "tool_name": "",
        "tool_args": {},
        "tool_result": "",
        "response": "",
        "session_id": session_id,
        "tools_description": ""
    })
    
    # Save to memory
    db.save_conversation(
        session_id=session_id,
        user_query=query,
        category=result.get("category", "general"),
        tool_used=result.get("tool_name", ""),
        response=result.get("response", "")[:2000]
    )
    
    sub = result.get("subject", "")
    top = result.get("topic", "")
    if sub and top:
        db.save_study_activity(session_id, sub, top, result.get("category", "study"))
    
    return result.get("response", "I could not generate a response.")


# ==============================================================================
# Interactive Mode
# ==============================================================================

async def interactive_mode(mcp_session: ClientSession, session_id: str):
    """Run interactive CLI session."""
    show_banner()
    console.print("[dim]Type your question, or 'help' for commands, 'exit' to quit.[/dim]\n")
    
    while True:
        try:
            query = console.input("[bold blue]Student:[/bold blue] ").strip()
            
            if not query:
                continue
            
            if query.lower() in ("exit", "quit", "q"):
                console.print("[dim]Goodbye! Keep studying![/dim]")
                break
            
            if query.lower() == "help":
                show_help()
                continue
            
            if query.lower() == "history":
                query = "What topics have I studied recently?"
            elif query.lower() == "progress":
                query = "How am I performing in my quizzes?"
            
            console.print()
            response = await run_agent(query, session_id, mcp_session)
            display_response(response, session_id)
        
        except KeyboardInterrupt:
            console.print("\n[dim]Type 'exit' to quit.[/dim]")
        except EOFError:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


# ==============================================================================
# Demo Mode
# ==============================================================================

async def demo_mode(mcp_session: ClientSession, session_id: str):
    """Run automated demo mode."""
    show_banner()
    console.print(Panel(
        "[bold yellow]DEMO MODE - Automated Demonstration[/bold yellow]\n"
        "[dim]Demonstrating all key features of the AI Study Assistant[/dim]",
        border_style="yellow"
    ))
    console.print()
    
    demo_queries = [
        "What is a process in operating systems?",
        "Explain inheritance in C++.",
        "Create a 5-question quiz on DBMS normalization.",
        "I have 3 hours to prepare for an Operating Systems exam. Create a study plan.",
        "What topics have I studied recently?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        console.print(Rule(f"[bold cyan]Demo Query {i}/{len(demo_queries)}[/bold cyan]"))
        console.print()
        console.print(f"[bold blue]Student:[/bold blue] {query}")
        console.print()
        
        try:
            response = await run_agent(query, session_id, mcp_session)
            
            # For demo, show quiz preview instead of interactive
            if response.startswith("__QUIZ__:"):
                quiz_data = json.loads(response.replace("__QUIZ__:", ""))
                questions = quiz_data.get("quiz", [])
                subject = quiz_data.get("subject", "")
                topic = quiz_data.get("topic", "")
                
                preview = f"Quiz: {subject} - {topic}\nGenerated {len(questions)} questions\n\n"
                for j, q in enumerate(questions[:3], 1):
                    preview += f"Q{j}: {q.get('question', '')}\n"
                    for opt, txt in q.get("options", {}).items():
                        preview += f"  {opt}. {txt}\n"
                    preview += f"  [Correct: {q.get('correct', 'A')}]\n\n"
                if len(questions) > 3:
                    preview += f"... and {len(questions) - 3} more questions"
                
                console.print(Panel(preview, title="[bold yellow]Quiz Generated[/bold yellow]", border_style="yellow"))
                console.print()
                
                # Save a demo quiz result
                db.save_quiz_result(session_id, subject, topic, 4, 5)
                db.save_study_activity(session_id, subject, topic, "quiz")
            else:
                display_response(response, session_id)
            
            await asyncio.sleep(2)
        
        except Exception as e:
            console.print(f"[red]Demo query failed: {e}[/red]")
            await asyncio.sleep(1)
    
    console.print()
    console.print(Rule("[bold green]Demo Complete![/bold green]"))
    console.print("[green]All demo queries completed successfully![/green]")
    console.print("[dim]Run without --demo flag for interactive mode.[/dim]")


# ==============================================================================
# Entry Point
# ==============================================================================

async def main():
    parser = argparse.ArgumentParser(description="AI Learning and Study Assistant")
    parser.add_argument("--demo", action="store_true", help="Run automated demo mode")
    parser.add_argument("--session", type=str, default=None, help="Session ID")
    args = parser.parse_args()
    
    # Check Ollama
    console.print("[dim]Checking Ollama connection...[/dim]")
    if not check_ollama():
        console.print(Panel(
            "[bold red]Ollama is not running![/bold red]\n\n"
            "Please:\n"
            "1. Install Ollama from https://ollama.com\n"
            "2. Start Ollama\n"
            "3. Run: ollama pull qwen2.5:3b\n"
            "4. Run this application again",
            title="Ollama Required",
            border_style="red"
        ))
        sys.exit(1)
    
    console.print("[green][OK] Ollama is running[/green]")
    
    session_id = args.session or str(uuid.uuid4())[:8]
    
    # Start MCP server via stdio
    server_params = StdioServerParameters(
        command="python",
        args=[MCP_SERVER_PATH],
        env=None
    )
    
    console.print("[dim]Starting MCP server and connecting...[/dim]")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Discover tools
                tools_resp = await session.list_tools()
                tool_names = [t.name for t in tools_resp.tools]
                console.print(f"[green][OK] MCP server ready. Available tools: {', '.join(tool_names)}[/green]")
                console.print(f"[dim]Session ID: {session_id}[/dim]\n")
                
                if args.demo:
                    await demo_mode(session, session_id)
                else:
                    await interactive_mode(session, session_id)
    
    except FileNotFoundError:
        console.print(f"[red]MCP server not found: {MCP_SERVER_PATH}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Failed to start MCP server: {e}[/red]")
        console.print("[dim]Ensure all dependencies are installed: pip install -r requirements.txt[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
