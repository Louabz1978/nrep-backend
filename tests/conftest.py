import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import get_db, Base
from main import app

# Used in-memory SQLite for isolated test DB
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
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
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(override_db):
    # Override the app's dependency
    def _override_get_db():
        yield override_db

    app.dependency_overrides[get_db] = _override_get_db
    from fastapi.testclient import TestClient
    return TestClient(app)
