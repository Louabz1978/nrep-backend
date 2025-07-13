from sqlalchemy import String, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

class Agency(Base):
    __tablename__ = "agencies"

    agency_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    broker_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    email: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(20))
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.address_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    created_by : Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"),nullable=True)
    
    # Relationships
    broker = relationship("User",foreign_keys=[broker_id])
    licenses = relationship("License", back_populates="agency")
    address = relationship("Address", back_populates="agencies")