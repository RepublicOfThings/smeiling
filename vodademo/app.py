import os
from urllib.parse import urljoin
from werkzeug.routing import Rule
from flask import Flask, render_template, request

PREFIX = os.getenv("SUBPATH", "/")

PROXY_BASE_URL = "https://35.186.244.102/vodademo-proxy/"

CONFIG = {
    "dashboards": {
        'Vodafone': {'app': 'rot_smart_homes_app', 'name': 'smeiling_dashboard_vodafone_demo_v10'}
    }
}


app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path=PREFIX+"/static/")

app.url_rule_class = lambda path, **options: Rule(PREFIX + path, **options)


@app.route("/")
def home():
    return render_template("pages/home/index.html",
                           title="Home", **CONFIG)


@app.route("/about")
def about():
    return render_template("pages/about/index.html",
                           title="About", **CONFIG)


@app.route("/dashboard")
def dashboard():
    id_ = request.args["id_"]
    return render_template("pages/dashboard/index.html",
                           title=f"{id_} Dashboard",
                           target=urljoin(PROXY_BASE_URL, "login" + f"?id_={id_}"),
                           dashboard=id_, **CONFIG)


@app.route("/ping")
def ping():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
