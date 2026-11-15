"""Our analysis, end to end: listings -> options -> ranking -> $10M allocation. Writes outputs/*.

Metric: gross yield = median yearly revenue / estimated purchase price (operating costs are not given).
Allocation rules:
  1. Option = neighbourhood x property type x bedrooms (active whole-home listings).
  2. Condos only; trust an option only with >= MIN_COMPARABLES listings.
  3. Rank by gross yield; buy top-down with the $10M budget (purchase price only).
  4. Max 40% of the budget per neighbourhood; max 10% of an option's listings.
  5. Within a neighbourhood, sizes within MIX_GAP of its best option share the money (alternate buys).
  6. Leftover money flows to the next-best option.
"""
import json
from collections import defaultdict

import numpy as np
import pandas as pd

from . import config as C, prep

CORE = ["Downtown", "Downtown Eastside"]


# ---------- data ----------
def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Raw listings, cleaned listings, and the filter log."""
    raw = prep.load_listings()
    clean, log = prep.clean(raw)
    return raw, prep.add_revenue(clean), log


def active_whole_homes(clean: pd.DataFrame) -> pd.DataFrame:
    d = clean[clean["is_active"] & (clean["room_type"] == "Entire home/apt")].copy()
    d["bedrooms_grp"] = d["bedrooms"].fillna(1).clip(upper=3).astype(int).astype(str).replace({"3": "3+"})
    return d


def options(clean: pd.DataFrame) -> pd.DataFrame:
    """Every buyable option with its listings, nightly price, nights booked, revenue, price and gross yield."""
    seg = prep.segments(clean)
    values = pd.read_csv(C.PROPERTY_VALUES_FILE)
    seg = seg[seg["bucket"].isin(C.BUCKET_TO_PROP_TYPE)].copy()          # suites / other can't be bought alone
    seg["prop_type"] = seg["bucket"].map(C.BUCKET_TO_PROP_TYPE)
    seg = seg.merge(values[["neighbourhood_cleansed", "prop_type", "median_value"]],
                    on=["neighbourhood_cleansed", "prop_type"], how="inner")  # Strathcona: no homes in tax data
    mult = seg["bedrooms_grp"].map(C.CONDO_BEDROOM_MULTIPLIER).where(seg["prop_type"] == "condo", 1.0)
    seg["price_cad"] = seg["median_value"] * mult
    seg["nights_booked"] = (seg["occ_median"] * 365).round()
    seg["gross_yield"] = seg["rev_median"] / seg["price_cad"]
    cols = C.SEGMENT_KEYS + ["n", "adr_median", "nights_booked", "occ_median", "rev_median", "price_cad", "gross_yield"]
    return seg[cols].sort_values("gross_yield", ascending=False).reset_index(drop=True)


# ---------- allocation ----------
def allocate(opts: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    s = opts[(opts["n"] >= C.MIN_COMPARABLES) & (opts["bucket"] == "condo")].copy()
    best = s.groupby("neighbourhood_cleansed")["gross_yield"].transform("max")
    s = s[s["gross_yield"] >= best - C.MIX_GAP]
    left, hood, picks = C.BUDGET_CAD, defaultdict(float), []
    for h, g in sorted(s.groupby("neighbourhood_cleansed"), key=lambda x: -x[1]["gross_yield"].max()):
        rows, bought = g.sort_values("gross_yield", ascending=False).to_dict("records"), defaultdict(int)
        while True:                                   # alternate between the near-tied sizes
            progress = False
            for r in rows:
                if bought[r["bedrooms_grp"]] >= int(r["n"] * C.MAX_SEGMENT_SHARE):
                    continue
                if r["price_cad"] > left or hood[h] + r["price_cad"] > C.BUDGET_CAD * C.MAX_NEIGHBOURHOOD_SHARE:
                    continue
                picks.append(r); left -= r["price_cad"]; hood[h] += r["price_cad"]
                bought[r["bedrooms_grp"]] += 1; progress = True
            if not progress:
                break
    p = pd.DataFrame(picks)
    alloc = (p.groupby(["neighbourhood_cleansed", "bedrooms_grp"], sort=False)
              .agg(units=("n", "size"), listings=("n", "first"), price_each=("price_cad", "first"),
                   revenue_each=("rev_median", "first"), gross_yield=("gross_yield", "first"),
                   money=("price_cad", "sum"), revenue=("rev_median", "sum")).reset_index())
    alloc["share_of_budget"] = alloc["money"] / C.BUDGET_CAD
    return alloc, left


def cost_based_model(opts: pd.DataFrame) -> dict:
    """Decision 3 comparison: our earlier model, which ranked by net yield after assumed operating costs."""
    s = opts.copy()
    fixed = (C.LICENCE_AND_REGISTRATION_CAD + C.INSURANCE_CAD_YEAR
             + 12 * s["bucket"].map(C.STRATA_FEES_CAD_MONTH).fillna(0) + s["price_cad"] * C.PROPERTY_TAX_RATE)
    s["cash"] = s["price_cad"] * (1 + C.CLOSING_COSTS) + C.FURNISHING_CAD
    s["noi"] = s["rev_median"] * (1 - C.PLATFORM_FEE - C.MANAGEMENT_FEE - C.CLEANING_AND_SUPPLIES) - fixed
    s["net_yield"] = s["noi"] / s["cash"]
    spent, hood, units, revenue, price = 0.0, defaultdict(float), 0, 0.0, 0.0
    for r in s[(s["n"] >= C.MIN_COMPARABLES) & (s["noi"] > 0)].sort_values("net_yield", ascending=False).itertuples():
        for _ in range(int(r.n * C.MAX_SEGMENT_SHARE)):
            h = r.neighbourhood_cleansed
            if spent + r.cash > C.BUDGET_CAD or hood[h] + r.cash > C.BUDGET_CAD * C.MAX_NEIGHBOURHOOD_SHARE:
                break
            spent += r.cash; hood[h] += r.cash; units += 1; revenue += r.rev_median; price += r.price_cad
    return {"units": units, "revenue": revenue, "money_spent": price}


def transfer_tax(price: float) -> float:
    """BC property transfer tax, standard rates, no exemptions: 1% to $200K, 2% to $2M, 3% to $3M, 5% above."""
    bands = [(200_000, 0.01), (2_000_000, 0.02), (3_000_000, 0.03), (float("inf"), 0.05)]
    tax, lower = 0.0, 0.0
    for upper, rate in bands:
        tax += max(0.0, min(price, upper) - lower) * rate
        lower = upper
    return tax


def acquisition_budget(alloc: pd.DataFrame) -> dict:
    """Appendix: does the plan fit $10M if transfer tax or higher prices are included? (one purchase per unit)"""
    prices = alloc.loc[alloc.index.repeat(alloc["units"]), "price_each"]
    purchase, tax = prices.sum(), prices.map(transfer_tax).sum()
    return {"purchase_prices": float(purchase), "transfer_tax": float(tax),
            "purchase_plus_transfer_tax": float(purchase + tax), "purchase_prices_plus5pct": float(purchase * 1.05)}


# ---------- checks ----------
def sample_size_test(d: pd.DataFrame) -> pd.DataFrame:
    """How far a median from n listings lands from the median of all Downtown 1-bed condos (5,000 draws each)."""
    g = d[(d["bucket"] == "condo") & (d["neighbourhood_cleansed"] == "Downtown") & (d["bedrooms_grp"] == "1")]
    r = g["revenue"].dropna().to_numpy(); true = np.median(r); rng = np.random.default_rng(0)
    rows = []
    for n in (5, 10, 20, 30, 50, 100):
        err = np.abs(np.array([np.median(rng.choice(r, n, replace=False)) for _ in range(5000)]) / true - 1)
        rows.append({"listings": n, "typical_error": np.median(err), "error_90pct": np.quantile(err, .9)})
    return pd.DataFrame(rows)


def condo_occupancy(d: pd.DataFrame) -> pd.DataFrame:
    t = (d[d["bucket"] == "condo"].groupby("neighbourhood_cleansed")["estimated_occupancy_l365d"]
          .agg(listings="size", median_nights="median").reset_index())
    t["occupancy"] = t["median_nights"] / 365
    return t[t["listings"] >= C.MIN_COMPARABLES].sort_values("occupancy", ascending=False)


def funnel(raw, clean, opts) -> pd.DataFrame:
    condo = opts[opts["bucket"] == "condo"]
    return pd.DataFrame([
        ("Raw listings (15 Jun 2026)", len(raw)),
        ("Clean: priced $30-$2,000, stay < 90 nights", len(clean)),
        ("Active whole homes", len(active_whole_homes(clean))),
        ("Buyable condos & houses", int(opts["n"].sum())),
        ("Condos", int(condo["n"].sum())),
        (f"Condos in options with >= {C.MIN_COMPARABLES} listings", int(condo.loc[condo["n"] >= C.MIN_COMPARABLES, "n"].sum())),
    ], columns=["stage", "listings"])


# ---------- run ----------
def main():
    C.OUTPUTS.mkdir(exist_ok=True)
    raw, clean, log = load()
    d = active_whole_homes(clean)
    opts = options(clean)
    alloc, left = allocate(opts)
    tables = {"filters": log, "options": opts, "allocation": alloc, "funnel": funnel(raw, clean, opts),
              "sample_size_test": sample_size_test(d), "condo_occupancy": condo_occupancy(d)}
    for name, t in tables.items():
        t.to_csv(C.OUTPUTS / f"{name}.csv", index=False)
    rev, money = alloc["revenue"].sum(), alloc["money"].sum()
    summary = {
        "units": int(alloc["units"].sum()), "neighbourhoods": int(alloc["neighbourhood_cleansed"].nunique()),
        "money_spent": float(money), "unspent": float(left), "revenue": float(rev), "gross_yield": float(rev / money),
        "scenarios_2027": {k: {"revenue": float(rev * f), "gross_yield": float(rev * f / money)}
                           for k, f in [("revenue_minus20", 0.8), ("base", 1.0), ("revenue_plus10", 1.1)]},
        "old_cost_based_model": cost_based_model(opts),
        "acquisition_budget": acquisition_budget(alloc),
        "concentration_downtown_core": float(alloc.loc[alloc["neighbourhood_cleansed"].isin(CORE), "money"].sum() / C.BUDGET_CAD),
        "data_checks": {"scrape_dates": raw["last_scraped"].value_counts().to_dict(),
                        "reviews_after_snapshot": int((raw["last_review"] > C.SNAPSHOT_DATE).sum()),
                        "missing_bedrooms_clean": int(clean["bedrooms"].isna().sum())},
        "rules": {"min_listings": C.MIN_COMPARABLES, "neighbourhood_cap": C.MAX_NEIGHBOURHOOD_SHARE,
                  "segment_share_cap": C.MAX_SEGMENT_SHARE, "mix_gap": C.MIX_GAP},
    }
    (C.OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2))
    print(alloc.to_string(index=False)); print(json.dumps({k: summary[k] for k in ["units", "revenue", "gross_yield", "old_cost_based_model"]}, indent=2))
    return summary


if __name__ == "__main__":
    main()
