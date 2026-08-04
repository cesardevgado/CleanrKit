SQL_OPERATION_PROFILES = {
    "beautify": {
        "action": "formatSql",
        "actions": ["formatSql"],
        "keyword_case": "upper",
        "indent_size": 4,
        "format_mode": "expanded",
        "summary": "Turn dense SQL into readable queries with clear clauses, indentation, and operator spacing.",
        "sample": "select u.id,u.name,o.total from users u left join orders o on o.user_id=u.id where o.status='paid' order by u.name",
        "examples": [
            ("Split SQL clauses", "select * from users where active=1", "SELECT *↵FROM users↵WHERE active = 1;"),
            ("Format selected columns", "select id,name,email from users", "SELECT↵····id,↵····name,↵····email↵FROM users;"),
            ("Organize joins", "select * from users u join orders o on o.user_id=u.id", "SELECT *↵FROM users u↵JOIN orders o on o.user_id = u.id;"),
        ],
    },
    "minify": {
        "action": "formatSql",
        "actions": ["formatSql"],
        "keyword_case": "upper",
        "indent_size": 4,
        "format_mode": "compact",
        "summary": "Compress formatted SQL into a compact single-line query with normalized spacing.",
        "sample": "SELECT\n    id,\n    name\nFROM users\nWHERE active = 1\nORDER BY name;",
        "examples": [
            ("Compact multiline SQL", "SELECT *↵FROM users↵WHERE id = 7;", "SELECT * FROM users WHERE id = 7;"),
            ("Compress selected fields", "SELECT↵··id,↵··name↵FROM users;", "SELECT id, name FROM users;"),
            ("Normalize operator spacing", "SELECT * FROM users WHERE id··=··7", "SELECT * FROM users WHERE id = 7;"),
        ],
    },
    "uppercase": {
        "action": "keywordCasing",
        "actions": ["keywordCasing"],
        "keyword_case": "upper",
        "indent_size": 4,
        "format_mode": "expanded",
        "summary": "Convert recognized SQL keywords to uppercase while keeping identifiers and values intact.",
        "sample": "select id, name from users where active is not null order by name asc",
        "examples": [
            ("Uppercase query clauses", "select * from users", "SELECT * FROM users"),
            ("Uppercase conditions", "where active is not null", "WHERE active IS NOT NULL"),
            ("Uppercase ordering", "order by name asc", "ORDER BY name ASC"),
        ],
    },
    "lowercase": {
        "action": "keywordCasing",
        "actions": ["keywordCasing"],
        "keyword_case": "lower",
        "indent_size": 4,
        "format_mode": "expanded",
        "summary": "Convert recognized SQL keywords to lowercase while preserving table names, columns, and values.",
        "sample": "SELECT id, name FROM users WHERE active IS NOT NULL ORDER BY name ASC",
        "examples": [
            ("Lowercase query clauses", "SELECT * FROM users", "select * from users"),
            ("Lowercase conditions", "WHERE active IS NOT NULL", "where active is not null"),
            ("Lowercase ordering", "ORDER BY name ASC", "order by name asc"),
        ],
    },
    "indent": {
        "action": "formatSql",
        "actions": ["formatSql"],
        "keyword_case": "upper",
        "indent_size": 4,
        "format_mode": "expanded",
        "summary": "Apply consistent indentation to SQL columns, clauses, joins, and nested query structures.",
        "sample": "select id,name,email from users where id in (select user_id from orders where total>100)",
        "examples": [
            ("Indent selected columns", "select id,name from users", "SELECT↵····id,↵····name↵FROM users;"),
            ("Align SQL clauses", "select * from users where active=1", "SELECT *↵FROM users↵WHERE active = 1;"),
            ("Structure long queries", "select * from users order by name", "SELECT *↵FROM users↵ORDER BY name;"),
        ],
    },
    "comments": {
        "action": "removeComments",
        "actions": ["removeComments"],
        "keyword_case": "upper",
        "indent_size": 4,
        "format_mode": "expanded",
        "summary": "Remove single-line and block comments from SQL without changing the remaining query text.",
        "sample": "-- Fetch active users\nSELECT * FROM users /* customer table */ WHERE active = 1;",
        "examples": [
            ("Remove line comments", "-- Get users↵SELECT * FROM users;", "↵SELECT * FROM users;"),
            ("Remove block comments", "SELECT /* all fields */ * FROM users;", "SELECT  * FROM users;"),
            ("Clean inline notes", "SELECT id -- identifier↵FROM users;", "SELECT id ↵FROM users;"),
        ],
    },
    "validation": {
        "action": "validateSql",
        "actions": ["validateSql"],
        "keyword_case": "upper",
        "indent_size": 4,
        "format_mode": "expanded",
        "summary": "Check SQL for common structural problems such as missing columns, unbalanced quotes, and unmatched parentheses.",
        "sample": "SELECT FROM users WHERE id IN (1, 2;",
        "examples": [
            ("Find missing columns", "SELECT FROM users;", "Invalid: SELECT is missing columns"),
            ("Detect open parentheses", "SELECT * FROM users WHERE id IN (1, 2;", "Invalid: unbalanced parentheses"),
            ("Check quotation marks", "SELECT * FROM users WHERE name = 'Ada;", "Invalid: unbalanced single quotes"),
        ],
    },
    "cleanup": {
        "action": "normalizeWhitespace",
        "actions": ["removeComments", "normalizeWhitespace"],
        "keyword_case": "upper",
        "indent_size": 4,
        "format_mode": "expanded",
        "summary": "Clean SQL by removing comments, repeated whitespace, empty lines, and inconsistent spacing.",
        "sample": "-- report\n\nSELECT    id,   name\n\nFROM    users\nWHERE   active = 1;",
        "examples": [
            ("Normalize whitespace", "SELECT····*··FROM··users;", "SELECT * FROM users;"),
            ("Remove empty lines", "SELECT *↵↵↵FROM users;", "SELECT *↵FROM users;"),
            ("Clean comments and spacing", "-- note↵SELECT··id FROM users;", "SELECT id FROM users;"),
        ],
    },
}


SQL_TASKS = {
    "sql-formatter": ("SQL Formatter", "beautify"),
    "sql-beautifier": ("SQL Beautifier", "beautify"),
    "pretty-print-sql": ("Pretty Print SQL", "beautify"),
    "format-sql-query": ("Format SQL Query", "beautify"),
    "minify-sql": ("Minify SQL", "minify"),
    "uppercase-sql-keywords": ("Uppercase SQL Keywords", "uppercase"),
    "lowercase-sql-keywords": ("Lowercase SQL Keywords", "lowercase"),
    "sql-indenter": ("SQL Indenter", "indent"),
    "remove-sql-comments": ("Remove SQL Comments", "comments"),
    "sql-validator": ("SQL Validator", "validation"),
    "compress-sql": ("Compress SQL", "minify"),
    "sql-cleaner": ("SQL Cleaner", "cleanup"),
    "sql-syntax-formatter": ("SQL Syntax Formatter", "beautify"),
    "normalize-sql": ("Normalize SQL", "cleanup"),
}


def build_sql_task(slug):
    title, profile_name = SQL_TASKS[slug]
    profile = SQL_OPERATION_PROFILES[profile_name]
    examples = [
        {"title": heading, "before": before, "after": after, "copy": f"Use {title} to {heading.lower()} and inspect the transformed query."}
        for heading, before, after in profile["examples"]
    ]

    return {
        **profile,
        "slug": slug,
        "title": title,
        "seo_title": f"{title} Online Free | CleanrKit",
        "seo_description": f"{profile['summary']} Use this free online {title.lower()} tool with instant output and SQL validation.",
        "intro_title": f"{title} online",
        "intro_copy": f"{profile['summary']} Paste your query below to apply the configured SQL operation and review the result instantly.",
        "examples": examples,
        "features": [
            {"title": f"Focused {title.lower()}", "copy": f"The page opens with the {title.lower()} operation and matching SQL style already configured."},
            {"title": "Built-in SQL checks", "copy": "Review structural validation feedback and query statistics with every result."},
            {"title": "Advanced SQLCleanr options", "copy": "Open Advanced Options to combine formatting, keyword, indentation, and cleanup controls."},
        ],
        "steps": [
            {"title": "Paste your SQL", "copy": "Add a query or SQL script to the Input field."},
            {"title": f"Run {title}", "copy": "Use the blue arrow or edit the query to refresh the configured output."},
            {"title": "Copy or download", "copy": "Review the result, then copy it or save it as a .sql file."},
        ],
        "faqs": [
            {"question": f"What does {title} do?", "answer": profile["summary"]},
            {"question": "Does this tool execute my SQL?", "answer": "No. SQLCleanr formats and checks text only; it never connects to a database or executes a query."},
            {"question": "Can I change the SQL style?", "answer": "Yes. Open Advanced Options or visit the full SQLCleanr tool for keyword case, indentation, formatting, and cleanup controls."},
        ],
    }
