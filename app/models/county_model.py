from app.database import Base
from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy.sql import func

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.city_model import City
    from app.models.area_model import Area

class County(Base):
    __tablename__ = "counties"

    county_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    created_by : Mapped[int] = mapped_column(Integer, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    updated_by : Mapped[int] = mapped_column(Integer, nullable=True)

    # ForeignKey
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.city_id", ondelete="CASCADE"))

    # Relationships
    city: Mapped["City"] = relationship("City", back_populates="counties")
    areas: Mapped[List["Area"]] = relationship(
        "Area", back_populates="county", cascade="all, delete-orphan"
    )
