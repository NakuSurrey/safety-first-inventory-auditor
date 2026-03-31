"""
Alembic environment configuration.

This file tells Alembic:
1. WHERE the database is (connection string from our settings)
2. WHAT models exist (by importing Base.metadata)
3. HOW to run migrations (online mode for real DB, offline for SQL scripts)
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from backend.app.core.config import settings
from backend.app.db.base import Base

# Import all models so Base.metadata knows about them
from backend.app.models import InventoryLog, Item, Location  # noqa: F401

# Alembic Config object — reads alembic.ini
config = context.config

# Override the connection string with our settings (from .env)
config.set_main_option("sqlalchemy.url", settings.effective_database_url)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Tell Alembic about our models — it compares this metadata
# against the actual database to generate migration diffs
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Generates SQL script without connecting to the database.
    Useful for reviewing what SQL will be executed.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_name="postgresql",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    Connects to the actual database and applies changes directly.
    This is the mode you use most of the time.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
