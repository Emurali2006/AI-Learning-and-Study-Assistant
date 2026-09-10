# ==============================================================================
# knowledge_base.py - Local JSON Knowledge Base Search
# ==============================================================================

import json
import re
from pathlib import Path
from typing import Optional

KB_PATH = Path(__file__).parent / "data" / "study_material.json"

_knowledge_base = None


def load_knowledge_base() -> list:
    """Load the knowledge base from JSON file."""
    global _knowledge_base
    if _knowledge_base is None:
        try:
            with open(KB_PATH, "r", encoding="utf-8") as f:
                _knowledge_base = json.load(f)
        except FileNotFoundError:
            print(f"[KB] Knowledge base not found at {KB_PATH}")
            _knowledge_base = []
        except json.JSONDecodeError as e:
            print(f"[KB] Error parsing knowledge base: {e}")
            _knowledge_base = []
    return _knowledge_base


def search_material(query: str, subject: Optional[str] = None,
                    topic: Optional[str] = None) -> list:
    """Search study material by query, subject, and/or topic."""
    kb = load_knowledge_base()
    query_lower = query.lower()
    results = []

    for entry in kb:
        # Filter by subject if specified
        if subject and subject.lower() not in entry["subject"].lower():
            continue
        # Filter by topic if specified
        if topic and topic.lower() not in entry["topic"].lower():
            continue

        # Score based on keyword matches
        score = 0
        entry_text = (
            entry["subject"] + " " +
            entry["topic"] + " " +
            entry["explanation"] + " " +
            " ".join(entry.get("key_points", [])) + " " +
            " ".join(entry.get("examples", []))
        ).lower()

        # Check query words against entry text
        query_words = query_lower.split()
        for word in query_words:
            if len(word) >= 3 and word in entry_text:
                score += 1

        # Boost score for topic/subject match
        if entry["topic"].lower() in query_lower:
            score += 5
        if entry["subject"].lower() in query_lower:
            score += 3

        if score > 0:
            results.append((score, entry))

    # Sort by score descending
    results.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in results[:3]]


def get_topic_detail(subject: str, topic: str) -> Optional[dict]:
    """Get detailed information about a specific topic."""
    kb = load_knowledge_base()
    subject_lower = subject.lower()
    topic_lower = topic.lower()

    # Exact match first
    for entry in kb:
        if (entry["subject"].lower() == subject_lower and
                entry["topic"].lower() == topic_lower):
            return entry

    # Partial match
    for entry in kb:
        if (subject_lower in entry["subject"].lower() and
                topic_lower in entry["topic"].lower()):
            return entry

    # Even more fuzzy - just topic match
    for entry in kb:
        if topic_lower in entry["topic"].lower():
            return entry

    return None


def get_all_subjects() -> list:
    """Get list of all subjects in knowledge base."""
    kb = load_knowledge_base()
    return list(set(entry["subject"] for entry in kb))


def get_topics_for_subject(subject: str) -> list:
    """Get all topics for a specific subject."""
    kb = load_knowledge_base()
    return [entry["topic"] for entry in kb
            if subject.lower() in entry["subject"].lower()]


def get_entry_count() -> int:
    """Get total number of entries in knowledge base."""
    return len(load_knowledge_base())
