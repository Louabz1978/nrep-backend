from sqlalchemy import text
from app.database import get_db  # or whatever your file is named

query = "SELECT * FROM users"

# get the session (only for non-FastAPI scripts)
db = next(get_db())

result = db.execute(text(query))

# Option 1: get rows as dict-like mappings
rows = result.mappings().all()

for row in rows:
    print(row)
