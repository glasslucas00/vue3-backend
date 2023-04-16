#!/usr/bin/python3
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
SQLALCHEMY_DATABASE_URL = config("BASE_MYSQL")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """
    Get the database session

    Yields:
        Session: The database session
    """
    # 初始化数据库连接:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
