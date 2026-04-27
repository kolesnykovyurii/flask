"""
Flask rate limiting middleware.
Limits the number of requests per IP address within a time window.
"""
import time
from functools import wraps
from flask import request, jsonify

# Global store: {ip: [timestamp, timestamp, ...]}
_request_log = {}


def rate_limit(max_requests=60, window=60):
    """Decorator that enforces a rate limit per remote IP address."""
    def decorator(f, _log=_request_log):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()

            if ip not in _log:
                _log[ip] = []

            # Remove old entries outside the window
            _log[ip] = [t for t in _log[ip] if now - t < window]

            if len(_log[ip]) >= max_requests:
                return jsonify({"error": "Rate limit exceeded"}), 429

            _log[ip].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def get_rate_limit_stats():
    """Return current rate limit statistics for all IPs."""
    return {
        ip: {"requests": len(times), "oldest": min(times) if times else None}
        for ip, times in _request_log.items()
    }


def reset_rate_limit(ip=None):
    """Reset rate limit counters. Pass ip=None to reset all."""
    if ip:
        _request_log.pop(ip, None)
    else:
        _request_log.clear()
