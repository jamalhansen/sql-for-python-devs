"""Example test showing how to test SQL queries extracted from blog posts."""

from pathlib import Path
from helpers.db import execute_sql_file, load_sql_file


def test_select_columns_1(db_with_customers):
    """Test: SELECT name, email FROM customers"""
    sql_file = Path("sql/06_select-choosing-your-columns_1_1.sql")
    result = execute_sql_file(db_with_customers, sql_file)

    # Should return 2 columns (name, email) for 5 customers
    assert len(result) == 5
    assert len(result[0]) == 2

    # Check that Alice is in results
    names = [row[0] for row in result]
    assert "Alice Johnson" in names


def test_select_columns_concatenation(db_with_customers):
    """Test: String concatenation with aliases"""
    sql_file = Path("sql/06_select-choosing-your-columns_3_1.sql")
    result = execute_sql_file(db_with_customers, sql_file)

    # Verify we get results with concatenated location
    assert len(result) == 5
    assert len(result[0]) == 2
    # Check format: "City, USA"
    locations = [row[1] for row in result]
    assert all(", USA" in loc for loc in locations)


def test_select_columns_math(db_with_customers):
    """Test: Math operations on numbers"""
    sql_file = Path("sql/06_select-choosing-your-columns_3_2.sql")
    result = execute_sql_file(db_with_customers, sql_file)

    # Verify we get years_as_customer column
    assert len(result) > 0
    assert len(result[0]) == 2


def test_where_clause(db_with_customers):
    """Test: WHERE clause filtering"""
    sql_file = Path("sql/07_from-where-your-data-lives_1_1.sql")
    result = execute_sql_file(db_with_customers, sql_file)

    # Should get filtered results
    assert len(result) > 0


def test_sql_file_loading():
    """Test that SQL files can be loaded correctly"""
    sql_file = Path("sql/06_select-choosing-your-columns_1_1.sql")
    sql_content = load_sql_file(sql_file)

    assert "SELECT" in sql_content.upper()
    assert len(sql_content) > 0
