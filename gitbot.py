import re
import flask
import requests

with open("github_token", "r") as file:
    G_TOKEN = file.read().strip()
with open("telegram_token", "r") as file:
    T_TOKEN = file.read().strip()
with open("google_token", "r") as file:
    GOO_TOKEN = file.read().strip()
with open("google_cx", "r") as file:
    GOO_CX = file.read().strip()

#User
git_user = ""
git_repo = ""	

URL_TEL_BOT = "https://api.telegram.org/bot{token}".format(**{"token": T_TOKEN})
URL_GIT = "https://api.github.com/repos/{user}/{repo}/issues/{}".format(**{"user": git_user,"repo": git_repo})
URL_GOO = "https://www.googleapis.com/customsearch/v1"

posted = set()

def analize(response: dict):
    if "action" in response and response["action"] == 'opened':
        if "body" in response['issue'] and re.match("[\S\s]*?`[\S\s]*?`[\S\s]*?", response["issue"]["body"]):
            sender_q = re.search("(Traceback)[^\n]+\n[^\n]+\n[^\n]+\n[^\n]+", response['issue']["body"])
            if sender_q:
                sender_q = sender_q.group().split("\n")[3].strip()
                if sender_q != "":
                    number = response["issue"]["number"]
                    google_response = requests.get(URL_GOO, params={"q": sender_q,
                                                                    "key": GOO_TOKEN,
                                                                    "cx": GOO_CX,
                                                                    "num": 1}).json()
                    if len(google_response["items"]) > 0 and number not in posted:
                        template = "Tal vez puede serte de ayuda:\n{}\n:smile:".format(
                            google_response["items"][0]["link"])
                        posted.add(number)
                        create_comment_git(template, number)
                        return google_response["items"][0]["link"], number
                    else:
                        return "No lo se solucionar", number
                else:
                    return "dude", 0
            else:
                return "mmmmm... usually work", 0
        else:
            return "nobody", 0
    elif "action" in response and response["action"] == "closed" and response["issue"]["number"] in posted:
        if response["issue"]["comments"] < 3:
            posted.remove(response["issue"]["number"])
            label_issue(response["issue"]["number"], "Googleable")
            return "labeled", 0
    else:
        return "problems?", 0


def create_comment_git(message, number):
    requests.post(url=URL_GIT.format(number) + "/comments", params={"access_token": G_TOKEN},
                  json={"body": message})


def label_issue(number, label):
    labels = requests.get(url=URL_GIT.format(number), params={"access_token": G_TOKEN})
    labels = labels.json()['labels']
    labels.append(label)
    req = requests.patch(url=URL_GIT.format(number), params={"access_token": G_TOKEN},
                         data=flask.json.dumps({'labels': labels}))
