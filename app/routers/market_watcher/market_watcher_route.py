from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app import database

from dateutil.relativedelta import relativedelta

router = APIRouter(prefix="/market_watcher", tags=["Market Watcher"])

def subtract_period(period: str):
    date_obj = datetime.today()
    if period == "1 week":
        new_date = date_obj - relativedelta(weeks=1)
    elif period == "1 month":
        new_date = date_obj - relativedelta(months=1)
    elif period == "3 months":
        new_date = date_obj - relativedelta(months=3)
    elif period == "6 months":
        new_date = date_obj - relativedelta(months=6)
    elif period == "1 year":
        new_date = date_obj - relativedelta(years=1)
    else:
        raise ValueError("Invalid period.")
    return new_date.strftime("%Y-%m-%d")


@router.get("/")
def Market_watcher(
    period: str,
    area: str,
    
    db: Session = Depends(database.get_db)
):
    start_date = subtract_period(period)
    end_date = datetime.today().strftime("%Y-%m-%d")

    query_new = """
        SELECT COUNT(*)
        FROM properties p
        JOIN addresses a ON p.property_id = a.property_id
        WHERE a.area = :area
        AND DATE(p.last_updated) BETWEEN :start_date AND :end_date 
        AND p.status = 'active'
    """
    query_pending = """
        SELECT COUNT(*) 
        FROM properties p
        JOIN addresses a ON p.property_id= a.property_id
        WHERE a.area = :area
        AND DATE(p.last_updated) BETWEEN :start_date AND :end_date 
        AND p.status = 'pending'
    """
    query_closed = """
        SELECT COUNT(*) 
        FROM properties p
        JOIN addresses a ON p.property_id = a.property_id
        WHERE a.area = :area
        AND DATE(p.last_updated) BETWEEN :start_date AND :end_date 
        AND p.status = 'closed'
    """
    query_out = """
        SELECT COUNT(*) 
        FROM properties p
        JOIN addresses a ON p.property_id = a.property_id
        WHERE a.area = :area
        AND DATE(p.last_updated) BETWEEN :start_date AND :end_date
        AND p.status = 'out_of_market'
    """
    query_return = """
        SELECT COUNT(*) 
        FROM properties p
        JOIN addresses a ON p.property_id = a.property_id
        WHERE a.area = :area
        AND DATE(p.last_updated) BETWEEN :start_date AND :end_date
        AND p.last_updated != p.created_at
    """

    result1 = (
        db.execute(
            text(query_new),
            {"area": area, "start_date": start_date, "end_date": end_date},
        ).scalar()
        or 0
    )
    result2 = (
        db.execute(
            text(query_pending),
            {"area": area, "start_date": start_date, "end_date": end_date},
        ).scalar()
        or 0
    )
    result3 = (
        db.execute(
            text(query_closed),
            {"area": area, "start_date": start_date, "end_date": end_date},
        ).scalar()
        or 0
    )
    result4 = (
        db.execute(
            text(query_out),
            {"area": area, "start_date": start_date, "end_date": end_date},
        ).scalar()
        or 0
    )
    result5 = (
        db.execute(
            text(query_return),
            {"area": area, "start_date": start_date, "end_date": end_date},
        ).scalar()
        or 0
    )
    return {
        "new_listings_count": result1,
        "pending_count": result2,
        "closed_count": result3,
        "out_of_market": result4,
        "return_the_market": result5,
    }
