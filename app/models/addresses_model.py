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
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True)
    property_id: Mapped[Optional[int]] = mapped_column(ForeignKey("properties.property_id", ondelete="CASCADE"), nullable=True, unique=True)

    # Relationship
    created_by_user = relationship("User", back_populates="address_created", foreign_keys=[created_by])
    user = relationship("User", back_populates="address", foreign_keys=[user_id], passive_deletes=True, uselist=False)

    agencies = relationship("Agency", back_populates="address", uselist=False)

    property = relationship("Property", back_populates="address", uselist=False)
    