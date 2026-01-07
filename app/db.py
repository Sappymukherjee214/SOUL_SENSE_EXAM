import os
import sqlite3
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from alembic.config import Config
from alembic import command

from app.config import DATABASE_URL, DB_PATH, BASE_DIR
from app.exceptions import DatabaseError

# Configure logger
logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_engine():
    return engine

def get_session() -> Session:
    """
    Returns a new SQLAlchemy Session.
    Caller is responsible for closing it (or usage via context manager).
    """
    return SessionLocal()

@contextmanager
def safe_db_context():
    """
    Context manager for safe database operations.
    Wraps SQLAlchemy and generic exceptions into DatabaseError.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}", exc_info=True)
        raise DatabaseError("A database error occurred.", original_exception=e)
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in DB context: {str(e)}", exc_info=True)
        raise DatabaseError("An unexpected database error occurred.", original_exception=e)
    finally:
        session.close()

def check_db_state():
    """
    Checks if the database exists and if it needs to be stamped with the initial migration.
    Then, upgrades the database to the latest head.
    """
    logger.info("Checking database state...")
    try:
        # Ensure dependencies are ready
        ini_path = os.path.join(BASE_DIR, "alembic.ini")
        if not os.path.exists(ini_path):
             # This is a config/resource error, but critical for DB
             raise DatabaseError(f"Alembic config not found at {ini_path}")

        alembic_cfg = Config(ini_path)
        script_location = os.path.join(BASE_DIR, "migrations")
        alembic_cfg.set_main_option("script_location", script_location)

        # Check for legacy state
        if os.path.exists(DB_PATH):
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if "scores" in tables and "alembic_version" not in tables:
                logger.info("Existing database detected without migrations. Stamping 'head'...")
                command.stamp(alembic_cfg, "head")
        
        # Always attempt to upgrade to the latest version
        logger.info("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migration check complete.")
            
    except (SQLAlchemyError, sqlite3.Error) as e:
        logger.critical(f"Database migration failed: {e}", exc_info=True)
        raise DatabaseError("Failed to verify/migrate database.", original_exception=e)
    except Exception as e:
        if isinstance(e, DatabaseError):
            raise
        logger.critical(f"Unexpected error during DB check: {e}", exc_info=True)
        raise DatabaseError("Critical error during database initialization.", original_exception=e)

# Call verify on import (or explicit init)
try:
    check_db_state()
except DatabaseError:
    # We re-raise to let the main app handle the crash gracefully if possible,
    # or just crash if it's during import time
    raise

# Backward compatibility for old code (raw sqlite3)
def get_connection(db_path=None):
    try:
        return sqlite3.connect(db_path or DB_PATH)
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to SQLite DB: {e}", exc_info=True)
        raise DatabaseError("Failed to connect to raw database.", original_exception=e)
