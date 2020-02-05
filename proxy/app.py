import os
import uuid
import logging
import requests

from werkzeug.routing import Rule
from flask import Flask, request, Response, redirect, url_for, render_template

logging.basicConfig(level=logging.DEBUG)

SUBPATH = os.getenv("SUBPATH", "/proxy")

SPLUNK_USERNAME = "andrewb"
SPLUNK_PASSWORD = "PkbdAGSdCJa8"
SPLUNK_BASE_URL = "http://37.48.244.187:8000"

app = Flask(__name__)

app.config.update(
    DEBUG=True,
    SECRET_KEY=uuid.uuid4().hex
)


DASHBOARDS = {'Vodafone': {'app': 'qrytical', 'name': 'combo_dashboard'}}
LOGGER = app.logger

app.url_rule_class = lambda path, **options: Rule(SUBPATH + path, **options)

session = requests.Session()


@app.route("/en-US/", defaults={"path": ""})
@app.route("/en-US/<path:path>", methods=("GET",))
def proxy(path: str):

    try:
        # app.logger.debug(path)
        # app.logger.debug(request.args)
        data = session.get(
            f"{SPLUNK_BASE_URL}/en-US/{path}", params=request.args
        ).content
        data = data.decode("utf-8")
        data = data.replace("/en-US", f"{SUBPATH}/en-US")
        if path.endswith("dashboard.js"):
            data = data.replace('make_url("/static/build/pages/enterprise")',
                                f'"{SUBPATH}" + make_url("/static/build/pages/enterprise")')
        elif path.endswith("common.js"):
            data = data.replace('splunkUtil.make_url',
                                f'"{SUBPATH}" + splunkUtil.make_url')

    except UnicodeDecodeError:
        data = session.get(
            f"{SPLUNK_BASE_URL}/en-US/{path}", params=request.args
        ).content

    if path.endswith(".js"):
        return Response(data, mimetype="text/javascript", headers={"content-length": len(data)})
    elif path.endswith(".css"):
        return Response(data, mimetype="text/css", headers={"content-length": len(data)})
    elif path.endswith(".html"):
        return Response(data, mimetype="text/html", headers={"content-length": len(data)})
    elif path.endswith(".png"):
        return Response(data, mimetype="image/png", headers={"content-length": len(data)})
    elif (
        path.endswith(".json")
        or request.args.get("output_mode") == "json"
        or request.args.get("output_mode") == "json_cols"
    ):
        return Response(data, mimetype="text/json", headers={"content-length": len(data)})

    return data


@app.route("/en-US/", defaults={"path": ""})
@app.route("/en-US/<path:path>", methods=("POST",))
def proxy_splunkd(path):

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "X-Splunk-Form-Key": session.cookies["splunkweb_csrf_token_8000"],
        "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    response = session.post(
        f"{SPLUNK_BASE_URL}/en-US/{path}",
        data=request.values.to_dict(),
        verify=False,
        headers=headers,
    )

    return Response(response.content, status=response.status_code)


@app.route("/login")
def login():

    dashboard = DASHBOARDS[request.args["id_"]]

    return_to = f"app/{dashboard['app']}/{dashboard['name']}"

    args = {
        "username": SPLUNK_USERNAME,
        "password": SPLUNK_PASSWORD
    }

    LOGGER.debug("Logging in...")
    response = session.get(f"{SPLUNK_BASE_URL}/en-US/account/insecurelogin", params=args)
    LOGGER.debug("Logged in.")

    if response.status_code == 200:
        LOGGER.debug("Redirecting...")
        return redirect(f"https://localhost:443{SUBPATH}/en-US/{return_to}")
    else:
        return redirect(url_for("error", message=response.content, status=response.status_code))


@app.route("/ping")
def ping():
    return "OK"


@app.route("/error")
def error():
    message = request.args["message"]
    status = request.args["message"]
    return render_template("error.html", message=message, status=status)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
