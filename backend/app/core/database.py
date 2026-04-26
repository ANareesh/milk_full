"""Database configuration and utilities."""
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.core.config import get_settings

settings = get_settings()
import os
logger = logging.getLogger(__name__)

# Prefer explicit DATABASE_URL, but if individual POSTGRES_* env vars are provided
# build the URL using SQLAlchemy's URL.create to ensure proper quoting/encoding.
db_url = settings.database_url
if os.getenv("POSTGRES_HOST") or os.getenv("POSTGRES_USER") or os.getenv("POSTGRES_PASSWORD"):
    db_url = str(
        URL.create(
            drivername="postgresql+psycopg2",
            username=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_host,
            port=settings.postgres_port,
            database=settings.postgres_db,
        )
    )

engine = create_engine(
    db_url,
    echo=settings.sqlalchemy_echo,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


# Enable foreign keys for SQLite (if used)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign keys for SQLite."""
    if "sqlite" in settings.database_url:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
