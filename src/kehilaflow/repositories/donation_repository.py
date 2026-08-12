from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from kehilaflow.database.tables import DonationTable
from kehilaflow.models.donation import Donation


class DonationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, donation: Donation) -> None:
        donation_table = DonationTable(
            donor_id=str(donation.donor_id),
            amount=donation.amount,
            donation_date=donation.donation_date.isoformat(),
            campaign_id=(str(donation.campaign_id) if donation.campaign_id else None),
        )

        self._session.add(donation_table)
        self._session.commit()

    def get_by_donor_id(
        self,
        donor_id: UUID,
    ) -> list[Donation]:
        donations = self._session.scalars(
            select(DonationTable).where(DonationTable.donor_id == str(donor_id))
        ).all()

        return [
            Donation(
                donor_id=UUID(donation.donor_id),
                amount=donation.amount,
                donation_date=date.fromisoformat(donation.donation_date),
                campaign_id=(
                    UUID(donation.campaign_id) if donation.campaign_id else None
                ),
            )
            for donation in donations
        ]
