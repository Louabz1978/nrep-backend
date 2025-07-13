from sqlalchemy import String, Boolean, ForeignKey, TIMESTAMP
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
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.address_id"), nullable=False)
    created_by : Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"),nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    

    # Relationships
    creator = relationship("User", remote_side=[user_id], back_populates="created_users")
    created_users = relationship("User", back_populates="creator")
    address = relationship("Address", back_populates="user")
    properties = relationship("Property", back_populates="seller", foreign_keys="Property.seller_id")
    realtor_properties = relationship("Property", back_populates="realtor", foreign_keys="Property.realtor_id")
    licenses = relationship("License", back_populates="user", uselist=False)
    favorites = relationship("Favorite", back_populates="user")
    brokered_agencies = relationship("Agency", back_populates="broker", foreign_keys="Agency.broker_id")
    roles = relationship("Role", back_populates="user", uselist=False, foreign_keys="Role.user_id")
