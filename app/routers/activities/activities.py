from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
import numpy as np

from app import database

from fastapi.responses import JSONResponse

router = APIRouter(prefix="/get_property_stats", tags=["get property stats"])

@router.get("/")
def get_property_stats(
    city: str,
    db: Session = Depends(database.get_db),
    area: str = None,
    year: int = None,
    month: int = None
):
    base_query = """
        SELECT 
            p.property_type,
            EXTRACT(YEAR FROM p.created_at)::INT AS year,
            EXTRACT(MONTH FROM p.created_at)::INT AS month,
            COUNT(*) AS number_of_closed,
            AVG(p.price) FILTER (WHERE p.status = 'closed') AS avg_closed_price
        FROM properties p
        JOIN addresses a ON p.property_id = a.property_id
        WHERE livable = TRUE and a.city = :city
        {area_filter} {year_filter} {month_filter}
        GROUP BY year, month, p.property_type
        ORDER BY year, month, p.property_type
    """

    filters = {"area_filter": "", "year_filter": "", "month_filter": ""}
    params_current = {"city": city}

    if area:
        filters["area_filter"] = "AND a.area = :area"
        params_current["area"] = area

    if year:
        filters["year_filter"] = "AND EXTRACT(YEAR FROM p.created_at) = :year"
        params_current["year"] = int(year)

    if month:
        filters["month_filter"] = "AND EXTRACT(MONTH FROM p.created_at) = :month"
        params_current["month"] = int(month)

    query_current = base_query.format(**filters)

    filters_prev = filters.copy()
    params_prev = params_current.copy()
    if year:
        filters_prev["year_filter"] = "AND EXTRACT(YEAR FROM p.created_at) = :prev_year"
        params_prev["prev_year"] = int(year) - 1
    query_prev = base_query.format(**filters_prev)

    connection = db.connection()
    df_current = pd.read_sql(text(query_current), connection, params=params_current)
    df_prev = pd.read_sql(text(query_prev), connection, params=params_prev)

    # المقارنة
    comparison = pd.DataFrame()
    if not df_prev.empty and not df_current.empty:
        comparison = pd.merge(
            df_current,
            df_prev,
            on=["property_type", "month"],
            how="left",
            suffixes=("_current", "_prev")
        )

        for col in ["number_of_closed", "avg_closed_price"]:
            comparison[f"{col}_change_pct"] = (
                (comparison[f"{col}_current"] - comparison[f"{col}_prev"])
                / comparison[f"{col}_prev"].replace(0, np.nan)
            ) * 100

    # دالة لتحويل كل القيم الغير صالحة إلى None
    def clean_dataframe(df):
        records = df.to_dict(orient="records")
        cleaned = []
        for row in records:
            new_row = {}
            for k, v in row.items():
                if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
                    new_row[k] = None
                elif isinstance(v, np.generic):
                    new_row[k] = v.item()
                else:
                    new_row[k] = v
            cleaned.append(new_row)
        return cleaned

    return JSONResponse(content={
        "current_year": clean_dataframe(df_current),
        "previous_year": clean_dataframe(df_prev),
        "comparison": clean_dataframe(comparison)
    })
