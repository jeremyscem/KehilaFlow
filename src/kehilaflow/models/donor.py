from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Donor:
    first_name: str
    last_name: str
    id: UUID = field(default_factory=uuid4)
    email: str | None = None
    phone: str | None = None
    active: bool = True
