from pydantic import BaseModel, computed_field

from kehilaflow.models.donation import Donation
from kehilaflow.models.donor import Donor
from kehilaflow.models.pledge import Pledge


class DonorCreate(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None


class DonorSummaryResponse(BaseModel):
    donor: Donor
    pledges: list[Pledge]
    donations: list[Donation]

    @computed_field
    @property
    def total_pledged(self) -> int:
        return sum(pledge.amount for pledge in self.pledges)

    @computed_field
    @property
    def total_paid(self) -> int:
        return sum(donation.amount for donation in self.donations)

    @computed_field
    @property
    def remaining(self) -> int:
        return self.total_pledged - self.total_paid

    model_config = {"from_attributes": True}
