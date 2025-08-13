import sys
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, get_db
from main import app

load_dotenv()
DB_USERNAME = os.getenv("DATABASE_TEST_USERNAME")
DB_PASSWORD = os.getenv("DATABASE_TEST_PASSWORD")
DB_HOST = os.getenv("DATABASE_TEST_HOST")
DB_PORT = os.getenv("DATABASE_TEST_PORT")
DB_NAME = os.getenv("DATABASE_TEST_NAME")

if DB_PORT is None or DB_PORT == "":
    DB_PORT = 5432
else:
    DB_PORT = int(DB_PORT)

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create test DB if it doesn't exist
if not database_exists(DATABASE_URL):
    create_database(DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@pytest.fixture(scope="function")
def override_db():
    # Import models to register tables in Base.metadata
    import app.models

    # Drop and recreate all tables fresh
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Run SQL seed file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(test_dir, "seed_data.sql")
    with open(sql_file_path, "r") as f:
        seed_sql = f.read()

    with engine.connect() as connection:
        connection.execute(text(seed_sql))
        connection.commit()

    # Create a new session instance
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Base.metadata.drop_all(bind=engine)

# Override the get_db dependency in FastAPI to use the test session
@pytest.fixture(scope="function")
def client(override_db):
    def _override_get_db():
        try:
            yield override_db
        finally:
            override_db.close()

    app.dependency_overrides[get_db] = _override_get_db

    from fastapi.testclient import TestClient
    return TestClient(app)
