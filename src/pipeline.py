"""End to end: python -m src.pipeline"""
from . import config, clean, features, analysis
from .load import load_calendar


def main():
    listings = clean.run()
    cal = load_calendar() if (config.RAW / "calendar.csv.gz").exists() else None
    feat = features.build(listings, cal)
    feat.to_parquet(config.PROCESSED / "listings_features.parquet", index=False)
    features.validation_table(feat).to_csv(config.TABLES / "revenue_method_validation.csv", index=False)
    seg = features.segment_table(feat)
    seg.to_csv(config.TABLES / "segments.csv", index=False)
    if (config.EXTERNAL / "purchase_prices.csv").exists():
        analysis.run(seg)
    else:
        print("No data/external/purchase_prices.csv yet: segments written, portfolio step skipped.")


if __name__ == "__main__":
    main()
