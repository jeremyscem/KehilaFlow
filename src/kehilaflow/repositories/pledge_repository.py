from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from kehilaflow.database.tables import PledgeTable
from kehilaflow.models.pledge import Pledge


class PledgeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, pledge: Pledge) -> None:
        pledge_table = PledgeTable(
            id=str(pledge.id),
            donor_id=str(pledge.donor_id),
            amount=pledge.amount,
            pledge_date=pledge.pledge_date.isoformat(),
            campaign_id=(str(pledge.campaign_id) if pledge.campaign_id else None),
        )

        self._session.add(pledge_table)
        self._session.commit()

    def get_by_donor_id(
        self,
        donor_id: UUID,
    ) -> list[Pledge]:
        pledges = self._session.scalars(
            select(PledgeTable).where(PledgeTable.donor_id == str(donor_id))
        ).all()

        return [
            Pledge(
                id=UUID(pledge.id),
                donor_id=UUID(pledge.donor_id),
                amount=pledge.amount,
                pledge_date=date.fromisoformat(pledge.pledge_date),
                campaign_id=(UUID(pledge.campaign_id) if pledge.campaign_id else None),
            )
            for pledge in pledges
        ]
