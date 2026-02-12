"""Tests for SQL queries extracted from blog posts.

These tests verify that the SQL examples from the blog work correctly
against the sample data. They validate both structure AND data correctness.
"""

import pytest
from pathlib import Path
from helpers.db import execute_sql_file, load_sql_file, query_to_dict_list


# SQL files that reference external data files - now provided in data/
EXTERNAL_DATA_FILES = set()  # All files have sample data

# SQL files that are intentional examples of invalid queries from the blog
EXPECTED_FAILURES = {
    "10_group-by-aggregating-your-data_4_2.sql",  # Demonstrates missing GROUP BY column
    "11_having-filtering-grouped-results_2_1.sql",  # Demonstrates aggregate in WHERE clause
}


def get_all_sql_files():
    """Discover all SQL files in the sql/ directory."""
    sql_dir = Path("sql")
    if not sql_dir.exists():
        return []
    return sorted(sql_dir.glob("*.sql"))


class TestAllSqlFilesExecute:
    """Auto-discovery tests that verify ALL SQL files execute without error."""

    @pytest.mark.parametrize(
        "sql_file",
        get_all_sql_files(),
        ids=lambda f: f.name,
    )
    def test_sql_file_executes_successfully(self, db_with_sample_data, sql_file):
        """Every SQL file should execute without syntax errors."""
        if sql_file.name in EXTERNAL_DATA_FILES:
            pytest.skip(f"Skipping {sql_file.name} - references external data file")

        if sql_file.name in EXPECTED_FAILURES:
            pytest.skip(f"Skipping {sql_file.name} - intentional example of invalid SQL")

        # This will raise if SQL has syntax errors or references missing tables
        result = execute_sql_file(db_with_sample_data, sql_file)
        assert result is not None, f"{sql_file.name} should return results"

    @pytest.mark.parametrize(
        "sql_file",
        get_all_sql_files(),
        ids=lambda f: f.name,
    )
    def test_sql_file_is_not_empty(self, sql_file):
        """Every SQL file should contain a query."""
        content = load_sql_file(sql_file)
        assert len(content.strip()) > 0, f"{sql_file.name} should not be empty"
        assert "SELECT" in content.upper(), f"{sql_file.name} should contain SELECT"


class TestSelectColumns:
    """Tests for SELECT column operations (Exercise 06)."""

    def test_select_name_email_returns_correct_columns(self, db_with_customers):
        """SELECT name, email should return exactly those two columns."""
        sql_file = Path("sql/06_select-choosing-your-columns_1_1.sql")
        result = execute_sql_file(db_with_customers, sql_file)

        assert len(result) == 5, "Should return all 5 customers"
        assert len(result[0]) == 2, "Should return exactly 2 columns"

        result_set = set(result)
        assert ("Alice Johnson", "alice@example.com") in result_set
        assert ("Bob Smith", "bob@example.com") in result_set
        assert ("Eve Davis", "eve@example.com") in result_set

    def test_select_with_alias(self, db_with_customers):
        """SELECT with AS alias should rename columns."""
        sql_file = Path("sql/06_select-choosing-your-columns_2_1.sql")
        if not sql_file.exists():
            pytest.skip("SQL file not found")

        result = execute_sql_file(db_with_customers, sql_file)
        assert len(result) == 5, "Should return all 5 customers"

    def test_string_concatenation_creates_location(self, db_with_customers):
        """String concatenation should create 'City, USA' format."""
        sql_file = Path("sql/06_select-choosing-your-columns_3_1.sql")
        result = execute_sql_file(db_with_customers, sql_file)

        locations = {row[0]: row[1] for row in result}

        assert locations["Alice Johnson"] == "New York, USA"
        assert locations["Bob Smith"] == "San Francisco, USA"
        assert locations["Carol White"] == "Boston, USA"
        assert locations["David Brown"] == "Seattle, USA"
        assert locations["Eve Davis"] == "Austin, USA"

    def test_year_calculation_computes_tenure(self, db_with_customers):
        """Year math should calculate years as customer correctly."""
        sql_file = Path("sql/06_select-choosing-your-columns_3_2.sql")
        result = execute_sql_file(db_with_customers, sql_file)

        tenure_by_name = {row[0]: row[1] for row in result}

        # 2026 - 2024 = 2 years for all customers
        assert tenure_by_name["Alice Johnson"] == 2
        assert tenure_by_name["Bob Smith"] == 2
        assert tenure_by_name["Carol White"] == 2

    def test_upper_function_transforms_city(self, db_with_customers):
        """UPPER() function should transform city to uppercase."""
        sql_file = Path("sql/06_select-choosing-your-columns_3_3.sql")
        if not sql_file.exists():
            pytest.skip("SQL file not found")

        result = execute_sql_file(db_with_customers, sql_file)
        cities_by_name = {row[0]: row[1] for row in result}

        assert cities_by_name["Alice Johnson"] == "NEW YORK"
        assert cities_by_name["Bob Smith"] == "SAN FRANCISCO"
        assert cities_by_name["Carol White"] == "BOSTON"

    def test_select_single_column(self, db_with_customers):
        """SELECT city should return just the city column."""
        sql_file = Path("sql/06_select-choosing-your-columns_4_1.sql")
        if not sql_file.exists():
            pytest.skip("SQL file not found")

        result = execute_sql_file(db_with_customers, sql_file)

        assert len(result) == 5, "Should return all 5 rows"
        assert len(result[0]) == 1, "Should return exactly 1 column"

        cities = [row[0] for row in result]
        assert "New York" in cities
        assert "San Francisco" in cities

    def test_select_distinct_removes_duplicates(self, db_with_customers):
        """SELECT DISTINCT should remove duplicate values."""
        sql_file = Path("sql/06_select-choosing-your-columns_4_2.sql")
        if not sql_file.exists():
            pytest.skip("SQL file not found")

        result = execute_sql_file(db_with_customers, sql_file)
        cities = [row[0] for row in result]

        # All 5 customers have different cities, so DISTINCT returns 5
        assert len(cities) == 5
        # No duplicates
        assert len(cities) == len(set(cities))


class TestSetOperations:
    """Tests for set-based SQL operations (Exercise 05)."""

    def test_where_filters_premium_customers(self, db_with_customers):
        """WHERE is_premium = true should return only premium customers."""
        sql_file = Path("sql/05_sql-thinks-in-sets-not-loops.sql")
        if not sql_file.exists():
            pytest.skip("SQL file not found")

        result = execute_sql_file(db_with_customers, sql_file)
        names = [row[0] for row in result]

        # Should return exactly the 3 premium customers
        assert len(names) == 3
        assert "Alice Johnson" in names
        assert "Carol White" in names
        assert "Eve Davis" in names
        # Non-premium customers should not be in results
        assert "Bob Smith" not in names
        assert "David Brown" not in names


class TestFromClause:
    """Tests for FROM clause operations (Exercise 07)."""

    def test_select_all_names_from_customers(self, db_with_customers):
        """Basic FROM should return all customer names."""
        sql_file = Path("sql/07_from-where-your-data-lives_1_1.sql")
        result = execute_sql_file(db_with_customers, sql_file)

        names = [row[0] for row in result]
        assert len(names) == 5
        assert "Alice Johnson" in names
        assert "Bob Smith" in names

    def test_select_star_returns_all_columns(self, db_with_customers):
        """SELECT * should return all columns from the table."""
        sql_file = Path("sql/07_from-where-your-data-lives_2_1.sql")
        if not sql_file.exists():
            pytest.skip("SQL file not found")

        result = execute_sql_file(db_with_customers, sql_file)

        assert len(result) == 5, "Should return all 5 customers"
        # customers table has 6 columns: id, name, email, city, signup_date, is_premium
        assert len(result[0]) == 6, "Should return all 6 columns"

    def test_select_specific_columns(self, db_with_customers):
        """SELECT name, email should return only those columns."""
        sql_file = Path("sql/07_from-where-your-data-lives_2_2.sql")
        if not sql_file.exists():
            pytest.skip("SQL file not found")

        result = execute_sql_file(db_with_customers, sql_file)

        assert len(result) == 5
        assert len(result[0]) == 2, "Should return exactly 2 columns"

        # Verify it's name and email (not other columns)
        result_set = set(result)
        assert ("Alice Johnson", "alice@example.com") in result_set

    def test_select_city_column(self, db_with_customers):
        """SELECT city should return city for all customers."""
        sql_file = Path("sql/07_from-where-your-data-lives_2_3.sql")
        if not sql_file.exists():
            pytest.skip("SQL file not found")

        result = execute_sql_file(db_with_customers, sql_file)
        cities = [row[0] for row in result]

        assert len(cities) == 5
        expected_cities = {"New York", "San Francisco", "Boston", "Seattle", "Austin"}
        assert set(cities) == expected_cities


class TestExternalDataQueries:
    """Tests for SQL queries that reference external data files.

    These queries demonstrate DuckDB's ability to query CSV/Parquet files directly.
    They're marked as expected to fail since the data files don't exist in tests.
    """

    def test_csv_query_documents_feature(self):
        """Document that DuckDB can query CSV files directly."""
        sql_file = Path("sql/07_from-where-your-data-lives_3_1.sql")
        if not sql_file.exists():
            pytest.skip("SQL file not found")

        content = load_sql_file(sql_file)
        assert "sales.csv" in content, "Should reference a CSV file"
        assert "SELECT" in content.upper()

    def test_parquet_query_documents_feature(self):
        """Document that DuckDB can query Parquet files directly."""
        sql_file = Path("sql/07_from-where-your-data-lives_3_2.sql")
        if not sql_file.exists():
            pytest.skip("SQL file not found")

        content = load_sql_file(sql_file)
        assert "logs.parquet" in content, "Should reference a Parquet file"
        assert "SELECT" in content.upper()


class TestSqlFileIntegrity:
    """General tests to verify SQL files are valid and well-formed."""

    def test_sql_directory_exists(self):
        """The sql/ directory should exist."""
        sql_dir = Path("sql")
        assert sql_dir.exists(), "sql/ directory should exist"

    def test_sql_files_exist(self):
        """Should have SQL files in the sql/ directory."""
        sql_files = get_all_sql_files()
        assert len(sql_files) > 0, "Should have at least one SQL file"

    def test_no_sql_file_is_empty(self):
        """No SQL file should be completely empty."""
        for sql_file in get_all_sql_files():
            content = load_sql_file(sql_file)
            assert len(content.strip()) > 0, f"{sql_file.name} should not be empty"


class TestSampleDataIntegration:
    """Integration tests verifying sample data works with SQL queries."""

    def test_customers_and_orders_can_be_joined(self, db_with_sample_data):
        """Customers and orders tables should be joinable."""
        result = query_to_dict_list(
            db_with_sample_data,
            """
            SELECT c.name, o.product, o.amount
            FROM customers c
            JOIN orders o ON c.id = o.customer_id
            ORDER BY o.id
            """,
        )

        assert len(result) == 5, "Should have 5 orders"
        assert result[0]["name"] == "Alice Johnson"
        assert float(result[0]["amount"]) == 150.50
        assert result[0]["product"] == "Widget"

    def test_aggregate_queries_work(self, db_with_sample_data):
        """Aggregate functions should work on sample data."""
        result = query_to_dict_list(
            db_with_sample_data,
            """
            SELECT
                COUNT(*) as order_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM orders
            """,
        )

        assert result[0]["order_count"] == 5
        # Total: 150.50 + 75.00 + 200.00 + 50.25 + 300.00 = 775.75
        assert float(result[0]["total_amount"]) == 775.75

    def test_filter_premium_customers(self, db_with_customers):
        """Should be able to filter by boolean column."""
        result = query_to_dict_list(
            db_with_customers,
            "SELECT name FROM customers WHERE is_premium ORDER BY name",
        )

        names = [r["name"] for r in result]
        assert names == ["Alice Johnson", "Carol White", "Eve Davis"]
