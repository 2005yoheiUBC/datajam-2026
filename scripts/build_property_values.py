"""Typical property value per neighbourhood x type, from City of Vancouver Open Data (free, no login).

Sources:
  property-tax-report (2026): assessed land + building value of every property (BC Assessment)
  property-parcel-polygons:   location of each property lot
Steps: download -> join on tax coordinate -> place each lot in a neighbourhood (Inside Airbnb map)
       -> keep homes only -> median value per neighbourhood x type.
Run from repo root: python scripts/build_property_values.py
"""
import io
import json
import sys
import urllib.request
import subprocess
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.path import Path as Poly

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config

API = "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets"


def download(dataset, params, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        url = f"{API}/{dataset}/exports/csv?{params}"
        print("downloading", dataset)
        temporary = out.with_suffix('.download')
        subprocess.run(['curl','-fL','--retry','2','--max-time','180','-o',str(temporary),url],check=True)
        temporary.replace(out)
    return pd.read_csv(out, sep=";", dtype=str)


tax = download("property-tax-report",
               "select=land_coordinate,legal_type,zoning_classification,current_land_value,current_improvement_value"
               "&where=report_year%3D%222026%22", config.RAW / "property_tax_2026.csv")
parcels = download("property-parcel-polygons", "select=tax_coord,geo_point_2d", config.RAW / "parcels.csv")

# --- location of each lot ---
latlon = parcels["geo_point_2d"].str.split(",", expand=True).astype(float)
parcels = parcels.assign(lat=latlon[0], lon=latlon[1]).drop_duplicates("tax_coord")
tax = tax.merge(parcels[["tax_coord", "lat", "lon"]], left_on="land_coordinate", right_on="tax_coord", how="inner")

# --- place each lot in an Inside Airbnb neighbourhood ---
geo = json.loads((config.RAW / "neighbourhoods.geojson").read_text())
pts = tax[["lon", "lat"]].to_numpy()
tax["neighbourhood_cleansed"] = None
for f in geo["features"]:
    polys = f["geometry"]["coordinates"]
    if f["geometry"]["type"] == "Polygon":
        polys = [polys]
    inside = np.zeros(len(pts), bool)
    for poly in polys:
        ring = Poly(np.array(poly[0])[:, :2]).contains_points(pts)
        for hole in poly[1:]:
            ring &= ~Poly(np.array(hole)[:, :2]).contains_points(pts)
        inside |= ring
    tax.loc[inside, "neighbourhood_cleansed"] = f["properties"]["neighbourhood"]

# --- homes only ---
tax["value"] = pd.to_numeric(tax["current_land_value"]) + pd.to_numeric(tax["current_improvement_value"])
residential = ["Comprehensive Development", "Residential", "Residential Inclusive", "Historical Area"]
condo = (tax["legal_type"] == "STRATA") & tax["zoning_classification"].isin(residential) \
        & tax["value"].between(200_000, 5_000_000)          # drops parking stalls / lockers and penthouses
house = (tax["legal_type"] == "LAND") & tax["zoning_classification"].isin(["Residential", "Residential Inclusive"]) \
        & tax["value"].between(800_000, 10_000_000)         # drops vacant lots and apartment buildings
tax["prop_type"] = np.select([condo, house], ["condo", "house"], None)
homes = tax.dropna(subset=["prop_type", "neighbourhood_cleansed"])

out = (homes.groupby(["neighbourhood_cleansed", "prop_type"])["value"]
            .agg(properties="size", median_value="median").reset_index())
out.to_csv(config.EXTERNAL / "property_values_2026.csv", index=False)
manifest = {'method':'tax coordinate to parcel centroid to Inside Airbnb polygon; zoning/legal-type/value filters are proxies',
            'matched_tax_rows':len(tax),'selected_home_rows':len(homes),
            'unassigned_neighbourhood_rows':int(tax.neighbourhood_cleansed.isna().sum()),
            'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                             [config.RAW/'property_tax_2026.csv',config.RAW/'parcels.csv',config.RAW/'neighbourhoods.geojson']}}
(config.EXTERNAL/'property_values_provenance.json').write_text(json.dumps(manifest,indent=2))
print(f"matched {len(tax):,} lots, {len(homes):,} homes in a neighbourhood")
print(out.pivot(index="neighbourhood_cleansed", columns="prop_type", values="median_value").round(-3))
