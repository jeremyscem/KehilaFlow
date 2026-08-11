from datetime import date

from pydantic import BaseModel


class PledgeCreate(BaseModel):
    amount: int
    pledge_date: date
    campaign: str | None = None
