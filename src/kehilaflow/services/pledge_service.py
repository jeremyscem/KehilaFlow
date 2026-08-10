from uuid import UUID

from kehilaflow.models.pledge import Pledge
from kehilaflow.repositories.pledge_repository import PledgeRepository


class PledgeService:
    def __init__(self, pledge_repository: PledgeRepository) -> None:
        self._pledge_repository = pledge_repository

    def create(self, pledge: Pledge) -> None:
        self._pledge_repository.add(pledge)

    def get_by_donor_id(self, donor_id: UUID) -> list[Pledge]:
        return self._pledge_repository.get_by_donor_id(donor_id)
