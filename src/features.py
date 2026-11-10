"""Revenue estimates per listing, three independent ways. Their agreement IS the validation
(rubric: Analysis & Validation -> 'a validation or sanity check')."""
import numpy as np
import pandas as pd
from . import config
from .clean import parse_price


def review_based_revenue(df: pd.DataFrame, review_rate=None, stay=None, cap=None) -> pd.Series:
    """'San Francisco model': reviews / review rate = stays; stays x nights x price = revenue."""
    review_rate = review_rate or config.REVIEW_RATE
    stay = stay or config.AVG_LENGTH_OF_STAY
    cap = cap or config.OCCUPANCY_CAP
    nights_per_stay = np.maximum(stay, df["minimum_nights"].clip(upper=config.MAX_MINIMUM_NIGHTS))
    nights = (df["number_of_reviews_ltm"].fillna(0) / review_rate) * nights_per_stay
    nights = np.minimum(nights, 365 * cap)
    return nights * df["price_num"], nights / 365


def calendar_features(cal: pd.DataFrame) -> pd.DataFrame:
    """Forward-looking: share of next 90 nights unavailable (an UPPER bound on bookings,
    since blocked nights look the same) and forward median nightly price."""
    snap = pd.Timestamp(config.SNAPSHOT_DATE)
    c = cal[(cal["date"] > snap) & (cal["date"] <= snap + pd.Timedelta(days=90))].copy()
    c["price_num"] = parse_price(c["price"]) if "price" in c else np.nan
    g = c.groupby("listing_id")
    out = pd.DataFrame({
        "cal_unavail_90": 1 - g["available"].mean(),
        "cal_median_price": g["price_num"].median(),
    })
    # Fully blocked calendars are almost certainly not booked solid: flag, don't trust.
    out["cal_fully_blocked"] = out["cal_unavail_90"] >= 0.999
    return out.reset_index().rename(columns={"listing_id": "id"})


def build(listings: pd.DataFrame, cal: pd.DataFrame | None = None) -> pd.DataFrame:
    df = listings.copy()
    df["rev_review_model"], df["occ_review_model"] = review_based_revenue(df)
    if "estimated_revenue_l365d" in df:  # Inside Airbnb's own estimate (an estimate, not reported)
        df["rev_iab_estimate"] = pd.to_numeric(df["estimated_revenue_l365d"], errors="coerce")
    if cal is not None:
        df = df.merge(calendar_features(cal), on="id", how="left")
    df["is_commercial_host"] = df["calculated_host_listings_count"] >= 3
    return df


def validation_table(df: pd.DataFrame) -> pd.DataFrame:
    """Compare the revenue methods. If they disagree wildly, say so in the pitch."""
    cols = [c for c in ["rev_review_model", "rev_iab_estimate"] if c in df]
    act = df[df["is_active"]]
    rows = [{"method": c, "median": act[c].median(), "p25": act[c].quantile(.25),
             "p75": act[c].quantile(.75), "n": int(act[c].notna().sum())} for c in cols]
    if len(cols) == 2:
        rows.append({"method": "spearman_corr(review, iab)",
                     "median": act[cols].corr(method="spearman").iloc[0, 1]})
    return pd.DataFrame(rows)


def segment_table(df: pd.DataFrame) -> pd.DataFrame:
    """Neighbourhood x property bucket x bedrooms. Only active, entire-home listings:
    that is what DDD would actually buy and operate."""
    d = df[df["is_active"] & (df["room_type"] == "Entire home/apt")].copy()
    d["bedrooms_grp"] = d["bedrooms"].fillna(1).clip(upper=3).astype(int).astype(str).replace({"3": "3+"})
    g = d.groupby(["neighbourhood_cleansed", "bucket", "bedrooms_grp"])
    seg = g.agg(n=("id", "size"),
                adr_median=("price_num", "median"),
                occ_median=("occ_review_model", "median"),
                rev_median=("rev_review_model", "median"),
                rev_p25=("rev_review_model", lambda s: s.quantile(.25)),
                rev_p75=("rev_review_model", lambda s: s.quantile(.75)),
                rating=("review_scores_rating", "median"),
                share_commercial=("is_commercial_host", "mean")).reset_index()
    if "licence_status" in d:
        lic = d.assign(lic=d["licence_status"].eq("has_number")).groupby(
            ["neighbourhood_cleansed", "bucket", "bedrooms_grp"])["lic"].mean()
        seg = seg.merge(lic.rename("share_with_licence_number_est").reset_index())
    return seg
