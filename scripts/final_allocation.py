"""Final allocation (13 Nov 2026 team decisions). Writes outputs/final/*.

Metric: gross yield = median yearly revenue / estimated purchase price (operating costs not given).
Rules:
  1. Options = neighbourhood x property type x bedrooms, active whole-home listings.
  2. Condos only; trust an option only with >= MIN_N listings.
  3. Rank by gross yield; buy top-down with the $10M budget (purchase price only).
  4. Max 40% of the budget per neighbourhood; max 10% of an option's listings.
  5. Within a neighbourhood, sizes within GAP of its best option share the money (alternate buys).
  6. Leftover money flows to the next-best option.
Run: python scripts/final_allocation.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import config as C, prep  # noqa: E402

OUT = ROOT / "outputs" / "final"
BUDGET, CAP, MIN_N, SEG, GAP = C.BUDGET_CAD, 0.40, 30, C.MAX_SEGMENT_SHARE, 0.01


def options() -> pd.DataFrame:
    """Every buyable option with revenue, price, nights booked and gross yield."""
    s = pd.read_csv(ROOT / "outputs/tables/segments_underwritten.csv")
    s["gross_yield"] = s["rev_median"] / s["price_cad"]
    s["nights_booked"] = (s["occ_median"] * 365).round()
    cols = ["neighbourhood_cleansed", "bucket", "bedrooms_grp", "n", "adr_median", "nights_booked",
            "occ_median", "rev_median", "price_cad", "gross_yield"]
    return s[cols].sort_values("gross_yield", ascending=False).reset_index(drop=True)


def allocate(opts: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    s = opts[(opts["n"] >= MIN_N) & (opts["bucket"] == "condo")].copy()
    best = s.groupby("neighbourhood_cleansed")["gross_yield"].transform("max")
    s = s[s["gross_yield"] >= best - GAP]
    left, hood, picks = BUDGET, defaultdict(float), []
    for h, g in sorted(s.groupby("neighbourhood_cleansed"), key=lambda x: -x[1]["gross_yield"].max()):
        opts_h, bought = g.sort_values("gross_yield", ascending=False).to_dict("records"), defaultdict(int)
        while True:
            progress = False
            for r in opts_h:
                if bought[r["bedrooms_grp"]] >= int(r["n"] * SEG):
                    continue
                if r["price_cad"] > left or hood[h] + r["price_cad"] > BUDGET * CAP:
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
    alloc["share_of_budget"] = alloc["money"] / BUDGET
    return alloc, left


def listing_level() -> pd.DataFrame:
    raw = prep.load_listings()
    clean, _ = prep.clean(raw)
    clean = prep.add_revenue(clean)
    return clean[clean["is_active"] & (clean["room_type"] == "Entire home/apt")].copy()


def sample_size_test(d: pd.DataFrame) -> pd.DataFrame:
    """How far a median from n listings lands from the median of all Downtown 1-bed condos."""
    g = d[(d["bucket"] == "condo") & (d["neighbourhood_cleansed"] == "Downtown") & (d["bedrooms"].fillna(1) == 1)]
    r = g["revenue"].dropna().to_numpy(); true = np.median(r); rng = np.random.default_rng(0)
    rows = []
    for n in (5, 10, 20, 30, 50, 100):
        err = np.abs(np.array([np.median(rng.choice(r, n, replace=False)) for _ in range(5000)]) / true - 1)
        rows.append({"listings": n, "typical_error": np.median(err), "error_90pct": np.quantile(err, .9)})
    return pd.DataFrame(rows)


def condo_occupancy(d: pd.DataFrame) -> pd.DataFrame:
    c = d[d["bucket"] == "condo"]
    t = (c.groupby("neighbourhood_cleansed")["estimated_occupancy_l365d"]
          .agg(listings="size", median_nights="median").reset_index())
    t["occupancy"] = t["median_nights"] / 365
    return t[t["listings"] >= MIN_N].sort_values("occupancy", ascending=False)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    opts = options(); opts.to_csv(OUT / "options.csv", index=False)
    alloc, left = allocate(opts); alloc.to_csv(OUT / "allocation.csv", index=False)
    d = listing_level()
    sample_size_test(d).to_csv(OUT / "sample_size_test.csv", index=False)
    condo_occupancy(d).to_csv(OUT / "condo_occupancy.csv", index=False)
    raw = json.loads((ROOT / "analysis/current/raw_validation.json").read_text())
    priced = pd.read_csv(ROOT / "outputs/tables/segments_underwritten.csv")
    condo = priced[priced["bucket"] == "condo"]
    funnel = [("Raw listings (15 Jun 2026)", raw["raw_rows"]),
              ("Clean: priced $30-$2,000, stay < 90 nights", raw["clean_rows"]),
              ("Active whole homes", raw["active_entire_home_rows"]),
              ("Buyable condos & houses", int(priced["n"].sum())),
              ("Condos", int(condo["n"].sum())),
              (f"Condos in options with >= {MIN_N} listings", int(condo.loc[condo["n"] >= MIN_N, "n"].sum()))]
    pd.DataFrame(funnel, columns=["stage", "listings"]).to_csv(OUT / "funnel.csv", index=False)
    summary = {"units": int(alloc["units"].sum()), "money_spent": float(alloc["money"].sum()),
               "unspent": float(left), "revenue": float(alloc["revenue"].sum()),
               "gross_yield": float(alloc["revenue"].sum() / alloc["money"].sum()),
               "neighbourhoods": int(alloc["neighbourhood_cleansed"].nunique()),
               "rules": {"min_listings": MIN_N, "neighbourhood_cap": CAP, "segment_share_cap": SEG, "mix_gap": GAP}}
    # 2027 scenarios: the median revenue moved up/down for the whole portfolio
    summary["scenarios_2027"] = {name: {"revenue": summary["revenue"] * f, "gross_yield": summary["gross_yield"] * f}
                                 for name, f in [("revenue_minus20", 0.8), ("base", 1.0), ("revenue_plus10", 1.1)]}
    # Decision 3 comparison: the older cost-based model (src/analysis.py -> analysis/current/holdings.csv)
    old = pd.read_csv(ROOT / "analysis/current/holdings.csv")
    summary["old_cost_based_model"] = {
        "units": int(old["units"].sum()),
        "revenue": float((old["units"] * old["revenue_each"]).sum()),
        "money_spent": float((old["units"] * old["purchase_price_each"]).sum())}
    summary["concentration_downtown_core"] = float(
        alloc.loc[alloc["neighbourhood_cleansed"].isin(["Downtown", "Downtown Eastside"]), "money"].sum() / BUDGET)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(alloc.to_string(index=False)); print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
