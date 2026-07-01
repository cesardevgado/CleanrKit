import re
import string


def remove_urls(text):
    return re.sub(
        r"\bhttps?://[^\s<>\"']+|\bwww\.[^\s<>\"']+", "", text, flags=re.IGNORECASE
    )


def remove_tabs(text):
    return text.replace("\t", "")


def remove_blank_lines(text):
    return re.sub(r"^[ \t]*\r?\n", "", text, flags=re.MULTILINE)


def remove_leading_spaces(text):
    return re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)


def remove_trailing_spaces(text):
    return re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)


def remove_line_breaks(text):
    return re.sub(r"\s*\r?\n\s*", " ", text)


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
    operation_map = {
        "removeUrls": remove_urls,
        "removeTabs": remove_tabs,
        "removeBlankLines": remove_blank_lines,
        "removeLeadingSpaces": remove_leading_spaces,
        "removeTrailingSpaces": remove_trailing_spaces,
        "removeLineBreaks": remove_line_breaks,
        "collapseSpaces": collapse_spaces,
        "removeNumbers": remove_numbers,
        "removePunctuation": remove_punctuation,
        "trimWhitespace": trim_whitespace,
    }

    for action in actions:
        formatter = operation_map.get(action)

        if formatter:
            text = formatter(text)

    return text
