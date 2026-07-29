import re
from html import unescape
from html.parser import HTMLParser


SAMPLE_MARKDOWN = """#  Product Notes

This is a **draft** with _formatting_, [links](https://example.com), and extra spacing.

### Details

-   First item
-   Second item with `inline code`

##  Next Steps

> Review the copy and clean the markdown.
"""


class MarkdownHTMLConverter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.list_stack = []
        self.link_stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag in {"p", "div", "section", "article"}:
            self.parts.append("\n\n")
        elif tag in {"br", "hr"}:
            self.parts.append("\n" if tag == "br" else "\n\n---\n\n")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "code":
            self.parts.append("`")
        elif tag == "pre":
            self.parts.append("\n\n```\n")
        elif tag in {"ul", "ol"}:
            self.list_stack.append({"tag": tag, "index": 1})
            self.parts.append("\n")
        elif tag == "li":
            marker = "- "
            if self.list_stack and self.list_stack[-1]["tag"] == "ol":
                marker = f"{self.list_stack[-1]['index']}. "
                self.list_stack[-1]["index"] += 1
            self.parts.append(f"\n{marker}")
        elif tag == "blockquote":
            self.parts.append("\n\n> ")
        elif tag == "a":
            self.link_stack.append(attrs.get("href", "").strip())
            self.parts.append("[")
        elif tag == "img":
            alt = attrs.get("alt", "").strip()
            src = attrs.get("src", "").strip()
            self.parts.append(f"![{alt}]({src})" if src else alt)
        elif re.fullmatch(r"h[1-6]", tag):
            self.parts.append("\n\n" + "#" * int(tag[1]) + " ")

    def handle_endtag(self, tag):
        if tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "code":
            self.parts.append("`")
        elif tag == "pre":
            self.parts.append("\n```\n\n")
        elif tag in {"ul", "ol"} and self.list_stack:
            self.list_stack.pop()
            self.parts.append("\n")
        elif tag == "a":
            href = self.link_stack.pop() if self.link_stack else ""
            self.parts.append(f"]({href})" if href else "]")
        elif re.fullmatch(r"h[1-6]", tag):
            self.parts.append("\n\n")

    def handle_data(self, data):
        self.parts.append(data)

    def markdown(self):
        return "".join(self.parts)


def clean_markdown(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^([ \t]*[-*+])\s{2,}", r"\1 ", text, flags=re.MULTILINE)
    text = re.sub(r"^([ \t]*\d+\.)\s{2,}", r"\1 ", text, flags=re.MULTILINE)
    return text.strip()


def convert_html_to_markdown(text):
    converter = MarkdownHTMLConverter()
    converter.feed(text)
    return clean_markdown(converter.markdown())


def remove_yaml_front_matter(text):
    return re.sub(r"\A---[ \t]*\n.*?\n---[ \t]*(?:\n|$)", "", text, count=1, flags=re.DOTALL)


def convert_tabs_to_spaces(text):
    return text.replace("\t", "    ")


def remove_trailing_spaces(text):
    return re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)


def remove_html(text):
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", text)
    text = re.sub(r"(?s)<!--.*?-->", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(text)


def normalize_headers(text):
    def replace_header(match):
        level = match.group(1)
        title = re.sub(r"\s+", " ", match.group(2).strip())
        return f"{level} {title}"

    return re.sub(r"^(#{1,6})[ \t]*(.*?)[ \t]*#*[ \t]*$", replace_header, text, flags=re.MULTILINE)


def remove_empty_headings(text):
    return re.sub(r"^\s{0,3}#{1,6}[ \t]*#*[ \t]*(?:\n|$)", "", text, flags=re.MULTILINE)


def cleanup_links(text, mode="label"):
    text = re.sub(
        r"(?<!!)\[([^\]]*)\]\(([^)]*)\)",
        lambda match: _clean_link(match.group(1), match.group(2), mode),
        text,
    )
    text = re.sub(r"(?<!!)\[\s*\]\([^)]*\)", "", text)
    return text


def _clean_link(label, target, mode):
    label = re.sub(r"\s+", " ", label.strip())
    target = target.strip()

    if mode == "url":
        return target or label

    return label or target


def cleanup_images(text, mode="label"):
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]*)\)",
        lambda match: _clean_image(match.group(1), match.group(2), mode),
        text,
    )
    return text


def _clean_image(alt_text, target, mode):
    alt_text = re.sub(r"\s+", " ", alt_text.strip())

    if mode == "remove":
        return ""

    return alt_text


def remove_formatting(text):
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`{1,3}([^`\n]+)`{1,3}", r"\1", text)
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    return text


def markdown_to_plain_text(text):
    text = remove_formatting(text)
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    return clean_markdown(text)


def get_heading_statistics(text):
    counts = {f"h{level}": 0 for level in range(1, 7)}
    headings = re.findall(r"^\s{0,3}(#{1,6})\s+\S.*$", text, flags=re.MULTILINE)

    for heading in headings:
        counts[f"h{len(heading)}"] += 1

    counts["total"] = len(headings)
    return counts


def get_markdown_statistics(text):
    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": text.count("\n") + 1 if text else 0,
        "headings": get_heading_statistics(text),
    }


def scrub_markdown(text, actions, link_cleanup_mode="label", image_cleanup_mode="label"):
    active_actions = set(actions)
    output = text

    if "removeYamlFrontMatter" in active_actions:
        output = remove_yaml_front_matter(output)

    if "htmlToMarkdown" in active_actions:
        output = convert_html_to_markdown(output)
    elif "removeHtml" in active_actions:
        output = remove_html(output)

    if "convertTabsToSpaces" in active_actions:
        output = convert_tabs_to_spaces(output)

    if "removeTrailingSpaces" in active_actions:
        output = remove_trailing_spaces(output)

    if "cleanMarkdown" in active_actions:
        output = clean_markdown(output)

    if "normalizeHeaders" in active_actions:
        output = normalize_headers(output)

    if "removeEmptyHeadings" in active_actions:
        output = remove_empty_headings(output)

    if "linkCleanup" in active_actions:
        output = cleanup_links(output, link_cleanup_mode)

    if "imageCleanup" in active_actions:
        output = cleanup_images(output, image_cleanup_mode)

    if "removeFormatting" in active_actions:
        output = remove_formatting(output)

    if "plainText" in active_actions:
        output = markdown_to_plain_text(output)

    return {
        "output": output,
        "input_statistics": get_markdown_statistics(text),
        "output_statistics": get_markdown_statistics(output),
        "heading_statistics": get_heading_statistics(output),
    }
