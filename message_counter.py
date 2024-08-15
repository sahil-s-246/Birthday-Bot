import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, jsonify
import json
from dotenv import load_dotenv
load_dotenv()

# Initializes your app with your bot token and socket mode handler
app = App(
    token=os.getenv("SLACK_BOT_TOK"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET") # not required for socket mode
)
status="Incomplete"
with open("count.json", "r") as f:
    new = dict(json.load(f))
checker = [i for i in list(new.values()) if i == True]
status = "Incomplete" if len(checker) != len(new) else "Complete"
# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )
@app.message(r'^(sa|sb|sc|sd|ta|tb|tc|td)$')
def update_status(message, say):
    # say() sends a message to the channel where the event was triggered
    t = list(message["text"].upper())
    t.insert(1,"E-") #ta to TE-A
    div = "".join(t)
    if new[div] is not True:
        new[div] = True

    if status == "Complete":
        ans = {i: False for i in list(new.keys())}
    else:
        ans = new
    with open('count.json', 'w+') as json_file:
        json.dump(ans, json_file, indent=4)
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Message shared:*\n```{ans}```\n\n*Status:*\n{status}"
                }
            }
        ],
        text=f"Message shared: {ans}\nStatus: {status}"  # Fallback text for notifications
    )


@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")

@app.command("/check")
def get_status(ack, say, command):
    # Acknowledge command request
    ack()
    say(f"Status:\n\n{new}\n\n{status}")

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


# Start your app
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)
if __name__ == "__main__":
#     SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
    flask_app.run(port=5000,host="localhost")