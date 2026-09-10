# ==============================================================================
# mcp_server.py - MCP Server for AI Learning & Study Assistant
# ==============================================================================
#
# Run standalone: python mcp_server.py
# The agent_client.py starts this automatically via stdio transport.
# ==============================================================================

import json
import sys
import os
import re
import asyncio
from pathlib import Path
from typing import Any

# Add parent directory context for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

import knowledge_base as kb
import database as db

# ==============================================================================
# Ollama helper - used by generate_quiz and create_study_plan tools
# ==============================================================================

def call_ollama(prompt: str, max_tokens: int = 1000) -> str:
    """Call Ollama qwen2.5:3b with a prompt. Returns the response text."""
    try:
        import urllib.request
        import urllib.error

        payload = json.dumps({
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.5}
        }).encode("utf-8")

        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except Exception as e:
        return f"[LLM Error: {e}]"


# ==============================================================================
# MCP Server
# ==============================================================================

app = Server("ai-learning-assistant")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List all available MCP tools."""
    return [
        types.Tool(
            name="search_study_material",
            description="Search the knowledge base for study material on a topic. Use for general questions, summaries, and explanations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or question"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Optional subject filter (e.g. Operating Systems, DBMS, C++, Java)"
                    },
                    "topic": {
                        "type": "string",
                        "description": "Optional topic filter (e.g. Process, Normalization, Inheritance)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_topic",
            description="Get detailed information about a specific subject and topic from the knowledge base.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject (e.g. Operating Systems, DBMS, C++, Java, Computer Networks, Data Structures)"
                    },
                    "topic": {
                        "type": "string",
                        "description": "The topic name (e.g. Process, Thread, Normalization, Inheritance)"
                    }
                },
                "required": ["subject", "topic"]
            }
        ),
        types.Tool(
            name="generate_quiz",
            description="Generate a quiz with multiple choice questions for a given subject and topic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject for the quiz"
                    },
                    "topic": {
                        "type": "string",
                        "description": "The topic for the quiz (or 'general' for mixed topic)"
                    },
                    "number_of_questions": {
                        "type": "integer",
                        "description": "Number of questions (1-10)",
                        "default": 5
                    },
                    "difficulty": {
                        "type": "string",
                        "description": "Difficulty level: beginner, intermediate, or advanced",
                        "default": "beginner"
                    }
                },
                "required": ["subject", "topic"]
            }
        ),
        types.Tool(
            name="create_study_plan",
            description="Create a personalized study plan for a subject given available time and goal.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject to study (e.g. Operating Systems, DBMS)"
                    },
                    "available_time": {
                        "type": "string",
                        "description": "Available time (e.g. '3 hours', '2 hours', '1 day')"
                    },
                    "goal": {
                        "type": "string",
                        "description": "Study goal (e.g. exam preparation, learning basics)",
                        "default": "exam preparation"
                    },
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of specific topics to focus on"
                    }
                },
                "required": ["subject", "available_time"]
            }
        ),
        types.Tool(
            name="save_quiz_result",
            description="Save a quiz result to memory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session identifier"},
                    "subject": {"type": "string", "description": "Subject of the quiz"},
                    "topic": {"type": "string", "description": "Topic of the quiz"},
                    "score": {"type": "integer", "description": "Score achieved"},
                    "total_questions": {"type": "integer", "description": "Total questions in quiz"}
                },
                "required": ["session_id", "subject", "topic", "score", "total_questions"]
            }
        ),
        types.Tool(
            name="get_study_history",
            description="Retrieve recent study activity and history for a session.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier to get history for"
                    }
                },
                "required": ["session_id"]
            }
        ),
        types.Tool(
            name="get_progress_summary",
            description="Get a progress summary including quiz scores, weak topics, and recently studied topics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    }
                },
                "required": ["session_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle MCP tool calls."""
    try:
        if name == "search_study_material":
            result = tool_search_study_material(arguments)
        elif name == "get_topic":
            result = tool_get_topic(arguments)
        elif name == "generate_quiz":
            result = tool_generate_quiz(arguments)
        elif name == "create_study_plan":
            result = tool_create_study_plan(arguments)
        elif name == "save_quiz_result":
            result = tool_save_quiz_result(arguments)
        elif name == "get_study_history":
            result = tool_get_study_history(arguments)
        elif name == "get_progress_summary":
            result = tool_get_progress_summary(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        error_result = {"error": str(e), "tool": name}
        return [types.TextContent(type="text", text=json.dumps(error_result))]


# ==============================================================================
# Tool Implementations
# ==============================================================================

def tool_search_study_material(args: dict) -> dict:
    """Search study material from knowledge base."""
    query = args.get("query", "")
    subject = args.get("subject")
    topic = args.get("topic")

    if not query:
        return {"error": "Query is required", "results": []}

    results = kb.search_material(query, subject, topic)

    if not results:
        return {
            "found": False,
            "message": f"No study material found for: {query}",
            "suggestion": "Try a different topic or subject",
            "available_subjects": kb.get_all_subjects()
        }

    return {
        "found": True,
        "query": query,
        "results_count": len(results),
        "results": results
    }


def tool_get_topic(args: dict) -> dict:
    """Get detailed topic information."""
    subject = args.get("subject", "")
    topic = args.get("topic", "")

    if not subject or not topic:
        return {"error": "Both subject and topic are required"}

    entry = kb.get_topic_detail(subject, topic)

    if not entry:
        available_topics = kb.get_topics_for_subject(subject)
        return {
            "found": False,
            "message": f"Topic '{topic}' not found in '{subject}'",
            "available_topics": available_topics or []
        }

    return {"found": True, "data": entry}


def tool_generate_quiz(args: dict) -> dict:
    """Generate a quiz using LLM + knowledge base material."""
    subject = args.get("subject", "")
    topic = args.get("topic", "")
    n_questions = min(int(args.get("number_of_questions", 5)), 10)
    difficulty = args.get("difficulty", "beginner")

    # Get study material for context
    results = kb.search_material(f"{subject} {topic}", subject, topic if topic != "general" else None)

    if not results:
        return {
            "error": f"No study material found for {subject} - {topic}",
            "quiz": []
        }

    # Build context from knowledge base
    context_parts = []
    for entry in results[:2]:
        context_parts.append(
            f"Topic: {entry['topic']}\n"
            f"Explanation: {entry['explanation']}\n"
            f"Key Points: {'; '.join(entry.get('key_points', []))}\n"
            f"Examples: {'; '.join(entry.get('examples', []))}"
        )
    context = "\n\n".join(context_parts)

    prompt = f"""You are a quiz generator. Create exactly {n_questions} multiple choice questions about {subject} - {topic}.
Difficulty: {difficulty}

Use this study material as reference:
{context}

Generate exactly {n_questions} questions in this JSON format:
[
  {{
    "question": "What is ...?",
    "options": {{"A": "option1", "B": "option2", "C": "option3", "D": "option4"}},
    "correct": "A",
    "explanation": "Brief explanation of why A is correct."
  }}
]

Rules:
- Each question must have exactly 4 options (A, B, C, D)
- Only one correct answer per question
- Base questions on the study material provided
- Return ONLY the JSON array, no other text

JSON array:"""

    llm_response = call_ollama(prompt, max_tokens=1500)

    # Try to parse JSON from LLM response
    questions = parse_quiz_json(llm_response, subject, topic, n_questions, results)

    return {
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "total_questions": len(questions),
        "quiz": questions
    }


def parse_quiz_json(llm_response: str, subject: str, topic: str,
                     n_questions: int, results: list) -> list:
    """Parse quiz JSON from LLM response, with fallback quiz generation."""
    # Try to extract JSON array from response
    try:
        # Find JSON array in response
        match = re.search(r'\[.*?\]', llm_response, re.DOTALL)
        if match:
            questions = json.loads(match.group())
            if questions and isinstance(questions, list):
                # Validate structure
                valid = []
                for q in questions:
                    if all(k in q for k in ["question", "options", "correct", "explanation"]):
                        valid.append(q)
                if valid:
                    return valid[:n_questions]
    except (json.JSONDecodeError, AttributeError):
        pass

    # Fallback: Generate questions from knowledge base manually
    return generate_fallback_quiz(subject, topic, n_questions, results)


def generate_fallback_quiz(subject: str, topic: str, n_questions: int, results: list) -> list:
    """Generate fallback quiz questions from knowledge base content."""
    questions = []

    for entry in results:
        key_points = entry.get("key_points", [])
        explanation = entry.get("explanation", "")

        if len(key_points) >= 2:
            q = {
                "question": f"Which of the following best describes {entry['topic']} in {entry['subject']}?",
                "options": {
                    "A": key_points[0],
                    "B": f"A type of sorting algorithm",
                    "C": f"A network protocol",
                    "D": f"A hardware component"
                },
                "correct": "A",
                "explanation": f"{entry['topic']}: {explanation[:150]}"
            }
            questions.append(q)

        if len(key_points) >= 3 and len(questions) < n_questions:
            q2 = {
                "question": f"What is a key characteristic of {entry['topic']}?",
                "options": {
                    "A": "It requires internet connection",
                    "B": key_points[1],
                    "C": "It only works on Linux",
                    "D": "It is deprecated"
                },
                "correct": "B",
                "explanation": key_points[1]
            }
            questions.append(q2)

        if len(questions) >= n_questions:
            break

    return questions[:n_questions]


def tool_create_study_plan(args: dict) -> dict:
    """Create a study plan using knowledge base + LLM."""
    subject = args.get("subject", "")
    available_time = args.get("available_time", "3 hours")
    goal = args.get("goal", "exam preparation")
    topics = args.get("topics", [])

    # Get all topics for subject from knowledge base
    kb_topics = kb.get_topics_for_subject(subject)

    if not kb_topics:
        return {
            "error": f"No topics found for subject: {subject}",
            "available_subjects": kb.get_all_subjects()
        }

    # Use specified topics or all KB topics
    study_topics = topics if topics else kb_topics

    # Parse time
    time_match = re.search(r'(\d+)', available_time)
    hours = int(time_match.group(1)) if time_match else 3
    unit = "hour" if "hour" in available_time.lower() else "day"
    total_minutes = hours * 60 if unit == "hour" else hours * 8 * 60

    prompt = f"""Create a study plan for {subject}.
Goal: {goal}
Available time: {available_time}
Topics to cover: {', '.join(study_topics[:8])}

Create a detailed time-based study plan with time blocks.
Format:
[Time Block 1]
Topics: ...
Activities: ...

[Time Block 2]
...

Include revision and practice time at the end.
Keep it practical and realistic for a student."""

    llm_response = call_ollama(prompt, max_tokens=800)

    if "[LLM Error" in llm_response or not llm_response.strip():
        # Fallback plan
        llm_response = generate_fallback_plan(subject, study_topics, hours, total_minutes)

    return {
        "subject": subject,
        "available_time": available_time,
        "goal": goal,
        "topics_covered": study_topics[:6],
        "study_plan": llm_response
    }


def generate_fallback_plan(subject: str, topics: list, hours: int, total_minutes: int) -> str:
    """Generate a fallback study plan without LLM."""
    plan = f"===== {hours}-HOUR STUDY PLAN FOR {subject.upper()} =====\n\n"

    topics_to_cover = topics[:min(len(topics), hours * 2)]
    time_per_topic = total_minutes // max(len(topics_to_cover), 1)

    current_min = 0
    for i, topic in enumerate(topics_to_cover):
        start_h = current_min // 60
        start_m = current_min % 60
        end_min = current_min + time_per_topic
        end_h = end_min // 60
        end_m = end_min % 60
        plan += f"[{start_h}:{start_m:02d} - {end_h}:{end_m:02d}] {topic}\n"
        plan += f"  - Read and understand key concepts\n"
        plan += f"  - Note down important points\n\n"
        current_min = end_min

    # Add revision block
    if current_min < total_minutes:
        start_h = current_min // 60
        start_m = current_min % 60
        plan += f"[{start_h}:{start_m:02d} - {hours}:00] Quick Revision + Practice Questions\n"
        plan += "  - Review all notes\n"
        plan += "  - Attempt practice questions\n"

    return plan


def tool_save_quiz_result(args: dict) -> dict:
    """Save quiz result to database."""
    session_id = args.get("session_id", "default")
    subject = args.get("subject", "")
    topic = args.get("topic", "")
    score = int(args.get("score", 0))
    total_questions = int(args.get("total_questions", 0))

    db.save_quiz_result(session_id, subject, topic, score, total_questions)
    db.save_study_activity(session_id, subject, topic, "quiz")

    percentage = round((score / total_questions * 100), 1) if total_questions > 0 else 0

    return {
        "saved": True,
        "subject": subject,
        "topic": topic,
        "score": f"{score}/{total_questions}",
        "percentage": percentage,
        "message": f"Quiz result saved: {score}/{total_questions} ({percentage}%)"
    }


def tool_get_study_history(args: dict) -> dict:
    """Get study history from database."""
    session_id = args.get("session_id", "default")

    history = db.get_study_history(session_id)
    conversations = db.get_recent_conversations(session_id, limit=5)
    quiz_history = db.get_quiz_history(session_id, limit=5)

    if not history and not conversations:
        return {
            "found": False,
            "message": "No study history found for this session.",
            "history": []
        }

    return {
        "found": True,
        "session_id": session_id,
        "recent_activity": history,
        "recent_queries": [c.get("user_query", "") for c in conversations],
        "quiz_history": quiz_history
    }


def tool_get_progress_summary(args: dict) -> dict:
    """Get progress summary from database."""
    session_id = args.get("session_id", "default")
    summary = db.get_progress_summary(session_id)

    return {
        "session_id": session_id,
        "total_quizzes_attempted": summary["total_quizzes"],
        "average_score_percentage": summary["average_score_percentage"],
        "recently_studied_topics": summary["recently_studied"],
        "weak_topics": summary["weak_topics"],
        "performance_level": (
            "Excellent" if summary["average_score_percentage"] >= 80 else
            "Good" if summary["average_score_percentage"] >= 60 else
            "Needs Improvement" if summary["average_score_percentage"] > 0 else
            "No quizzes taken yet"
        )
    }


# ==============================================================================
# Entry point
# ==============================================================================

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
