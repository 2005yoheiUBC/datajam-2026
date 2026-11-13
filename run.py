"""Run everything: python run.py  ->  outputs/tables/*.csv + outputs/key_numbers.json"""
import json
from src import config, prep, portfolio

config.TABLES.mkdir(parents=True, exist_ok=True)
config.PROCESSED.mkdir(parents=True, exist_ok=True)

raw = prep.load_listings()
listings, filter_log = prep.clean(raw)
listings = prep.add_revenue(listings)
seg = prep.segments(listings)

listings.to_csv(config.PROCESSED / "listings_clean.csv", index=False)
filter_log.to_csv(config.TABLES / "filters_applied.csv", index=False)
prep.validation(listings).to_csv(config.TABLES / "revenue_validation.csv", index=False)
seg.to_csv(config.TABLES / "segments.csv", index=False)
print(f"listings: {len(raw):,} raw -> {len(listings):,} clean -> {len(seg)} segments")
print(filter_log.to_string(index=False))

seg = portfolio.add_purchase_prices(seg)
uw = portfolio.underwrite(seg)
port = portfolio.build_portfolio(uw)
fvm = portfolio.few_vs_many(uw)
sens = portfolio.sensitivity(seg, port)
for name, t in [("segments_underwritten", uw), ("recommended_portfolio", port),
                ("few_vs_many", fvm), ("sensitivity", sens)]:
    t.to_csv(config.TABLES / f"{name}.csv", index=False)

s = portfolio.summarise(port, "recommended")
key_numbers = {
    "units": s["units"],
    "cash_deployed_cad": round(s["cash_deployed"], -3),
    "noi_2027_cad": round(s["noi"], -3),
    "net_yield_base": round(s["net_yield"], 3),
    "net_yield_range": [round(sens["net_yield"].min(), 3), round(sens["net_yield"].max(), 3)],
    "neighbourhoods": s["neighbourhoods"],
}
(config.OUTPUTS / "key_numbers.json").write_text(json.dumps(key_numbers, indent=2, default=float))
print(json.dumps(key_numbers, indent=2, default=float))
