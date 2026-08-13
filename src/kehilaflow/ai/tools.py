from datetime import date
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
from kehilaflow.services.donation_service import DonationService
from kehilaflow.services.donor_service import DonorService


def _build_donor_service(session: Session) -> DonorService:
    return DonorService(
        donor_repository=DonorRepository(session),
        donation_repository=DonationRepository(session),
        pledge_repository=PledgeRepository(session),
    )


# ------------------------------------------------------------------
# READ TOOLS
# ------------------------------------------------------------------


@ai_tool(
    description=(
        "Search KehilaFlow donors by name, email or phone. "
        "Use this first when the admin mentions a donor by name "
        "and you do not know their donor ID."
    ),
)
def search_donors(
    query: str,
    session: Session,
) -> dict:
    donors = DonorRepository(session).get_all()

    normalized_query = query.casefold()

    matches = [
        donor
        for donor in donors
        if normalized_query
        in (
            f"{donor.first_name} {donor.last_name} {donor.email} {donor.phone or ''}"
        ).casefold()
    ]

    return {
        "count": len(matches),
        "donors": [
            {
                "id": str(donor.id),
                "first_name": donor.first_name,
                "last_name": donor.last_name,
                "email": donor.email,
                "phone": donor.phone,
                "active": donor.active,
            }
            for donor in matches[:10]
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
    description="List all KehilaFlow fundraising campaigns.",
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
        "using its campaign ID."
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
        "Get overall KehilaFlow statistics including pledged, paid, "
        "remaining, active donors and active campaigns."
    ),
)
def get_dashboard_stats(
    session: Session,
) -> dict:
    donor_repository = DonorRepository(session)
    donation_repository = DonationRepository(session)
    pledge_repository = PledgeRepository(session)
    campaign_repository = CampaignRepository(session)

    donors = donor_repository.get_all()
    campaigns = campaign_repository.get_all()

    total_pledged = 0
    total_paid = 0

    for donor in donors:
        total_pledged += sum(
            pledge.amount for pledge in pledge_repository.get_by_donor_id(donor.id)
        )

        total_paid += sum(
            donation.amount
            for donation in donation_repository.get_by_donor_id(donor.id)
        )

    return {
        "total_pledged": total_pledged,
        "total_paid": total_paid,
        "remaining": total_pledged - total_paid,
        "active_donors": sum(1 for donor in donors if donor.active),
        "active_campaigns": sum(1 for campaign in campaigns if campaign.active),
    }


@ai_tool(
    description=(
        "List donors who still have money to pay, ordered from "
        "the highest outstanding balance to the lowest."
    ),
)
def list_unpaid_donors(
    session: Session,
    limit: int = 20,
) -> dict:
    limit = min(max(limit, 1), 50)

    donor_repository = DonorRepository(session)
    donor_service = _build_donor_service(session)

    results = []

    for donor in donor_repository.get_all():
        summary = donor_service.get_summary(donor.id)

        if summary.remaining <= 0:
            continue

        results.append(
            {
                "id": str(donor.id),
                "first_name": donor.first_name,
                "last_name": donor.last_name,
                "email": donor.email,
                "total_pledged": summary.total_pledged,
                "total_paid": summary.total_paid,
                "remaining": summary.remaining,
            }
        )

    results.sort(
        key=lambda donor: donor["remaining"],
        reverse=True,
    )

    return {
        "count": len(results),
        "donors": results[:limit],
    }


# ------------------------------------------------------------------
# WRITE TOOLS
# ------------------------------------------------------------------


@ai_tool(
    description="Create a new donor in KehilaFlow.",
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
    description="Create a new KehilaFlow fundraising campaign.",
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
