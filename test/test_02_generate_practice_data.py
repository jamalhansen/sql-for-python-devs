from ex_02_generate_practice_data import (
    generate_customer_data,
    load_customer_data,
    main,
)
from datetime import date


def test_generate_customer_data():
    customers = generate_customer_data()

    assert len(customers) == 50

    expected_keys = ["id", "name", "email", "city", "signup_date", "is_premium"]
    actual_keys = customers[0].keys()

    assert len(expected_keys) == len(actual_keys)

    for expected_key in expected_keys:
        assert expected_key in actual_keys


def test_load_customer_data():
    test_data = {
        "id": 1,
        "name": "test_name",
        "email": "test@email.com",
        "city": "test city",
        "signup_date": date.today(),
        "is_premium": False,
    }

    customers = [test_data]
    results_df = load_customer_data(customers)

    assert len(results_df) == 1

    first_row = results_df.iloc[0].to_dict()
    assert first_row["id"] == test_data["id"]
    assert first_row["name"] == test_data["name"]
    assert first_row["email"] == test_data["email"]
    assert first_row["city"] == test_data["city"]
    assert first_row["signup_date"].date() == test_data["signup_date"]
    assert first_row["is_premium"] == test_data["is_premium"]


def test_main(capsys):
    main()
    captured = capsys.readouterr()

    assert "Returned 50 rows of data." in captured.out
    assert "Here are the first 5 rows:" in captured.out
