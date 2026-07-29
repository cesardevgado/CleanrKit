import json
from collections import Counter

SAMPLE_JSON = """{
  "name": "TextCleanr",
  "version": 1,
  "active": true,
  "description": null,
  "tools": [
    "text",
    "json"
  ],
  "settings": {
    "theme": "dark",
    "theme": "system",
    "autosave": null
  }
}"""


class JsonObject(list):
    pass


def _collect_duplicate_keys(pairs):
    counts = Counter(key for key, _value in pairs)
    duplicates = sum(count - 1 for count in counts.values() if count > 1)
    return duplicates


def parse_json(text):
    duplicate_count = 0

    def object_pairs_hook(pairs):
        nonlocal duplicate_count
        duplicate_count += _collect_duplicate_keys(pairs)
        return JsonObject(pairs)

    value = json.loads(text, object_pairs_hook=object_pairs_hook)
    return value, duplicate_count


def convert_escaped_json(text):
    value, duplicate_keys = parse_json(text)

    while isinstance(value, str):
        candidate = value.strip()
        if not candidate or candidate[0] not in "[{":
            break
        value, nested_duplicate_keys = parse_json(candidate)
        duplicate_keys += nested_duplicate_keys

    return value, duplicate_keys


def remove_null_values(value):
    if isinstance(value, JsonObject):
        return JsonObject(
            (key, remove_null_values(child))
            for key, child in value
            if child is not None
        )

    if isinstance(value, list):
        return [remove_null_values(child) for child in value if child is not None]

    return value


def remove_duplicate_keys(value):
    if isinstance(value, JsonObject):
        seen = set()
        deduped_pairs = []

        for key, child in reversed(value):
            if key in seen:
                continue
            seen.add(key)
            deduped_pairs.append((key, remove_duplicate_keys(child)))

        return JsonObject(reversed(deduped_pairs))

    if isinstance(value, list):
        return [remove_duplicate_keys(child) for child in value]

    return value


def dump_json(value, indent=2, sort_keys=False):
    if indent is None:
        return _dump_minified_json(value, sort_keys)

    return _dump_pretty_json(value, sort_keys, indent, 0)


def _sorted_pairs(value, sort_keys):
    if sort_keys:
        return sorted(value, key=lambda pair: pair[0])

    return list(value)


def _dump_minified_json(value, sort_keys):
    if isinstance(value, JsonObject):
        pairs = _sorted_pairs(value, sort_keys)
        return (
            "{"
            + ",".join(
                f"{json.dumps(key, ensure_ascii=False)}:{_dump_minified_json(child, sort_keys)}"
                for key, child in pairs
            )
            + "}"
        )

    if isinstance(value, list):
        return (
            "["
            + ",".join(_dump_minified_json(child, sort_keys) for child in value)
            + "]"
        )

    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _dump_pretty_json(value, sort_keys, indent, depth):
    if isinstance(value, JsonObject):
        pairs = _sorted_pairs(value, sort_keys)
        if not pairs:
            return "{}"

        current_indent = " " * (indent * depth)
        child_indent = " " * (indent * (depth + 1))
        lines = [
            f"{child_indent}{json.dumps(key, ensure_ascii=False)}: {_dump_pretty_json(child, sort_keys, indent, depth + 1)}"
            for key, child in pairs
        ]
        return "{\n" + ",\n".join(lines) + f"\n{current_indent}" + "}"

    if isinstance(value, list):
        if not value:
            return "[]"

        current_indent = " " * (indent * depth)
        child_indent = " " * (indent * (depth + 1))
        lines = [
            f"{child_indent}{_dump_pretty_json(child, sort_keys, indent, depth + 1)}"
            for child in value
        ]
        return "[\n" + ",\n".join(lines) + f"\n{current_indent}" + "]"

    return json.dumps(value, ensure_ascii=False)


def get_json_statistics(value, duplicate_keys=0):
    statistics = {
        "objects": 0,
        "arrays": 0,
        "keys": 0,
        "strings": 0,
        "numbers": 0,
        "booleans": 0,
        "nulls": 0,
        "nodes": 0,
        "max_depth": 0,
        "duplicate_keys": duplicate_keys,
    }

    def visit(child, depth):
        statistics["nodes"] += 1
        statistics["max_depth"] = max(statistics["max_depth"], depth)

        if isinstance(child, JsonObject):
            statistics["objects"] += 1
            statistics["keys"] += len(child)
            for _key, nested in child:
                visit(nested, depth + 1)
        elif isinstance(child, list):
            statistics["arrays"] += 1
            for nested in child:
                visit(nested, depth + 1)
        elif isinstance(child, str):
            statistics["strings"] += 1
        elif isinstance(child, bool):
            statistics["booleans"] += 1
        elif child is None:
            statistics["nulls"] += 1
        elif isinstance(child, (int, float)):
            statistics["numbers"] += 1

    visit(value, 1)
    return statistics


def scrub_json(text, actions):
    active_actions = set(actions)

    if "convertEscapedJson" in active_actions:
        value, duplicate_keys = convert_escaped_json(text)
    else:
        value, duplicate_keys = parse_json(text)

    if "removeNullValues" in active_actions:
        value = remove_null_values(value)

    if "removeDuplicateKeys" in active_actions:
        value = remove_duplicate_keys(value)

    indent = None if "minifyJson" in active_actions else 2
    output = dump_json(value, indent=indent, sort_keys="sortKeys" in active_actions)

    return {
        "output": output,
        "statistics": get_json_statistics(value, duplicate_keys),
        "duplicate_keys_removed": (
            duplicate_keys if "removeDuplicateKeys" in active_actions else 0
        ),
        "valid": True,
        "error": "",
    }
