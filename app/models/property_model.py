from sqlalchemy import String, Integer, Float, ForeignKey, Date, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime
from sqlalchemy import Numeric
from sqlalchemy import Enum

from ..routers.properties.properties_status_enum import PropertyStatus
from ..routers.properties.properties_type_enum import PropertyTypes


class Property(Base):
    __tablename__ = "properties"

    property_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    property_type: Mapped[PropertyTypes] = mapped_column(
        Enum(PropertyTypes, name="property_type_enum"),
        default=PropertyTypes.house,
        nullable=False
    )
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[float] = mapped_column(Float)
    property_realtor_commission: Mapped[float] = mapped_column(Float)
    buyer_realtor_commission: Mapped[float] = mapped_column(Float)
    area_space: Mapped[int] = mapped_column(Integer)
    year_built: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[PropertyStatus] = mapped_column(
        Enum(PropertyStatus, name="property_status_enum"),
        default=PropertyStatus.active,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    image_urls: Mapped[Optional[str]] = mapped_column(String)
    mls_num: Mapped[Optional[int]] = mapped_column(Integer)
    
    # ForeignKey
    created_by : Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.address_id"), nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="property_created", foreign_keys=[created_by])
    owner = relationship("User", back_populates="property", foreign_keys=[owner_id])

    address = relationship("Address", back_populates="properties", foreign_keys=[address_id])
    favorites = relationship("Favorite", back_populates="property")
    additional_details = relationship("Additional", back_populates="property", uselist=False)
