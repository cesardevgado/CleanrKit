import re
import string


def get_text_statistics(text):
    num_characters = len(text)
    num_words = len(text.split())
    num_lines = text.count("\n") + 1 if text else 0

    return {
        "num_characters": num_characters,
        "num_words": num_words,
        "num_lines": num_lines,
    }


def remove_urls(text):
    return re.sub(
        r"\bhttps?://[^\s<>\"']+|\bwww\.[^\s<>\"']+", "", text, flags=re.IGNORECASE
    )


def replace_tabs(text, actions):
    if "replaceTabsWithComma" in actions and "replaceTabsWithWhitespace" in actions:
        replacement = ", "
    elif "replaceTabsWithComma" in actions:
        replacement = ","
    elif "replaceTabsWithWhitespace" in actions:
        replacement = " "
    else:
        replacement = ""

    return text.replace("\t", replacement)


def replace_line_breaks(text, actions):
    if (
        "replaceLineBreaksWithComma" in actions
        and "replaceLineBreaksWithWhitespace" in actions
    ):
        replacement = ", "
    elif "replaceLineBreaksWithComma" in actions:
        replacement = ","
    elif "replaceLineBreaksWithWhitespace" in actions:
        replacement = " "
    else:
        replacement = ""

    return re.sub(r"\s*\r?\n\s*", replacement, text)


def remove_blank_lines(text):
    return re.sub(r"^[ \t]*\r?\n", "", text, flags=re.MULTILINE)


def remove_leading_spaces(text):
    return re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)


def remove_trailing_spaces(text):
    return re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)


def collapse_spaces(text):
    return re.sub(r"[ \t]{2,}", " ", text)


def remove_numbers(text):
    return re.sub(r"\d+", "", text)


def remove_punctuation(text):
    punctuation_pattern = f"[{re.escape(string.punctuation)}]"
    return re.sub(punctuation_pattern, "", text)


def trim_whitespace(text):
    return text.strip()


def apply_formatting(text, actions):
    line_break_actions = {
        "removeLineBreaks",
        "replaceLineBreaksWithWhitespace",
        "replaceLineBreaksWithComma",
    }
    tab_actions = {
        "removeTabs",
        "replaceTabsWithWhitespace",
        "replaceTabsWithComma",
    }
    operation_map = {
        "removeUrls": remove_urls,
        "removeBlankLines": remove_blank_lines,
        "removeLeadingSpaces": remove_leading_spaces,
        "removeTrailingSpaces": remove_trailing_spaces,
        "collapseSpaces": collapse_spaces,
        "removeNumbers": remove_numbers,
        "removePunctuation": remove_punctuation,
        "trimWhitespace": trim_whitespace,
    }

    line_breaks_handled = False
    tabs_handled = False

    for action in actions:
        if action in line_break_actions:
            if not line_breaks_handled:
                text = replace_line_breaks(text, actions)
                line_breaks_handled = True
            continue

        if action in tab_actions:
            if not tabs_handled:
                text = replace_tabs(text, actions)
                tabs_handled = True
            continue

        formatter = operation_map.get(action)

        if formatter:
            text = formatter(text)

    return text
