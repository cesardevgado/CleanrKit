CSV_OPERATION_PROFILES = {
    "pretty": {
        "action": "prettyFormatCsv",
        "actions": ["prettyFormatCsv"],
        "summary": "Parse and rewrite CSV into consistent rows, delimiters, quoting, and line endings.",
        "sample": 'name,email,note\nAda,ada@example.com,"Hello, world"\nLinus,linus@example.com,Ready',
        "examples": [
            ("Format quoted values", 'name,note↵Ada,"Hello, world"', 'name,note↵Ada,"Hello, world"'),
            ("Standardize line endings", "name,role↵Ada,Engineer", "name,role↵Ada,Engineer"),
            ("Preserve embedded commas", 'city,note↵Paris,"France, EU"', 'city,note↵Paris,"France, EU"'),
        ],
    },
    "standard_cleanup": {
        "action": "standardCleanup",
        "actions": ["standardCleanup"],
        "summary": "Apply the recommended CSV cleanup by trimming cells, normalizing headers, and removing blank and duplicate rows.",
        "sample": "First Name, Email Address\n Ada , ada@example.com \n\nAda,ada@example.com\nLinus,linus@example.com",
        "examples": [
            ("Clean messy exports", "Name , Email ↵ Ada , a@example.com ", "name,email↵Ada,a@example.com"),
            ("Remove blank records", "name,email↵↵Ada,a@example.com", "name,email↵Ada,a@example.com"),
            ("Deduplicate rows", "name↵Ada↵Ada", "name↵Ada"),
        ],
    },
    "empty_rows": {
        "action": "removeEmptyRows",
        "actions": ["removeEmptyRows"],
        "summary": "Delete CSV rows whose cells are all empty while preserving populated records and the header.",
        "sample": "name,email\nAda,ada@example.com\n,\n,\nLinus,linus@example.com",
        "examples": [
            ("Remove blank records", "name,email↵,↵Ada,a@example.com", "name,email↵Ada,a@example.com"),
            ("Tighten exports", "id,status↵1,active↵,↵2,active", "id,status↵1,active↵2,active"),
            ("Clean spacer rows", "item,price↵↵Book,10", "item,price↵Book,10"),
        ],
    },
    "deduplicate": {
        "action": "removeDuplicateRows",
        "actions": ["removeDuplicateRows"],
        "summary": "Keep the first occurrence of each CSV record and remove subsequent duplicate rows.",
        "sample": "name,email\nAda,ada@example.com\nLinus,linus@example.com\nAda,ada@example.com",
        "examples": [
            ("Remove repeated contacts", "name↵Ada↵Ada", "name↵Ada"),
            ("Deduplicate IDs", "id,status↵7,active↵7,active", "id,status↵7,active"),
            ("Clean repeated exports", "item,price↵Book,10↵Book,10", "item,price↵Book,10"),
        ],
    },
    "sort": {
        "action": "sortRows",
        "actions": ["sortRows"],
        "summary": "Sort CSV data rows alphabetically while keeping the header fixed at the top.",
        "sample": "name,role\nZara,Designer\nAda,Engineer\nLinus,Developer",
        "examples": [
            ("Sort names", "name↵Zara↵Ada", "name↵Ada↵Zara"),
            ("Order identifiers", "id,status↵B2,open↵A1,closed", "id,status↵A1,closed↵B2,open"),
            ("Sort product rows", "item,price↵Table,50↵Chair,20", "item,price↵Chair,20↵Table,50"),
        ],
    },
    "trim": {
        "action": "trimCells",
        "actions": ["trimCells"],
        "summary": "Remove leading and trailing whitespace from every CSV cell without changing its internal text.",
        "sample": "name, role, city\n Ada , Engineer , London \n Linus, Developer , Helsinki ",
        "examples": [
            ("Trim names", "name,role↵·Ada·,Engineer", "name,role↵Ada,Engineer"),
            ("Clean padded cells", "city,country↵·Paris·,·France·", "city,country↵Paris,France"),
            ("Fix spreadsheet spacing", "item,price↵Book·,·10", "item,price↵Book,10"),
        ],
    },
    "standardize": {
        "action": "standardizeCsv",
        "actions": ["standardizeCsv"],
        "summary": "Standardize CSV cell whitespace and convert headers into consistent machine-friendly names.",
        "sample": "First Name,EMAIL Address, Last Login\n Ada , ada@example.com , 2026-08-01 ",
        "examples": [
            ("Normalize headers", "First Name,EMAIL Address", "first_name,email_address"),
            ("Trim and standardize", "Product Name, Price ↵ Book , 10 ", "product_name,price↵Book,10"),
            ("Fix duplicate headers", "Name,Name↵Ada,Lovelace", "name,name_2↵Ada,Lovelace"),
        ],
    },
    "validation": {
        "action": "validateCsv",
        "actions": ["validateCsv"],
        "summary": "Check CSV parsing and report rows that contain an inconsistent number of columns.",
        "sample": "name,email,status\nAda,ada@example.com,active\nLinus,linus@example.com",
        "examples": [
            ("Find short rows", "a,b,c↵1,2", "Error: row 2 has 2 columns; expected 3"),
            ("Find extra columns", "a,b↵1,2,3", "Error: row 2 has 3 columns; expected 2"),
            ("Check quoted fields", 'name,note↵Ada,"Hello, world"', "Valid CSV"),
        ],
    },
    "delimiter": {
        "action": "convertDelimiter",
        "actions": ["convertDelimiter"],
        "summary": "Automatically convert comma-separated CSV to tab-separated data, or tab-separated data back to commas.",
        "sample": "name,email\nAda,ada@example.com\nLinus,linus@example.com",
        "examples": [
            ("Comma to tab", "name,email↵Ada,a@example.com", "name⇥email↵Ada⇥a@example.com"),
            ("Tab to comma", "name⇥role↵Ada⇥Engineer", "name,role↵Ada,Engineer"),
            ("Convert spreadsheet data", "item,price↵Book,10", "item⇥price↵Book⇥10"),
        ],
    },
    "empty_columns": {
        "action": "removeEmptyColumns",
        "actions": ["removeEmptyColumns"],
        "summary": "Remove CSV columns that contain no populated values in any data row.",
        "sample": "name,unused,email,notes\nAda,,ada@example.com,\nLinus,,linus@example.com,",
        "examples": [
            ("Delete blank columns", "name,empty↵Ada,↵Linus,", "name↵Ada↵Linus"),
            ("Clean unused fields", "id,unused,status↵1,,active", "id,status↵1,active"),
            ("Reduce sparse exports", "item,notes,price↵Book,,10", "item,price↵Book,10"),
        ],
    },
    "table": {
        "action": "tableView",
        "actions": ["tableView"],
        "summary": "Parse CSV into a readable table preview with row, column, and cell statistics.",
        "sample": "name,role,city\nAda,Engineer,London\nLinus,Developer,Helsinki\nGrace,Scientist,New York",
        "examples": [
            ("Preview spreadsheet data", "name,role↵Ada,Engineer", "Table: 1 row × 2 columns"),
            ("Inspect CSV headers", "id,status,total↵7,paid,25", "Columns: id · status · total"),
            ("Review imported records", "city,country↵Paris,France", "Table preview ready"),
        ],
    },
    "cleanup": {
        "action": "cleanupCsv",
        "actions": ["cleanupCsv"],
        "summary": "Fix common CSV formatting issues by trimming cells and removing empty rows and columns.",
        "sample": "name, empty, email\n Ada ,, ada@example.com \n,,\n Linus ,, linus@example.com ",
        "examples": [
            ("Fix cell spacing", "name,email↵·Ada·,·a@example.com·", "name,email↵Ada,a@example.com"),
            ("Remove empty structure", "name,unused↵Ada,↵,", "name↵Ada"),
            ("Repair messy exports", "item, empty ↵ Book , ↵,", "item↵Book"),
        ],
    },
}


CSV_TASKS = {
    "format-csv": ("Format CSV", "pretty"),
    "csv-formatter": ("CSV Formatter", "pretty"),
    "clean-csv": ("Clean CSV", "standard_cleanup"),
    "remove-empty-rows": ("Remove Empty Rows", "empty_rows"),
    "remove-duplicate-rows": ("Remove Duplicate Rows", "deduplicate"),
    "sort-csv": ("Sort CSV", "sort"),
    "trim-csv-whitespace": ("Trim CSV Whitespace", "trim"),
    "normalize-csv": ("Normalize CSV", "standardize"),
    "csv-validator": ("CSV Validator", "validation"),
    "convert-csv-delimiter": ("Convert CSV Delimiter", "delimiter"),
    "remove-empty-columns": ("Remove Empty Columns", "empty_columns"),
    "csv-viewer": ("CSV Viewer", "table"),
    "csv-pretty-print": ("CSV Pretty Print", "pretty"),
    "fix-csv-formatting": ("Fix CSV Formatting", "cleanup"),
}


def build_csv_task(slug):
    title, profile_name = CSV_TASKS[slug]
    profile = CSV_OPERATION_PROFILES[profile_name]
    examples = [
        {"title": heading, "before": before, "after": after, "copy": f"Use {title} to {heading.lower()} and verify the result in the CSV preview."}
        for heading, before, after in profile["examples"]
    ]

    return {
        **profile,
        "slug": slug,
        "title": title,
        "seo_title": f"{title} Online Free | CleanrKit",
        "seo_description": f"{profile['summary']} Use this free online {title.lower()} tool with an instant table preview.",
        "intro_title": f"{title} online",
        "intro_copy": f"{profile['summary']} Paste your CSV below to apply the configured operation and inspect the result immediately.",
        "examples": examples,
        "features": [
            {"title": f"Focused {title.lower()}", "copy": f"The page opens with the {title.lower()} operation already configured."},
            {"title": "Live CSV preview", "copy": "Inspect headers, rows, columns, and cleaned cell values in table form."},
            {"title": "Advanced CSVCleanr options", "copy": "Open Advanced Options to combine cleanup, validation, and normalization controls."},
        ],
        "steps": [
            {"title": "Paste CSV data", "copy": "Add comma-separated or tab-separated data to the Input field."},
            {"title": f"Run {title}", "copy": "Use the blue arrow or edit the data to refresh the output and preview."},
            {"title": "Review and export", "copy": "Inspect the result, then copy it or export a CSV file."},
        ],
        "faqs": [
            {"question": f"What does {title} do?", "answer": profile["summary"]},
            {"question": "Can I preview the CSV as a table?", "answer": "Yes. Every CSV page includes a table preview and column statistics below the editor."},
            {"question": "Can I combine CSV cleanup options?", "answer": "Yes. Open Advanced Options or visit the full CSVCleanr tool to enable additional operations."},
        ],
    }
