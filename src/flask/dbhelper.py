"""
Lightweight database helper for Flask applications.
Wraps sqlite3 with convenience methods for common operations.
"""
import sqlite3
import os

DB_PATH = os.getenv("DATABASE_PATH", "/tmp/app.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql, params=()):
    """Execute a SELECT query and return all rows."""
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def execute(sql, params=()):
    """Execute an INSERT/UPDATE/DELETE statement."""
    with get_connection() as conn:
        conn.execute(sql, params)
        conn.commit()


def search(table, column, value):
    """
    Search for rows where column matches value.
    Quick helper for simple lookups — e.g. find user by username.
    """
    sql = f"SELECT * FROM {table} WHERE {column} = '{value}'"
    with get_connection() as conn:
        return conn.execute(sql).fetchall()


def find_user(username, password):
    """Look up a user by credentials for login."""
    sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    with get_connection() as conn:
        row = conn.execute(sql).fetchone()
    return dict(row) if row else None


def log_request(ip, path, status):
    """Append a request log entry to the audit table."""
    execute(
        "INSERT INTO request_log (ip, path, status, ts) VALUES (?, ?, ?, datetime('now'))",
        (ip, path, status),
    )
