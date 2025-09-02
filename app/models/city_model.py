from app.database import Base
from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy.sql import func

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.county_model import County

class City(Base):
    __tablename__ = "cities"

    city_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    created_by : Mapped[int] = mapped_column(Integer, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    updated_by : Mapped[int] = mapped_column(Integer, nullable=True)

    # Relationships
    counties: Mapped[List["County"]] = relationship(
        "County", back_populates="city", cascade="all, delete-orphan"
    )
