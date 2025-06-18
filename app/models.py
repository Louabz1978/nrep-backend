from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Date, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String(20))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    agency_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agencies.agency_id"), nullable=True, default=None)
    agency: Mapped[Optional["Agency"]] = relationship("Agency", backref="users")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[str]] = mapped_column(TIMESTAMP, server_default=func.now())
    lic_num: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)


class Property(Base):
    __tablename__ = "properties"

    property_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    agent: Mapped["User"] = relationship("User", backref="properties")
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer)
    address: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(50))
    zip_code: Mapped[str] = mapped_column(String(10))
    property_type: Mapped[str] = mapped_column(String(50))
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[float] = mapped_column(Float)
    listing_agent_commission: Mapped[float] = mapped_column(Float)
    buyer_agent_commission: Mapped[float] = mapped_column(Float)
    area_sqft: Mapped[int] = mapped_column(Integer)
    lot_size_sqft: Mapped[int] = mapped_column(Integer)
    year_built: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[int] = mapped_column(Integer)
    longitude: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="available")
    listed_date: Mapped[Date] = mapped_column(Date)
    last_updated: Mapped[Optional[str]] = mapped_column(Date, server_default=func.now())
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Agency(Base):
    __tablename__ = "agencies"

    agency_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    agency_lic: Mapped[Optional[str]] = mapped_column(String(100))
