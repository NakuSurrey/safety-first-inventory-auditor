"""
Database engine and session management.

Engine: the actual connection to PostgreSQL.
SessionLocal: a factory that creates new database sessions.
get_db: a FastAPI dependency that opens a session, gives it to
        a route function, and closes it when the route is done.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import settings

# --- ENGINE ---
# The engine is the lowest-level connection to PostgreSQL.
# pool_pre_ping=True means: before reusing a connection from the pool,
# send a quick "are you alive?" ping to the database. If the connection
# died (e.g. database restarted), discard it and create a new one.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# --- SESSION FACTORY ---
# sessionmaker creates a factory (not a session itself).
# Every time you call SessionLocal(), it creates a NEW session.
# autocommit=False: you must explicitly call session.commit()
# autoflush=False: SQLAlchemy does not auto-send queries to the DB
# bind=engine: every session uses our PostgreSQL engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# --- DEPENDENCY FOR FASTAPI ---
# FastAPI routes will use this function to get a database session.
# The "yield" keyword makes this a generator:
#   1. Before yield: create and open a session
#   2. yield: give the session to the route function
#   3. After yield (in finally): close the session no matter what
def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session to FastAPI route functions.
    Automatically closes the session when the request is done,
    even if an error occurred during the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
