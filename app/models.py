from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Date, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String(20))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    agency_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agencies.agency_id"), nullable=True, default=None)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    neighborhood: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(255))
    county: Mapped[Optional[str]] = mapped_column(String(255))
    lic_num: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    # Relationships
    agency = relationship("Agency",back_populates="users",foreign_keys=[agency_id])
    properties = relationship("Property", back_populates="owner", foreign_keys="Property.owner_id")
    agent_properties = relationship("Property", back_populates="agent", foreign_keys="Property.agent_id")
    licenses = relationship("License", back_populates="user", uselist=False)
    favorites = relationship("Favorite", back_populates="user")
    brokered_agencies = relationship("Agency", back_populates="broker", foreign_keys="Agency.broker_id")



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


class Agency(Base):
    __tablename__ = "agencies"

    agency_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    broker_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    email: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(255))
    neighborhood: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    county: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(20))

    # Relationships
    users = relationship("User",back_populates="agency",foreign_keys="[User.agency_id]")
    broker = relationship("User",foreign_keys=[broker_id])




class Additional(Base):
    __tablename__ = "additional"

    additional_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.property_id"), nullable=False)
    elevator: Mapped[Optional[bool]] = mapped_column(Boolean)
    balcony: Mapped[Optional[int]] = mapped_column(Integer)
    ac: Mapped[Optional[int]] = mapped_column(Integer)
    fan_number: Mapped[Optional[int]] = mapped_column(Integer)
    garage: Mapped[Optional[bool]] = mapped_column(Boolean)
    garden: Mapped[Optional[bool]] = mapped_column(Boolean)
    solar_system: Mapped[Optional[bool]] = mapped_column(Boolean)
    water: Mapped[Optional[str]] = mapped_column(String(100))
    jacuzzi: Mapped[Optional[bool]] = mapped_column(Boolean)
    pool: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Relationship
    property = relationship("Property", back_populates="additional_details")


class License(Base):
    __tablename__ = "licenses"

    license_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True)
    license_number: Mapped[int] = mapped_column(Integer)
    license_status: Mapped[str] = mapped_column(String(100))

    # Relationship
    user = relationship("User", back_populates="licenses")


class Favorite(Base):
    __tablename__ = "favorites"

    favorite_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.property_id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="favorites")
    property = relationship("Property", back_populates="favorites")
