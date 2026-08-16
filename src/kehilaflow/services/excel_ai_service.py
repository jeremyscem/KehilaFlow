import json
import os
import unicodedata

import anthropic
from dotenv import load_dotenv

from kehilaflow.api.schemas.imports import (
    ExcelAnalysisResponse,
    ExcelPreviewResponse,
    ExcelTarget,
)
from kehilaflow.services.excel_import_service import (
    read_excel_rows,
)

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


KNOWN_MAPPINGS: dict[str, ExcelTarget] = {
    "du": "pledged_amount",
    "paye": "paid_amount",
}


def _normalize_column_name(
    value: str,
) -> str:
    """
    Normalize a column name so known mappings are
    case-insensitive and accent-insensitive.

    Examples:
    DU   -> du
    Du   -> du
    DÛ   -> du
    PAYÉ -> paye
    Paye -> paye
    """
    value = value.strip().casefold()

    return "".join(
        character
        for character in unicodedata.normalize(
            "NFD",
            value,
        )
        if unicodedata.category(character) != "Mn"
    )


def _get_column_samples(
    columns: list[str],
    rows: list[dict],
    limit: int = 8,
) -> dict[str, list[object]]:
    """
    Get representative values for each column.

    We look through the whole Excel file instead of
    only using the first few rows.
    """
    column_samples: dict[str, list[object]] = {}

    for column in columns:
        samples: list[object] = []

        # First try to collect meaningful non-zero values.
        for row in rows:
            value = row.get(column)

            if value is None or value == "":
                continue

            if value == 0:
                continue

            if value in samples:
                continue

            samples.append(value)

            if len(samples) >= limit:
                break

        # If the column contains only zeros,
        # still show Claude that the column exists.
        if not samples:
            for row in rows:
                value = row.get(column)

                if value is None or value == "":
                    continue

                if value not in samples:
                    samples.append(value)

                if len(samples) >= limit:
                    break

        column_samples[column] = samples

    return column_samples


def _apply_known_mappings(
    analysis: ExcelAnalysisResponse,
) -> ExcelAnalysisResponse:
    """
    Business rules always override Claude.

    Claude helps understand unknown columns,
    but known KehilaFlow columns are deterministic.
    """
    for mapping in analysis.mappings:
        normalized_source = _normalize_column_name(mapping.source)

        known_target = KNOWN_MAPPINGS.get(normalized_source)

        if known_target is None:
            continue

        mapping.target = known_target
        mapping.confidence = 1.0
        mapping.reason = "Known KehilaFlow column mapping."

    return analysis


def analyze_excel_columns(
    preview: ExcelPreviewResponse,
    file_bytes: bytes,
) -> ExcelAnalysisResponse:
    _, rows = read_excel_rows(file_bytes)

    column_samples = _get_column_samples(
        columns=preview.columns,
        rows=rows,
    )

    data_for_claude = {
        "columns": preview.columns,
        "column_samples": column_samples,
    }

    response = client.messages.parse(
        model="claude-haiku-4-5",
        max_tokens=1200,
        system="""
You analyze Excel files for KehilaFlow,
a synagogue donation management application.

Your job is to understand what each Excel column means.

Map every source Excel column to exactly one
supported KehilaFlow target field.

Supported targets:

first_name
last_name
email
phone
date
campaign_name
pledged_amount
paid_amount
ignore

Definitions:

first_name:
The donor's first name.

last_name:
The donor's family name / surname.

email:
The donor's email address.

phone:
The donor's phone number.

date:
The date associated with the financial operation.

campaign_name:
The fundraising campaign, holiday or event.

pledged_amount:
Money promised, pledged, due or owed by the donor.

paid_amount:
Money actually paid by the donor.

ignore:
A column for which KehilaFlow currently has no
corresponding field.

Important rules:

- Do not ignore a financial column only because many
  or even all sample values are zero.

- Determine meaning primarily from the column name
  and its semantic meaning.

- Sample values are additional evidence only.

- A French column named DU or DÛ normally represents
  money due/owed and therefore corresponds to
  pledged_amount.

- A French column named PAYE or PAYÉ represents
  money paid and therefore corresponds to
  paid_amount.

- Do not invent KehilaFlow fields.

- Use ignore only when the source column genuinely
  has no corresponding KehilaFlow field.

- Every source column must appear exactly once in
  the returned mappings.

Confidence must be a number between 0 and 1.
""",
        messages=[
            {
                "role": "user",
                "content": json.dumps(
                    data_for_claude,
                    ensure_ascii=False,
                    default=str,
                ),
            }
        ],
        output_format=ExcelAnalysisResponse,
    )

    analysis = response.parsed_output

    if analysis is None:
        raise ValueError("Claude did not return an Excel mapping.")

    return _apply_known_mappings(analysis)
