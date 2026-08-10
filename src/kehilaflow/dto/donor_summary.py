from dataclasses import dataclass

from kehilaflow.models.donation import Donation
from kehilaflow.models.donor import Donor
from kehilaflow.models.pledge import Pledge


@dataclass
class DonorSummary:
    donor: Donor
    donations: list[Donation]
    pledges: list[Pledge]

    @property
    def total_paid(self) -> int:
        return sum(donation.amount for donation in self.donations)

    @property
    def total_pledged(self) -> int:
        return sum(pledge.amount for pledge in self.pledges)

    @property
    def remaining(self) -> int:
        return self.total_pledged - self.total_paid
