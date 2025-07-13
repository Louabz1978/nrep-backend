from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class License(Base):
    __tablename__ = "licenses"

    license_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    license_number: Mapped[int] = mapped_column(Integer)
    license_status: Mapped[str] = mapped_column(String(100))
    license_type : Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True)
    agency_id: Mapped[int] = mapped_column(ForeignKey("agencies.agency_id"), nullable=False)

    user = relationship("User", back_populates="licenses")
    agency = relationship("Agency", back_populates="licenses")

