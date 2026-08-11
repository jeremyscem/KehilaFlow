from uuid import UUID

from kehilaflow.dto.donor_summary import DonorSummary
from kehilaflow.exceptions.donor_exceptions import (
    DonorAlreadyExistsError,
    DonorNotFoundError,
)
from kehilaflow.models.donor import Donor
from kehilaflow.repositories.donation_repository import DonationRepository
from kehilaflow.repositories.donor_repository import DonorRepository
from kehilaflow.repositories.pledge_repository import PledgeRepository


class DonorService:
    def __init__(
        self,
        donor_repository: DonorRepository,
        donation_repository: DonationRepository,
        pledge_repository: PledgeRepository,
    ) -> None:
        self._donor_repository = donor_repository
        self._donation_repository = donation_repository
        self._pledge_repository = pledge_repository

    def create(self, donor: Donor) -> None:
        existing_donor = self._donor_repository.find_by_email(donor.email)

        if existing_donor is not None:
            raise DonorAlreadyExistsError(
                f"A donor with email {donor.email} already exists."
            )

        self._donor_repository.add(donor)

    def get_by_email(self, email: str) -> Donor | None:
        return self._donor_repository.find_by_email(email)

    def get_by_id(self, donor_id: UUID) -> Donor | None:
        return self._donor_repository.find_by_id(donor_id)

    def update(self, donor: Donor) -> None:
        existing_donor = self._donor_repository.find_by_id(donor.id)

        if existing_donor is None:
            raise DonorNotFoundError(f"No donor found with id {donor.id}.")

        self._donor_repository.update(donor)

    def delete(self, email: str) -> None:
        deleted = self._donor_repository.delete(email)

        if not deleted:
            raise DonorNotFoundError(f"No donor found with email {email}.")

    def get_all(self) -> list[Donor]:
        return self._donor_repository.get_all()

    def get_summary(self, donor_id: UUID) -> DonorSummary:
        donor = self._donor_repository.find_by_id(donor_id)

        if donor is None:
            raise DonorNotFoundError(f"No donor found with id {donor_id}.")

        donations = self._donation_repository.get_by_donor_id(donor_id)
        pledges = self._pledge_repository.get_by_donor_id(donor_id)

        return DonorSummary(
            donor=donor,
            donations=donations,
            pledges=pledges,
        )
