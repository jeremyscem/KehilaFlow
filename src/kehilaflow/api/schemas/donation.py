from datetime import date

from pydantic import BaseModel


class DonationCreate(BaseModel):
    amount: int
    donation_date: date
    campaign: str | None = None
