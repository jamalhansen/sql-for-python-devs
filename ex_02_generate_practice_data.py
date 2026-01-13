from faker import Faker
import duckdb
import random
from pandas import DataFrame

fake = Faker()

# Set seeds for reproducible results
Faker.seed(42)
random.seed(42)


def generate_customer_data() -> list[dict]:
    """Generate 50 fake customer records with seeded data for reproducibility."""
    customers = []
    for i in range(50):
        customers.append(
            {
                "id": i + 1,
                "name": fake.name(),
                "email": fake.email(),
                "city": fake.city(),
                "signup_date": fake.date_between(start_date="-2y", end_date="today"),
                "is_premium": random.choice([True, False, False, False]),
            }
        )
    return customers


def load_customer_data(customers: list[dict]) -> DataFrame:
    """Load customer data into DuckDB and return as a pandas DataFrame."""
    with duckdb.connect(":memory:") as con:
        con.execute("""
            CREATE TABLE customers (
                id INTEGER,
                name VARCHAR,
                email VARCHAR,
                city VARCHAR,
                signup_date DATE,
                is_premium BOOLEAN
            )
        """)

        con.executemany(
            "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    c["id"],
                    c["name"],
                    c["email"],
                    c["city"],
                    c["signup_date"],
                    c["is_premium"],
                )
                for c in customers
            ],
        )

        results = con.execute("SELECT * FROM customers").fetchdf()
    return results


def main() -> None:
    """Generate customer data, load into DuckDB, and display results."""
    customers = generate_customer_data()
    results = load_customer_data(customers)

    print(f"Returned {len(results)} rows of data.")
    print("Here are the first 5 rows:")
    print(results.head(5))


if __name__ == "__main__":
    main()
