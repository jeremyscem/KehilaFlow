import re
import unicodedata
from datetime import date
from difflib import SequenceMatcher
from uuid import UUID

from sqlalchemy.orm import Session

from kehilaflow.ai.registry import ai_tool
from kehilaflow.models.campaign import Campaign
from kehilaflow.models.donation import Donation
from kehilaflow.models.donor import Donor
from kehilaflow.models.pledge import Pledge
from kehilaflow.repositories.campaign_repository import CampaignRepository
from kehilaflow.repositories.donation_repository import DonationRepository
from kehilaflow.repositories.donor_repository import DonorRepository
from kehilaflow.repositories.pledge_repository import PledgeRepository
from kehilaflow.services.campaign_service import CampaignService
from kehilaflow.services.dashboard_service import (
    get_dashboard_stats as get_dashboard_stats_service,
)
from kehilaflow.services.donation_service import DonationService
from kehilaflow.services.donor_service import DonorService


def _build_donor_service(
    session: Session,
) -> DonorService:
    return DonorService(
        donor_repository=DonorRepository(session),
        donation_repository=DonationRepository(session),
        pledge_repository=PledgeRepository(session),
    )


def _date_to_string(
    value: date | str,
) -> str:
    if isinstance(value, date):
        return value.isoformat()

    return str(value)


# ------------------------------------------------------------------
# DONOR SEARCH HELPERS
# ------------------------------------------------------------------


def _normalize_search_text(
    value: str | None,
) -> str:
    if not value:
        return ""

    value = value.strip().casefold()

    value = "".join(
        character
        for character in unicodedata.normalize(
            "NFD",
            value,
        )
        if unicodedata.category(character) != "Mn"
    )

    value = re.sub(
        r"[^a-z0-9@+]+",
        " ",
        value,
    )

    return " ".join(value.split())


def _similarity(
    left: str,
    right: str,
) -> float:
    if not left or not right:
        return 0

    return SequenceMatcher(
        None,
        left,
        right,
    ).ratio()


def _donor_match_score(
    query: str,
    donor: Donor,
) -> float:
    first_name = _normalize_search_text(donor.first_name)

    last_name = _normalize_search_text(donor.last_name)

    full_name = (f"{first_name} {last_name}").strip()

    email = _normalize_search_text(donor.email)

    phone = re.sub(
        r"\D",
        "",
        donor.phone or "",
    )

    normalized_query = _normalize_search_text(query)

    query_phone = re.sub(
        r"\D",
        "",
        query,
    )

    searchable_values = [
        first_name,
        last_name,
        full_name,
        email,
    ]

    # Exact / substring matches always win.
    for value in searchable_values:
        if normalized_query and normalized_query in value:
            return 1.0

    if query_phone and len(query_phone) >= 4 and query_phone in phone:
        return 1.0

    # Fuzzy comparison against first name,
    # last name and full name.
    direct_score = max(
        _similarity(
            normalized_query,
            first_name,
        ),
        _similarity(
            normalized_query,
            last_name,
        ),
        _similarity(
            normalized_query,
            full_name,
        ),
    )

    # For multi-word searches, compare every
    # word against first and last name.
    query_tokens = normalized_query.split()

    token_score = 0.0

    if query_tokens:
        token_scores = []

        for token in query_tokens:
            token_scores.append(
                max(
                    _similarity(
                        token,
                        first_name,
                    ),
                    _similarity(
                        token,
                        last_name,
                    ),
                )
            )

        token_score = sum(token_scores) / len(token_scores)

    return max(
        direct_score,
        token_score,
    )


# ------------------------------------------------------------------
# READ TOOLS
# ------------------------------------------------------------------


@ai_tool(
    description=(
        "Search KehilaFlow donors by name, email or phone. "
        "The search tolerates spelling mistakes and approximate names. "
        "For example Jefrokin, Jefroykin or Jefroikin may match JEYFROKIN. "
        "Results are ranked by similarity. "
        "Use this first when the admin mentions a donor by name "
        "and you do not know their donor ID. "
        "If several donors have similar scores, do not guess which person "
        "the admin means; present the candidates or ask for clarification."
    ),
)
def search_donors(
    query: str,
    session: Session,
) -> dict:
    donors = DonorRepository(session).get_all()

    scored_matches = []

    for donor in donors:
        score = _donor_match_score(
            query,
            donor,
        )

        if score < 0.72:
            continue

        scored_matches.append(
            (
                score,
                donor,
            )
        )

    scored_matches.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    matches = scored_matches[:10]

    return {
        "count": len(scored_matches),
        "donors": [
            {
                "id": str(donor.id),
                "first_name": donor.first_name,
                "last_name": donor.last_name,
                "email": donor.email,
                "phone": donor.phone,
                "active": donor.active,
                "match_score": round(
                    score,
                    3,
                ),
            }
            for score, donor in matches
        ],
    }


@ai_tool(
    description=(
        "Get the financial summary of a donor using their donor ID. "
        "Returns total pledged, total paid and remaining balance."
    ),
)
def get_donor_summary(
    donor_id: str,
    session: Session,
) -> dict:
    service = _build_donor_service(session)

    try:
        donor_uuid = UUID(donor_id)
    except ValueError:
        return {
            "found": False,
            "error": "Invalid donor ID.",
        }

    donor = service.get_by_id(donor_uuid)

    if donor is None:
        return {
            "found": False,
            "donor_id": donor_id,
        }

    summary = service.get_summary(donor.id)

    return {
        "found": True,
        "donor": {
            "id": str(donor.id),
            "first_name": donor.first_name,
            "last_name": donor.last_name,
            "email": donor.email,
            "phone": donor.phone,
            "active": donor.active,
        },
        "total_pledged": summary.total_pledged,
        "total_paid": summary.total_paid,
        "remaining": summary.remaining,
    }


@ai_tool(
    description=(
        "Get the complete pledge and payment history "
        "of a specific donor. "
        "Use this when the admin asks what a donor pledged, "
        "what they paid, when they paid, their latest payments, "
        "or which campaigns their transactions belong to."
    ),
)
def get_donor_transactions(
    donor_id: str,
    session: Session,
) -> dict:
    try:
        donor_uuid = UUID(donor_id)
    except ValueError:
        return {
            "found": False,
            "error": "Invalid donor ID.",
        }

    donor_repository = DonorRepository(session)

    donor = donor_repository.find_by_id(donor_uuid)

    if donor is None:
        return {
            "found": False,
            "error": "Donor not found.",
        }

    pledge_repository = PledgeRepository(session)

    donation_repository = DonationRepository(session)

    campaign_repository = CampaignRepository(session)

    campaigns = {campaign.id: campaign for campaign in campaign_repository.get_all()}

    pledges = pledge_repository.get_by_donor_id(donor_uuid)

    donations = donation_repository.get_by_donor_id(donor_uuid)

    transactions = []

    for pledge in pledges:
        campaign = campaigns.get(pledge.campaign_id)

        transactions.append(
            {
                "type": "pledge",
                "amount": pledge.amount,
                "date": _date_to_string(pledge.pledge_date),
                "campaign_id": (
                    str(pledge.campaign_id) if pledge.campaign_id else None
                ),
                "campaign_name": (campaign.name if campaign else None),
            }
        )

    for donation in donations:
        campaign = campaigns.get(donation.campaign_id)

        transactions.append(
            {
                "type": "payment",
                "amount": donation.amount,
                "date": _date_to_string(donation.donation_date),
                "campaign_id": (
                    str(donation.campaign_id) if donation.campaign_id else None
                ),
                "campaign_name": (campaign.name if campaign else None),
            }
        )

    transactions.sort(
        key=lambda transaction: transaction["date"],
        reverse=True,
    )

    return {
        "found": True,
        "donor": {
            "id": str(donor.id),
            "first_name": donor.first_name,
            "last_name": donor.last_name,
        },
        "count": len(transactions),
        "transactions": transactions,
    }


@ai_tool(
    description=(
        "Get how much a specific donor pledged, paid and still owes "
        "for a specific fundraising campaign. "
        "Use this for questions such as "
        "'How much did Ilan pay for Kippour?' "
        "or 'How much does Jonathan still owe for Kippour?'. "
        "If the campaign ID is unknown, use list_campaigns first."
    ),
)
def get_donor_campaign_summary(
    donor_id: str,
    campaign_id: str,
    session: Session,
) -> dict:
    try:
        donor_uuid = UUID(donor_id)

        campaign_uuid = UUID(campaign_id)
    except ValueError:
        return {
            "found": False,
            "error": ("Invalid donor or campaign ID."),
        }

    donor = DonorRepository(session).find_by_id(donor_uuid)

    if donor is None:
        return {
            "found": False,
            "error": "Donor not found.",
        }

    campaign = CampaignRepository(session).find_by_id(campaign_uuid)

    if campaign is None:
        return {
            "found": False,
            "error": "Campaign not found.",
        }

    pledges = PledgeRepository(session).get_by_donor_id(donor_uuid)

    donations = DonationRepository(session).get_by_donor_id(donor_uuid)

    campaign_pledges = [
        pledge for pledge in pledges if pledge.campaign_id == campaign_uuid
    ]

    campaign_donations = [
        donation for donation in donations if donation.campaign_id == campaign_uuid
    ]

    total_pledged = sum(pledge.amount for pledge in campaign_pledges)

    total_paid = sum(donation.amount for donation in campaign_donations)

    return {
        "found": True,
        "donor": {
            "id": str(donor.id),
            "first_name": donor.first_name,
            "last_name": donor.last_name,
        },
        "campaign": {
            "id": str(campaign.id),
            "name": campaign.name,
        },
        "total_pledged": total_pledged,
        "total_paid": total_paid,
        "remaining": (total_pledged - total_paid),
        "pledges_count": len(campaign_pledges),
        "payments_count": len(campaign_donations),
    }


@ai_tool(
    description=(
        "List all KehilaFlow fundraising campaigns. "
        "Use this to find a campaign ID when the admin "
        "mentions a campaign by name."
    ),
)
def list_campaigns(
    session: Session,
) -> dict:
    campaigns = CampaignRepository(session).get_all()

    return {
        "count": len(campaigns),
        "campaigns": [
            {
                "id": str(campaign.id),
                "name": campaign.name,
                "description": campaign.description,
                "target_amount": campaign.target_amount,
                "active": campaign.active,
            }
            for campaign in campaigns
        ],
    }


@ai_tool(
    description=(
        "Get financial statistics for a specific fundraising campaign "
        "using its campaign ID. "
        "Returns total pledged, total paid, remaining amount "
        "and campaign progress."
    ),
)
def get_campaign_summary(
    campaign_id: str,
    session: Session,
) -> dict:
    try:
        campaign_uuid = UUID(campaign_id)
    except ValueError:
        return {
            "found": False,
            "error": "Invalid campaign ID.",
        }

    campaign_repository = CampaignRepository(session)

    donor_repository = DonorRepository(session)

    donation_repository = DonationRepository(session)

    pledge_repository = PledgeRepository(session)

    campaign = campaign_repository.find_by_id(campaign_uuid)

    if campaign is None:
        return {
            "found": False,
            "campaign_id": campaign_id,
        }

    total_pledged = 0
    total_paid = 0

    for donor in donor_repository.get_all():
        pledges = pledge_repository.get_by_donor_id(donor.id)

        donations = donation_repository.get_by_donor_id(donor.id)

        total_pledged += sum(
            pledge.amount for pledge in pledges if pledge.campaign_id == campaign_uuid
        )

        total_paid += sum(
            donation.amount
            for donation in donations
            if donation.campaign_id == campaign_uuid
        )

    remaining = total_pledged - total_paid

    progress_percent = (
        round(
            total_paid / campaign.target_amount * 100,
            2,
        )
        if campaign.target_amount > 0
        else 0
    )

    return {
        "found": True,
        "campaign": {
            "id": str(campaign.id),
            "name": campaign.name,
            "description": campaign.description,
            "target_amount": campaign.target_amount,
            "active": campaign.active,
        },
        "total_pledged": total_pledged,
        "total_paid": total_paid,
        "remaining": remaining,
        "progress_percent": progress_percent,
    }


@ai_tool(
    description=(
        "Get overall KehilaFlow dashboard statistics including "
        "total donors, active campaigns, total pledged, total paid, "
        "total outstanding and number of donors who still owe money."
    ),
)
def get_dashboard_stats(
    session: Session,
) -> dict:
    return get_dashboard_stats_service(session)


@ai_tool(
    description=(
        "List donors who still owe money. "
        "Results are ordered from the highest outstanding balance "
        "to the lowest. "
        "Use min_balance when the admin asks who owes more than "
        "a specific amount. "
        "Use limit for questions such as the top 5 or top 10 debtors."
    ),
)
def list_unpaid_donors(
    session: Session,
    limit: int = 20,
    min_balance: int = 1,
) -> dict:
    limit = min(
        max(
            limit,
            1,
        ),
        50,
    )

    min_balance = max(
        min_balance,
        1,
    )

    donor_repository = DonorRepository(session)

    donor_service = _build_donor_service(session)

    results = []

    for donor in donor_repository.get_all():
        summary = donor_service.get_summary(donor.id)

        if summary.remaining < min_balance:
            continue

        results.append(
            {
                "id": str(donor.id),
                "first_name": donor.first_name,
                "last_name": donor.last_name,
                "email": donor.email,
                "total_pledged": (summary.total_pledged),
                "total_paid": (summary.total_paid),
                "remaining": (summary.remaining),
            }
        )

    results.sort(
        key=lambda donor: donor["remaining"],
        reverse=True,
    )

    return {
        "count": len(results),
        "min_balance": min_balance,
        "donors": results[:limit],
    }


# ------------------------------------------------------------------
# WRITE TOOLS
# ------------------------------------------------------------------


@ai_tool(
    description=("Create a new donor in KehilaFlow."),
    write=True,
)
def create_donor(
    first_name: str,
    last_name: str,
    email: str,
    session: Session,
    phone: str | None = None,
) -> dict:
    donor = Donor(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
    )

    _build_donor_service(session).create(donor)

    return {
        "created": True,
        "donor": {
            "id": str(donor.id),
            "first_name": donor.first_name,
            "last_name": donor.last_name,
            "email": donor.email,
            "phone": donor.phone,
        },
    }


@ai_tool(
    description=(
        "Create a pledge for an existing KehilaFlow donor. "
        "A pledge is money the donor promises to pay."
    ),
    write=True,
)
def create_pledge(
    donor_id: str,
    amount: int,
    pledge_date: str,
    session: Session,
    campaign_id: str | None = None,
) -> dict:
    if amount <= 0:
        raise ValueError("Pledge amount must be greater than zero.")

    donor_uuid = UUID(donor_id)

    donor = DonorRepository(session).find_by_id(donor_uuid)

    if donor is None:
        raise ValueError("Donor not found.")

    campaign_uuid = UUID(campaign_id) if campaign_id else None

    if campaign_uuid is not None:
        campaign = CampaignRepository(session).find_by_id(campaign_uuid)

        if campaign is None:
            raise ValueError("Campaign not found.")

    pledge = Pledge(
        donor_id=donor_uuid,
        amount=amount,
        pledge_date=date.fromisoformat(pledge_date),
        campaign_id=campaign_uuid,
    )

    PledgeRepository(session).add(pledge)

    return {
        "created": True,
        "pledge_id": str(pledge.id),
        "donor_id": donor_id,
        "amount": amount,
        "campaign_id": campaign_id,
    }


@ai_tool(
    description=("Register money actually received from an existing donor."),
    write=True,
)
def register_donation(
    donor_id: str,
    amount: int,
    donation_date: str,
    session: Session,
    campaign_id: str | None = None,
) -> dict:
    if amount <= 0:
        raise ValueError("Donation amount must be greater than zero.")

    donor_uuid = UUID(donor_id)

    donor = DonorRepository(session).find_by_id(donor_uuid)

    if donor is None:
        raise ValueError("Donor not found.")

    campaign_uuid = UUID(campaign_id) if campaign_id else None

    if campaign_uuid is not None:
        campaign = CampaignRepository(session).find_by_id(campaign_uuid)

        if campaign is None:
            raise ValueError("Campaign not found.")

    donation = Donation(
        donor_id=donor_uuid,
        amount=amount,
        donation_date=date.fromisoformat(donation_date),
        campaign_id=campaign_uuid,
    )

    service = DonationService(
        donation_repository=DonationRepository(session),
        donor_repository=DonorRepository(session),
    )

    service.create(donation)

    return {
        "created": True,
        "donor_id": donor_id,
        "amount": amount,
        "campaign_id": campaign_id,
    }


@ai_tool(
    description=("Create a new KehilaFlow fundraising campaign."),
    write=True,
)
def create_campaign(
    name: str,
    session: Session,
    description: str | None = None,
    target_amount: int = 0,
) -> dict:
    if target_amount < 0:
        raise ValueError("Campaign target amount cannot be negative.")

    campaign = Campaign(
        name=name,
        description=description,
        target_amount=target_amount,
    )

    CampaignService(CampaignRepository(session)).create(campaign)

    return {
        "created": True,
        "campaign": {
            "id": str(campaign.id),
            "name": campaign.name,
            "description": campaign.description,
            "target_amount": campaign.target_amount,
        },
    }
