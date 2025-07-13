from sqlalchemy import String, Integer, Float, ForeignKey, Date, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

class Property(Base):
    __tablename__ = "properties"

    property_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    realtor_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer)
    property_type: Mapped[Optional[str]] = mapped_column(String(100))
    floor: Mapped[Optional[int]] = mapped_column(Integer)
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[float] = mapped_column(Float)
    property_realtor_commission: Mapped[float] = mapped_column(Float)
    buyer_realtor_commission: Mapped[float] = mapped_column(Float)
    area_space: Mapped[int] = mapped_column(Integer)
    year_built: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="available")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    image_url: Mapped[Optional[str]] = mapped_column(String)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.address_id"), nullable=False)
    created_by : Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"),nullable=False)

    # Relationships
    address = relationship("Address", back_populates="properties")
    created_user = relationship("User", foreign_keys=[created_by])
    favorites = relationship("Favorite", back_populates="property")
    seller = relationship("User", back_populates="properties", foreign_keys=[seller_id])
    realtor = relationship("User", back_populates="realtor_properties", foreign_keys="Property.realtor_id")
    additional_details = relationship("Additional", back_populates="property", uselist=False)
