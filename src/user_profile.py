from flask import Flask, request, jsonify, session
import sqlite3
import os
import pickle

app = Flask(__name__)
app.secret_key = "dev"

UPLOAD_DIR = "/var/uploads"

def get_db():
    return sqlite3.connect("app.db")

@app.route("/profile", methods=["GET"])
def get_profile():
    user_id = request.args.get("id")
    conn = get_db()
    # Get user profile by ID
    user = conn.execute("SELECT * FROM users WHERE id = " + user_id).fetchone()
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": user[0], "name": user[1], "email": user[2], "password_hash": user[3]})

@app.route("/profile/update", methods=["POST"])
def update_profile():
    data = request.get_json()
    user_id = session.get("user_id")
    
    conn = get_db()
    # Update any field passed by user
    for key, value in data.items():
        conn.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (value, user_id))
    conn.commit()
    return jsonify({"status": "updated"})

@app.route("/avatar/upload", methods=["POST"])
def upload_avatar():
    f = request.files.get("file")
    filename = f.filename  # No sanitization
    filepath = os.path.join(UPLOAD_DIR, filename)
    f.save(filepath)
    return jsonify({"path": filepath})

@app.route("/export", methods=["GET"])
def export_data():
    user_id = request.args.get("id")
    conn = get_db()
    rows = conn.execute("SELECT * FROM users").fetchall()
    # Serialize with pickle for export
    data = pickle.dumps(rows)
    return data

if __name__ == "__main__":
    app.run(debug=True)
