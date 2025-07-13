from sqlalchemy import String, Integer, Float, ForeignKey, Date, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from sqlalchemy import Boolean

class Role(Base):
    __tablename__ = "roles"
    
    roles_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    admin: Mapped[bool] = mapped_column(Boolean)
    broker: Mapped[bool] = mapped_column(Boolean)
    realtor: Mapped[bool] = mapped_column(Boolean)
    buyer: Mapped[bool] = mapped_column(Boolean)
    seller: Mapped[bool] = mapped_column(Boolean)
    tenant: Mapped[bool] = mapped_column(Boolean)
    
    # ForeignKey
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    #Relationships
    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    