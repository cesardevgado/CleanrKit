from flask import Flask, jsonify, render_template, request

from services.formatter import apply_formatting

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.post("/format")
def format_text():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    actions = payload.get("actions", [])

    if not isinstance(actions, list):
        actions = []

    return jsonify({"output": apply_formatting(text, set(actions))})


if __name__ == "__main__":
    app.run(debug=True)
