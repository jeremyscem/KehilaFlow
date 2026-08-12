from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass
class Donation:
    donor_id: UUID
    amount: int
    donation_date: date
    campaign_id: UUID | None = None
