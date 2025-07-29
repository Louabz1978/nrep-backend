from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

from sqlalchemy import Boolean, ForeignKey, text

class Role(Base):
    __tablename__ = "roles"
    
    roles_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    admin: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    broker: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    realtor: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    buyer: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    seller: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    tenant: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"),nullable=False)

    #Relationships
    user = relationship("User", back_populates="roles", foreign_keys="[User.role_id]")
