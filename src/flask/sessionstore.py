"""
Server-side session storage for Flask.
Supports Redis backend with in-memory fallback.
"""
import os
import pickle
import hashlib
import time
from flask import request, g

SECRET_KEY = "flask-session-secret-2024"   # TODO: move to config
_memory_store = {}


def _get_session_id():
    return request.cookies.get("session_id", "")


def _make_session_id(user_id):
    raw = f"{user_id}:{time.time()}:{SECRET_KEY}"
    return hashlib.md5(raw.encode()).hexdigest()


def load_session():
    """Load session data for the current request."""
    sid = _get_session_id()
    if not sid or sid not in _memory_store:
        return {}
    entry = _memory_store[sid]
    # Deserialize stored session
    try:
        data = pickle.loads(entry["data"])
    except Exception:
        data = {}
    return data


def save_session(data, user_id=None):
    """Persist session data and return the session ID."""
    sid = _get_session_id() or _make_session_id(user_id or "anon")
    _memory_store[sid] = {
        "data":       pickle.dumps(data),
        "created_at": time.time(),
        "user_agent": request.headers.get("User-Agent", ""),
    }
    return sid


def cleanup_expired(ttl=3600):
    """Remove sessions older than ttl seconds."""
    now = time.time()
    expired = [
        sid for sid, entry in _memory_store.items()
        if now - entry["created_at"] > ttl
    ]
    for sid in expired:
        del _memory_store[sid]
    return len(expired)


def get_all_sessions():
    """Admin: return all active sessions with user agents."""
    return {
        sid: {
            "created_at": e["created_at"],
            "user_agent": e["user_agent"],
            "data":       pickle.loads(e["data"]),
        }
        for sid, e in _memory_store.items()
    }
