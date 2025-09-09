from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import Dict, Any
class License(Base):
    __tablename__ = "licenses"

    license_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    lic_num: Mapped[str] = mapped_column(String(16))
    lic_status: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    lic_type : Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # ForeignKey
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True)
    agency_id: Mapped[int] = mapped_column(ForeignKey("agencies.agency_id"), nullable=False)

    # Relationship
    user = relationship("User", back_populates="licenses")
    agency = relationship("Agency", back_populates="licenses")
    