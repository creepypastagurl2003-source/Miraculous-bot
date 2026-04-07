from flask import Flask
from threading import Thread
import logging
import os

app = Flask(__name__)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


@app.route("/")
def home():
    return "Bot is alive"


def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
