import hashlib
import unicodedata
from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from kehilaflow.api.schemas.imports import (
    DonorResolution,
    ExcelAnalysisResponse,
    ExcelImportResponse,
    ExcelValue,
)
from kehilaflow.models.campaign import Campaign
from kehilaflow.models.donation import Donation
from kehilaflow.models.donor import Donor
from kehilaflow.models.pledge import Pledge
from kehilaflow.repositories.campaign_repository import (
    CampaignRepository,
)
from kehilaflow.repositories.donation_repository import (
    DonationRepository,
)
from kehilaflow.repositories.donor_repository import (
    DonorRepository,
)
from kehilaflow.repositories.import_repository import (
    ImportRepository,
)
from kehilaflow.repositories.pledge_repository import (
    PledgeRepository,
)
from kehilaflow.services.excel_import_service import (
    read_excel_rows,
)
from kehilaflow.services.excel_match_service import (
    match_excel_donors,
)
from kehilaflow.services.excel_prepare_service import (
    prepare_excel_import,
)


class ExcelAlreadyImportedError(Exception):
    pass


class ExcelAmbiguousDonorsError(Exception):
    pass


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


def _to_number(
    value: ExcelValue,
) -> float:
    if value is None:
        return 0

    if isinstance(value, bool):
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(" ", "").replace(",", ".")

    if not text:
        return 0

    try:
        return float(text)

    except ValueError:
        return 0


def _to_amount(
    value: ExcelValue,
) -> int:
    number = _to_number(value)

    if number == 0:
        return 0

    if not number.is_integer():
        raise ValueError(f"Amount {number} is not a whole number.")

    return int(number)


def _to_date(
    value: ExcelValue,
) -> date | None:
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    try:
        return date.fromisoformat(text[:10])

    except ValueError:
        return None


def _get_text(
    row: dict[str, ExcelValue],
    column: str | None,
) -> str:
    if column is None:
        return ""

    value = row.get(column)

    if value is None:
        return ""

    return str(value).strip()


def confirm_excel_import(
    *,
    file_bytes: bytes,
    file_name: str,
    analysis: ExcelAnalysisResponse,
    resolutions: list[DonorResolution],
    session: Session,
) -> ExcelImportResponse:
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    import_repository = ImportRepository(session)

    if import_repository.exists_by_hash(file_hash):
        raise ExcelAlreadyImportedError("This Excel file has already been imported.")

    prepared = prepare_excel_import(
        file_bytes=file_bytes,
        analysis=analysis,
    )

    matched = match_excel_donors(
        prepared=prepared,
        session=session,
    )

    _, rows = read_excel_rows(file_bytes)

    source_by_target = {
        mapping.target: mapping.source
        for mapping in analysis.mappings
        if mapping.target != "ignore"
    }

    first_name_column = source_by_target.get("first_name")

    last_name_column = source_by_target.get("last_name")

    date_column = source_by_target.get("date")

    campaign_column = source_by_target.get("campaign_name")

    pledged_column = source_by_target.get("pledged_amount")

    paid_column = source_by_target.get("paid_amount")

    donor_repository = DonorRepository(session)

    campaign_repository = CampaignRepository(session)

    pledge_repository = PledgeRepository(session)

    donation_repository = DonationRepository(session)

    database_donors = donor_repository.get_all()

    database_campaigns = campaign_repository.get_all()

    donor_by_name: dict[
        tuple[str, str],
        Donor,
    ] = {
        (
            _normalize(donor.first_name),
            _normalize(donor.last_name),
        ): donor
        for donor in database_donors
    }

    campaign_by_name: dict[
        str,
        Campaign,
    ] = {_normalize(campaign.name): campaign for campaign in database_campaigns}

    resolution_by_source = {
        (
            _normalize(resolution.source_first_name),
            _normalize(resolution.source_last_name),
        ): resolution
        for resolution in resolutions
    }

    resolved_ambiguous: dict[
        tuple[str, str],
        Donor | None,
    ] = {}

    created_donors = 0
    created_campaigns = 0
    created_pledges = 0
    created_donations = 0

    total_pledged = 0
    total_paid = 0

    existing_donors = matched.existing_donors

    try:
        # ---------------------------------
        # CREATE NORMAL NEW DONORS
        # ---------------------------------

        for matched_donor in matched.donors:
            if matched_donor.status != "new":
                continue

            first_name = matched_donor.first_name.strip()

            last_name = matched_donor.last_name.strip()

            if not first_name or not last_name:
                raise ExcelAmbiguousDonorsError(
                    "A new donor must have a first name and last name."
                )

            key = (
                _normalize(first_name),
                _normalize(last_name),
            )

            if key in donor_by_name:
                continue

            donor = Donor(
                first_name=first_name,
                last_name=last_name,
                email=None,
                phone=None,
            )

            donor_repository.add(donor)

            donor_by_name[key] = donor

            created_donors += 1

        # ---------------------------------
        # RESOLVE AMBIGUOUS DONORS
        # ---------------------------------

        for matched_donor in matched.donors:
            if matched_donor.status != "ambiguous":
                continue

            source_key = (
                _normalize(matched_donor.first_name),
                _normalize(matched_donor.last_name),
            )

            resolution = resolution_by_source.get(source_key)

            if resolution is None:
                raise ExcelAmbiguousDonorsError(
                    "Missing resolution for "
                    f"{matched_donor.first_name} "
                    f"{matched_donor.last_name}."
                )

            # -----------------------------
            # IGNORE
            # -----------------------------

            if resolution.action == "ignore":
                resolved_ambiguous[source_key] = None

                continue

            # -----------------------------
            # LINK DATABASE
            # -----------------------------

            if resolution.action == "link_database":
                if resolution.donor_id is None:
                    raise ExcelAmbiguousDonorsError(
                        "donor_id is required for link_database."
                    )

                donor = donor_repository.find_by_id(resolution.donor_id)

                if donor is None:
                    raise ExcelAmbiguousDonorsError(
                        "Selected database donor does not exist."
                    )

                resolved_ambiguous[source_key] = donor

                existing_donors += 1

                continue

            # -----------------------------
            # LINK TO AN EXCEL DONOR
            # -----------------------------

            if resolution.action == "link_excel":
                if not resolution.target_first_name or not resolution.target_last_name:
                    raise ExcelAmbiguousDonorsError(
                        "Target first name and last name are required for link_excel."
                    )

                target_key = (
                    _normalize(resolution.target_first_name),
                    _normalize(resolution.target_last_name),
                )

                donor = donor_by_name.get(target_key)

                if donor is None:
                    raise ExcelAmbiguousDonorsError(
                        "Selected Excel donor could not be found."
                    )

                resolved_ambiguous[source_key] = donor

                continue

            # -----------------------------
            # CREATE MANUALLY
            # -----------------------------

            if resolution.action == "create":
                first_name = (
                    resolution.target_first_name or matched_donor.first_name
                ).strip()

                last_name = (
                    resolution.target_last_name or matched_donor.last_name
                ).strip()

                if not first_name or not last_name:
                    raise ExcelAmbiguousDonorsError(
                        "A first name and last name are required to create a donor."
                    )

                target_key = (
                    _normalize(first_name),
                    _normalize(last_name),
                )

                existing = donor_by_name.get(target_key)

                if existing is not None:
                    resolved_ambiguous[source_key] = existing

                    continue

                donor = Donor(
                    first_name=first_name,
                    last_name=last_name,
                    email=None,
                    phone=None,
                )

                donor_repository.add(donor)

                donor_by_name[target_key] = donor

                resolved_ambiguous[source_key] = donor

                created_donors += 1

                continue

            raise ExcelAmbiguousDonorsError("Unknown donor resolution action.")

        # ---------------------------------
        # IMPORT EXCEL ROWS
        # ---------------------------------

        for row in rows:
            first_name = _get_text(
                row,
                first_name_column,
            )

            last_name = _get_text(
                row,
                last_name_column,
            )

            if not first_name and not last_name:
                continue

            source_key = (
                _normalize(first_name),
                _normalize(last_name),
            )

            # Ambiguous donor previously
            # resolved by admin.
            if source_key in resolved_ambiguous:
                donor = resolved_ambiguous[source_key]

                # Admin chose Ignore.
                if donor is None:
                    continue

            else:
                donor = donor_by_name.get(source_key)

            if donor is None:
                raise ExcelAmbiguousDonorsError(
                    f"Could not identify donor {first_name} {last_name}."
                )

            pledged_amount = _to_amount(
                row.get(pledged_column) if pledged_column else None
            )

            paid_amount = _to_amount(row.get(paid_column) if paid_column else None)

            # Nothing financial on this row.
            if pledged_amount <= 0 and paid_amount <= 0:
                continue

            operation_date = _to_date(row.get(date_column) if date_column else None)

            if operation_date is None:
                raise ValueError(
                    f"A financial row for {first_name} {last_name} has no valid date."
                )

            campaign_id: UUID | None = None

            campaign_name = _get_text(
                row,
                campaign_column,
            )

            if campaign_name:
                campaign_key = _normalize(campaign_name)

                campaign = campaign_by_name.get(campaign_key)

                if campaign is None:
                    campaign = Campaign(name=campaign_name)

                    campaign_repository.add(campaign)

                    campaign_by_name[campaign_key] = campaign

                    created_campaigns += 1

                campaign_id = campaign.id

            # -----------------------------
            # PLEDGE
            # -----------------------------

            if pledged_amount > 0:
                pledge = Pledge(
                    donor_id=donor.id,
                    amount=pledged_amount,
                    pledge_date=operation_date,
                    campaign_id=campaign_id,
                )

                pledge_repository.add(pledge)

                created_pledges += 1
                total_pledged += pledged_amount

            # -----------------------------
            # DONATION / PAYMENT
            # -----------------------------

            if paid_amount > 0:
                donation = Donation(
                    donor_id=donor.id,
                    amount=paid_amount,
                    donation_date=operation_date,
                    campaign_id=campaign_id,
                )

                donation_repository.add(donation)

                created_donations += 1
                total_paid += paid_amount

        # ---------------------------------
        # MARK FILE AS IMPORTED
        # ---------------------------------

        import_repository.add(
            file_name=file_name,
            file_hash=file_hash,
        )

        session.commit()

    except (
        ExcelAmbiguousDonorsError,
        ValueError,
    ):
        session.rollback()
        raise

    return ExcelImportResponse(
        file_name=file_name,
        created_donors=created_donors,
        existing_donors=existing_donors,
        created_campaigns=created_campaigns,
        created_pledges=created_pledges,
        created_donations=created_donations,
        total_pledged=float(total_pledged),
        total_paid=float(total_paid),
    )
