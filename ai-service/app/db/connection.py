from contextlib import contextmanager
from typing import Generator

import psycopg
from pgvector.psycopg import register_vector

from app.config import get_settings


@contextmanager
def get_raw_connection() -> Generator[psycopg.Connection, None, None]:
    """Open a PostgreSQL connection without registering the pgvector adapter."""
    settings = get_settings()
    with psycopg.connect(settings.database_url) as conn:
        yield conn


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    """Open a PostgreSQL connection with the pgvector adapter registered."""
    settings = get_settings()
    with psycopg.connect(settings.database_url) as conn:
        register_vector(conn)
        yield conn
