from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import Optional

class Additional(Base):
    __tablename__ = "additional"

    additional_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    elevator: Mapped[Optional[bool]] = mapped_column(Boolean)
    balcony: Mapped[Optional[int]] = mapped_column(Integer)
    ac: Mapped[Optional[bool]] = mapped_column(Boolean)
    fan_number: Mapped[Optional[int]] = mapped_column(Integer)
    garage: Mapped[Optional[bool]] = mapped_column(Boolean)
    garden: Mapped[Optional[bool]] = mapped_column(Boolean)
    solar_system: Mapped[Optional[bool]] = mapped_column(Boolean)
    water: Mapped[Optional[str]] = mapped_column(String(100))
    jacuzzi: Mapped[Optional[bool]] = mapped_column(Boolean)
    pool: Mapped[Optional[bool]] = mapped_column(Boolean)

    # ForeignKey
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.property_id"), nullable=False)

    # Relationship
    property = relationship("Property", back_populates="additional_details", foreign_keys=[property_id])
    