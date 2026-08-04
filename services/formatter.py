import re
import string
import unicodedata
from html.parser import HTMLParser


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


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


def normalize_unicode(text):
    return unicodedata.normalize("NFKC", text)


def normalize_non_ascii(text):
    decomposed_text = unicodedata.normalize("NFKD", text)
    return "".join(
        character
        for character in decomposed_text
        if not unicodedata.combining(character)
    )


def remove_non_ascii(text):
    return re.sub(r"[^\x00-\x7F]+", "", text)


def remove_smart_quotes(text):
    return text.translate(
        str.maketrans(
            {
                "“": '"',
                "”": '"',
                "‘": "'",
                "’": "'",
            }
        )
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


def remove_duplicate_lines(text):
    seen = set()
    unique_lines = []

    for line in text.splitlines(keepends=True):
        comparable_line = line.rstrip("\r\n")
        if comparable_line not in seen:
            seen.add(comparable_line)
            unique_lines.append(line)

    return "".join(unique_lines)


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


def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F1E6-\U0001F1FF"
        "\U0001F300-\U0001FAFF"
        "\u2600-\u27BF"
        "]+",
        flags=re.UNICODE,
    )
    cleaned_text = emoji_pattern.sub("", text)
    return cleaned_text.replace("\ufe0f", "").replace("\u200d", "")


def strip_html(text):
    extractor = _TextExtractor()
    extractor.feed(text)
    extractor.close()
    return "".join(extractor.parts)


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
        "removeSmartQuotes": remove_smart_quotes,
        "normalizeUnicode": normalize_unicode,
        "normalizeNonAscii": normalize_non_ascii,
        "removeNonAscii": remove_non_ascii,
        "removeBlankLines": remove_blank_lines,
        "removeDuplicateLines": remove_duplicate_lines,
        "removeLeadingSpaces": remove_leading_spaces,
        "removeTrailingSpaces": remove_trailing_spaces,
        "collapseSpaces": collapse_spaces,
        "removeNumbers": remove_numbers,
        "removePunctuation": remove_punctuation,
        "removeEmojis": remove_emojis,
        "stripHtml": strip_html,
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
