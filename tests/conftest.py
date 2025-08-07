import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from app.database import get_db, Base
from main import app
load_dotenv()
DB_USERNAME = os.getenv("DATABASE_USERNAME")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("DATABASE_TEST_NAME")

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL
)

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Override the get_db dependency for FastAPI app
@pytest.fixture(scope="function")
def override_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(override_db):
    # Override the app's dependency
    def _override_get_db():
        yield override_db

    app.dependency_overrides[get_db] = _override_get_db
    from fastapi.testclient import TestClient
    return TestClient(app)
