from __future__ import annotations

from sqlalchemy import String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime
from app.models.agency_model import agency_brokers

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.role_model import Role
    from app.models.addresses_model import Address
    from app.models.sales_model import Sale
    from app.models.rents_model import Rent

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50),nullable=False)
    last_name: Mapped[str] = mapped_column(String(50),nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20),nullable=False) 
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    
    # ForeignKey
    created_by : Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Relationships
    creator = relationship("User", remote_side=[user_id], backref="created_users")

    roles: Mapped["Role"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined"
    )

    licenses = relationship("License", back_populates="user", uselist=False)

    agency_created = relationship("Agency", back_populates="created_by_user", foreign_keys="[Agency.created_by]")
    agency_brokers = relationship("Agency", secondary=agency_brokers, back_populates="brokers")

    favorites = relationship("Favorite", back_populates="user")

    address_created: Mapped["Address"] = relationship(
        back_populates="created_by_user",
        foreign_keys="[Address.created_by]",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined"
    )

    property_created = relationship("Property", back_populates="created_by_user", foreign_keys="[Property.created_by]")

    consumer_created = relationship("Consumer", back_populates="created_by_user", foreign_keys="[Consumer.created_by]")

    closed_sales: Mapped[list["Sale"]] = relationship(
    "Sale",
    back_populates="closed_by",
    foreign_keys="Sale.closed_by_id"
)
    closed_rents: Mapped[list["Rent"]] = relationship(
    "Rent",
    back_populates="closed_by",
    foreign_keys="Rent.closed_by_id"
)

