import re


def remove_line_breaks(text):
    return re.sub(r"\s*\r?\n\s*", " ", text)


def remove_blank_lines(text):
    return re.sub(r"^[ \t]*\r?\n", "", text, flags=re.MULTILINE)


def collapse_multiple_spaces(text):
    return re.sub(r"[ \t]{2,}", " ", text)


def remove_tabs(text):
    return text.replace("\t", "")


def trim_whitespace(text):
    return text.strip()


def remove_leading_spaces(text):
    return re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)


def remove_trailing_spaces(text):
    return re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)


def remove_punctuation(text):
    return re.sub(r"""[!"#$%&'()*+,./:;<=>?@[\]^_`{|}~-]""", "", text)


def remove_numbers(text):
    return re.sub(r"\d+", "", text)


def remove_urls(text):
    return re.sub(r"""\bhttps?://[^\s<>"']+|\bwww\.[^\s<>"']+""", "", text, flags=re.IGNORECASE)


FORMATTERS = {
    "removeUrls": remove_urls,
    "removeTabs": remove_tabs,
    "removeBlankLines": remove_blank_lines,
    "removeLeadingSpaces": remove_leading_spaces,
    "removeTrailingSpaces": remove_trailing_spaces,
    "removeLineBreaks": remove_line_breaks,
    "collapseSpaces": collapse_multiple_spaces,
    "removeNumbers": remove_numbers,
    "removePunctuation": remove_punctuation,
    "trimWhitespace": trim_whitespace,
}


def apply_formatting(text, actions):
    formatted = text or ""

    for action, formatter in FORMATTERS.items():
        if action in actions:
            formatted = formatter(formatted)

    return formatted
