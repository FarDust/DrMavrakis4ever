import flask
import requests
import re

from flask import request

from gitbot import analize
from telegram import get_issue, close_issue, label_issue, create_comment, send, message_format

with open("telegram_token", "r") as file:
    T_TOKEN = file.read().strip()

URL_TEL_BOT = "https://api.telegram.org/bot{token}".format(**{"token": T_TOKEN})

#admin chat id
admin_id = 0 

#Deploy URL
deploy = "https://"

requests.get(URL_TEL_BOT + "/sendMessage", params={"chat_id": admin_id, "text": "new_deploy"}).json()
requests.get(URL_TEL_BOT + "/setWebhook", params={"url": deploy,
                                                  "allowed_updates": ["message"]})

app = flask.Flask(__name__)

ids = list()

try:
    with open("registry.txt", "r") as data:
        ids = [int(i.strip()) for i in data.readlines()]
except FileNotFoundError:
    ids = [admin_id]


@app.route("/")
def index():
    return "<h1>I'm a Dr. Mavrakis</h1>"


@app.route("/admin/<message>")
def admin(message):
    requests.get(URL_TEL_BOT + "/sendMessage", params={"chat_id": admin_id, "text": message})
    return "200 OK"


@app.route("/payload", methods=["POST"])
def github():
    data = request.json
    admin("GitHub webHook")
    if "action" in data and data["action"] == 'opened':
        for i in ids:
            send(message_format("Nueva issue abierta", data["issue"],json=False), {"id": i})
    analize(data)
    return "200 OK"


@app.route("/telegram", methods=["POST"])
def telegram():
    data = request.json
    if 'message' in data and 'entities' in data['message']:
        if data["message"]["from"]["id"] not in ids:
            with open("registry.txt", "a") as file:
                file.write("{}\n".format(data["message"]["from"]["id"]))
                ids.append(data["message"]["from"]["id"])
        from_data = data['message']['from']
        chat_data = data['message']['chat']
        text = data['message']['text']
        if bool(re.match("\/(get #[0-9]+|post #[0-9]+ \*[\w \n]+|label #[0-9]+ [\w]+|close #[0-9]+)", text)):
            admin("I receive a command")
            regex_match_execute(text,chat_data)
        elif text == "/start":
            template = "Hola soy Void un bot creado para controlarlos a todos.\n" \
                       " El repositorio DrMavrakis4ever es mi mision.\n" \
                       "Los comandos disponibles te los mostrara telegram al escribir /."
            send(template, chat_data)
    return "200 OK"

def regex_match_execute(text, chat_data):
    if re.match("\/(get|close) #[0-9]+", text):
        quarry = text[text.index("#") + 1:].strip()
        if re.match("\/get #[0-9]+", text):
            get_issue(quarry, chat_data)
        elif re.match("\/close #[0-9]+", text):
            close_issue(quarry, chat_data)
    elif re.match("\/label #[0-9]+ [\w]+", text):
        text = text.split(" ")
        label_issue(text[1][1:], text[2], chat_data)
    elif re.match("\/post #[0-9]+ \*[\w \n]+", text):
        text = text.split(" ")
        create_comment(text[1][1:], " ".join(text[2:])[1:], chat_data)
