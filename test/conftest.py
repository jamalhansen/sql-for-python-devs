"""Shared test fixtures for SQL for Python Developers exercises."""

import os
import pytest
import duckdb
from pathlib import Path
from helpers.db import load_sample_customers, load_sample_orders


def pytest_configure(config):
    """
    Pytest hook that runs before test collection.
    Automatically extracts latest code from blog before running tests.

    Set BLOG_PATH environment variable to enable automatic extraction.
    """
    try:
        from extract_from_blog import extract_series_exercises

        blog_path_str = os.environ.get("BLOG_PATH", "")
        if not blog_path_str:
            # No blog path configured, skip extraction silently
            return

        blog_path = Path(blog_path_str)
        series = "SQL for Python Developers"
        output_path = Path("exercises")

        # Only run extraction if blog path exists
        if blog_path.exists():
            print("\nExtracting latest exercises from blog...", flush=True)
            extract_series_exercises(blog_path, series, output_path, code_block_index=0)
    except ImportError:
        # extract_from_blog not available, skip extraction
        pass
    except Exception as e:
        # Log but don't fail tests if extraction fails
        print(f"\nExtraction skipped: {e}", flush=True)


@pytest.fixture
def db_connection():
    """Provide a clean in-memory DuckDB connection for each test."""
    conn = duckdb.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def db_with_customers(db_connection):
    """Provide DuckDB connection with sample customer table."""
    load_sample_customers(db_connection)
    return db_connection


@pytest.fixture
def db_with_orders(db_connection):
    """Provide DuckDB connection with sample order table."""
    load_sample_orders(db_connection)
    return db_connection


@pytest.fixture
def db_with_sample_data(db_connection):
    """Provide DuckDB connection with both customer and order tables."""
    load_sample_customers(db_connection)
    load_sample_orders(db_connection)
    return db_connection


@pytest.fixture
def temp_db_file(tmp_path):
    """Provide a file-based DuckDB for persistence testing."""
    db_path = tmp_path / "test.duckdb"
    conn = duckdb.connect(str(db_path))
    yield conn
    conn.close()
