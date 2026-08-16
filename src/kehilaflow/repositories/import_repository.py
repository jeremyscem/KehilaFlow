from sqlalchemy import select
from sqlalchemy.orm import Session

from kehilaflow.database.tables import ImportBatchTable


class ImportRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def exists_by_hash(
        self,
        file_hash: str,
    ) -> bool:
        statement = select(ImportBatchTable).where(
            ImportBatchTable.file_hash == file_hash
        )

        return self._session.scalar(statement) is not None

    def add(
        self,
        file_name: str,
        file_hash: str,
    ) -> None:
        self._session.add(
            ImportBatchTable(
                file_name=file_name,
                file_hash=file_hash,
            )
        )
