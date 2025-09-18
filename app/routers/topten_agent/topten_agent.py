from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app import database

router = APIRouter(prefix="/Top_10_agent", tags=["Top 10 agent"])

@router.get("/")
def get_closed_properties(
    month: int,
    year: int,

    db: Session = Depends(database.get_db)
):
    current_month = datetime.now().month
    current_year = datetime.now().year

    # validation
    if not (1 <= month <= 12):
        raise ValueError(f"Invalid month {month}. Must be between 1 and 12.")
    if year > current_year:
        raise ValueError(
            f"Invalid year: {year}. Cannot be greater than {current_year}."
        )
    if year == current_year and month > current_month:
        raise ValueError(
            f"Invalid month: {month}. Cannot be greater than current month {current_month} for year {year}"
        )

    # previous month/year
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    query_template = """
        SELECT 
            CONCAT(u.first_name, ' ', u.last_name) AS full_name, 
            COUNT(p.status) AS closed_count, 
            l.lic_num AS license_number,
            COALESCE(SUM(p.price),0) AS total_price
        FROM properties p
        LEFT JOIN users u ON u.user_id = p.created_by
        LEFT JOIN licenses l ON l.user_id = u.user_id
        WHERE p.status = 'closed'
        AND EXTRACT(MONTH FROM p.created_at) = :month
        AND EXTRACT(YEAR FROM p.created_at) = :year
        GROUP BY u.user_id, full_name, l.lic_num
        ORDER BY closed_count DESC
        LIMIT 10
    """

    # run for current month
    current_query = text(query_template)
    current_res = (
        db.execute(current_query, {"month": month, "year": year}).mappings().all()
    )

    # run for previous month
    prev_query = text(query_template)
    prev_res = (
        db.execute(prev_query, {"month": prev_month, "year": prev_year})
        .mappings()
        .all()
    )

    return {
        "current_month": month,
        "results": [dict(r) for r in current_res],
        "previous_month": prev_month,
        "previous_results": [dict(r) for r in prev_res],
    }

