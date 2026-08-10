from uuid import UUID

from kehilaflow.models.donation import Donation


class DonationRepository:
    def __init__(self) -> None:
        self._donations: list[Donation] = []

    def add(self, donation: Donation) -> None:
        self._donations.append(donation)

    def get_by_donor_id(self, donor_id: UUID) -> list[Donation]:
        return [
            donation for donation in self._donations if donation.donor_id == donor_id
        ]
