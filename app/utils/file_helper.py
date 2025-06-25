from pathlib import Path

def load_sql(filename: str) -> str:
    sql_path = Path(__file__).parent.parent / "sql_queries" / filename
    return sql_path.read_text()
