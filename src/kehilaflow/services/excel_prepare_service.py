from collections import defaultdict

from kehilaflow.api.schemas.imports import (
    ExcelAnalysisResponse,
    ExcelPrepareResponse,
    ExcelValue,
    PreparedDonor,
)
from kehilaflow.services.excel_import_service import (
    read_excel_rows,
)


def _to_number(value: ExcelValue) -> float:
    if value is None:
        return 0

    if isinstance(value, bool):
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return 0


def prepare_excel_import(
    file_bytes: bytes,
    analysis: ExcelAnalysisResponse,
) -> ExcelPrepareResponse:
    _, rows = read_excel_rows(file_bytes)

    source_by_target = {
        mapping.target: mapping.source
        for mapping in analysis.mappings
        if mapping.target != "ignore"
    }

    first_name_column = source_by_target.get("first_name")
    last_name_column = source_by_target.get("last_name")
    pledged_column = source_by_target.get("pledged_amount")
    paid_column = source_by_target.get("paid_amount")

    # First pass:
    # find all known first names for each last name.
    known_first_names: dict[str, set[str]] = {}

    for row in rows:
        first_name = (
            str(row.get(first_name_column) or "").strip() if first_name_column else ""
        )

        last_name = (
            str(row.get(last_name_column) or "").strip() if last_name_column else ""
        )

        if not first_name or not last_name:
            continue

        last_name_key = last_name.casefold()

        known_first_names.setdefault(
            last_name_key,
            set(),
        ).add(first_name)

    donors: dict[
        tuple[str, str],
        dict[str, object],
    ] = {}

    # Second pass:
    # group financial rows by donor.
    for row in rows:
        first_name = (
            str(row.get(first_name_column) or "").strip() if first_name_column else ""
        )

        last_name = (
            str(row.get(last_name_column) or "").strip() if last_name_column else ""
        )

        if not first_name and not last_name:
            continue

        # If first name is missing but there is exactly
        # one known person with this last name, use it.
        if not first_name and last_name:
            possible_first_names = known_first_names.get(
                last_name.casefold(),
                set(),
            )

            if len(possible_first_names) == 1:
                first_name = next(iter(possible_first_names))

        key = (
            first_name.casefold(),
            last_name.casefold(),
        )

        if key not in donors:
            donors[key] = {
                "first_name": first_name,
                "last_name": last_name,
                "pledged": 0.0,
                "paid": 0.0,
            }

        pledged = _to_number(row.get(pledged_column) if pledged_column else 0)

        paid = _to_number(row.get(paid_column) if paid_column else 0)

        donors[key]["pledged"] = float(donors[key]["pledged"]) + pledged

        donors[key]["paid"] = float(donors[key]["paid"]) + paid

    prepared_donors = []

    for data in donors.values():
        pledged = float(data["pledged"])
        paid = float(data["paid"])

        prepared_donors.append(
            PreparedDonor(
                first_name=str(data["first_name"]),
                last_name=str(data["last_name"]),
                pledged_amount=pledged,
                paid_amount=paid,
                remaining=pledged - paid,
            )
        )

    prepared_donors.sort(
        key=lambda donor: donor.remaining,
        reverse=True,
    )

    return ExcelPrepareResponse(
        total_rows=len(rows),
        total_donors=len(prepared_donors),
        total_pledged=sum(donor.pledged_amount for donor in prepared_donors),
        total_paid=sum(donor.paid_amount for donor in prepared_donors),
        total_remaining=sum(donor.remaining for donor in prepared_donors),
        donors=prepared_donors,
        mappings=analysis.mappings,
    )
