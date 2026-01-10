import duckdb

def run_query():
    # Connect to DuckDB in-memory
    with duckdb.connect(':memory:') as con:
        # Create table
        con.execute("""
            CREATE TABLE data(name VARCHAR, score INTEGER)
        """)

        # Insert data
        con.executemany(
            "INSERT INTO data VALUES (?, ?)",
            [('Alice', 95), ('Bob', 87), ('Carol', 92)]
        )

        # Query the data
        result = con.execute("""
            SELECT name, score 
            FROM data 
        """).fetchall()

    print(result)

if __name__ == "__main__":
    run_query()