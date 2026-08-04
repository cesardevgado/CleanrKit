JSON_OPERATION_PROFILES = {
    "pretty": {
        "action": "prettyPrintJson",
        "actions": ["prettyPrintJson", "validateJson"],
        "summary": "Turn compact JSON into readable, consistently indented output.",
        "sample": '{"user":{"name":"Ada","active":true},"roles":["admin","editor"]}',
        "examples": [
            ("Expand compact objects", '{"name":"Ada","active":true}', '{↵··"name": "Ada",↵··"active": true↵}'),
            ("Format nested data", '{"user":{"id":7}}', '{↵··"user": {↵····"id": 7↵··}↵}'),
            ("Beautify arrays", '{"tags":["api","json"]}', '{↵··"tags": [↵····"api",↵····"json"↵··]↵}'),
        ],
    },
    "minify": {
        "action": "minifyJson",
        "actions": ["minifyJson", "validateJson"],
        "summary": "Remove unnecessary JSON whitespace and line breaks to produce compact output.",
        "sample": '{\n  "name": "Ada",\n  "active": true,\n  "roles": ["admin", "editor"]\n}',
        "examples": [
            ("Compact objects", '{↵··"name": "Ada"↵}', '{"name":"Ada"}'),
            ("Minify arrays", '[↵··1,↵··2,↵··3↵]', '[1,2,3]'),
            ("Create one-line JSON", '{↵··"ready": true,↵··"count": 2↵}', '{"ready":true,"count":2}'),
        ],
    },
    "validation": {
        "action": "validateJson",
        "actions": ["validateJson", "prettyPrintJson"],
        "summary": "Check JSON syntax and identify errors with clear line and column details.",
        "sample": '{\n  "name": "Ada",\n  "active": true,\n}',
        "examples": [
            ("Find trailing commas", '{"name":"Ada",}', 'Error: trailing comma'),
            ("Detect missing quotes", '{name:"Ada"}', 'Error: property name must be quoted'),
            ("Check unclosed structures", '{"items":[1,2}', 'Error: expected closing bracket'),
        ],
    },
    "escape": {
        "action": "escapeJson",
        "actions": ["escapeJson", "prettyPrintJson", "validateJson"],
        "summary": "Escape quotes, newlines, and special characters so JSON can be embedded as a string.",
        "sample": '{"message":"Hello world","path":"C:\\\\files"}',
        "examples": [
            ("Escape object strings", '{"name":"Ada"}', '"{\\n··\\"name\\": \\"Ada\\"\\n}"'),
            ("Escape quotation marks", '{"quote":"Hello"}', '"{\\"quote\\":\\"Hello\\"}"'),
            ("Prepare embedded JSON", '{"ready":true}', '"{\\"ready\\":true}"'),
        ],
    },
    "unescape": {
        "action": "convertEscapedJson",
        "actions": ["convertEscapedJson", "prettyPrintJson", "validateJson"],
        "summary": "Convert an escaped JSON string back into readable, structured JSON.",
        "sample": '"{\\"name\\":\\"Ada\\",\\"active\\":true}"',
        "examples": [
            ("Decode escaped objects", '"{\\"name\\":\\"Ada\\"}"', '{↵··"name": "Ada"↵}'),
            ("Restore escaped arrays", '"[1,2,3]"', '[↵··1,↵··2,↵··3↵]'),
            ("Read embedded JSON", '"{\\"ready\\":true}"', '{↵··"ready": true↵}'),
        ],
    },
    "sort": {
        "action": "sortKeys",
        "actions": ["sortKeys", "prettyPrintJson", "validateJson"],
        "summary": "Sort JSON object keys alphabetically at every nesting level.",
        "sample": '{"zebra":1,"alpha":2,"middle":{"z":3,"a":4}}',
        "examples": [
            ("Sort object keys", '{"z":1,"a":2}', '{↵··"a": 2,↵··"z": 1↵}'),
            ("Order nested keys", '{"user":{"z":1,"a":2}}', '{"user":{"a":2,"z":1}}'),
            ("Standardize API data", '{"status":true,"id":7}', '{"id":7,"status":true}'),
        ],
    },
    "remove_empty": {
        "action": "removeEmptyValues",
        "actions": ["removeEmptyValues", "prettyPrintJson", "validateJson"],
        "summary": "Recursively remove nulls, empty strings, empty arrays, and empty objects from JSON.",
        "sample": '{"name":"Ada","bio":"","avatar":null,"tags":[],"settings":{},"active":true}',
        "examples": [
            ("Remove null properties", '{"name":"Ada","bio":null}', '{"name":"Ada"}'),
            ("Delete empty strings", '{"name":"Ada","note":""}', '{"name":"Ada"}'),
            ("Clean empty containers", '{"items":[],"settings":{},"ready":true}', '{"ready":true}'),
        ],
    },
}


JSON_TASKS = {
    "format-json": ("Format JSON", "pretty"),
    "pretty-print-json": ("Pretty Print JSON", "pretty"),
    "minify-json": ("Minify JSON", "minify"),
    "validate-json": ("Validate JSON", "validation"),
    "json-formatter": ("JSON Formatter", "pretty"),
    "json-validator": ("JSON Validator", "validation"),
    "json-beautifier": ("JSON Beautifier", "pretty"),
    "escape-json": ("Escape JSON", "escape"),
    "unescape-json": ("Unescape JSON", "unescape"),
    "sort-json-keys": ("Sort JSON Keys", "sort"),
    "remove-empty-json-values": ("Remove Empty JSON Values", "remove_empty"),
    "compact-json": ("Compact JSON", "minify"),
    "convert-json-to-one-line": ("Convert JSON to One Line", "minify"),
    "fix-invalid-json": ("Fix Invalid JSON", "validation"),
}


def build_json_task(slug):
    title, profile_name = JSON_TASKS[slug]
    profile = JSON_OPERATION_PROFILES[profile_name]
    examples = [
        {"title": heading, "before": before, "after": after, "copy": f"Use {title} to {heading.lower()} and review the result immediately."}
        for heading, before, after in profile["examples"]
    ]

    return {
        **profile,
        "slug": slug,
        "title": title,
        "seo_title": f"{title} Online Free | CleanrKit",
        "seo_description": f"{profile['summary']} Use this free online {title.lower()} tool with instant JSON validation and output.",
        "intro_title": f"{title} online",
        "intro_copy": f"{profile['summary']} Paste your JSON below to validate it and generate the configured output instantly.",
        "examples": examples,
        "features": [
            {"title": f"Focused {title.lower()}", "copy": f"The page opens with the {title.lower()} operation already configured."},
            {"title": "Built-in JSON validation", "copy": "See syntax feedback with line and column details whenever the input is invalid."},
            {"title": "Advanced JSONCleanr options", "copy": "Open Advanced Options to combine formatting, sorting, and cleanup controls."},
        ],
        "steps": [
            {"title": "Paste your JSON", "copy": "Add an object, array, API response, or escaped JSON string to the Input field."},
            {"title": f"Run {title}", "copy": "Use the blue arrow or edit the input to update validation and output."},
            {"title": "Copy or download", "copy": "Review the result, then copy it or save it as a JSON file."},
        ],
        "faqs": [
            {"question": f"What does {title} do?", "answer": profile["summary"]},
            {"question": "Does this tool validate JSON syntax?", "answer": "Yes. Every request is parsed as JSON, and invalid input returns a specific syntax message."},
            {"question": "Can I use other JSON cleanup options?", "answer": "Yes. Open Advanced Options or visit the full JSONCleanr tool to combine more operations."},
        ],
    }
