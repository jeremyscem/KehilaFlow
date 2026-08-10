from uuid import UUID

from kehilaflow.exceptions.donor_exceptions import DonorNotFoundError
from kehilaflow.models.donation import Donation
from kehilaflow.repositories.donation_repository import DonationRepository
from kehilaflow.repositories.donor_repository import DonorRepository


class DonationService:
    def __init__(
        self,
        donation_repository: DonationRepository,
        donor_repository: DonorRepository,
    ) -> None:
        self._donation_repository = donation_repository
        self._donor_repository = donor_repository

    def create(self, donation: Donation) -> None:
        donor = self._donor_repository.find_by_id(donation.donor_id)

        if donor is None:
            raise DonorNotFoundError(f"No donor found with id {donation.donor_id}.")

        self._donation_repository.add(donation)

    def get_by_donor_id(self, donor_id: UUID) -> list[Donation]:
        return self._donation_repository.get_by_donor_id(donor_id)

    def get_total_by_donor_id(self, donor_id: UUID) -> int:
        donations = self._donation_repository.get_by_donor_id(donor_id)

        return sum(donation.amount for donation in donations)
