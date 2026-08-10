from datetime import date
from uuid import uuid4

import pytest

from kehilaflow.exceptions.donor_exceptions import DonorNotFoundError
from kehilaflow.models.donation import Donation
from kehilaflow.models.donor import Donor
from kehilaflow.repositories.donation_repository import DonationRepository
from kehilaflow.repositories.donor_repository import DonorRepository
from kehilaflow.services.donation_service import DonationService


def test_create_donation() -> None:

    donor_id = uuid4()

    donation = Donation(
        donor_id=donor_id,
        amount=500,
        donation_date=date(2026, 8, 5),
        campaign="Kiddush",
    )

    assert donation.amount == 500
    assert donation.donor_id == donor_id


def test_create_donation_for_existing_donor() -> None:
    donor_repository = DonorRepository()
    donation_repository = DonationRepository()

    donor = Donor(
        first_name="Jeremy",
        last_name="Scemama",
        email="scemama@gmail.com",
    )

    donor_repository.add(donor)

    service = DonationService(
        donation_repository=donation_repository,
        donor_repository=donor_repository,
    )

    donation = Donation(
        donor_id=donor.id,
        amount=500,
        donation_date=date(2026, 8, 5),
        campaign="Kiddush",
    )

    service.create(donation)

    assert donation_repository.get_by_donor_id(donor.id) == [donation]


def test_create_donation_for_non_existing_donor_raises_error() -> None:
    donor_repository = DonorRepository()
    donation_repository = DonationRepository()

    service = DonationService(
        donation_repository=donation_repository,
        donor_repository=donor_repository,
    )

    donation = Donation(
        donor_id=uuid4(),
        amount=500,
        donation_date=date(2026, 8, 5),
        campaign="Kiddush",
    )

    with pytest.raises(DonorNotFoundError):
        service.create(donation)


def test_get_donations_by_donor_id() -> None:
    donor_repository = DonorRepository()
    donation_repository = DonationRepository()

    donor = Donor(
        first_name="Jeremy",
        last_name="Scemama",
        email="scemama@gmail.com",
    )

    donor_repository.add(donor)

    service = DonationService(
        donation_repository=donation_repository,
        donor_repository=donor_repository,
    )

    donation_1 = Donation(
        donor_id=donor.id,
        amount=500,
        donation_date=date(2026, 8, 5),
    )

    donation_2 = Donation(
        donor_id=donor.id,
        amount=300,
        donation_date=date(2026, 8, 6),
    )

    service.create(donation_1)
    service.create(donation_2)

    assert service.get_by_donor_id(donor.id) == [
        donation_1,
        donation_2,
    ]


def test_get_total_by_donor_id() -> None:
    donor_repository = DonorRepository()
    donation_repository = DonationRepository()

    donor = Donor(
        first_name="Jeremy",
        last_name="Scemama",
        email="scemama@gmail.com",
    )

    donor_repository.add(donor)

    service = DonationService(
        donation_repository=donation_repository,
        donor_repository=donor_repository,
    )

    service.create(
        Donation(
            donor_id=donor.id,
            amount=500,
            donation_date=date(2026, 8, 5),
        )
    )

    service.create(
        Donation(
            donor_id=donor.id,
            amount=300,
            donation_date=date(2026, 8, 6),
        )
    )

    assert service.get_total_by_donor_id(donor.id) == 800
