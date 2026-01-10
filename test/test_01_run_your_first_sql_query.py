from ex_01_first_query import run_query

def test_run_query(capsys):
    run_query()
    captured = capsys.readouterr()

    assert "[('Alice', 95), ('Bob', 87), ('Carol', 92)]" in captured.out