from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4


@dataclass
class Pledge:
    donor_id: UUID
    amount: int
    pledge_date: date

    id: UUID = field(default_factory=uuid4)
    campaign_id: UUID | None = None
