from flask import Flask, render_template, request, jsonify
from services.formatter import apply_formatting

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/format", methods=["POST"])
def format_text():
    data = request.get_json() or {}

    text = data.get("text", "")
    actions = data.get("actions", [])

    output = apply_formatting(text, actions)

    return jsonify({"output": output})


if __name__ == "__main__":
    app.run(debug=True)
