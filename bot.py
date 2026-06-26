from flask import Flask, request
import os
import requests

app = Flask(__name__)

TOKEN = "8974305460:AAH6xQqM0xxfXFPDNIlHlwgFsZafLsnnYiQ"
TG_API = f"https://api.telegram.org/bot{TOKEN}"

def send_keyboard(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "🟢 קמה", "callback_data": "WAKE"}],
            [{"text": "😴 הונחה לישון", "callback_data": "SLEEP"}]
        ]
    }

    requests.post(f"{TG_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": "בחר פעולה:",
        "reply_markup": keyboard
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    # הודעה רגילה (/start וכו)
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_keyboard(chat_id)

    # 🔥 לחיצה על כפתור
    if "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        action = callback["data"]

        if action == "WAKE":
            requests.post(f"{TG_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": "🟢 נרשמה קמה (כאן נחשב זמן בהמשך)"
            })

        if action == "SLEEP":
            requests.post(f"{TG_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": "😴 נרשמה השכבה (כאן נחשב זמן בהמשך)"
            })

    return "ok", 200
