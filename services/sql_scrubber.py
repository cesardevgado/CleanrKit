import re


SAMPLE_SQL = """select u.id,u.name,o.total
from users u
left join orders o on o.user_id=u.id
where u.age>18 and o.status='paid'
order by u.name"""

SQL_KEYWORDS = {
    "select",
    "from",
    "where",
    "join",
    "inner",
    "left",
    "right",
    "full",
    "outer",
    "cross",
    "on",
    "and",
    "or",
    "group",
    "by",
    "order",
    "having",
    "limit",
    "offset",
    "insert",
    "into",
    "values",
    "update",
    "set",
    "delete",
    "create",
    "alter",
    "drop",
    "table",
    "as",
    "case",
    "when",
    "then",
    "else",
    "end",
    "distinct",
    "union",
    "all",
    "is",
    "not",
    "null",
    "in",
    "exists",
    "between",
    "like",
    "desc",
    "asc",
}

START_KEYWORDS = {
    "select",
    "insert",
    "update",
    "delete",
    "create",
    "alter",
    "drop",
    "with",
}

CLAUSE_KEYWORDS = {
    "SELECT",
    "FROM",
    "WHERE",
    "GROUP BY",
    "ORDER BY",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "VALUES",
    "SET",
}


def remove_comments(sql):
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    sql = re.sub(r"--[^\n]*", "", sql)
    return sql


def normalize_whitespace(sql):
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in sql.splitlines()]
    sql = "\n".join(line for line in lines if line)
    return re.sub(r"\n{3,}", "\n\n", sql).strip()


def tokenize_sql(sql):
    token_pattern = r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|`[^`]*`|\b[\w.]+\b|<>|!=|<=|>=|[(),;=*<>/+%-]"
    return re.findall(token_pattern, sql)


def apply_keyword_case(token, keyword_case):
    lower = token.lower()
    if lower not in SQL_KEYWORDS:
        return token

    return lower if keyword_case == "lower" else lower.upper()


def keyword_case_sql(sql, keyword_case):
    return " ".join(apply_keyword_case(token, keyword_case) for token in tokenize_sql(sql))


def compact_sql(sql, keyword_case):
    tokens = [apply_keyword_case(token, keyword_case) for token in tokenize_sql(sql)]
    output = " ".join(tokens)
    output = re.sub(r"\s+([,);])", r"\1", output)
    output = re.sub(r"([(])\s+", r"\1", output)
    output = re.sub(r"\s*([=<>+\-*/%])\s*", r" \1 ", output)
    output = re.sub(r"\s+", " ", output).strip()

    if output and not output.endswith(";"):
        output += ";"

    return output


def expanded_sql(sql, keyword_case, indent_size):
    compact = compact_sql(sql, keyword_case).rstrip(";")
    tokens = compact.split()
    clause_starters = {
        "SELECT",
        "FROM",
        "WHERE",
        "HAVING",
        "LIMIT",
        "OFFSET",
        "VALUES",
        "SET",
    }
    lines = []
    current = []
    indent = " " * indent_size
    index = 0

    while index < len(tokens):
        token = tokens[index]
        upper = token.upper()
        phrase = upper

        if index + 1 < len(tokens) and f"{upper} {tokens[index + 1].upper()}" in CLAUSE_KEYWORDS:
            phrase = f"{upper} {tokens[index + 1].upper()}"
            token = phrase if keyword_case == "upper" else phrase.lower()
            index += 1

        if phrase in clause_starters or phrase in {"GROUP BY", "ORDER BY"}:
            if current:
                lines.append(" ".join(current).strip())
            current = [token]
        elif upper in {"INNER", "LEFT", "RIGHT", "FULL", "CROSS"} and index + 1 < len(tokens) and tokens[index + 1].upper() == "JOIN":
            if current:
                lines.append(" ".join(current).strip())
            join_phrase = f"{upper} JOIN" if keyword_case == "upper" else f"{upper.lower()} join"
            current = [join_phrase]
            index += 1
        elif upper == "JOIN":
            if current:
                lines.append(" ".join(current).strip())
            current = [token]
        else:
            current.append(token)

        index += 1

    if current:
        lines.append(" ".join(current).strip())

    formatted = []
    for line in lines:
        upper_line = line.upper()
        if upper_line.startswith("SELECT "):
            fields = split_select_fields(line[len("SELECT "):])
            select_word = "SELECT" if keyword_case == "upper" else "select"
            formatted.append(select_word)
            formatted.extend(f"{indent}{field}{',' if idx < len(fields) - 1 else ''}" for idx, field in enumerate(fields))
        else:
            formatted.append(format_operators(line))

    return "\n".join(formatted).strip() + ";"


def split_select_fields(fields_text):
    parts = []
    current = []
    depth = 0

    for char in fields_text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(depth - 1, 0)

        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if current:
        parts.append("".join(current).strip())

    return parts or [fields_text.strip()]


def format_operators(line):
    line = re.sub(r"\s*([=<>+\-*/%])\s*", r" \1 ", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def validate_sql(sql):
    stripped = sql.strip()
    if not stripped:
        return False, "SQL is empty."

    first = re.match(r"^\s*(\w+)", stripped)
    if not first or first.group(1).lower() not in START_KEYWORDS:
        return False, "SQL should start with a common statement keyword."

    if stripped.count("(") != stripped.count(")"):
        return False, "Unbalanced parentheses."

    if len(re.findall(r"(?<!')'(?!')", stripped)) % 2:
        return False, "Unbalanced single quotes."

    if re.search(r"\bselect\s+from\b", stripped, flags=re.IGNORECASE):
        return False, "SELECT appears to be missing columns."

    return True, "Valid SQL"


def get_query_statistics(sql):
    clean_sql = remove_comments(sql)
    lowered = clean_sql.lower()
    tables = set(re.findall(r"\b(?:from|join)\s+([`\"\[]?[\w.]+[`\"\]]?)", lowered))
    joins = len(re.findall(r"\bjoin\b", lowered))
    where_clauses = len(re.findall(r"\bwhere\b", lowered))
    subqueries = len(re.findall(r"\(\s*select\b", lowered))
    score = joins + where_clauses + (subqueries * 2) + max(len(tables) - 1, 0)

    if score <= 2:
        complexity = "Low"
    elif score <= 6:
        complexity = "Medium"
    else:
        complexity = "High"

    return {
        "lines": clean_sql.count("\n") + 1 if clean_sql else 0,
        "characters": len(clean_sql),
        "tables_used": len(tables),
        "joins": joins,
        "where_clauses": where_clauses,
        "subqueries": subqueries,
        "complexity": complexity,
    }


def scrub_sql(sql, actions, keyword_case="upper", indent_size=4, format_mode="expanded"):
    active_actions = set(actions)
    output = sql

    if "removeComments" in active_actions:
        output = remove_comments(output)

    if "normalizeWhitespace" in active_actions:
        output = normalize_whitespace(output)

    if "formatSql" in active_actions:
        if format_mode == "compact":
            output = compact_sql(output, keyword_case)
        else:
            output = expanded_sql(output, keyword_case, indent_size)
    elif "keywordCasing" in active_actions:
        output = keyword_case_sql(output, keyword_case)

    valid, validation_message = validate_sql(output)
    display_message = "Valid SQL" if valid else f"Syntax appears invalid: {validation_message}"

    return {
        "output": output,
        "valid": valid,
        "validation_message": display_message,
        "statistics": get_query_statistics(output),
    }
