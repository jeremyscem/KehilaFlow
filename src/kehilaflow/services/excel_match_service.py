import unicodedata

from sqlalchemy.orm import Session

from kehilaflow.api.schemas.imports import (
    DonorImportMatch,
    DonorMatchCandidate,
    ExcelMatchResponse,
    ExcelPrepareResponse,
)
from kehilaflow.repositories.donor_repository import (
    DonorRepository,
)


def _normalize(value: str) -> str:
    value = value.strip().casefold()

    return "".join(
        character
        for character in unicodedata.normalize(
            "NFD",
            value,
        )
        if unicodedata.category(character) != "Mn"
    )


def match_excel_donors(
    prepared: ExcelPrepareResponse,
    session: Session,
) -> ExcelMatchResponse:
    database_donors = DonorRepository(session).get_all()

    donors: list[DonorImportMatch] = []

    for excel_donor in prepared.donors:
        first_name = _normalize(excel_donor.first_name)

        last_name = _normalize(excel_donor.last_name)

        # No last name:
        # impossible to identify safely.
        if not last_name:
            donors.append(
                DonorImportMatch(
                    first_name=excel_donor.first_name,
                    last_name=excel_donor.last_name,
                    pledged_amount=excel_donor.pledged_amount,
                    paid_amount=excel_donor.paid_amount,
                    remaining=excel_donor.remaining,
                    status="ambiguous",
                )
            )
            continue

        # Missing first name:
        # search candidates in PostgreSQL AND
        # inside the same Excel file.
        if not first_name:
            database_candidates = [
                DonorMatchCandidate(
                    donor_id=donor.id,
                    first_name=donor.first_name,
                    last_name=donor.last_name,
                    source="database",
                )
                for donor in database_donors
                if _normalize(donor.last_name) == last_name
            ]

            excel_candidates = [
                DonorMatchCandidate(
                    donor_id=None,
                    first_name=other.first_name,
                    last_name=other.last_name,
                    source="excel",
                )
                for other in prepared.donors
                if (other.first_name and _normalize(other.last_name) == last_name)
            ]

            donors.append(
                DonorImportMatch(
                    first_name=excel_donor.first_name,
                    last_name=excel_donor.last_name,
                    pledged_amount=excel_donor.pledged_amount,
                    paid_amount=excel_donor.paid_amount,
                    remaining=excel_donor.remaining,
                    status="ambiguous",
                    candidates=(database_candidates + excel_candidates),
                )
            )
            continue

        # Exact first name + last name match
        # against PostgreSQL.
        database_matches = [
            donor
            for donor in database_donors
            if (
                _normalize(donor.first_name) == first_name
                and _normalize(donor.last_name) == last_name
            )
        ]

        # Exactly one donor already exists.
        if len(database_matches) == 1:
            donors.append(
                DonorImportMatch(
                    first_name=excel_donor.first_name,
                    last_name=excel_donor.last_name,
                    pledged_amount=excel_donor.pledged_amount,
                    paid_amount=excel_donor.paid_amount,
                    remaining=excel_donor.remaining,
                    status="existing",
                    donor_id=database_matches[0].id,
                )
            )
            continue

        # More than one exact DB match:
        # admin must choose.
        if len(database_matches) > 1:
            donors.append(
                DonorImportMatch(
                    first_name=excel_donor.first_name,
                    last_name=excel_donor.last_name,
                    pledged_amount=excel_donor.pledged_amount,
                    paid_amount=excel_donor.paid_amount,
                    remaining=excel_donor.remaining,
                    status="ambiguous",
                    candidates=[
                        DonorMatchCandidate(
                            donor_id=donor.id,
                            first_name=donor.first_name,
                            last_name=donor.last_name,
                            source="database",
                        )
                        for donor in database_matches
                    ],
                )
            )
            continue

        # No DB match:
        # this donor is new.
        donors.append(
            DonorImportMatch(
                first_name=excel_donor.first_name,
                last_name=excel_donor.last_name,
                pledged_amount=excel_donor.pledged_amount,
                paid_amount=excel_donor.paid_amount,
                remaining=excel_donor.remaining,
                status="new",
            )
        )

    return ExcelMatchResponse(
        total_donors=len(donors),
        existing_donors=sum(donor.status == "existing" for donor in donors),
        new_donors=sum(donor.status == "new" for donor in donors),
        ambiguous_donors=sum(donor.status == "ambiguous" for donor in donors),
        donors=donors,
    )
