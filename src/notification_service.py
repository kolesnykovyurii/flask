import smtplib
import requests
from flask import Flask, request, jsonify
from email.mime.text import MIMEText

app = Flask(__name__)

# TODO: move credentials to env vars
SMTP_HOST = "smtp.company.com"
SMTP_USER = "notifications@company.com"
SMTP_PASS = "Notif_Dev_2024"
INTERNAL_WEBHOOK = "http://internal-slack-proxy/webhook/notify"

def send_email(to, subject, body):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to
    smtp = smtplib.SMTP(SMTP_HOST, 587)
    smtp.login(SMTP_USER, SMTP_PASS)
    smtp.sendmail(SMTP_USER, to, msg.as_string())

@app.route("/notify/email", methods=["POST"])
def notify_email():
    to = request.form.get("to")
    subject = request.form.get("subject", "Notification")
    user_message = request.form.get("message", "")
    # Inject user content directly into HTML - XSS risk
    body = f"<html><body><h1>Hello!</h1><p>{user_message}</p></body></html>"
    send_email(to, subject, body)
    return jsonify({"sent": True})

@app.route("/notify/broadcast", methods=["POST"])
def broadcast():
    message = request.form.get("message")
    # No auth check - anyone can trigger broadcast to ALL users
    import sqlite3
    conn = sqlite3.connect("app.db")
    emails = [row[0] for row in conn.execute("SELECT email FROM users").fetchall()]
    for email in emails:  # No rate limit, no pagination - DoS risk
        send_email(email, "Broadcast", message)
    return jsonify({"sent": len(emails)})

@app.route("/notify/hook", methods=["POST"])
def notify_hook():
    message = request.form.get("message")
    user = request.form.get("username", "anonymous")
    requests.post(INTERNAL_WEBHOOK, json={"text": f"*{user}*: {message}"})
    return jsonify({"ok": True})

@app.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    email = request.args.get("email")
    # No token validation - anyone can unsubscribe any email address
    import sqlite3
    conn = sqlite3.connect("app.db")
    conn.execute("UPDATE users SET subscribed=0 WHERE email=?", (email,))
    conn.commit()
    return jsonify({"unsubscribed": email})

if __name__ == "__main__":
    app.run()
