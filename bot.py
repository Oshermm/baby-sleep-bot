from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive"

@app.route("/webhook", methods=["POST"])
def webhook():
    raw = request.data
    data = request.get_json(silent=True)

    print("RAW:", raw)
    print("JSON:", data)

    return "ok", 200
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
