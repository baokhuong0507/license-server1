from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# Use sync SQLite for simplicity; for Postgres, point DATABASE_URL to postgres and remove replace()
engine = create_engine(settings.DATABASE_URL.replace("+aiosqlite", ""), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
