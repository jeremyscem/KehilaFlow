from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = "postgresql+psycopg://kehilaflow:kehilaflow@localhost:5432/kehilaflow"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_session() -> Generator[Session]:
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
