from kehilaflow.models.campaign import Campaign
from kehilaflow.repositories.campaign_repository import CampaignRepository


class CampaignService:
    def __init__(self, repository: CampaignRepository) -> None:
        self._repository = repository

    def create(self, campaign: Campaign) -> None:
        self._repository.add(campaign)

    def get_all(self) -> list[Campaign]:
        return self._repository.get_all()
