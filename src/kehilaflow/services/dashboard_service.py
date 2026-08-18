from collections import defaultdict

from sqlalchemy.orm import Session

from kehilaflow.repositories.campaign_repository import (
    CampaignRepository,
)
from kehilaflow.repositories.donation_repository import (
    DonationRepository,
)
from kehilaflow.repositories.donor_repository import (
    DonorRepository,
)
from kehilaflow.repositories.pledge_repository import (
    PledgeRepository,
)


def get_dashboard_stats(
    session: Session,
) -> dict[str, int]:
    donor_repository = DonorRepository(session)
    donation_repository = DonationRepository(session)
    pledge_repository = PledgeRepository(session)
    campaign_repository = CampaignRepository(session)

    donors = donor_repository.get_all()
    campaigns = campaign_repository.get_all()

    total_pledged = 0
    total_paid = 0

    pledged_by_donor: dict[
        object,
        int,
    ] = defaultdict(int)

    paid_by_donor: dict[
        object,
        int,
    ] = defaultdict(int)

    for donor in donors:
        pledges = pledge_repository.get_by_donor_id(donor.id)

        donations = donation_repository.get_by_donor_id(donor.id)

        for pledge in pledges:
            total_pledged += pledge.amount
            pledged_by_donor[donor.id] += pledge.amount

        for donation in donations:
            total_paid += donation.amount
            paid_by_donor[donor.id] += donation.amount

    total_outstanding = 0
    donors_with_balance = 0

    for donor in donors:
        remaining = pledged_by_donor[donor.id] - paid_by_donor[donor.id]

        if remaining > 0:
            total_outstanding += remaining
            donors_with_balance += 1

    active_campaigns = sum(campaign.active for campaign in campaigns)

    return {
        "total_donors": len(donors),
        "active_campaigns": active_campaigns,
        "total_pledged": total_pledged,
        "total_paid": total_paid,
        "total_outstanding": total_outstanding,
        "donors_with_balance": donors_with_balance,
    }
