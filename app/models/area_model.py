from app.database import Base
from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy.sql import func

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.county_model import County

class Area(Base):
    __tablename__ = "areas"

    area_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    created_by : Mapped[int] = mapped_column(Integer, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    updated_by : Mapped[int] = mapped_column(Integer, nullable=True)

    # ForeignKey
    county_id: Mapped[int] = mapped_column(ForeignKey("counties.county_id", ondelete="CASCADE"))

    # Relationships
    county: Mapped["County"] = relationship("County", back_populates="areas")
