import pytest


def insecure_sql_query(cursor, user_input):
    # Construye la consulta concatenando directamente
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    cursor.execute(query)
    return query


def insecure_html(param):
    # Genera HTML incluyendo directamente el parámetro
    return f"<div>{param}</div>"


class DummyCursor:
    def __init__(self):
        self.executed = None

    def execute(self, query):
        self.executed = query


@pytest.mark.timeout(5)
def test_insecure_sql_query_executes_with_safe_input():
    cursor = DummyCursor()
    result = insecure_sql_query(cursor, "Alice")
    assert result == "SELECT * FROM users WHERE name = 'Alice'"
    assert cursor.executed == result


@pytest.mark.timeout(5)
def test_insecure_html_returns_expected_string():
    html = insecure_html("<script>alert('x')</script>")
    assert html == "<div><script>alert('x')</script></div>"
