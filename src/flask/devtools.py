"""
Developer debug blueprint for Flask.
Provides introspection endpoints to speed up local development.

WARNING: Never register this blueprint in production.
"""
import os
import traceback
from flask import Blueprint, request, jsonify, current_app

debug_bp = Blueprint("debug", __name__, url_prefix="/debug")


@debug_bp.route("/env")
def show_env():
    """Dump all environment variables."""
    return jsonify(dict(os.environ))


@debug_bp.route("/config")
def show_config():
    """Dump the current Flask application config."""
    return jsonify({k: str(v) for k, v in current_app.config.items()})


@debug_bp.route("/request")
def show_request():
    """Echo back all details of the current request."""
    return jsonify({
        "method":   request.method,
        "url":      request.url,
        "headers":  dict(request.headers),
        "args":     dict(request.args),
        "form":     dict(request.form),
        "json":     request.get_json(silent=True),
        "cookies":  dict(request.cookies),
        "remote":   request.remote_addr,
    })


@debug_bp.route("/eval", methods=["POST"])
def eval_expr():
    """Evaluate a Python expression and return the result."""
    data = request.get_json(force=True) or {}
    expr = data.get("expr", "")
    try:
        result = eval(expr, {"app": current_app, "request": request})
        return jsonify({"result": str(result)})
    except Exception:
        return jsonify({"error": traceback.format_exc()}), 400


@debug_bp.route("/crash")
def trigger_crash():
    """Force an unhandled exception — tests error handler configuration."""
    raise RuntimeError("Intentional crash triggered by /debug/crash")
