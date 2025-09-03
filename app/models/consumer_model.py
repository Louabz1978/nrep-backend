from __future__ import annotations

from sqlalchemy import BigInteger, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime
from sqlalchemy import Date

class Consumer(Base):
    __tablename__ = "consumers"

    consumer_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    father_name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    mother_name_surname: Mapped[str] = mapped_column(String, nullable=False)
    place_birth: Mapped[str] = mapped_column(String, nullable=False)
    date_birth: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    registry: Mapped[str] = mapped_column(String, nullable=False)
    national_number: Mapped[int] = mapped_column(BigInteger)
    
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    
    created_by_type: Mapped[str] = mapped_column(String, nullable=False)
    
    # ForeignKey
    created_by : Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="consumer_created", foreign_keys=[created_by])
