# SQL for Python Developers

A structured learning project for SQL fundamentals using DuckDB and Python.

## Project Structure

```text
├── exercises/           # Extracted code from blog posts
│   ├── 02_zero-setup-sql-*.py
│   ├── 03_generate-practice-data-*.py
│   └── ...
├── helpers/             # Shared utilities
│   ├── __init__.py
│   └── db.py           # DuckDB helpers and fixtures
├── test/                # Test files
│   ├── conftest.py     # Shared pytest fixtures
│   └── test_*.py       # Exercise tests
├── extract_from_blog.py # Script to extract exercises from blog posts
└── pyproject.toml      # Project configuration
```

## Installation

```bash
# Install dependencies
pip install -e .
```

## Extracting Exercises from Blog

The `extract_from_blog.py` script automatically pulls code examples from your Hugo blog posts that are tagged with the "SQL for Python Developers" series.

Set the `BLOG_PATH` environment variable to point to your Hugo blog directory:

```bash
# Extract the first Python code block from each post (default)
BLOG_PATH=/path/to/your/hugo/blog python3 extract_from_blog.py

# Extract the second code block from each post
BLOG_PATH=/path/to/your/hugo/blog python3 extract_from_blog.py 1

# Or export it for your session
export BLOG_PATH=/path/to/your/hugo/blog
python3 extract_from_blog.py
```

The script:

- Filters posts by series tag (case-insensitive)
- Sorts by `weight` field to maintain post order
- Extracts Python code blocks and saves as numbered exercises
- Handles both list and string format for series tags
- Creates readable filenames from post titles

## Running Tests

```bash
pytest test/
```

If `BLOG_PATH` is set, tests will automatically extract the latest exercises from your blog before running. Otherwise, tests run against the existing exercise files.

## Using Test Helpers

The `test/conftest.py` provides shared fixtures for DuckDB:

```python
# Using the fixtures in your tests
def test_customers(db_with_customers):
    """Test with pre-loaded customer data"""
    result = db_with_customers.execute(
        "SELECT COUNT(*) as count FROM customers"
    ).fetchone()
    assert result[0] == 5

def test_custom_data(db_connection):
    """Test with a blank connection"""
    db_connection.execute("CREATE TABLE test (id INT)")
    # ... your test code
```

### Available Fixtures

- `db_connection` - Clean in-memory connection
- `db_with_customers` - Connection with sample customer table
- `db_with_orders` - Connection with sample order table
- `db_with_sample_data` - Connection with both tables
- `temp_db_file` - File-based database for persistence testing

## Using Database Helpers

The `helpers/db.py` module provides utility functions:

```python
from helpers.db import (
    create_connection,
    load_sample_customers,
    query_to_list,
    query_to_dict_list,
)

# Create a connection
conn = create_connection(":memory:")

# Load sample data
load_sample_customers(conn)

# Query results as list of tuples
results = query_to_list(conn, "SELECT * FROM customers")

# Query results as list of dicts
results = query_to_dict_list(conn, "SELECT * FROM customers WHERE is_premium")
```
