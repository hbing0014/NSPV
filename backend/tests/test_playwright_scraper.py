from app.services.scrapers.playwright_amazon import parse_int, parse_price, parse_rating


def test_parse_price() -> None:
    assert parse_price("$1,234.56") == 1234.56
    assert parse_price("$6931") == 69.31
    assert parse_price("JPY 6,931") == 46.44
    assert parse_price("No price") is None
    assert parse_price(None) is None


def test_parse_rating() -> None:
    assert parse_rating("4.6 out of 5 stars") == 4.6
    assert parse_rating("No rating") is None
    assert parse_rating(None) is None


def test_parse_int() -> None:
    assert parse_int("1,234") == 1234
    assert parse_int("No reviews") is None
    assert parse_int(None) is None
