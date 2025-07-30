from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from app.database import Base


class Address(Base):
    __tablename__ = "addresses"

    address_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    apt: Mapped[int] = mapped_column(Integer, nullable=False)
    area: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(255))
    county: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    building_num: Mapped[Optional[str]] = mapped_column(String)
    street: Mapped[Optional[str]] = mapped_column(String)

    # ForeignKey
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.property_id", ondelete="CASCADE"), unique=True, nullable=True)

    # Relationship
    created_by_user = relationship("User", back_populates="address_created", foreign_keys=[created_by])
    properties: Mapped["Property"] = relationship(back_populates="address")

    agencies = relationship("Agency", back_populates="address", uselist=False)

    # properties = relationship("Property", back_populates="address")
    