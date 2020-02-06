import os
import uuid
import logging
import requests
from urllib.parse import urljoin
from werkzeug.routing import Rule
from flask import Flask, render_template, request, abort, redirect, url_for, Response
from flask_login import LoginManager, login_user, login_required, logout_user

from utils import get_user

logging.basicConfig(level=logging.DEBUG)

PREFIX = os.getenv("SUBPATH", "/")

PROXY_BASE_URL = "https://localhost/vodademo-proxy/"

STATIC_PATH = PREFIX+"/static/"

CONFIG = {
    "dashboards": {
        'Vodafone': {
            'app': 'rot_smart_homes_app',
            'name': 'smeiling_dashboard_vodafone_demo_v10'
        }
    }
}


stylesheet = "content/republic.css"


images = {
    "smeiling": "img/logos/smeiling.png",
    "republic": "img/logos/republic.png",
    "partner": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Yin_and_yang.svg/600px-Yin_and_yang.svg.png"
}

# https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Yin_and_yang.svg/600px-Yin_and_yang.svg.png


app = Flask(__name__,
            template_folder="templates",
            static_folder="static",
            static_url_path=STATIC_PATH)

app.config.update(
    DEBUG=False,
    SECRET_KEY=uuid.uuid4().hex
)


app.url_rule_class = lambda path, **options: Rule(PREFIX + path, **options)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.route("/")
@login_required
def home():
    return render_template("pages/home/index.html",
                           title="Home", **CONFIG)


@app.route("/about")
@login_required
def about():
    return render_template("pages/about/index.html",
                           title="About", **CONFIG)


@app.route("/dashboard")
@login_required
def dashboard():
    id_ = request.args["id_"]
    return render_template("pages/dashboard/index.html",
                           title=f"{id_} Dashboard",
                           target=urljoin(PROXY_BASE_URL, "login" + f"?id_={id_}"),
                           dashboard=id_, **CONFIG)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user(username)

        if user is not None and user.password == password:
            login_user(user)
            return redirect(request.args.get("next", PREFIX))
        else:
            return abort(401)
    else:
        return render_template("pages/login/index.html", title="Login", **CONFIG)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/content/<string:variant>")
def content(variant):

    if variant in images:
        path = images[variant]
    elif variant == "stylesheet":
        path = stylesheet
    else:
        raise ValueError(f"Unknown variant '{variant}'.")

    if path.startswith("http"):
        response = requests.get(path)
        if response.ok:
            return response.content
        else:
            return Response(response.content, status=response.status_code)
    else:
        with open(os.path.join("static", path), "rb") as file:
            app.logger.debug(f"{os.path.join('static', path)}'")
            return Response(file.read(), status=200)


@app.errorhandler(401)
def page_not_found(e):
    return render_template("pages/login/index.html", title="Ooops", e=e, **CONFIG)


@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)


@app.route("/ping")
def ping():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
