"""Load -> clean -> revenue estimate per listing -> segment table.
Every filter logs how many rows it removed so we can quote it on a slide."""
import numpy as np
import pandas as pd
from . import config


def parse_price(s: pd.Series) -> pd.Series:
    """'$1,234.00' -> 1234.0"""
    return pd.to_numeric(s.astype(str).str.replace(r"[$,\s]", "", regex=True), errors="coerce")


def load_listings() -> pd.DataFrame:
    df = pd.read_csv(config.RAW / "listings.csv.gz", low_memory=False)
    df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
    return df


def licence_status(raw: pd.Series) -> pd.Series:
    """Categorise the licence field without keeping the number (privacy). An estimate from free text."""
    t = raw.fillna("").astype(str).str.strip().str.lower()
    out = pd.Series("missing", index=raw.index)
    out[t.str.contains("exempt")] = "exempt_claimed"
    out[t.str.contains(r"\d{2}-\d{6}|\d{6,}", regex=True)] = "has_number"
    out[t.str.contains("pending")] = "pending"
    out[(t != "") & (out == "missing")] = "other_text"
    return out


def property_bucket(pt: pd.Series) -> pd.Series:
    """Collapse Airbnb's ~40 property types into what DDD would buy."""
    pt = pt.fillna("").str.lower()
    out = pd.Series("other", index=pt.index)
    out[pt.str.contains("condo|apartment|rental unit|loft|serviced")] = "condo"
    out[pt.str.contains("townhouse")] = "townhouse"
    out[pt.str.contains(r"\bhome\b|house|villa|bungalow|cottage")] = "house"
    out[pt.str.contains("guest suite|guesthouse|laneway")] = "suite"
    return out


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    df["price_num"] = parse_price(df["price"])
    df["licence_status"] = licence_status(df["license"])
    df["bucket"] = property_bucket(df["property_type"])
    df = df.drop(columns=[c for c in config.PRIVACY_DROP if c in df.columns])

    log = []
    def keep(mask, step, why):
        log.append({"step": step, "rows_before": len(df), "removed": int((~mask).sum()), "why": why})
        return df[mask].copy()

    df = keep(df["price_num"].notna(), "has_price", "no price: not bookable at scrape")
    df = keep(df["price_num"].between(config.MIN_NIGHTLY_PRICE, config.MAX_NIGHTLY_PRICE), "price_in_range",
              f"outside ${config.MIN_NIGHTLY_PRICE}-${config.MAX_NIGHTLY_PRICE}/night")
    df = keep(df["minimum_nights"] <= config.MAX_MINIMUM_NIGHTS, "short_term_only",
              "min stay >= 30 nights = monthly rental, not STR")
    days = (pd.Timestamp(config.SNAPSHOT_DATE) - df["last_review"]).dt.days
    df["is_active"] = days <= config.ACTIVE_REVIEW_WINDOW_DAYS
    return df, pd.DataFrame(log)


def add_revenue(df: pd.DataFrame, review_rate=config.REVIEW_RATE) -> pd.DataFrame:
    """Review model: reviews / review rate = stays; stays x nights x price = revenue."""
    df = df.copy()
    nights_per_stay = np.maximum(config.AVG_LENGTH_OF_STAY, df["minimum_nights"])
    nights = (df["number_of_reviews_ltm"].fillna(0) / review_rate) * nights_per_stay
    nights = np.minimum(nights, 365 * config.OCCUPANCY_CAP)
    df["occ_review_model"] = nights / 365
    df["rev_review_model"] = nights * df["price_num"]
    df["rev_iab_estimate"] = pd.to_numeric(df["estimated_revenue_l365d"], errors="coerce")
    df["is_commercial_host"] = df["calculated_host_listings_count"] >= 3
    return df


def validation(df: pd.DataFrame) -> pd.DataFrame:
    """Our revenue model vs Inside Airbnb's own estimate. Agreement = sanity check for the pitch."""
    act = df[df["is_active"]]
    cols = ["rev_review_model", "rev_iab_estimate"]
    rows = [{"method": c, "p25": act[c].quantile(.25), "median": act[c].median(),
             "p75": act[c].quantile(.75), "n": int(act[c].notna().sum())} for c in cols]
    rows.append({"method": "spearman_corr", "median": act[cols].corr(method="spearman").iloc[0, 1]})
    return pd.DataFrame(rows)


def segments(df: pd.DataFrame) -> pd.DataFrame:
    """Neighbourhood x property type x bedrooms, active entire-home listings only (what DDD would run)."""
    d = df[df["is_active"] & (df["room_type"] == "Entire home/apt")].copy()
    d["bedrooms_grp"] = d["bedrooms"].fillna(1).clip(upper=3).astype(int).astype(str).replace({"3": "3+"})
    d["licensed"] = d["licence_status"].eq("has_number")
    return d.groupby(config.SEGMENT_KEYS).agg(
        n=("id", "size"),
        adr_median=("price_num", "median"),
        occ_median=("occ_review_model", "median"),
        rev_median=("rev_review_model", "median"),
        rev_p25=("rev_review_model", lambda s: s.quantile(.25)),
        rev_p75=("rev_review_model", lambda s: s.quantile(.75)),
        rating=("review_scores_rating", "median"),
        share_commercial=("is_commercial_host", "mean"),
        share_licensed_est=("licensed", "mean"),
    ).reset_index()
