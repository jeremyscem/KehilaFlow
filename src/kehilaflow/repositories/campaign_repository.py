from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from kehilaflow.database.tables import CampaignTable
from kehilaflow.models.campaign import Campaign


class CampaignRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, campaign: Campaign) -> None:
        table = CampaignTable(
            id=str(campaign.id),
            name=campaign.name,
            description=campaign.description,
            target_amount=campaign.target_amount,
            active=campaign.active,
        )

        self._session.add(table)
        self._session.commit()

    def get_all(self) -> list[Campaign]:
        campaigns = self._session.scalars(select(CampaignTable)).all()

        return [
            Campaign(
                id=UUID(campaign.id),
                name=campaign.name,
                description=campaign.description,
                target_amount=campaign.target_amount,
                active=campaign.active,
            )
            for campaign in campaigns
        ]

    def find_by_id(self, campaign_id: UUID) -> Campaign | None:
        campaign = self._session.get(
            CampaignTable,
            str(campaign_id),
        )

        if campaign is None:
            return None

        return Campaign(
            id=UUID(campaign.id),
            name=campaign.name,
            description=campaign.description,
            target_amount=campaign.target_amount,
            active=campaign.active,
        )
