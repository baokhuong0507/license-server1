# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Tạo engine kết nối tới CSDL PostgreSQL
engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Hàm để lấy một phiên làm việc với CSDL
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
