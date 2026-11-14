"""Every path and assumption in one place. Change a number here, rerun `python run.py`,
and every output updates. Each assumption is documented in docs/assumptions.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EXTERNAL = ROOT / "data" / "external"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
TABLES = OUTPUTS / "tables"
FIGURES = OUTPUTS / "figures"

SNAPSHOT_DATE = "2026-06-15"
BUDGET_CAD = 10_000_000
SEGMENT_KEYS = ["neighbourhood_cleansed", "bucket", "bedrooms_grp"]
# Never in any output or slide: host names, URLs, licence numbers
PRIVACY_DROP = ["listing_url", "host_url", "host_profile_url", "host_name", "host_about", "host_thumbnail_url",
                "host_picture_url", "picture_url", "license"]

# --- Cleaning thresholds (each one is a candidate decision-log entry) ---
MIN_NIGHTLY_PRICE = 30          # below this is almost certainly a placeholder
MAX_NIGHTLY_PRICE = 2_000       # above this: check by hand before dropping
MAX_MINIMUM_NIGHTS = 89         # <90 consecutive nights = short-term rental (BC STRAA + Vancouver bylaw since 2024)
ACTIVE_REVIEW_WINDOW_DAYS = 365 # "active" = reviewed in the year before the snapshot

# --- Cost assumptions (fraction of gross revenue unless noted) ---
PLATFORM_FEE = 0.155  # Airbnb single-host-fee scenario; checked 2026-11-13, help/article/1857.
MANAGEMENT_FEE = 0.20
CLEANING_AND_SUPPLIES = 0.08
LICENCE_AND_REGISTRATION_CAD = 1_500   # per property per year, check current City + provincial fees
PROPERTY_TAX_RATE = 0.003              # of purchase price; Vancouver residential mill rate is ~0.3%
STRATA_FEES_CAD_MONTH = {"condo": 500, "townhouse": 400, "house": 0}
INSURANCE_CAD_YEAR = 2_000
CLOSING_COSTS = 0.04                   # property transfer tax + legal, fraction of price
FURNISHING_CAD = 25_000                # per property, one-off
MIN_COMPARABLES = 30
MAX_NEIGHBOURHOOD_SHARE = 0.4
MAX_SEGMENT_SHARE = 0.1

# --- Purchase prices (outside data) ---
# City of Vancouver Open Data, property tax report 2026 (BC Assessment values), built by
# scripts/build_property_values.py -> median value per neighbourhood x (condo | house)
PROPERTY_VALUES_FILE = EXTERNAL / "property_values_2026.csv"
BUCKET_TO_PROP_TYPE = {"condo": "condo", "townhouse": "condo", "house": "house"}  # townhouses are strata units
# "suite" and "other" are not buyable on their own (a suite comes with a whole house) -> excluded
CONDO_BEDROOM_MULTIPLIER = {"0": 0.7, "1": 0.85, "2": 1.15, "3+": 1.5}  # median unit = typical; assumption
