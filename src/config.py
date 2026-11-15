"""Every path and assumption in one place. Change a number here, rerun `python run.py`."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EXTERNAL = ROOT / "data" / "external"
OUTPUTS = ROOT / "outputs"

SNAPSHOT_DATE = "2026-06-15"
BUDGET_CAD = 10_000_000
SEGMENT_KEYS = ["neighbourhood_cleansed", "bucket", "bedrooms_grp"]
# Never in any output or slide: host names, URLs, licence numbers
PRIVACY_DROP = ["listing_url", "host_url", "host_profile_url", "host_name", "host_about", "host_thumbnail_url",
                "host_picture_url", "picture_url", "license"]

# --- Cleaning ---
MIN_NIGHTLY_PRICE = 30           # below this is almost certainly a placeholder
MAX_NIGHTLY_PRICE = 2_000        # above this is almost certainly an error
MAX_MINIMUM_NIGHTS = 89          # <90 consecutive nights = short-term rental (BC STRAA + Vancouver bylaw)
ACTIVE_REVIEW_WINDOW_DAYS = 365  # "active" = reviewed in the year before the snapshot

# --- Allocation rules (team decisions) ---
MIN_COMPARABLES = 30             # trust an option only with 30+ listings (see sample_size_test)
MAX_NEIGHBOURHOOD_SHARE = 0.4    # max 40% of the budget in one neighbourhood
MAX_SEGMENT_SHARE = 0.1          # max 10% of an option's listings
MIX_GAP = 0.01                   # sizes within 1 point of an area's best share the money

# --- Purchase prices (City of Vancouver property tax report 2026, built by scripts/build_property_values.py) ---
PROPERTY_VALUES_FILE = EXTERNAL / "property_values_2026.csv"
BUCKET_TO_PROP_TYPE = {"condo": "condo", "townhouse": "condo", "house": "house"}  # suites / other can't be bought alone
CONDO_BEDROOM_MULTIPLIER = {"0": 0.7, "1": 0.85, "2": 1.15, "3+": 1.5}           # tax data has no bedrooms: assumption

# --- Assumed operating costs: ONLY for the decision-3 comparison (our earlier cost-based model) ---
PLATFORM_FEE = 0.155
MANAGEMENT_FEE = 0.20
CLEANING_AND_SUPPLIES = 0.08
LICENCE_AND_REGISTRATION_CAD = 1_500
PROPERTY_TAX_RATE = 0.003
STRATA_FEES_CAD_MONTH = {"condo": 500, "townhouse": 400, "house": 0}
INSURANCE_CAD_YEAR = 2_000
CLOSING_COSTS = 0.04
FURNISHING_CAD = 25_000
