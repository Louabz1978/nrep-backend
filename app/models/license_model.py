from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class License(Base):
    __tablename__ = "licenses"

    license_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True)
    license_number: Mapped[int] = mapped_column(Integer)
    license_status: Mapped[str] = mapped_column(String(100))

    # Relationship
    user = relationship("User", back_populates="licenses")

