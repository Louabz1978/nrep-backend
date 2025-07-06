from sqlalchemy import String, Integer, Float, ForeignKey, Date, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

class Property(Base):
    __tablename__ = "properties"

    property_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    agent_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    address: Mapped[str] = mapped_column(String(255))
    neighborhood: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    county: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer)
    property_type: Mapped[Optional[str]] = mapped_column(String(100))
    floor: Mapped[Optional[int]] = mapped_column(Integer)
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[float] = mapped_column(Float)
    listing_agent_commission: Mapped[float] = mapped_column(Float)
    buyer_agent_commission: Mapped[float] = mapped_column(Float)
    area_space: Mapped[int] = mapped_column(Integer)
    year_built: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="available")
    listed_date: Mapped[Date] = mapped_column(Date)
    last_updated: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    image_url: Mapped[Optional[str]] = mapped_column(String)

    # Relationships
    owner = relationship("User", back_populates="properties", foreign_keys=[owner_id])
    agent = relationship("User", back_populates="agent_properties", foreign_keys=[agent_id])
    additional_details = relationship("Additional", back_populates="property", uselist=False)
    favorites = relationship("Favorite", back_populates="property")
