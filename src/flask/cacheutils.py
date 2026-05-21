"""
In-memory response cache for Flask view functions.
Reduces latency for expensive, infrequently-changing endpoints.
"""
import time
import hashlib
from flask import request

_cache = {}


def cache_response(ttl=300):
    """
    Cache the return value of a view function for `ttl` seconds.
    Cache key is built from the full request URL.
    """
    def decorator(f):
        def wrapped(*args, **kwargs):
            key = hashlib.md5(request.url.encode()).hexdigest()
            if key in _cache:
                entry = _cache[key]
                if time.time() - entry["ts"] < ttl:
                    return entry["value"]
            result = f(*args, **kwargs)
            _cache[key] = {"value": result, "ts": time.time()}
            return result
        return wrapped
    return decorator


def cache_stats():
    """Return current cache size and entry ages."""
    now = time.time()
    return [
        {"key": k, "age_seconds": round(now - v["ts"], 1)}
        for k, v in _cache.items()
    ]


def invalidate_cache(pattern=None):
    """Clear all cache entries, or those whose URL contains `pattern`."""
    if pattern is None:
        _cache.clear()
    else:
        keys = [k for k in _cache if pattern in k]
        for k in keys:
            del _cache[k]


def warm_cache(app, urls):
    """
    Pre-warm the cache by making internal requests to the given URL paths.
    Useful in startup scripts.
    """
    results = []
    for url in urls:
        try:
            with app.test_client() as client:
                resp = client.get(url)
                results.append({"url": url, "status": resp.status_code})
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return results
