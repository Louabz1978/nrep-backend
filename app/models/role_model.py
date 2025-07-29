from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from sqlalchemy import Boolean, ForeignKey

class Role(Base):
    __tablename__ = "roles"
    
    roles_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)
    broker: Mapped[bool] = mapped_column(Boolean, default=False)
    realtor: Mapped[bool] = mapped_column(Boolean, default=False)
    buyer: Mapped[bool] = mapped_column(Boolean, default=False)
    seller: Mapped[bool] = mapped_column(Boolean, default=False)
    tenant: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"),nullable=False)

    #Relationships
    user = relationship("User", back_populates="roles")
