from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from kehilaflow.database.tables import DonorTable
from kehilaflow.models.donor import Donor


class DonorRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, donor: Donor) -> None:
        donor_table = DonorTable(
            id=str(donor.id),
            first_name=donor.first_name,
            last_name=donor.last_name,
            email=donor.email,
            phone=donor.phone,
            active=donor.active,
        )

        self._session.add(donor_table)
        self._session.commit()

    def find_by_email(self, email: str) -> Donor | None:
        donor_table = self._session.scalar(
            select(DonorTable).where(DonorTable.email == email)
        )

        if donor_table is None:
            return None

        return self._to_donor(donor_table)

    def find_by_id(self, donor_id: UUID) -> Donor | None:
        donor_table = self._session.get(
            DonorTable,
            str(donor_id),
        )

        if donor_table is None:
            return None

        return self._to_donor(donor_table)

    def get_all(self) -> list[Donor]:
        donors = self._session.scalars(select(DonorTable)).all()

        return [self._to_donor(donor) for donor in donors]

    def update(self, donor: Donor) -> None:
        donor_table = self._session.get(
            DonorTable,
            str(donor.id),
        )

        if donor_table is None:
            return

        donor_table.first_name = donor.first_name
        donor_table.last_name = donor.last_name
        donor_table.email = donor.email
        donor_table.phone = donor.phone
        donor_table.active = donor.active

        self._session.commit()

    def delete(self, email: str) -> bool:
        donor_table = self._session.scalar(
            select(DonorTable).where(DonorTable.email == email)
        )

        if donor_table is None:
            return False

        self._session.delete(donor_table)
        self._session.commit()

        return True

    def _to_donor(self, donor_table: DonorTable) -> Donor:
        return Donor(
            id=UUID(donor_table.id),
            first_name=donor_table.first_name,
            last_name=donor_table.last_name,
            email=donor_table.email,
            phone=donor_table.phone,
            active=donor_table.active,
        )
