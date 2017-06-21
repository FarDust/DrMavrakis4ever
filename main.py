import flask
import requests
from flask import request

with open("telegram_token", "r") as file:
    T_TOKEN = file.read().strip()

URL_TEL_BOT = "https://api.telegram.org/bot{token}".format(**{"token": T_TOKEN})

requests.get(URL_TEL_BOT + "/sendMessage", params={"chat_id": 413925182, "text": "new_deploy"}).json()
request.get(URL_TEL_BOT + "/setWebhook", params={"url": "https://drmavrakis4ever.herokuapp.com/telegram"})

app = flask.Flask(__name__)


@app.route("/")
def index():
    return "<h1>I'm a bot</h1>"


@app.route("/admin/<message>")
def send(message):
    req = requests.get(URL_TEL_BOT + "/sendMessage", params={"chat_id": 413925182, "text": message})
    return "<p>{}</p>".format(req.status_code)


@app.route("/payload", methods=["POST"])
def github():
    data = request.json
    send("GitHub say something")
    return "200 OK"


@app.route("/telegram", methods=["GET", "POST"])
def telegram():
    send("I recived a querry")
    data = request.json
    return "200 OK"

# app.run(port="")
