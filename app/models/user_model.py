from sqlalchemy import String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime

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
    address_id: Mapped[Optional[int]] = mapped_column(ForeignKey("addresses.address_id"), nullable=True)
    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("roles.roles_id"), nullable=True)

    # Relationships
    creator = relationship("User", remote_side=[user_id], backref="created_users")

    roles = relationship("Role", back_populates="user", foreign_keys=[role_id], uselist=False)

    licenses = relationship("License", back_populates="user", uselist=False)

    agency_created = relationship("Agency", back_populates="created_by_user", foreign_keys="[Agency.created_by]")
    agency_broker = relationship("Agency", back_populates="broker", foreign_keys="[Agency.broker_id]")

    favorites = relationship("Favorite", back_populates="user")

    address_created = relationship("Address", back_populates="created_by_user", foreign_keys="[Address.created_by]")
    address = relationship("Address", back_populates="user", foreign_keys=[address_id])

    property_created = relationship("Property", back_populates="created_by_user", foreign_keys="[Property.created_by]")
    property = relationship("Property", back_populates="owner", foreign_keys="[Property.owner_id]")
