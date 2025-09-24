from sqlalchemy import String, ForeignKey, Integer, TIMESTAMP, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.addresses_model import Address

agency_brokers = Table(
    "agency_brokers",
    Base.metadata,
    Column("agency_id", ForeignKey("agencies.agency_id", ondelete="CASCADE"), primary_key=True),
    Column("broker_id", ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True),
)
class Agency(Base):
    __tablename__ = "agencies"

    agency_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    
    # ForeignKey
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)

    # Relationships
    created_by_user = relationship("User", back_populates="agency_created", foreign_keys=[created_by])
    address: Mapped["Address"] = relationship(
        back_populates="agencies",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined"
    )
    #many_to_many relationship for brokers
    brokers = relationship("User", secondary=agency_brokers, back_populates="agency_brokers")

    licenses = relationship("License", back_populates="agency", uselist=False)
