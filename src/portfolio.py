"""Segment revenue -> costs -> $10M portfolio -> range of outcomes.

Return metric: year-1 net cash yield = NOI / (purchase + closing + furnishing), all-cash.
"""
import pandas as pd
from . import config

VAR_COST_SHARE = config.PLATFORM_FEE + config.MANAGEMENT_FEE + config.CLEANING_AND_SUPPLIES


def add_purchase_prices(seg: pd.DataFrame) -> pd.DataFrame:
    """Price each segment from the GVR benchmark (type x East/West), condos scaled by bedrooms.
    Drops segments DDD can't buy on their own (suite, other)."""
    gvr = pd.read_csv(config.GVR_FILE)
    s = seg[seg["bucket"].isin(config.BUCKET_TO_GVR_TYPE)].copy()
    s["side"] = s["neighbourhood_cleansed"].map({**{n: "West" for n in config.WEST},
                                                 **{n: "East" for n in config.EAST}})
    s["gvr_type"] = s["bucket"].map(config.BUCKET_TO_GVR_TYPE)
    s = s.merge(gvr, on=["side", "gvr_type"], how="left")
    mult = s["bedrooms_grp"].map(config.CONDO_BEDROOM_MULTIPLIER).where(s["bucket"] == "condo", 1.0)
    s["price_cad"] = s["benchmark_price_cad"] * mult
    return s


def underwrite(seg: pd.DataFrame, rev_col="rev_median", months_offline=0) -> pd.DataFrame:
    s = seg.copy()
    gross = s[rev_col] * (1 - months_offline / 12)
    strata = s["bucket"].map(config.STRATA_FEES_CAD_MONTH).fillna(400) * 12
    fixed = (config.LICENCE_AND_REGISTRATION_CAD + config.INSURANCE_CAD_YEAR + strata
             + s["price_cad"] * config.PROPERTY_TAX_RATE)
    s["noi"] = gross * (1 - VAR_COST_SHARE) - fixed
    s["cash_in"] = s["price_cad"] * (1 + config.CLOSING_COSTS) + config.FURNISHING_CAD
    s["net_yield"] = s["noi"] / s["cash_in"]
    return s


def build_portfolio(uw: pd.DataFrame, budget=config.BUDGET_CAD, min_n=5, max_per_hood=0.4) -> pd.DataFrame:
    """Greedy: buy highest-yield segments first.
    Caps: <=40% of budget per neighbourhood, <=10% of a segment's existing supply,
    and skip segments with < min_n comparables (median not trustworthy)."""
    cands = uw[(uw["n"] >= min_n) & uw["net_yield"].notna()].sort_values("net_yield", ascending=False)
    left, picks, by_hood = budget, [], {}
    for _, r in cands.iterrows():
        for _ in range(max(1, int(r["n"] // 10))):
            spent = by_hood.get(r["neighbourhood_cleansed"], 0)
            if r["cash_in"] > left or spent + r["cash_in"] > budget * max_per_hood:
                break
            picks.append(r)
            left -= r["cash_in"]
            by_hood[r["neighbourhood_cleansed"]] = spent + r["cash_in"]
    return pd.DataFrame(picks)


def summarise(port: pd.DataFrame, label: str) -> dict:
    return {"scenario": label, "units": len(port), "cash_deployed": port["cash_in"].sum(),
            "noi": port["noi"].sum(), "net_yield": port["noi"].sum() / port["cash_in"].sum(),
            "neighbourhoods": port["neighbourhood_cleansed"].nunique()}


def few_vs_many(uw: pd.DataFrame) -> pd.DataFrame:
    """The 'how many' question: optimised vs a few expensive units vs many cheap ones."""
    med = uw["price_cad"].median()
    return pd.DataFrame([summarise(build_portfolio(uw), "optimised"),
                         summarise(build_portfolio(uw[uw["price_cad"] >= med]), "few high-value"),
                         summarise(build_portfolio(uw[uw["price_cad"] < med]), "many modest")])


def sensitivity(seg: pd.DataFrame, port: pd.DataFrame) -> pd.DataFrame:
    """Re-price the chosen portfolio under low/base/high revenue and a regulatory shock."""
    rows = []
    for label, col, off in [("low (p25 revenue)", "rev_p25", 0), ("base (median)", "rev_median", 0),
                            ("high (p75 revenue)", "rev_p75", 0), ("base + 2 months offline", "rev_median", 2)]:
        p = port[config.SEGMENT_KEYS].merge(underwrite(seg, col, off), on=config.SEGMENT_KEYS, how="left")
        rows.append({"case": label, "noi": p["noi"].sum(), "net_yield": p["noi"].sum() / p["cash_in"].sum()})
    return pd.DataFrame(rows)
