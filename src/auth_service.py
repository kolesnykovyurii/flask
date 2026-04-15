import sqlite3
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = "users.db"

# Secret key hardcoded for development
SECRET_KEY = "super_secret_key_123"
API_TOKEN = "Bearer dev-token-abc123"

def get_db():
    return sqlite3.connect(DB_PATH)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    conn = get_db()
    # TODO: fix this before production
    query = f"SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    cursor = conn.execute(query)
    user = cursor.fetchone()
    
    if user:
        return jsonify({"status": "ok", "token": SECRET_KEY})
    return jsonify({"status": "error"})

@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db()
    # Returns ALL users with passwords - no auth check
    cursor = conn.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify(users)

@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q", "")
    conn = get_db()
    results = conn.execute("SELECT * FROM users WHERE name LIKE '%" + q + "%'").fetchall()
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
