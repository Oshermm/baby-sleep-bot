from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "HOME OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    return "WEBHOOK HIT", 200
