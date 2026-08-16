from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from kehilaflow.database.orm import Base


class DonorTable(Base):
    __tablename__ = "donors"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    first_name: Mapped[str] = mapped_column(String)

    last_name: Mapped[str] = mapped_column(String)

    email: Mapped[str | None] = mapped_column(
        String,
        unique=True,
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


class DonationTable(Base):
    __tablename__ = "donations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    donor_id: Mapped[str] = mapped_column(
        ForeignKey("donors.id"),
    )

    amount: Mapped[int] = mapped_column(Integer)
    donation_date: Mapped[str] = mapped_column(String)
    campaign_id: Mapped[str | None] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=True,
    )


class PledgeTable(Base):
    __tablename__ = "pledges"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    donor_id: Mapped[str] = mapped_column(
        ForeignKey("donors.id"),
    )

    amount: Mapped[int] = mapped_column(Integer)
    pledge_date: Mapped[str] = mapped_column(String)
    campaign_id: Mapped[str | None] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=True,
    )


class CampaignTable(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    target_amount: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


class ImportBatchTable(Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    file_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    file_hash: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
