from datetime import date

from kehilaflow.models.donation import Donation
from kehilaflow.models.donor import Donor
from kehilaflow.models.pledge import Pledge
from kehilaflow.repositories.donation_repository import DonationRepository
from kehilaflow.repositories.donor_repository import DonorRepository
from kehilaflow.repositories.pledge_repository import PledgeRepository
from kehilaflow.services.donation_service import DonationService
from kehilaflow.services.donor_service import DonorService
from kehilaflow.services.pledge_service import PledgeService


def main() -> None:
    donor_repository = DonorRepository()
    donation_repository = DonationRepository()
    pledge_repository = PledgeRepository()
    donor_service = DonorService(
        donor_repository=donor_repository,
        donation_repository=donation_repository,
        pledge_repository=pledge_repository,
    )

    pledge_service = PledgeService(
        pledge_repository=pledge_repository,
    )

    donation_service = DonationService(
        donation_repository=donation_repository,
        donor_repository=donor_repository,
    )

    donor = Donor(
        first_name="Jeremy",
        last_name="Scemama",
        email="scemama@gmail.com",
    )

    pledge_service.create(
        Pledge(
            donor_id=donor.id,
            amount=1200,
            pledge_date=date(2026, 8, 1),
        )
    )

    pledge_service.create(
        Pledge(
            donor_id=donor.id,
            amount=800,
            pledge_date=date(2026, 8, 2),
        )
    )
    donor_service.create(donor)

    donation_service.create(
        Donation(
            donor_id=donor.id,
            amount=500,
            donation_date=date(2026, 8, 5),
        )
    )

    donation_service.create(
        Donation(
            donor_id=donor.id,
            amount=300,
            donation_date=date(2026, 8, 6),
        )
    )
    summary = donor_service.get_summary(donor.id)

    print(summary.total_pledged)
    print(summary.total_paid)
    print(summary.remaining)
