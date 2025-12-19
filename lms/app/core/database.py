"""
Database configuration and session management.
"""
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool

from .unit_of_work import UnitOfWork

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/lms_db"
)

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_db() -> Generator:
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_uow() -> Generator[UnitOfWork, None, None]:
    """Dependency for FastAPI to get a transactional Unit of Work.
    
    Yields a UnitOfWork instance that manages transaction lifecycle:
    - Starts a transaction on entry
    - Commits on successful request completion
    - Rolls back on any exception
    - Always closes the session
    
    Ensures atomicity: either all domain changes + audit logs persist, or none do.
    """
    session = SessionLocal()
    uow = UnitOfWork(session)
    with uow:
        yield uow
