"""Raw readers. Dates are parsed explicitly because formats differ across the three CSVs."""
import pandas as pd
from . import config


def load_listings() -> pd.DataFrame:
    df = pd.read_csv(config.RAW / "listings.csv.gz", low_memory=False)
    for c in ["last_scraped", "host_since", "first_review", "last_review", "calendar_last_scraped"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], format="%Y-%m-%d", errors="coerce")
    return df


def load_calendar() -> pd.DataFrame:
    usecols = ["listing_id", "date", "available", "price", "adjusted_price", "minimum_nights", "maximum_nights"]
    df = pd.read_csv(config.RAW / "calendar.csv.gz", usecols=lambda c: c in usecols, low_memory=False)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    df["available"] = df["available"].map({"t": True, "f": False})
    return df


def load_reviews() -> pd.DataFrame:
    df = pd.read_csv(config.RAW / "reviews.csv.gz", usecols=["listing_id", "id", "date"], low_memory=False)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    return df


def load_neighbourhoods():
    import geopandas as gpd
    return gpd.read_file(config.RAW / "neighbourhoods.geojson")
