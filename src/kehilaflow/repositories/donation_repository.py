from datetime import date
from sqlite3 import Connection
from uuid import UUID

from kehilaflow.models.donation import Donation


class DonationRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def add(self, donation: Donation) -> None:
        self._connection.execute(
            """
            INSERT INTO donations (
                donor_id,
                amount,
                donation_date,
                campaign
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                str(donation.donor_id),
                donation.amount,
                donation.donation_date.isoformat(),
                donation.campaign,
            ),
        )

        self._connection.commit()

    def get_by_donor_id(self, donor_id: UUID) -> list[Donation]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM donations
            WHERE donor_id = ?
            """,
            (str(donor_id),),
        ).fetchall()

        return [
            Donation(
                donor_id=UUID(row["donor_id"]),
                amount=row["amount"],
                donation_date=date.fromisoformat(row["donation_date"]),
                campaign=row["campaign"],
            )
            for row in rows
        ]
