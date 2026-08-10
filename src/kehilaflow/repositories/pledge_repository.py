from uuid import UUID

from kehilaflow.models.pledge import Pledge


class PledgeRepository:
    def __init__(self) -> None:
        self._pledges: list[Pledge] = []

    def add(self, pledge: Pledge) -> None:
        self._pledges.append(pledge)

    def get_by_donor_id(self, donor_id: UUID) -> list[Pledge]:
        return [pledge for pledge in self._pledges if pledge.donor_id == donor_id]
