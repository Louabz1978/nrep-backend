from __future__ import annotations

from sqlalchemy import Integer, Float, ForeignKey, TIMESTAMP, Text, Table, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime
from sqlalchemy import Numeric, Date
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import JSONB

from ..utils.enums import PropertyStatus, PropertyTypes, PropertyTransactionType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.addresses_model import Address

property_owners = Table(
    "property_owners",
    Base.metadata,
    Column("property_id", ForeignKey("properties.property_id", ondelete="CASCADE"), primary_key=True),
    Column("seller_id", ForeignKey("consumers.consumer_id", ondelete="CASCADE"), primary_key=True),
)
class Property(Base):
    __tablename__ = "properties"

    property_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    description: Mapped[str] = mapped_column(Text)
    show_inst: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    property_type: Mapped[PropertyTypes] = mapped_column(
        Enum(PropertyTypes, name="property_type_enum"),
        default=PropertyTypes.apartment,
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
    trans_type: Mapped[PropertyTransactionType] = mapped_column(
        Enum(PropertyTransactionType, name="property_transaction_type_enum"),
        default=PropertyTransactionType.sell,
        nullable=False
    )
    exp_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    images_urls: Mapped[Optional[list[dict]]] = mapped_column(JSONB)
    mls_num: Mapped[Optional[int]] = mapped_column(
        Integer,
        unique=True,
        nullable=False
    )
    livable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)

    # ForeignKey
    created_by : Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="property_created", foreign_keys=[created_by])

    #many_to_many relationship for owners
    sellers = relationship("Consumer", secondary=property_owners, back_populates="owned_properties")

    address: Mapped["Address"] = relationship(
        back_populates="properties",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined"
    )

    favorites = relationship("Favorite", back_populates="property")
    additional_details = relationship("Additional", back_populates="property", uselist=False)
