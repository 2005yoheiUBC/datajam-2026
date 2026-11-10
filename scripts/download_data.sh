#!/usr/bin/env bash
# Downloads the Inside Airbnb Vancouver snapshot used by every team.
# If a URL 404s, copy the exact link from https://insideairbnb.com/get-the-data/ (Vancouver, 15 June 2026).
set -euo pipefail
cd "$(dirname "$0")/../data/raw"
BASE="https://data.insideairbnb.com/canada/bc/vancouver/2026-06-15"
for f in data/listings.csv.gz data/calendar.csv.gz data/reviews.csv.gz visualisations/neighbourhoods.geojson; do
  echo "-> $f"
  curl -fL --retry 3 -o "$(basename "$f")" "$BASE/$f"
done
ls -lh
