"""From segment revenue to a $10M portfolio, a return metric, and a range.

Return metric (default): year-1 net cash yield on total cash deployed
    = NOI_2027 / (purchase + closing + furnishing)
assuming all-cash purchase (no leverage). Swap or justify this in the decision log.
"""
import json
import numpy as np
import pandas as pd
from . import config

KEY_NUMBERS: dict = {}


def record(key, value, source):
    """Every number on a slide goes through here so a judge can trace it."""
    KEY_NUMBERS[key] = {"value": value if not isinstance(value, (np.floating, np.integer)) else value.item(),
                        "source": source}
    return value


def load_purchase_prices() -> pd.DataFrame:
    """External: typical purchase price by neighbourhood x bucket x bedrooms.
    Fill data/external/purchase_prices.csv from a public source (see docs/assumptions.md)."""
    p = pd.read_csv(config.EXTERNAL / "purchase_prices.csv", dtype={"bedrooms_grp": str})
    return p[["neighbourhood_cleansed", "bucket", "bedrooms_grp", "price_cad", "source"]]


def underwrite(seg: pd.DataFrame, rev_col="rev_median") -> pd.DataFrame:
    s = seg.copy()
    gross = s[rev_col]
    var_costs = gross * (config.PLATFORM_FEE + config.MANAGEMENT_FEE + config.CLEANING_AND_SUPPLIES)
    strata = s["bucket"].map(config.STRATA_FEES_CAD_MONTH).fillna(400) * 12
    fixed = (config.LICENCE_AND_REGISTRATION_CAD + config.INSURANCE_CAD_YEAR + strata
             + s["price_cad"] * config.PROPERTY_TAX_RATE)
    s["noi"] = gross - var_costs - fixed
    s["cash_in"] = s["price_cad"] * (1 + config.CLOSING_COSTS) + config.FURNISHING_CAD
    s["net_yield"] = s["noi"] / s["cash_in"]
    return s


def build_portfolio(uw: pd.DataFrame, budget=config.BUDGET_CAD, min_n=5,
                    max_per_neighbourhood=0.4, max_units_per_segment=None) -> pd.DataFrame:
    """Greedy: buy the highest-yield segment first, with a concentration cap per neighbourhood.
    min_n: ignore segments with too few comparable listings to trust the median."""
    cands = uw[(uw["n"] >= min_n) & uw["net_yield"].notna()].sort_values("net_yield", ascending=False)
    left, picks, spent_by_hood = budget, [], {}
    for _, r in cands.iterrows():
        cap_units = max_units_per_segment or max(1, int(r["n"] // 10))  # don't be >10% of a segment's supply
        for _ in range(cap_units):
            hood_spent = spent_by_hood.get(r["neighbourhood_cleansed"], 0)
            if r["cash_in"] > left or hood_spent + r["cash_in"] > budget * max_per_neighbourhood:
                break
            picks.append(r)
            left -= r["cash_in"]
            spent_by_hood[r["neighbourhood_cleansed"]] = hood_spent + r["cash_in"]
    return pd.DataFrame(picks)


def summarise(port: pd.DataFrame, label: str) -> dict:
    return {"scenario": label, "units": len(port), "cash_deployed": port["cash_in"].sum(),
            "noi": port["noi"].sum(), "net_yield": port["noi"].sum() / port["cash_in"].sum(),
            "neighbourhoods": port["neighbourhood_cleansed"].nunique()}


def few_vs_many(uw: pd.DataFrame) -> pd.DataFrame:
    """The central trade-off, made explicit."""
    med = uw["price_cad"].median()
    rows = [summarise(build_portfolio(uw), "optimised (greedy yield)"),
            summarise(build_portfolio(uw[uw["price_cad"] >= med]), "few high-value"),
            summarise(build_portfolio(uw[uw["price_cad"] < med]), "many modest")]
    return pd.DataFrame(rows)


def sensitivity(seg_with_prices: pd.DataFrame, port_keys: pd.DataFrame) -> pd.DataFrame:
    """Range around the 2027 number: low/base/high revenue (p25/median/p75 of comparable listings)
    plus a regulation shock (e.g. X% of nights lost to enforcement / licence suspension)."""
    keys = ["neighbourhood_cleansed", "bucket", "bedrooms_grp"]
    rows = []
    for label, col, haircut in [("low (p25 revenue)", "rev_p25", 0.0), ("base (median)", "rev_median", 0.0),
                                ("high (p75 revenue)", "rev_p75", 0.0),
                                ("base + 2 months offline (licence/regulatory)", "rev_median", 2 / 12)]:
        uw = underwrite(seg_with_prices, rev_col=col)
        uw["noi"] = uw["noi"] - uw[col] * haircut * (1 - config.PLATFORM_FEE - config.MANAGEMENT_FEE - config.CLEANING_AND_SUPPLIES)
        p = port_keys[keys].merge(uw, on=keys, how="left")
        rows.append({"case": label, "noi": p["noi"].sum(), "net_yield": p["noi"].sum() / p["cash_in"].sum()})
    return pd.DataFrame(rows)


def run(seg: pd.DataFrame):
    config.TABLES.mkdir(parents=True, exist_ok=True)
    seg = seg.merge(load_purchase_prices(), on=["neighbourhood_cleansed", "bucket", "bedrooms_grp"], how="inner")
    uw = underwrite(seg)
    uw.to_csv(config.TABLES / "segments_underwritten.csv", index=False)
    port = build_portfolio(uw)
    port.to_csv(config.TABLES / "recommended_portfolio.csv", index=False)
    fvm = few_vs_many(uw); fvm.to_csv(config.TABLES / "few_vs_many.csv", index=False)
    sens = sensitivity(seg, port); sens.to_csv(config.TABLES / "sensitivity.csv", index=False)

    s = summarise(port, "recommended")
    record("portfolio_units", s["units"], "analysis.build_portfolio")
    record("portfolio_cash_deployed_cad", round(s["cash_deployed"], -3), "analysis.build_portfolio")
    record("portfolio_noi_2027_cad", round(s["noi"], -3), "analysis.underwrite + build_portfolio")
    record("portfolio_net_yield_base", round(s["net_yield"], 3), "analysis.summarise")
    record("net_yield_range", [round(sens["net_yield"].min(), 3), round(sens["net_yield"].max(), 3)],
           "analysis.sensitivity")
    (config.OUTPUTS / "key_numbers.json").write_text(json.dumps(KEY_NUMBERS, indent=2, default=float))
    print(json.dumps(KEY_NUMBERS, indent=2, default=float))
    return port, fvm, sens
