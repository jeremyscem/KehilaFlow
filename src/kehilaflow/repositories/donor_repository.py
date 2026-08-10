from uuid import UUID

from kehilaflow.models.donor import Donor


class DonorRepository:
    def __init__(self) -> None:
        self._donors: list[Donor] = []

    def add(self, donor: Donor) -> None:
        self._donors.append(donor)

    def find_by_email(self, email: str) -> Donor | None:
        for donor in self._donors:
            if donor.email == email:
                return donor

        return None

    def get_all(self) -> list[Donor]:
        return self._donors.copy()

    def update(self, donor: Donor) -> None:
        for index, existing_donor in enumerate(self._donors):
            if existing_donor.email == donor.email:
                self._donors[index] = donor
                return

    def delete(self, email: str) -> bool:
        for index, donor in enumerate(self._donors):
            if donor.email == email:
                del self._donors[index]
                return True
        return False

    def find_by_id(self, donor_id: UUID) -> Donor | None:
        for donor in self._donors:
            if donor.id == donor_id:
                return donor

        return None
