from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
default_db_url = f"sqlite:///{os.path.join(BASE_DIR, 'guardrail.db')}"
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", default_db_url)
DATABASE_URL = SQLALCHEMY_DATABASE_URL

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
