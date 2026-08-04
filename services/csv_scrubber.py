import csv
import io
import re


SAMPLE_CSV = """Name, Email, Status, Last Login
 Alice Smith , alice@example.com , active, 2026-07-01
Bob Jones,bob@example.com,NULL,
Alice Smith, alice@example.com , active, 2026-07-01
,,,
Carla Ruiz,carla@example.com,n/a,2026-07-12
"""

NULL_TOKENS = {"", "null", "none", "n/a", "na", "nil"}


def detect_delimiter(text):
    first_line = text.splitlines()[0] if text.splitlines() else ""
    return "\t" if first_line.count("\t") > first_line.count(",") else ","


def parse_csv(text, delimiter=","):
    reader = csv.reader(io.StringIO(text), delimiter=delimiter, strict=True)
    return [row for row in reader]


def write_csv(rows, delimiter=","):
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter, lineterminator="\n")
    writer.writerows(rows)
    return buffer.getvalue()


def trim_cells(rows):
    return [[cell.strip() for cell in row] for row in rows]


def normalize_header(header):
    normalized = header.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "column"


def normalize_headers(rows):
    if not rows:
        return rows

    seen = {}
    headers = []

    for header in rows[0]:
        normalized = normalize_header(header)
        count = seen.get(normalized, 0) + 1
        seen[normalized] = count
        headers.append(normalized if count == 1 else f"{normalized}_{count}")

    return [headers, *rows[1:]]


def remove_empty_rows(rows):
    removed = 0
    cleaned_rows = []

    for index, row in enumerate(rows):
        if index > 0 and all(not cell.strip() for cell in row):
            removed += 1
            continue
        cleaned_rows.append(row)

    return cleaned_rows, removed


def remove_duplicate_rows(rows):
    if not rows:
        return rows, 0

    seen = set()
    removed = 0
    cleaned_rows = [rows[0]]

    for row in rows[1:]:
        row_key = tuple(row)
        if row_key in seen:
            removed += 1
            continue
        seen.add(row_key)
        cleaned_rows.append(row)

    return cleaned_rows, removed


def sort_rows(rows):
    if len(rows) <= 1:
        return rows

    return [rows[0], *sorted(rows[1:], key=lambda row: tuple(cell.casefold() for cell in row))]


def remove_empty_columns(rows):
    rectangular_rows = rectangularize_rows(rows)
    if not rectangular_rows:
        return rows, 0

    data_rows = rectangular_rows[1:]
    kept_indices = [
        index
        for index in range(len(rectangular_rows[0]))
        if any(row[index].strip() for row in data_rows)
    ]
    removed = len(rectangular_rows[0]) - len(kept_indices)
    return [[row[index] for index in kept_indices] for row in rectangular_rows], removed


def validate_rows(rows):
    if not rows:
        return

    expected_columns = len(rows[0])
    for row_number, row in enumerate(rows[1:], start=2):
        if len(row) != expected_columns:
            raise csv.Error(
                f"Row {row_number} has {len(row)} columns; expected {expected_columns}."
            )


def replace_null_values(rows, replacement):
    replaced = 0
    cleaned_rows = []

    for row_index, row in enumerate(rows):
        cleaned_row = []
        for cell in row:
            if row_index > 0 and cell.strip().lower() in NULL_TOKENS:
                cleaned_row.append(replacement)
                replaced += 1
            else:
                cleaned_row.append(cell)
        cleaned_rows.append(cleaned_row)

    return cleaned_rows, replaced


def rectangularize_rows(rows):
    width = max((len(row) for row in rows), default=0)
    return [row + [""] * (width - len(row)) for row in rows]


def get_column_statistics(rows):
    rows = rectangularize_rows(rows)
    if not rows:
        return []

    headers = rows[0]
    data_rows = rows[1:]
    statistics = []

    for index, header in enumerate(headers):
        values = [row[index] for row in data_rows]
        empty_count = sum(1 for value in values if not value.strip())
        non_empty_values = [value for value in values if value.strip()]
        statistics.append(
            {
                "name": header or f"Column {index + 1}",
                "empty": empty_count,
                "filled": len(non_empty_values),
                "unique": len(set(non_empty_values)),
            }
        )

    return statistics


def get_csv_statistics(rows, duplicate_rows_removed=0, empty_rows_removed=0, null_values_replaced=0):
    rows = rectangularize_rows(rows)
    headers = rows[0] if rows else []
    data_rows = rows[1:] if rows else []
    empty_cells = sum(
        1
        for row in data_rows
        for cell in row
        if not cell.strip()
    )

    return {
        "rows": len(data_rows),
        "columns": len(headers),
        "cells": len(data_rows) * len(headers),
        "empty_cells": empty_cells,
        "duplicate_rows_removed": duplicate_rows_removed,
        "empty_rows_removed": empty_rows_removed,
        "null_values_replaced": null_values_replaced,
        "columns_detail": get_column_statistics(rows),
    }


def scrub_csv(text, actions, null_replacement=""):
    active_actions = set(actions)
    if "standardCleanup" in active_actions:
        active_actions.update(
            {"trimCells", "normalizeHeaders", "removeEmptyRows", "removeDuplicateRows"}
        )
    if "standardizeCsv" in active_actions:
        active_actions.update({"trimCells", "normalizeHeaders"})
    if "cleanupCsv" in active_actions:
        active_actions.update({"trimCells", "removeEmptyRows", "removeEmptyColumns"})

    input_delimiter = detect_delimiter(text)
    output_delimiter = (
        "\t" if input_delimiter == "," else ","
    ) if "convertDelimiter" in active_actions else input_delimiter
    rows = parse_csv(text, delimiter=input_delimiter)
    if "validateCsv" in active_actions:
        validate_rows(rows)
    duplicate_rows_removed = 0
    empty_rows_removed = 0
    null_values_replaced = 0

    if "trimCells" in active_actions:
        rows = trim_cells(rows)

    if "normalizeHeaders" in active_actions:
        rows = normalize_headers(rows)

    if "removeEmptyRows" in active_actions:
        rows, empty_rows_removed = remove_empty_rows(rows)

    if "replaceNullValues" in active_actions:
        rows, null_values_replaced = replace_null_values(rows, null_replacement)

    if "removeDuplicateRows" in active_actions:
        rows, duplicate_rows_removed = remove_duplicate_rows(rows)

    if "removeEmptyColumns" in active_actions:
        rows, _empty_columns_removed = remove_empty_columns(rows)

    if "sortRows" in active_actions:
        rows = sort_rows(rows)

    output = write_csv(rows, delimiter=output_delimiter)

    return {
        "output": output,
        "statistics": get_csv_statistics(
            rows,
            duplicate_rows_removed,
            empty_rows_removed,
            null_values_replaced,
        ),
        "preview": rectangularize_rows(rows[:9]),
        "valid": True,
        "error": "",
    }
