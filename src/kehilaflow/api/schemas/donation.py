from datetime import date
from uuid import UUID

from pydantic import BaseModel


class DonationCreate(BaseModel):
    amount: int
    donation_date: date
    campaign_id: UUID | None = None
