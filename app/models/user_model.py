from sqlalchemy import String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String(20))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    agency_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agencies.agency_id"), nullable=True, default=None)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    neighborhood: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(255))
    county: Mapped[Optional[str]] = mapped_column(String(255))
    lic_num: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    # Relationships
    agency = relationship("Agency",back_populates="users",foreign_keys=[agency_id])
    properties = relationship("Property", back_populates="owner", foreign_keys="Property.owner_id")
    agent_properties = relationship("Property", back_populates="agent", foreign_keys="Property.agent_id")
    licenses = relationship("License", back_populates="user", uselist=False)
    favorites = relationship("Favorite", back_populates="user")
    brokered_agencies = relationship("Agency", back_populates="broker", foreign_keys="Agency.broker_id")
