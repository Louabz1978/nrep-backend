from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional

class Agency(Base):
    __tablename__ = "agencies"

    agency_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    broker_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    email: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(255))
    neighborhood: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    county: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(20))

    # Relationships
    users = relationship("User",back_populates="agency",foreign_keys="[User.agency_id]")
    broker = relationship("User",foreign_keys=[broker_id])

