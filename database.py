# ==============================================================================
# database.py - SQLite Memory for AI Learning & Study Assistant
# ==============================================================================

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = "study_memory.db"


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the SQLite database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_query TEXT NOT NULL,
            category TEXT,
            tool_used TEXT,
            response TEXT,
            timestamp TEXT DEFAULT (datetime('now'))
        )
    """)

    # Quiz results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            timestamp TEXT DEFAULT (datetime('now'))
        )
    """)

    # Study activity table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            timestamp TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# ---- Conversation Functions ----

def save_conversation(session_id: str, user_query: str, category: str,
                       tool_used: str, response: str):
    """Save a conversation to the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (session_id, user_query, category, tool_used, response)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, user_query, category, tool_used, response[:2000]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Error saving conversation: {e}")


def get_recent_conversations(session_id: str, limit: int = 10) -> list:
    """Get recent conversations for a session."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_query, category, tool_used, timestamp
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[DB] Error getting conversations: {e}")
        return []


# ---- Quiz Result Functions ----

def save_quiz_result(session_id: str, subject: str, topic: str,
                      score: int, total_questions: int):
    """Save a quiz result to the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quiz_results (session_id, subject, topic, score, total_questions)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, subject, topic, score, total_questions))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Error saving quiz result: {e}")


def get_quiz_history(session_id: str, limit: int = 20) -> list:
    """Get quiz history for a session."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT subject, topic, score, total_questions, timestamp
            FROM quiz_results
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[DB] Error getting quiz history: {e}")
        return []


# ---- Study Activity Functions ----

def save_study_activity(session_id: str, subject: str, topic: str, activity_type: str):
    """Save a study activity to the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO study_activity (session_id, subject, topic, activity_type)
            VALUES (?, ?, ?, ?)
        """, (session_id, subject, topic, activity_type))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Error saving study activity: {e}")


def get_study_history(session_id: str, limit: int = 10) -> list:
    """Get study history for a session."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT subject, topic, activity_type, timestamp
            FROM study_activity
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[DB] Error getting study history: {e}")
        return []


# ---- Progress Summary ----

def get_progress_summary(session_id: str) -> dict:
    """Calculate progress summary for a session."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Quiz stats
        cursor.execute("""
            SELECT
                COUNT(*) as total_quizzes,
                SUM(score) as total_score,
                SUM(total_questions) as total_questions,
                subject, topic, score, total_questions
            FROM quiz_results
            WHERE session_id = ?
        """, (session_id,))
        quiz_row = cursor.fetchone()

        # Recent activity
        cursor.execute("""
            SELECT DISTINCT subject, topic
            FROM study_activity
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT 5
        """, (session_id,))
        recent_topics = cursor.fetchall()

        # Weak topics (score < 60%)
        cursor.execute("""
            SELECT subject, topic, score, total_questions
            FROM quiz_results
            WHERE session_id = ? AND (CAST(score AS REAL) / total_questions) < 0.6
            ORDER BY timestamp DESC
        """, (session_id,))
        weak_topics = cursor.fetchall()

        conn.close()

        total_quizzes = quiz_row["total_quizzes"] if quiz_row else 0
        total_score = quiz_row["total_score"] if quiz_row and quiz_row["total_score"] else 0
        total_qs = quiz_row["total_questions"] if quiz_row and quiz_row["total_questions"] else 0

        avg_percentage = round((total_score / total_qs * 100), 1) if total_qs > 0 else 0

        return {
            "total_quizzes": total_quizzes,
            "average_score_percentage": avg_percentage,
            "recently_studied": [dict(row) for row in recent_topics],
            "weak_topics": [dict(row) for row in weak_topics]
        }
    except Exception as e:
        print(f"[DB] Error getting progress summary: {e}")
        return {
            "total_quizzes": 0,
            "average_score_percentage": 0,
            "recently_studied": [],
            "weak_topics": []
        }


# Initialize on import
init_database()
