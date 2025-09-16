from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from sqlalchemy import Enum

from ..utils.enums import LicenseType, LicenseStatus

class License(Base):
    __tablename__ = "licenses"

    license_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    lic_num: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)

    lic_status: Mapped[LicenseStatus] = mapped_column(
        Enum(LicenseStatus, name="license_status_enum"),
        default=LicenseStatus.active,
        nullable=False
    )

    lic_type: Mapped[LicenseType] = mapped_column(
        Enum(LicenseType, name="license_type_enum"),
        default=LicenseType.company,
        nullable=False
    )

    # ForeignKey
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True)
    agency_id: Mapped[int] = mapped_column(ForeignKey("agencies.agency_id"), nullable=False)

    # Relationship
    user = relationship("User", back_populates="licenses")
    agency = relationship("Agency", back_populates="licenses")
    