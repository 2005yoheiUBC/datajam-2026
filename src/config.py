"""Every path and assumption in one place. Change a number here, rerun `make all`,
and every output updates. Each assumption is documented in docs/assumptions.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EXTERNAL = ROOT / "data" / "external"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
TABLES = OUTPUTS / "tables"
FIGURES = OUTPUTS / "figures"
DOCS = ROOT / "docs"

SNAPSHOT_DATE = "2026-06-15"
BUDGET_CAD = 10_000_000

# --- Cleaning thresholds (each one is a candidate decision-log entry) ---
MIN_NIGHTLY_PRICE = 30          # below this is almost certainly a placeholder
MAX_NIGHTLY_PRICE = 2_000       # above this: check by hand before dropping
MAX_MINIMUM_NIGHTS = 29         # >=30 nights = monthly rental, not STR (BC STR definition)
ACTIVE_REVIEW_WINDOW_DAYS = 365 # "active" = reviewed in the year before the snapshot

# --- Revenue model assumptions ---
REVIEW_RATE = 0.50              # share of stays that leave a review (sensitivity: 0.30-0.70)
AVG_LENGTH_OF_STAY = 3.0        # nights, floored at minimum_nights per listing
OCCUPANCY_CAP = 0.70            # cap on modelled occupancy

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
