from sqlalchemy import String, Integer, Float, ForeignKey, Date, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from sqlalchemy import Boolean

class Role(Base):
    __tablename__ = "roles"
    
    roles_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)
    broker: Mapped[bool] = mapped_column(Boolean, default=False)
    realtor: Mapped[bool] = mapped_column(Boolean, default=False)
    buyer: Mapped[bool] = mapped_column(Boolean, default=False)
    seller: Mapped[bool] = mapped_column(Boolean, default=False)
    tenant: Mapped[bool] = mapped_column(Boolean, default=False)
    
    #Relationships
    user = relationship("User", back_populates="roles", foreign_keys="[User.role_id]")
