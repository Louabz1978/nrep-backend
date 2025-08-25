from sqlalchemy import String, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.addresses_model import Address

class Agency(Base):
    __tablename__ = "agencies"

    agency_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    
    # ForeignKey
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    broker_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)

    # Relationships
    created_by_user = relationship("User", back_populates="agency_created", foreign_keys=[created_by])
    broker = relationship("User", back_populates="agency_broker", foreign_keys=[broker_id])
    address: Mapped["Address"] = relationship(
        back_populates="agencies",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined"
    )
    
    licenses = relationship("License", back_populates="agency", uselist=False)
