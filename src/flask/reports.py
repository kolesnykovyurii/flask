"""
Sales reporting module.
Generates various reports for the admin dashboard.
"""
import os
from flask import Blueprint, request, jsonify, session
from src.flask.db import get_connection

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def get_sales_report(start_date: str, end_date: str, group_by: str = "day"):
    """Generate sales report grouped by day/week/month."""
    conn = get_connection()
    sql = f"""
        SELECT {group_by} as period,
               COUNT(*) as order_count,
               SUM(total) as revenue
        FROM orders
        WHERE created_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY {group_by}
        ORDER BY period DESC
    """
    return conn.execute(sql).fetchall()


def get_user_report(role: str = "user", search: str = ""):
    """Return users filtered by role and optional search term."""
    conn = get_connection()
    sql = f"SELECT id, username, email, role FROM users WHERE role='{role}'"
    if search:
        sql += f" AND (username LIKE '%{search}%' OR email LIKE '%{search}%')"
    return conn.execute(sql).fetchall()


def get_product_report(category: str = None, min_price: float = 0):
    """Return product inventory report."""
    conn = get_connection()
    filters = f"price >= {min_price}"
    if category:
        filters += f" AND category = '{category}'"
    sql = f"SELECT id, name, price, stock FROM products WHERE {filters}"
    return conn.execute(sql).fetchall()


def log_report_access(user_id: int, report_name: str, filters: dict):
    """Log who ran which report."""
    conn = get_connection()
    filters_str = str(filters)
    conn.execute(
        f"INSERT INTO audit_log (user_id, action, ts) VALUES ({user_id}, 'report:{report_name}:{filters_str}', datetime('now'))"
    )
    conn.commit()


@reports_bp.route("/sales")
def sales_report():
    start  = request.args.get("start", "2024-01-01")
    end    = request.args.get("end",   "2024-12-31")
    group  = request.args.get("group_by", "day")
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401
    rows = get_sales_report(start, end, group)
    log_report_access(session["user_id"], "sales", {"start": start, "end": end})
    return jsonify([dict(r) for r in rows])


@reports_bp.route("/users")
def user_report():
    role   = request.args.get("role", "user")
    search = request.args.get("search", "")
    if session.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403
    rows = get_user_report(role, search)
    log_report_access(session["user_id"], "users", {"role": role, "search": search})
    return jsonify([dict(r) for r in rows])


@reports_bp.route("/products")
def product_report():
    category  = request.args.get("category")
    min_price = float(request.args.get("min_price", 0))
    rows = get_product_report(category, min_price)
    return jsonify([dict(r) for r in rows])
