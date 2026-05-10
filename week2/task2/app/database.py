import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

from app.core.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set")
    raise RuntimeError("DATABASE_URL is not set")

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    logger.info("Database engine created")
except Exception as exc:
    logger.error("Failed to create database engine: %s", exc)
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.info("Database session closed")
