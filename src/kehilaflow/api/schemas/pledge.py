from datetime import date
from uuid import UUID

from pydantic import BaseModel


class PledgeCreate(BaseModel):
    amount: int
    pledge_date: date
    campaign_id: UUID | None = None
