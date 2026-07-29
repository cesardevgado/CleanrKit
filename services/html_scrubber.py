import html
import re
from html.parser import HTMLParser


SAMPLE_HTML = """<div><h1>Title</h1><p>Hello <strong>world</strong>.</p><!-- draft --><script>alert("x")</script></div>"""

VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class FormattingHTMLParser(HTMLParser):
    def __init__(self, indent_size=2):
        super().__init__(convert_charrefs=False)
        self.indent_size = indent_size
        self.depth = 0
        self.lines = []

    def handle_starttag(self, tag, attrs):
        attr_text = format_attrs(attrs)
        self.lines.append(f"{self.indent()}<{tag}{attr_text}>")
        if tag not in VOID_TAGS:
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        attr_text = format_attrs(attrs)
        self.lines.append(f"{self.indent()}<{tag}{attr_text} />")

    def handle_endtag(self, tag):
        if tag not in VOID_TAGS:
            self.depth = max(self.depth - 1, 0)
        self.lines.append(f"{self.indent()}</{tag}>")

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.lines.append(f"{self.indent()}{text}")

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def handle_comment(self, data):
        self.lines.append(f"{self.indent()}<!--{data}-->")

    def indent(self):
        return " " * (self.depth * self.indent_size)

    def output(self):
        return "\n".join(self.lines).strip()


class PlainTextHTMLParser(HTMLParser):
    BLOCK_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "div",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "tr",
        "ul",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)

    def output(self):
        text = "".join(self.parts)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line).strip()


def format_attrs(attrs):
    if not attrs:
        return ""

    parts = []
    for key, value in attrs:
        if value is None:
            parts.append(key)
        else:
            parts.append(f'{key}="{html.escape(value, quote=True)}"')

    return " " + " ".join(parts)


def format_html_markup(markup, indent_size=2):
    parser = FormattingHTMLParser(indent_size)
    parser.feed(markup)
    return collapse_simple_text_nodes(parser.output())


def collapse_simple_text_nodes(markup):
    pattern = re.compile(
        r"^([ \t]*)<([a-zA-Z][\w:-]*)([^>]*)>\n[ \t]+([^<>\n]+)\n\1</\2>$",
        flags=re.MULTILINE,
    )
    previous = None
    output = markup

    while output != previous:
        previous = output
        output = pattern.sub(r"\1<\2\3>\4</\2>", output)

    return output


def minify_html(markup):
    markup = re.sub(r">\s+<", "><", markup)
    markup = re.sub(r"\s+", " ", markup)
    return markup.strip()


def strip_tags_to_plain_text(markup):
    parser = PlainTextHTMLParser()
    parser.feed(markup)
    return parser.output()


def remove_comments(markup):
    return re.sub(r"(?s)<!--.*?-->", "", markup)


def remove_scripts_and_styles(markup):
    return re.sub(r"(?is)<(script|style)\b.*?>.*?</\1>", "", markup)


def remove_inline_styles(markup):
    return re.sub(r"\sstyle=(\"[^\"]*\"|'[^']*'|[^\s>]+)", "", markup, flags=re.IGNORECASE)


def remove_classes_and_ids(markup):
    markup = re.sub(r"\sclass=(\"[^\"]*\"|'[^']*'|[^\s>]+)", "", markup, flags=re.IGNORECASE)
    return re.sub(r"\sid=(\"[^\"]*\"|'[^']*'|[^\s>]+)", "", markup, flags=re.IGNORECASE)


def remove_empty_elements(markup):
    pattern = re.compile(
        r"<(?!br\b|hr\b|img\b|input\b|meta\b|link\b)([a-zA-Z][\w:-]*)(?:\s[^>]*)?>\s*</\1>",
        flags=re.IGNORECASE,
    )
    previous = None
    output = markup
    while output != previous:
        previous = output
        output = pattern.sub("", output)
    return output


def get_html_statistics(markup):
    tags = re.findall(r"<\s*([a-zA-Z][\w:-]*)\b", markup)
    closing_tags = re.findall(r"</\s*([a-zA-Z][\w:-]*)\s*>", markup)
    comments = len(re.findall(r"(?s)<!--.*?-->", markup))
    scripts = len(re.findall(r"(?is)<script\b", markup))
    styles = len(re.findall(r"(?is)<style\b", markup))
    links = len(re.findall(r"(?is)<a\b", markup))
    images = len(re.findall(r"(?is)<img\b", markup))

    return {
        "characters": len(markup),
        "lines": markup.count("\n") + 1 if markup else 0,
        "elements": len(tags),
        "unique_tags": len(set(tag.lower() for tag in tags)),
        "closing_tags": len(closing_tags),
        "comments": comments,
        "scripts": scripts,
        "styles": styles,
        "links": links,
        "images": images,
    }


def scrub_html(markup, actions, format_mode="format", entity_mode="none", indent_size=2):
    active_actions = set(actions)
    output = markup

    if "removeScriptsStyles" in active_actions:
        output = remove_scripts_and_styles(output)

    if "removeComments" in active_actions:
        output = remove_comments(output)

    if "removeInlineStyles" in active_actions:
        output = remove_inline_styles(output)

    if "removeClassesIds" in active_actions:
        output = remove_classes_and_ids(output)

    if "removeEmptyElements" in active_actions:
        output = remove_empty_elements(output)

    if entity_mode == "decode":
        output = html.unescape(output)
    elif entity_mode == "encode":
        output = html.escape(output, quote=False)

    if "plainText" in active_actions:
        output = strip_tags_to_plain_text(output)
    elif "formatHtml" in active_actions:
        output = minify_html(output) if format_mode == "minify" else format_html_markup(output, indent_size)

    return {
        "output": output,
        "input_statistics": get_html_statistics(markup),
        "output_statistics": get_html_statistics(output),
    }
