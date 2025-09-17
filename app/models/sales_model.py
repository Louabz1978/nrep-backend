from __future__ import annotations

from sqlalchemy import Integer,Float, ForeignKey, TIMESTAMP, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base
from typing import Optional


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.consumer_model import  Consumer
    from app.models.property_model import  Property



class Sale(Base):
    __tablename__ = "sales_trans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.property_id"), nullable=False)
    sold_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    buyer_agent_commission: Mapped[float] = mapped_column(Float)
    seller_agent_commission: Mapped[float] = mapped_column(Float)
    date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=False)

    buyer_id: Mapped[int] = mapped_column(ForeignKey("consumers.consumer_id"), nullable=False)
    seller_id: Mapped[int] = mapped_column(ForeignKey("consumers.consumer_id"), nullable=False)
    closed_by_id:Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

  # Relationships
    property: Mapped["Property"] = relationship("Property",foreign_keys=[property_id])
    buyer: Mapped["Consumer"] = relationship("Consumer", foreign_keys=[buyer_id])
    seller: Mapped["Consumer"] = relationship("Consumer", foreign_keys=[seller_id])
    closed_by: Mapped["User"] = relationship("User", foreign_keys=[closed_by_id])