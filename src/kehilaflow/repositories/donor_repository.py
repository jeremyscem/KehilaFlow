from sqlite3 import Connection
from uuid import UUID

from kehilaflow.models.donor import Donor


class DonorRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def add(self, donor: Donor) -> None:
        self._connection.execute(
            """
            INSERT INTO donors (
                id,
                first_name,
                last_name,
                email,
                phone,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(donor.id),
                donor.first_name,
                donor.last_name,
                donor.email,
                donor.phone,
                donor.active,
            ),
        )

        self._connection.commit()

    def find_by_email(self, email: str) -> Donor | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM donors
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

        if row is None:
            return None

        return self._to_donor(row)

    def find_by_id(self, donor_id: UUID) -> Donor | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM donors
            WHERE id = ?
            """,
            (str(donor_id),),
        ).fetchone()

        if row is None:
            return None

        return self._to_donor(row)

    def get_all(self) -> list[Donor]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM donors
            """
        ).fetchall()

        return [self._to_donor(row) for row in rows]

    def update(self, donor: Donor) -> None:
        self._connection.execute(
            """
            UPDATE donors
            SET
                first_name = ?,
                last_name = ?,
                email = ?,
                phone = ?,
                active = ?
            WHERE id = ?
            """,
            (
                donor.first_name,
                donor.last_name,
                donor.email,
                donor.phone,
                donor.active,
                str(donor.id),
            ),
        )

        self._connection.commit()

    def delete(self, email: str) -> bool:
        cursor = self._connection.execute(
            """
            DELETE FROM donors
            WHERE email = ?
            """,
            (email,),
        )

        self._connection.commit()

        return cursor.rowcount > 0

    def _to_donor(self, row) -> Donor:
        return Donor(
            id=UUID(row["id"]),
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            phone=row["phone"],
            active=bool(row["active"]),
        )
