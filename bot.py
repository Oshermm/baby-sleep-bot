from flask import Flask, request
from datetime import datetime
import os
import requests


app = Flask(__name__)

TOKEN = "8974305460:AAH6xQqM0xxfXFPDNIlHlwgFsZafLsnnYiQ"
TG_API = f"https://api.telegram.org/bot{TOKEN}"

# 🔥 חובה להוסיף את זה:
last_wake_time = None
last_sleep_time = None


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

        global last_wake_time
        global last_sleep_time

        if action == "WAKE":
            now = datetime.now()
        
            message = "🟢 קמה"
        
            if last_sleep_time:
                sleep_duration = now - last_sleep_time
                message += f"\n😴 ישנה: {str(sleep_duration).split('.')[0]}"
        
            last_wake_time = now
        
            requests.post(f"{TG_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": message
            })
        
        
        if action == "SLEEP":
            now = datetime.now()
        
            message = "😴 הונחה לישון"
        
            if last_wake_time:
                awake_duration = now - last_wake_time
                message += f"\n⏰ ערה: {str(awake_duration).split('.')[0]}"
        
            last_sleep_time = now
        
            requests.post(f"{TG_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": message
            })
    return "ok", 200
