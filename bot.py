from flask import Flask, request
from datetime import datetime
import requests
import json
import gspread
from google.oauth2.service_account import Credentials
import os


app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
TG_API = f"https://api.telegram.org/bot{TOKEN}"

def get_sheet():
    creds_json = json.loads(os.environ["GOOGLE_CREDS_JSON"])

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(creds_json, scopes=scope)
    client = gspread.authorize(creds)

    sheet = client.open("Baby Tracker").sheet1
    return sheet

def log_event(event_type, duration=None, child_id="Maya", user="unknown"):
    sheet = get_sheet()

    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        child_id,
        event_type,
        str(duration) if duration else "",
        user
    ])
# 🔥 חובה להוסיף את זה:
last_wake_time = None
last_sleep_time = None


def send_keyboard(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "🟢 קמה", "callback_data": "WAKE"}],
            [{"text": "😴 הונחה לישון", "callback_data": "SLEEP"}],
            [{"text": "🙌 הרמתי, לא נרדמה", "callback_data": "UP"}],
            [
                {"text": "⏰ כמה זמן ערה", "callback_data": "AWAKE_TIME"},
                {"text": "💤 כמה זמן ישנה", "callback_data": "SLEEP_TIME"}
            ]
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
        tg_user = callback["from"]

        user_label = tg_user.get("first_name", "unknown")

        global last_wake_time
        global last_sleep_time

        if action == "WAKE":
            now = datetime.now()
            message = "🟢 קמה"
        
            sleep_duration = None
        
            if last_sleep_time is not None:
                sleep_duration = now - last_sleep_time
                message += f"\n😴 ישנה: {str(sleep_duration).split('.')[0]}"
        
            last_wake_time = now
        
            log_event(
                "WAKE",
                sleep_duration,
                child_id="Maya",
                user=user_label
            )        
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

            log_event(
                "SLEEP",
                awake_duration,
                child_id="Maya",
                user=user_label
            )        
            requests.post(f"{TG_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": message
            })

            if action == "UP":
                now = datetime.now()
                message = "🙌 הרמתי, לא נרדמה"
            
                awake_duration = None
            
                # 👇 חשוב: תמיד מחשבים מה-wake האחרון, לא מאפסים
                if last_wake_time:
                    awake_duration = now - last_wake_time
                    message += f"\n⏰ ערה ברצף: {str(awake_duration).split('.')[0]}"
            
                # ❌ לא מאפסים last_wake_time כאן!
            
                log_event("UP", awake_duration, child_id="Maya", user=user_label)
                
                requests.post(f"{TG_API}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": message
                })

            if action == "SLEEP_TIME":
                now = datetime.now()
            
                if last_sleep_time:
                    duration = now - last_sleep_time
                    message = f"💤 ישנה כבר: {str(duration).split('.')[0]}"
                else:
                    message = "אין נתון על שינה אחרונה"
            
                requests.post(f"{TG_API}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": message
                })

            if action == "AWAKE_TIME":
                now = datetime.now()
            
                if last_wake_time:
                    duration = now - last_wake_time
                    message = f"⏰ ערה כבר: {str(duration).split('.')[0]}"
                else:
                    message = "אין נתון על זמן ערות אחרון"
            
                requests.post(f"{TG_API}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": message
                })
            
    return "ok", 200
