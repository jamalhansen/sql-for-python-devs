"""Tests for helpers/db.py functions."""

import pytest
from pathlib import Path
from helpers.db import (
    create_connection,
    load_sample_customers,
    load_sample_orders,
    query_to_list,
    query_to_dict_list,
    load_sql_file,
    execute_sql_file,
)


class TestCreateConnection:
    """Tests for create_connection function."""

    def test_creates_memory_connection(self):
        """In-memory connection should work and be queryable."""
        conn = create_connection(":memory:")
        result = conn.execute("SELECT 1 as num").fetchone()
        assert result[0] == 1
        conn.close()

    def test_creates_file_connection(self, tmp_path):
        """File-based connection should create a database file."""
        db_path = tmp_path / "test.duckdb"
        conn = create_connection(str(db_path))
        conn.execute("CREATE TABLE test (id INT)")
        conn.close()

        # Verify file was created and data persists
        assert db_path.exists()
        conn2 = create_connection(str(db_path))
        tables = conn2.execute("SHOW TABLES").fetchall()
        assert len(tables) == 1
        assert tables[0][0] == "test"
        conn2.close()

    def test_default_is_memory(self):
        """Default connection should be in-memory."""
        conn = create_connection()
        result = conn.execute("SELECT 1").fetchone()
        assert result[0] == 1
        conn.close()


class TestLoadSampleCustomers:
    """Tests for load_sample_customers function."""

    def test_returns_correct_count(self, db_connection):
        """Should return the number of records loaded."""
        count = load_sample_customers(db_connection)
        assert count == 5

    def test_creates_customers_table(self, db_connection):
        """Should create customers table with correct schema."""
        load_sample_customers(db_connection)

        # Check table exists and has correct columns
        columns = db_connection.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'customers' ORDER BY ordinal_position"
        ).fetchall()

        column_names = [c[0] for c in columns]
        assert column_names == ["id", "name", "email", "city", "signup_date", "is_premium"]

    def test_loads_expected_data(self, db_connection):
        """Should load the exact expected customer records."""
        load_sample_customers(db_connection)

        customers = db_connection.execute(
            "SELECT id, name, email, city FROM customers ORDER BY id"
        ).fetchall()

        assert customers[0] == (1, "Alice Johnson", "alice@example.com", "New York")
        assert customers[1] == (2, "Bob Smith", "bob@example.com", "San Francisco")
        assert customers[4] == (5, "Eve Davis", "eve@example.com", "Austin")

    def test_premium_customers(self, db_connection):
        """Should have correct premium status for each customer."""
        load_sample_customers(db_connection)

        premium = db_connection.execute(
            "SELECT name FROM customers WHERE is_premium ORDER BY name"
        ).fetchall()

        premium_names = [p[0] for p in premium]
        assert premium_names == ["Alice Johnson", "Carol White", "Eve Davis"]


class TestLoadSampleOrders:
    """Tests for load_sample_orders function."""

    def test_returns_correct_count(self, db_connection):
        """Should return the number of records loaded."""
        count = load_sample_orders(db_connection)
        assert count == 5

    def test_creates_orders_table(self, db_connection):
        """Should create orders table with correct schema."""
        load_sample_orders(db_connection)

        columns = db_connection.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'orders' ORDER BY ordinal_position"
        ).fetchall()

        column_names = [c[0] for c in columns]
        assert column_names == ["id", "customer_id", "product", "amount", "order_date"]

    def test_loads_expected_data(self, db_connection):
        """Should load the exact expected order records."""
        load_sample_orders(db_connection)

        orders = db_connection.execute(
            "SELECT id, customer_id, product FROM orders ORDER BY id"
        ).fetchall()

        assert orders[0] == (1001, 1, "Widget")
        assert orders[2] == (1003, 1, "Gizmo")
        assert orders[4] == (1005, 4, "Doohickey")

    def test_order_amounts(self, db_connection):
        """Should have correct decimal amounts."""
        load_sample_orders(db_connection)

        amounts = db_connection.execute(
            "SELECT id, amount FROM orders ORDER BY id"
        ).fetchall()

        assert float(amounts[0][1]) == 150.50
        assert float(amounts[1][1]) == 75.00
        assert float(amounts[3][1]) == 50.25


class TestQueryToList:
    """Tests for query_to_list function."""

    def test_returns_list_of_tuples(self, db_with_customers):
        """Should return results as list of tuples."""
        result = query_to_list(db_with_customers, "SELECT id, name FROM customers LIMIT 2")

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], tuple)
        assert result[0] == (1, "Alice Johnson")

    def test_empty_result(self, db_with_customers):
        """Should return empty list for no matches."""
        result = query_to_list(
            db_with_customers, "SELECT * FROM customers WHERE id = 999"
        )
        assert result == []

    def test_single_column(self, db_with_customers):
        """Should work with single column queries."""
        result = query_to_list(db_with_customers, "SELECT name FROM customers WHERE id = 1")
        assert result == [("Alice Johnson",)]


class TestQueryToDictList:
    """Tests for query_to_dict_list function."""

    def test_returns_list_of_dicts(self, db_with_customers):
        """Should return results as list of dictionaries."""
        result = query_to_dict_list(
            db_with_customers, "SELECT id, name FROM customers WHERE id = 1"
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)
        assert result[0] == {"id": 1, "name": "Alice Johnson"}

    def test_preserves_column_names(self, db_with_customers):
        """Should use column names/aliases as dictionary keys."""
        result = query_to_dict_list(
            db_with_customers,
            "SELECT name AS customer_name, city AS location FROM customers WHERE id = 1",
        )

        assert "customer_name" in result[0]
        assert "location" in result[0]
        assert result[0]["customer_name"] == "Alice Johnson"
        assert result[0]["location"] == "New York"

    def test_empty_result(self, db_with_customers):
        """Should return empty list for no matches."""
        result = query_to_dict_list(
            db_with_customers, "SELECT * FROM customers WHERE id = 999"
        )
        assert result == []


class TestLoadSqlFile:
    """Tests for load_sql_file function."""

    def test_loads_file_content(self, tmp_path):
        """Should load SQL content from file."""
        sql_file = tmp_path / "test.sql"
        sql_file.write_text("SELECT * FROM users")

        result = load_sql_file(sql_file)
        assert result == "SELECT * FROM users"

    def test_strips_whitespace(self, tmp_path):
        """Should strip leading/trailing whitespace."""
        sql_file = tmp_path / "test.sql"
        sql_file.write_text("  \n  SELECT 1  \n  ")

        result = load_sql_file(sql_file)
        assert result == "SELECT 1"

    def test_accepts_string_path(self, tmp_path):
        """Should accept string path as well as Path object."""
        sql_file = tmp_path / "test.sql"
        sql_file.write_text("SELECT 1")

        result = load_sql_file(str(sql_file))
        assert result == "SELECT 1"

    def test_missing_file_raises_error(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_sql_file("/nonexistent/path/query.sql")


class TestExecuteSqlFile:
    """Tests for execute_sql_file function."""

    def test_executes_and_returns_results(self, db_with_customers, tmp_path):
        """Should execute SQL from file and return results."""
        sql_file = tmp_path / "query.sql"
        sql_file.write_text("SELECT name FROM customers WHERE id = 1")

        result = execute_sql_file(db_with_customers, sql_file)
        assert result == [("Alice Johnson",)]

    def test_missing_file_raises_error(self, db_with_customers):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            execute_sql_file(db_with_customers, "/nonexistent/query.sql")

    def test_invalid_sql_raises_error(self, db_with_customers, tmp_path):
        """Should raise error for invalid SQL."""
        sql_file = tmp_path / "bad.sql"
        sql_file.write_text("SELEKT * FORM users")

        with pytest.raises(Exception):  # DuckDB raises various exceptions
            execute_sql_file(db_with_customers, sql_file)
