import pandas as pd
from src.clean import parse_price, licence_status
from src.analysis import underwrite, build_portfolio


def test_parse_price():
    assert parse_price(pd.Series(["$1,234.00", "$85.00", None])).tolist()[:2] == [1234.0, 85.0]


def test_licence_status_hides_numbers():
    s = licence_status(pd.Series(["24-123456", "Exempt", None, "pending", "abc"]))
    assert s.tolist() == ["has_number", "exempt_claimed", "missing", "pending", "other_text"]


def test_portfolio_respects_budget():
    seg = pd.DataFrame({"neighbourhood_cleansed": list("ABCDE"), "bucket": "condo", "bedrooms_grp": "1",
                        "n": 50, "rev_median": [60e3, 55e3, 50e3, 45e3, 40e3], "price_cad": 700e3})
    port = build_portfolio(underwrite(seg), budget=10e6)
    assert port["cash_in"].sum() <= 10e6
    assert port.groupby("neighbourhood_cleansed")["cash_in"].sum().max() <= 0.4 * 10e6
