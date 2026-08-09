import csv
import json
import xml.etree.ElementTree as ET

from flask import (
    Flask,
    Response,
    abort,
    jsonify,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from services.csv_scrubber import SAMPLE_CSV, scrub_csv
from services.html_scrubber import SAMPLE_HTML, scrub_html
from services.json_scrubber import SAMPLE_JSON, scrub_json
from services.markdown_scrubber import SAMPLE_MARKDOWN, scrub_markdown
from services.sql_scrubber import SAMPLE_SQL, scrub_sql
from services.formatter import apply_formatting, get_text_statistics
from csv_tasks import CSV_TASKS, build_csv_task
from json_tasks import JSON_TASKS, build_json_task
from sql_tasks import SQL_TASKS, build_sql_task
from text_tasks import TEXT_TASKS, build_text_task

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

SITE_PAGES = {
    "about": {
        "title": "About CleanrKit",
        "eyebrow": "Our story",
        "description": "Learn why CleanrKit exists, how its privacy-first browser tools work, and who builds them.",
    },
    "features": {
        "title": "CleanrKit Features",
        "eyebrow": "One kit, focused tools",
        "description": "Explore the privacy-conscious tools and practical features that make everyday text and data cleanup easier.",
    },
    "privacy": {
        "title": "Privacy Policy",
        "eyebrow": "Your data, respected",
        "description": "Learn how CleanrKit handles tool input, analytics, advertising, and other website data.",
    },
    "terms": {
        "title": "Terms of Use",
        "eyebrow": "The ground rules",
        "description": "Review the terms that apply when you access and use CleanrKit and its browser tools.",
    },
    "contact": {
        "title": "Contact",
        "eyebrow": "Let’s talk",
        "description": "Contact CleanrKit with questions, feedback, partnership ideas, or general inquiries.",
    },
    "changelog": {
        "title": "Changelog",
        "eyebrow": "What’s new",
        "description": "Follow new CleanrKit tools, improvements, fixes, and product milestones.",
    },
    "roadmap": {
        "title": "Roadmap",
        "eyebrow": "Where we’re going",
        "description": "See what CleanrKit is exploring, building, and improving during beta.",
    },
    "report-bug": {
        "title": "Report a Bug",
        "eyebrow": "Help us improve",
        "description": "Report a CleanrKit issue with enough detail for us to investigate and fix it.",
    },
}


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


@app.route("/about", endpoint="about")
@app.route("/features", endpoint="features")
@app.route("/privacy", endpoint="privacy")
@app.route("/terms", endpoint="terms")
@app.route("/contact", endpoint="contact")
@app.route("/changelog", endpoint="changelog")
@app.route("/roadmap", endpoint="roadmap")
@app.route("/report-bug", endpoint="report_bug")
def site_page():
    page_key = request.path.strip("/")
    return render_template("site_page.html", page_key=page_key, page=SITE_PAGES[page_key])


@app.route("/sitemap.xml")
def sitemap():
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    urlset = ET.Element(ET.QName(namespace, "urlset"))

    public_rules = sorted(
        (
            rule
            for rule in app.url_map.iter_rules()
            if "GET" in rule.methods
            and not rule.arguments
            and rule.endpoint not in {"sitemap", "static"}
        ),
        key=lambda rule: rule.rule,
    )

    for rule in public_rules:
        url = ET.SubElement(urlset, ET.QName(namespace, "url"))
        location = ET.SubElement(url, ET.QName(namespace, "loc"))
        location.text = url_for(rule.endpoint, _external=True)

    for task_slug in sorted(TEXT_TASKS):
        url = ET.SubElement(urlset, ET.QName(namespace, "url"))
        location = ET.SubElement(url, ET.QName(namespace, "loc"))
        location.text = url_for("text_task", task_slug=task_slug, _external=True)

    for task_slug in sorted(JSON_TASKS):
        url = ET.SubElement(urlset, ET.QName(namespace, "url"))
        location = ET.SubElement(url, ET.QName(namespace, "loc"))
        location.text = url_for("text_task", task_slug=task_slug, _external=True)

    for task_slug in sorted(SQL_TASKS):
        url = ET.SubElement(urlset, ET.QName(namespace, "url"))
        location = ET.SubElement(url, ET.QName(namespace, "loc"))
        location.text = url_for("text_task", task_slug=task_slug, _external=True)

    for task_slug in sorted(CSV_TASKS):
        url = ET.SubElement(urlset, ET.QName(namespace, "url"))
        location = ET.SubElement(url, ET.QName(namespace, "loc"))
        location.text = url_for("text_task", task_slug=task_slug, _external=True)

    document = ET.tostring(urlset, encoding="utf-8", xml_declaration=True)
    return Response(document, mimetype="application/xml")


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


@app.route("/<task_slug>")
def text_task(task_slug):
    if task_slug in TEXT_TASKS:
        task_page = build_text_task(task_slug)
        sample_text = task_page["sample"]
        output = apply_formatting(sample_text, task_page["actions"])

        return render_template(
            "index.html",
            task_page=task_page,
            seo_canonical_url=url_for("text_task", task_slug=task_slug, _external=True),
            sample_text=sample_text,
            initial_output=output,
            input_statistics=get_text_statistics(sample_text),
            output_statistics=get_text_statistics(output),
            reduction_statistics=get_reduction_statistics(sample_text, output),
        )

    if task_slug in JSON_TASKS:
        task_page = build_json_task(task_slug)
        sample_json = task_page["sample"]

        try:
            result = scrub_json(sample_json, task_page["actions"])
            initial_output = result["output"]
            json_statistics = result["statistics"]
            initial_valid = True
            validation_message = "Valid JSON"
        except json.JSONDecodeError as error:
            initial_output = (
                f"Invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}"
            )
            json_statistics = {}
            initial_valid = False
            validation_message = initial_output

        return render_template(
            "jsonscrubber.html",
            task_page=task_page,
            seo_canonical_url=url_for("text_task", task_slug=task_slug, _external=True),
            sample_json=sample_json,
            initial_output=initial_output,
            json_statistics=json_statistics,
            initial_valid=initial_valid,
            validation_message=validation_message,
        )

    if task_slug in SQL_TASKS:
        task_page = build_sql_task(task_slug)
        result = scrub_sql(
            task_page["sample"],
            task_page["actions"],
            keyword_case=task_page["keyword_case"],
            indent_size=task_page["indent_size"],
            format_mode=task_page["format_mode"],
        )

        return render_template(
            "sqlscrubber.html",
            task_page=task_page,
            seo_canonical_url=url_for("text_task", task_slug=task_slug, _external=True),
            sample_sql=task_page["sample"],
            initial_output=result["output"],
            sql_statistics=result["statistics"],
            validation_message=result["validation_message"],
            valid=result["valid"],
        )

    if task_slug in CSV_TASKS:
        task_page = build_csv_task(task_slug)

        try:
            result = scrub_csv(task_page["sample"], task_page["actions"])
            initial_output = result["output"]
            csv_statistics = result["statistics"]
            csv_preview = result["preview"]
            initial_valid = True
            validation_message = "Ready"
        except csv.Error as error:
            initial_output = f"Invalid CSV: {error}"
            csv_statistics = {}
            csv_preview = []
            initial_valid = False
            validation_message = initial_output

        return render_template(
            "csvscrubber.html",
            task_page=task_page,
            seo_canonical_url=url_for("text_task", task_slug=task_slug, _external=True),
            sample_csv=task_page["sample"],
            initial_output=initial_output,
            csv_statistics=csv_statistics,
            csv_preview=csv_preview,
            initial_valid=initial_valid,
            validation_message=validation_message,
        )

    abort(404)


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
