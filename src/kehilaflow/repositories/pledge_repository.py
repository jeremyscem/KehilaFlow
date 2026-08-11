from datetime import date
from sqlite3 import Connection
from uuid import UUID

from kehilaflow.models.pledge import Pledge


class PledgeRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def add(self, pledge: Pledge) -> None:
        self._connection.execute(
            """
            INSERT INTO pledges (
                id,
                donor_id,
                amount,
                pledge_date,
                campaign
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(pledge.id),
                str(pledge.donor_id),
                pledge.amount,
                pledge.pledge_date.isoformat(),
                pledge.campaign,
            ),
        )

        self._connection.commit()

    def get_by_donor_id(self, donor_id: UUID) -> list[Pledge]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM pledges
            WHERE donor_id = ?
            """,
            (str(donor_id),),
        ).fetchall()

        return [
            Pledge(
                id=UUID(row["id"]),
                donor_id=UUID(row["donor_id"]),
                amount=row["amount"],
                pledge_date=date.fromisoformat(row["pledge_date"]),
                campaign=row["campaign"],
            )
            for row in rows
        ]
