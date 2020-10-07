import json
from flask import Flask, request, render_template, Response
import traceback
from worker import start_scraper

import time
from time import sleep
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

app = Flask(__name__)


@app.route("/get_comment", methods=["GET"])
def dashboard():
    data_dict = start_scraper(741583832)

    def generate():
        for data in data_dict:
            time.sleep(1)
            yield json.dumps(data, indent=4, default=str)

    env = Environment(loader=FileSystemLoader("templates"))
    tmpl = env.get_template("home.html")
    return Response(tmpl.generate(result=generate()), content_type="application/json")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
