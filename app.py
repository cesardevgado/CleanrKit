from flask import Flask, render_template, request, jsonify
from services.formatter import apply_formatting, get_text_statistics

app = Flask(__name__)

SAMPLE_TEXT = """This is a  sample text

with   irregular   spacing,

multiple    spaces, and

line breaks,


and extra blank  lines.
Let's clean this up!"""

DEFAULT_ACTIONS = [
    "removeLineBreaks",
    "replaceLineBreaksWithWhitespace",
    "removeBlankLines",
    "collapseSpaces",
    "trimWhitespace",
]


def get_reduction_statistics(input_text, output_text):
    input_length = len(input_text)
    output_length = len(output_text)
    characters_removed = max(input_length - output_length, 0)
    percent_reduced = (
        round((characters_removed / input_length) * 100) if input_length else 0
    )

    return {
        "characters_removed": characters_removed,
        "percent_reduced": percent_reduced,
    }


@app.route("/")
def home():
    output = apply_formatting(SAMPLE_TEXT, DEFAULT_ACTIONS)

    return render_template(
        "index.html",
        sample_text=SAMPLE_TEXT,
        initial_output=output,
        input_statistics=get_text_statistics(SAMPLE_TEXT),
        output_statistics=get_text_statistics(output),
        reduction_statistics=get_reduction_statistics(SAMPLE_TEXT, output),
    )


@app.route("/format", methods=["POST"])
def format_text():
    data = request.get_json() or {}

    text = data.get("text", "")
    actions = data.get("actions", [])

    output = apply_formatting(text, actions)

    return jsonify(
        {
            "output": output,
            "input_statistics": get_text_statistics(text),
            "output_statistics": get_text_statistics(output),
            "reduction_statistics": get_reduction_statistics(text, output),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
