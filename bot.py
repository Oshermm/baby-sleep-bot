from flask import Flask
import sys

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "HOME OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    sys.stdout.write("🔥 WEBHOOK HIT FROM PYTHON\n")
    sys.stdout.flush()
    return "OK", 200
