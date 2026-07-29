import csv
import json

from flask import Flask, render_template, request, jsonify, send_from_directory
from services.csv_scrubber import SAMPLE_CSV, scrub_csv
from services.html_scrubber import SAMPLE_HTML, scrub_html
from services.json_scrubber import SAMPLE_JSON, scrub_json
from services.markdown_scrubber import SAMPLE_MARKDOWN, scrub_markdown
from services.sql_scrubber import SAMPLE_SQL, scrub_sql
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
    return render_template("home.html")


@app.route("/template-img/<path:filename>")
def template_image(filename):
    return send_from_directory("templates/img", filename)


@app.route("/text")
def text_scrubber():
    output = apply_formatting(SAMPLE_TEXT, DEFAULT_ACTIONS)

    return render_template(
        "index.html",
        sample_text=SAMPLE_TEXT,
        initial_output=output,
        input_statistics=get_text_statistics(SAMPLE_TEXT),
        output_statistics=get_text_statistics(output),
        reduction_statistics=get_reduction_statistics(SAMPLE_TEXT, output),
    )


@app.route("/json")
def json_scrubber():
    result = scrub_json(SAMPLE_JSON, ["prettyPrintJson", "sortKeys", "removeDuplicateKeys"])

    return render_template(
        "jsonscrubber.html",
        sample_json=SAMPLE_JSON,
        initial_output=result["output"],
        json_statistics=result["statistics"],
    )


@app.route("/csv")
def csv_scrubber():
    result = scrub_csv(
        SAMPLE_CSV,
        ["trimCells", "normalizeHeaders", "removeEmptyRows", "removeDuplicateRows"],
    )

    return render_template(
        "csvscrubber.html",
        sample_csv=SAMPLE_CSV,
        initial_output=result["output"],
        csv_statistics=result["statistics"],
        csv_preview=result["preview"],
    )


@app.route("/markdown")
def markdown_scrubber():
    result = scrub_markdown(
        SAMPLE_MARKDOWN,
        ["cleanMarkdown", "normalizeHeaders"],
    )

    return render_template(
        "markdownscrubber.html",
        sample_markdown=SAMPLE_MARKDOWN,
        initial_output=result["output"],
        input_statistics=result["input_statistics"],
        output_statistics=result["output_statistics"],
        heading_statistics=result["heading_statistics"],
    )


@app.route("/sql")
def sql_scrubber():
    result = scrub_sql(
        SAMPLE_SQL,
        ["formatSql", "normalizeWhitespace"],
        keyword_case="upper",
        indent_size=4,
        format_mode="expanded",
    )

    return render_template(
        "sqlscrubber.html",
        sample_sql=SAMPLE_SQL,
        initial_output=result["output"],
        sql_statistics=result["statistics"],
        validation_message=result["validation_message"],
        valid=result["valid"],
    )


@app.route("/html")
def html_scrubber():
    result = scrub_html(
        SAMPLE_HTML,
        ["formatHtml", "removeComments", "removeScriptsStyles"],
        format_mode="format",
        entity_mode="none",
        indent_size=2,
    )

    return render_template(
        "htmlscrubber.html",
        sample_html=SAMPLE_HTML,
        initial_output=result["output"],
        input_statistics=result["input_statistics"],
        output_statistics=result["output_statistics"],
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


@app.route("/json/format", methods=["POST"])
def format_json():
    data = request.get_json() or {}
    text = data.get("text", "")
    actions = data.get("actions", [])

    try:
        result = scrub_json(text, actions)
    except json.JSONDecodeError as error:
        return jsonify(
            {
                "output": "",
                "statistics": {},
                "valid": False,
                "error": f"Invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}",
                "error_line": error.lineno,
                "error_column": error.colno,
            }
        )
    except TypeError as error:
        return jsonify(
            {
                "output": "",
                "statistics": {},
                "valid": False,
                "error": f"Invalid JSON: {error}",
                "error_line": None,
                "error_column": None,
            }
        )

    return jsonify(result)


@app.route("/csv/format", methods=["POST"])
def format_csv():
    data = request.get_json() or {}
    text = data.get("text", "")
    actions = data.get("actions", [])
    null_replacement = data.get("nullReplacement", "")

    try:
        result = scrub_csv(text, actions, null_replacement)
    except csv.Error as error:
        return jsonify(
            {
                "output": "",
                "statistics": {},
                "preview": [],
                "valid": False,
                "error": f"Invalid CSV: {error}",
            }
        )

    return jsonify(result)


@app.route("/markdown/format", methods=["POST"])
def format_markdown():
    data = request.get_json() or {}
    text = data.get("text", "")
    actions = data.get("actions", [])
    link_cleanup_mode = data.get("linkCleanupMode", "label")
    image_cleanup_mode = data.get("imageCleanupMode", "label")

    return jsonify(scrub_markdown(text, actions, link_cleanup_mode, image_cleanup_mode))


@app.route("/sql/format", methods=["POST"])
def format_sql():
    data = request.get_json() or {}
    text = data.get("text", "")
    actions = data.get("actions", [])
    keyword_case = data.get("keywordCase", "upper")
    indent_size = int(data.get("indentSize", 4))
    format_mode = data.get("formatMode", "expanded")

    return jsonify(scrub_sql(text, actions, keyword_case, indent_size, format_mode))


@app.route("/html/format", methods=["POST"])
def format_html():
    data = request.get_json() or {}
    text = data.get("text", "")
    actions = data.get("actions", [])
    format_mode = data.get("formatMode", "format")
    entity_mode = data.get("entityMode", "none")
    indent_size = int(data.get("indentSize", 2))

    return jsonify(scrub_html(text, actions, format_mode, entity_mode, indent_size))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
