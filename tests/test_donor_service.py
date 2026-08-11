import pytest

from kehilaflow.exceptions.donor_exceptions import (
    DonorAlreadyExistsError,
    DonorNotFoundError,
)
from kehilaflow.models.donor import Donor
from kehilaflow.repositories.donation_repository import DonationRepository
from kehilaflow.repositories.donor_repository import DonorRepository
from kehilaflow.repositories.pledge_repository import PledgeRepository
from kehilaflow.services.donor_service import DonorService


@pytest.fixture
def donor() -> Donor:
    return Donor(
        first_name="Jeremy",
        last_name="Scemama",
        email="scemama@gmail.com",
    )


@pytest.fixture
def donor_repository() -> DonorRepository:
    return DonorRepository()


@pytest.fixture
def donation_repository() -> DonationRepository:
    return DonationRepository()


@pytest.fixture
def service(
    donor_repository: DonorRepository,
    donation_repository: DonationRepository,
    pledge_repository: PledgeRepository,
) -> DonorService:
    return DonorService(
        donor_repository=donor_repository,
        donation_repository=donation_repository,
        pledge_repository=pledge_repository,
    )


@pytest.fixture
def pledge_repository() -> PledgeRepository:
    return PledgeRepository()


def test_create_donor(service: DonorService, donor: Donor) -> None:
    service.create(donor)

    assert service.get_by_email("scemama@gmail.com") == donor


def test_create_donor_with_existing_email_raises_error(
    service: DonorService,
    donor: Donor,
) -> None:
    service.create(donor)

    with pytest.raises(DonorAlreadyExistsError):
        service.create(donor)


def test_delete_existing_donor(
    service: DonorService,
    donor: Donor,
) -> None:
    service.create(donor)

    service.delete("scemama@gmail.com")

    assert service.get_by_email("scemama@gmail.com") is None


def test_delete_non_existing_donor_raises_error(
    service: DonorService,
) -> None:
    with pytest.raises(DonorNotFoundError):
        service.delete("scemama@gmail.com")


def test_update_existing_donor(
    service: DonorService,
    donor: Donor,
) -> None:
    service.create(donor)

    updated_donor = Donor(
        id=donor.id,
        first_name="Jeremy",
        last_name="Scemama",
        email="newemail@gmail.com",
        phone="0500000000",
        active=False,
    )

    service.update(updated_donor)

    assert service.get_by_email("newemail@gmail.com") == updated_donor


def test_update_non_existing_donor_raises_error(
    service: DonorService,
    donor: Donor,
) -> None:
    with pytest.raises(DonorNotFoundError):
        service.update(donor)
