"""DuckDB utilities and helpers for testing."""

import duckdb
from pathlib import Path
from typing import Optional


def create_connection(
    database: Optional[str] = ":memory:",
) -> duckdb.DuckDBPyConnection:
    """
    Create a DuckDB connection.

    Args:
        database: Path to database file or ":memory:" for in-memory DB

    Returns:
        DuckDB connection object
    """
    return duckdb.connect(database)


def load_sample_customers(conn: duckdb.DuckDBPyConnection) -> int:
    """
    Load sample customer data into DuckDB.

    Args:
        conn: DuckDB connection

    Returns:
        Number of records loaded
    """
    conn.execute("""
        CREATE TABLE customers (
            id INTEGER,
            name VARCHAR,
            email VARCHAR,
            city VARCHAR,
            signup_date DATE,
            is_premium BOOLEAN
        )
    """)

    sample_data = [
        (1, "Alice Johnson", "alice@example.com", "New York", "2024-01-15", True),
        (2, "Bob Smith", "bob@example.com", "San Francisco", "2024-02-20", False),
        (3, "Carol White", "carol@example.com", "Boston", "2024-01-10", True),
        (4, "David Brown", "david@example.com", "Seattle", "2024-03-05", False),
        (5, "Eve Davis", "eve@example.com", "Austin", "2024-02-28", True),
    ]

    conn.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)",
        sample_data,
    )

    return len(sample_data)


def load_sample_orders(conn: duckdb.DuckDBPyConnection) -> int:
    """
    Load sample order data into DuckDB.

    Args:
        conn: DuckDB connection

    Returns:
        Number of records loaded
    """
    conn.execute("""
        CREATE TABLE orders (
            id INTEGER,
            customer_id INTEGER,
            product VARCHAR,
            amount DECIMAL(10, 2),
            order_date DATE
        )
    """)

    sample_data = [
        (1001, 1, "Widget", 150.50, "2024-03-01"),
        (1002, 2, "Gadget", 75.00, "2024-03-02"),
        (1003, 1, "Gizmo", 200.00, "2024-03-05"),
        (1004, 3, "Widget", 50.25, "2024-03-06"),
        (1005, 4, "Doohickey", 300.00, "2024-03-07"),
    ]

    conn.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?)",
        sample_data,
    )

    return len(sample_data)


def query_to_list(conn: duckdb.DuckDBPyConnection, query: str) -> list:
    """
    Execute a query and return results as a list of tuples.

    Args:
        conn: DuckDB connection
        query: SQL query to execute

    Returns:
        List of result tuples
    """
    return conn.execute(query).fetchall()


def query_to_dict_list(conn: duckdb.DuckDBPyConnection, query: str) -> list[dict]:
    """
    Execute a query and return results as a list of dictionaries.

    Args:
        conn: DuckDB connection
        query: SQL query to execute

    Returns:
        List of result dictionaries with column names as keys
    """
    cursor = conn.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def load_sql_file(file_path: Path | str) -> str:
    """
    Load SQL query from a file.

    Args:
        file_path: Path to SQL file

    Returns:
        SQL query string
    """
    return Path(file_path).read_text().strip()


def execute_sql_file(
    conn: duckdb.DuckDBPyConnection, file_path: Path | str
) -> list[tuple]:
    """
    Load and execute SQL from a file.

    Args:
        conn: DuckDB connection
        file_path: Path to SQL file

    Returns:
        List of result tuples
    """
    query = load_sql_file(file_path)
    return conn.execute(query).fetchall()
