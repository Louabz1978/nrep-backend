from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv
import os
from typing import Annotated
from fastapi import Depends

load_dotenv()

DB_USERNAME = os.getenv("DATABASE_USERNAME", "postgres")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "1234")
DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "nrep_database")

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
LocalSession = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

db_depends = Annotated[Session, Depends(get_db)]
