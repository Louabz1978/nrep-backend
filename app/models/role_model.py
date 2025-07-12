from sqlalchemy import String, Integer, Float, ForeignKey, Date, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Role(Base):
    __tablename__ = "roles"
    
    roles_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    admin: Mapped[bool] = mapped_column(bool)
    broker: Mapped[bool] = mapped_column(bool)
    realtor: Mapped[bool] = mapped_column(bool)
    buyer: Mapped[bool] = mapped_column(bool)
    seller: Mapped[bool] = mapped_column(bool)
    tenant: Mapped[bool] = mapped_column(bool)
    
    #Relationships
    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    