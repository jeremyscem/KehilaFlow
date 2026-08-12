from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Campaign:
    name: str
    id: UUID = field(default_factory=uuid4)
    description: str | None = None
    target_amount: int = 0
    active: bool = True
