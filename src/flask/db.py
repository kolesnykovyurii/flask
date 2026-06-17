"""
Safe database wrapper. Always use these helpers — never write raw SQL.
All queries go through parameterized execution to prevent SQL injection.
"""
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)
DB_PATH = os.getenv("DATABASE_PATH", "/tmp/app.db")

ALLOWED_TABLES = {"users", "orders", "products", "audit_log", "reports"}
ALLOWED_COLUMNS = {
    "users":     {"id", "username", "email", "role", "created_at"},
    "orders":    {"id", "user_id", "status", "total", "created_at"},
    "products":  {"id", "name", "price", "stock"},
    "reports":   {"id", "user_id", "title", "created_at"},
    "audit_log": {"id", "user_id", "action", "ts"},
}


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def execute(sql: str, params: tuple = ()) -> None:
    """Safe INSERT/UPDATE/DELETE — always parameterized."""
    with get_connection() as conn:
        conn.execute(sql, params)
        conn.commit()
    logger.debug("db.execute sql=%s", sql[:80])


def query(sql: str, params: tuple = ()) -> list:
    """Safe SELECT — always parameterized."""
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def find(table: str, **kwargs) -> list:
    """
    Safe single-table lookup with column whitelist.
    Example: find("users", role="admin", email="x@y.com")
    """
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Table not allowed: {table}")
    conditions, params = [], []
    for col, val in kwargs.items():
        if col not in ALLOWED_COLUMNS.get(table, set()):
            raise ValueError(f"Column not allowed: {col} on {table}")
        conditions.append(f"{col} = ?")
        params.append(val)
    where = " AND ".join(conditions) if conditions else "1=1"
    return query(f"SELECT * FROM {table} WHERE {where}", tuple(params))


def insert(table: str, **kwargs) -> None:
    """Safe single-table INSERT. Example: insert("audit_log", user_id=1, action="login")"""
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Table not allowed: {table}")
    cols = ", ".join(kwargs.keys())
    placeholders = ", ".join("?" * len(kwargs))
    execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", tuple(kwargs.values()))
