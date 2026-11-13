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
MAX_MINIMUM_NIGHTS = 29         # >=30 nights = monthly rental, not STR (BC STR definition)
ACTIVE_REVIEW_WINDOW_DAYS = 365 # "active" = reviewed in the year before the snapshot

# --- Cost assumptions (fraction of gross revenue unless noted) ---
PLATFORM_FEE = 0.03
MANAGEMENT_FEE = 0.20
CLEANING_AND_SUPPLIES = 0.08
LICENCE_AND_REGISTRATION_CAD = 1_500   # per property per year, check current City + provincial fees
PROPERTY_TAX_RATE = 0.003              # of purchase price; Vancouver residential mill rate is ~0.3%
STRATA_FEES_CAD_MONTH = {"condo": 500, "townhouse": 400, "house": 0}
INSURANCE_CAD_YEAR = 2_000
CLOSING_COSTS = 0.04                   # property transfer tax + legal, fraction of price
FURNISHING_CAD = 25_000                # per property, one-off

# --- Purchase prices (outside data) ---
# Greater Vancouver REALTORS, MLS Home Price Index, October 2026 stats package (p.3-4), public PDF:
# https://members.gvrealtors.ca/news/GVR-Stats-Package-October-2026.pdf
GVR_FILE = EXTERNAL / "gvr_benchmark_2026-10.csv"
BUCKET_TO_GVR_TYPE = {"condo": "Apartment", "townhouse": "Townhouse", "house": "Detached"}
# "suite" and "other" are not buyable on their own (a suite comes with a whole house) -> excluded
CONDO_BEDROOM_MULTIPLIER = {"0": 0.7, "1": 0.85, "2": 1.15, "3+": 1.5}  # benchmark = typical unit; assumption
# City local areas -> GVR sub-area (roughly split at Ontario St)
WEST = ["Arbutus Ridge", "Downtown", "Dunbar Southlands", "Fairview", "Kerrisdale", "Kitsilano", "Marpole",
        "Oakridge", "Shaughnessy", "South Cambie", "West End", "West Point Grey"]
EAST = ["Downtown Eastside", "Grandview-Woodland", "Hastings-Sunrise", "Kensington-Cedar Cottage", "Killarney",
        "Mount Pleasant", "Renfrew-Collingwood", "Riley Park", "Strathcona", "Sunset", "Victoria-Fraserview"]
