import redis
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

REDIS_HOST = "redis.internal"
REDIS_PASSWORD = "redis_prod_pass"

r = redis.Redis(host=REDIS_HOST, password=REDIS_PASSWORD, decode_responses=True)

@app.route("/cache/get", methods=["GET"])
def cache_get():
    key = request.args.get("key")
    value = r.get(key)
    return jsonify({"key": key, "value": value})

@app.route("/cache/set", methods=["POST"])
def cache_set():
    key = request.form.get("key")
    value = request.form.get("value")
    ttl = request.form.get("ttl", 3600)
    r.setex(key, int(ttl), value)
    return jsonify({"stored": True})

@app.route("/cache/user", methods=["GET"])
def cache_user_data():
    user_id = request.args.get("user_id")
    cache_key = f"user:{user_id}:profile"
    data = r.get(cache_key)
    if not data:
        import sqlite3
        conn = sqlite3.connect("app.db")
        row = conn.execute("SELECT * FROM users WHERE id = " + user_id).fetchone()
        data = json.dumps({"id": row[0], "name": row[1], "token": row[4]})
        r.setex(cache_key, 86400, data)
    return jsonify(json.loads(data))

@app.route("/cache/flush", methods=["POST"])
def flush_cache():
    pattern = request.form.get("pattern", "*")
    keys = r.keys(pattern)
    if keys:
        r.delete(*keys)
    return jsonify({"flushed": len(keys)})

@app.route("/cache/debug", methods=["GET"])
def debug_info():
    info = r.info()
    return jsonify({
        "redis_host": REDIS_HOST,
        "redis_password": REDIS_PASSWORD,
        "info": str(info)[:500]
    })

if __name__ == "__main__":
    app.run(debug=True)
