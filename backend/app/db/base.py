"""
Declarative base for all SQLAlchemy models.
Every model class in backend/app/models/ inherits from this Base.
When Alembic runs migrations, it reads Base.metadata to discover
all tables that need to be created or updated.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all database models.

    SQLAlchemy uses this class to:
    1. Track every model that inherits from it
    2. Store table definitions in Base.metadata
    3. Generate CREATE TABLE statements from that metadata
    """

    pass
