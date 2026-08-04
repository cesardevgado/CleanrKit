TEXT_TASKS = {
    "remove-line-breaks": {
        "title": "Remove Line Breaks",
        "action": "removeLineBreaks",
        "actions": ["removeLineBreaks", "replaceLineBreaksWithWhitespace"],
        "summary": "Turn multiline text into a clean continuous paragraph without manually joining every line.",
        "sample": "A sentence split\nacross several\nlines becomes one paragraph.",
        "examples": [
            ("Join wrapped text", "A sentence↵split across lines", "A sentence split across lines"),
            ("Clean copied PDFs", "First line↵second line↵third line", "First line second line third line"),
            ("Flatten address lists", "New York↵Boston↵Chicago", "New York Boston Chicago"),
        ],
    },
    "remove-blank-lines": {
        "title": "Remove Blank Lines",
        "action": "removeBlankLines",
        "actions": ["removeBlankLines"],
        "summary": "Delete empty lines while preserving the text and meaningful line breaks around them.",
        "sample": "First paragraph\n\n\nSecond paragraph\n\nThird paragraph",
        "examples": [
            ("Tighten notes", "First note↵↵Second note", "First note↵Second note"),
            ("Clean pasted lists", "Apples↵↵↵Oranges", "Apples↵Oranges"),
            ("Fix document spacing", "Heading↵↵↵Body copy", "Heading↵Body copy"),
        ],
    },
    "remove-duplicate-lines": {
        "title": "Remove Duplicate Lines",
        "action": "removeDuplicateLines",
        "actions": ["removeDuplicateLines"],
        "summary": "Keep the first occurrence of each line and remove repeated lines from lists, logs, or pasted data.",
        "sample": "alpha\nbeta\nalpha\ngamma\nbeta",
        "examples": [
            ("Deduplicate lists", "alpha↵beta↵alpha", "alpha↵beta"),
            ("Clean repeated tags", "design↵code↵design", "design↵code"),
            ("Remove repeated IDs", "A-12↵B-07↵A-12", "A-12↵B-07"),
        ],
    },
    "remove-extra-spaces": {
        "title": "Remove Extra Spaces",
        "action": "collapseSpaces",
        "actions": ["collapseSpaces"],
        "summary": "Collapse repeated spaces and tabs into consistent single spaces without changing line structure.",
        "sample": "This    sentence has      too many spaces.",
        "examples": [
            ("Fix sentence spacing", "Hello····world", "Hello world"),
            ("Clean table text", "Name⇥··Role", "Name Role"),
            ("Normalize pasted copy", "Fast···private···tools", "Fast private tools"),
        ],
    },
    "remove-tabs": {
        "title": "Remove Tabs",
        "action": "removeTabs",
        "actions": ["removeTabs"],
        "summary": "Delete tab characters from copied text, code output, and tab-delimited content in one step.",
        "sample": "Name\tRole\nAda\tEngineer\nLinus\tDeveloper",
        "examples": [
            ("Clean tabbed text", "Name⇥Role", "NameRole"),
            ("Fix copied columns", "Ada⇥Engineer", "AdaEngineer"),
            ("Remove indentation tabs", "⇥Indented line", "Indented line"),
        ],
    },
    "remove-urls": {
        "title": "Remove URLs",
        "action": "removeUrls",
        "actions": ["removeUrls"],
        "summary": "Strip HTTP, HTTPS, and www links from text while keeping the surrounding words intact.",
        "sample": "Visit https://cleanrkit.com for tools or see www.example.com today.",
        "examples": [
            ("Remove inline links", "Visit https://example.com today", "Visit  today"),
            ("Clean social copy", "More at www.example.com", "More at"),
            ("Strip reference URLs", "Source: https://example.com/report", "Source:"),
        ],
    },
    "remove-numbers": {
        "title": "Remove Numbers",
        "action": "removeNumbers",
        "actions": ["removeNumbers"],
        "summary": "Remove digits from names, labels, notes, and mixed text while leaving letters and punctuation unchanged.",
        "sample": "Order 123 contains 4 items and ships in 2 days.",
        "examples": [
            ("Clean product labels", "Model 2026 Pro", "Model  Pro"),
            ("Remove quantities", "Buy 3 items", "Buy  items"),
            ("Strip numbered text", "Step 1: Start", "Step : Start"),
        ],
    },
    "remove-punctuation": {
        "title": "Remove Punctuation",
        "action": "removePunctuation",
        "actions": ["removePunctuation"],
        "summary": "Delete common punctuation marks from text for matching, analysis, or simplified plain-text output.",
        "sample": "Hello, world! Is everything ready? Yes—it is.",
        "examples": [
            ("Simplify sentences", "Hello, world!", "Hello world"),
            ("Clean search terms", "fast, free & private", "fast free  private"),
            ("Prepare text analysis", "What's new?", "Whats new"),
        ],
    },
    "normalize-unicode": {
        "title": "Normalize Unicode",
        "action": "normalizeUnicode",
        "actions": ["normalizeUnicode"],
        "summary": "Convert visually equivalent Unicode characters into a consistent compatibility-normalized form.",
        "sample": "Full-width text: ＡＢＣ１２３ and ligature: ﬁ",
        "examples": [
            ("Convert full-width text", "ＡＢＣ１２３", "ABC123"),
            ("Normalize ligatures", "ﬁle and ﬂow", "file and flow"),
            ("Standardize symbols", "① ② ③", "1 2 3"),
        ],
    },
    "remove-emojis": {
        "title": "Remove Emojis",
        "action": "removeEmojis",
        "actions": ["removeEmojis"],
        "summary": "Remove emoji characters and presentation marks while preserving the surrounding plain text.",
        "sample": "Great work! 🎉 The launch is ready 🚀 and approved ✅",
        "examples": [
            ("Clean social text", "Big news 🎉 today", "Big news  today"),
            ("Remove status icons", "Approved ✅ Complete", "Approved  Complete"),
            ("Simplify messages", "Hello 👋 team", "Hello  team"),
        ],
    },
    "strip-html": {
        "title": "Strip HTML",
        "action": "stripHtml",
        "actions": ["stripHtml"],
        "summary": "Remove HTML tags from snippets or documents and keep the readable text content behind them.",
        "sample": "<h1>Welcome</h1><p>This is <strong>clean</strong> text.</p>",
        "examples": [
            ("Remove formatting tags", "<strong>Bold text</strong>", "Bold text"),
            ("Extract paragraph text", "<p>Hello <em>world</em></p>", "Hello world"),
            ("Clean linked copy", "<a href=\"/\">Home</a>", "Home"),
        ],
    },
    "remove-non-ascii-characters": {
        "title": "Remove Non-ASCII Characters",
        "action": "removeNonAscii",
        "actions": ["removeNonAscii"],
        "summary": "Delete characters outside the ASCII range for systems that require basic English letters, numbers, and symbols.",
        "sample": "Café résumé — 東京 © 2026",
        "examples": [
            ("Clean legacy-system input", "Café résumé", "Caf rsum"),
            ("Remove special symbols", "Price © 2026", "Price  2026"),
            ("Restrict mixed scripts", "Hello 東京", "Hello"),
        ],
    },
}


def build_text_task(slug):
    spec = TEXT_TASKS[slug]
    title = spec["title"]
    examples = [
        {"title": heading, "before": before, "after": after, "copy": f"Use {title} to {heading.lower()} instantly."}
        for heading, before, after in spec["examples"]
    ]

    return {
        **spec,
        "slug": slug,
        "seo_title": f"{title} Online Free | CleanrKit",
        "seo_description": f"{spec['summary']} Use this free online {title.lower()} tool with instant before-and-after results.",
        "intro_title": f"{title} online",
        "intro_copy": f"{spec['summary']} Paste your content below and get an instant cleaned result.",
        "examples": examples,
        "features": [
            {"title": f"Focused {title.lower()}", "copy": f"The page opens with only the {title.lower()} action selected."},
            {"title": "Instant before and after", "copy": "Compare input and output statistics as your content is cleaned."},
            {"title": "Advanced TextCleanr options", "copy": "Open Advanced Options when you need additional cleanup controls."},
        ],
        "steps": [
            {"title": "Paste your content", "copy": "Add the text you want to clean to the Input field."},
            {"title": f"Run {title}", "copy": "Use the blue arrow or edit the text to generate an updated result."},
            {"title": "Copy or download", "copy": "Review the output, then copy it or save it as a text file."},
        ],
        "faqs": [
            {"question": f"What does {title} do?", "answer": spec["summary"]},
            {"question": "Can I combine this with other cleanup options?", "answer": "Yes. Open Advanced Options to enable any of the additional TextCleanr actions."},
            {"question": "Can I copy or download the result?", "answer": "Yes. Use the output controls to copy the cleaned text or download it as a .txt file."},
        ],
    }
