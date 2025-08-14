from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

from sqlalchemy import Boolean, ForeignKey, text

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.consumer_model import Consumer

class Role(Base):
    __tablename__ = "roles"
    
    roles_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    admin: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    broker: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    realtor: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    buyer: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    seller: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    tenant: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))

    # ForeignKey
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, unique=True)
    consumer_id: Mapped[int] = mapped_column(ForeignKey("consumers.consumer_id", ondelete="CASCADE"), nullable=True, unique=True)

    #Relationships
    user: Mapped["User"] = relationship(back_populates="roles")
    consumer: Mapped["Consumer"] = relationship(back_populates="roles")
