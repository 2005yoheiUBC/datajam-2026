"""Boundary and independent financial checks for aggregate scenario analysis."""
import unittest

from deep_analysis import C, select, summary, underwrite


def fixture(n=10, hood="Strathcona"):
    return {C.SEGMENT_KEYS[0]:hood, "bucket":"condo", "bedrooms_grp":"1",
            "n":n,"price_cad":539835.0,"rev_median":83406.0,
            "rev_p25":30499.75,"rev_p75":89265.75}


class AnalysisChecks(unittest.TestCase):
    def test_independent_underwriting(self):
        # Purchase 539,835 + closing 21,593.40 + furniture 25,000.
        r=underwrite(fixture(),fee=.03)
        self.assertAlmostEqual(r["cash_in"],586428.4)
        # Revenue 83,406 less 25,855.86 variable and 11,119.505 fixed.
        self.assertAlmostEqual(r["noi"],46430.635)
        fee=underwrite(fixture(),fee=.155)
        self.assertAlmostEqual(r["noi"]-fee["noi"],83406*.125)

    def test_strict_capacity_boundaries(self):
        for n,expected in ((5,0),(9,0),(10,1),(19,1),(20,2)):
            self.assertEqual(len(select([underwrite(fixture(n))],min_n=5)),expected)
        self.assertEqual(len(select([underwrite(fixture(7))],min_n=5,strict=False)),1)

    def test_fixed_costs_remain_during_shutdown(self):
        base=underwrite(fixture())
        offline=underwrite(fixture(),offline=12)
        self.assertAlmostEqual(offline["gross"],0)
        self.assertAlmostEqual(offline["noi"],-base["fixed"])
        downside=underwrite(fixture(),fee=.155,revenue_factor=.8,reserve=.05)
        self.assertAlmostEqual(downside["noi"],83406*.8*.515-base["fixed"])

    def test_caps_and_no_negative_profit_purchases(self):
        rows=[underwrite(fixture(100,h)) for h in ("Strathcona","Downtown","Mount Pleasant")]
        p=select(rows)
        self.assertLessEqual(sum(r["cash_in"] for r in p),C.BUDGET_CAD)
        for hood in {r[C.SEGMENT_KEYS[0]] for r in p}:
            self.assertLessEqual(sum(r["cash_in"] for r in p if r[C.SEGMENT_KEYS[0]]==hood),C.BUDGET_CAD*.4)
        self.assertEqual(select([underwrite(fixture(),revenue_factor=0)]),[])
        self.assertIsNone(summary([],"empty")["yield_on_deployed"])

    def test_fee_exclusion_is_separate_from_operating_income(self):
        full=underwrite(fixture())
        excluded=underwrite(fixture(),fee=0,management=0,cleaning=0)
        self.assertAlmostEqual(excluded['noi']-full['noi'],83406*(C.PLATFORM_FEE+C.MANAGEMENT_FEE+C.CLEANING_AND_SUPPLIES))

    def test_price_shock_updates_acquisition_and_property_tax(self):
        base=underwrite(fixture());shock=underwrite(fixture(),price_factor=1.2)
        self.assertAlmostEqual(shock['noi'],base['noi']-539835*.2*.003)
        self.assertAlmostEqual(shock['cash_in'],539835*1.2*1.04+25000)

    def test_latest_inputs_reconcile_independently(self):
        import csv,json
        result_path=C.ROOT/'analysis/current/results.json'
        if not result_path.exists():self.skipTest('Run python3 run.py first')
        d=json.loads(result_path.read_text());holding=d['recommendation']
        cash=sum(r['units']*(r['purchase_price_each']*1.04+25000) for r in holding)
        gross=sum(r['units']*r['revenue_each'] for r in holding)
        fixed=sum(r['units']*(r['purchase_price_each']*.003+6000+2000+1500) for r in holding)
        self.assertAlmostEqual(d['performance']['cash_deployed'],cash)
        self.assertAlmostEqual(d['performance']['noi'],gross*(1-C.PLATFORM_FEE-.2-.08)-fixed)
        self.assertEqual(sum(r['units'] for r in holding),d['performance']['units'])

    def test_future_review_dates_are_not_active(self):
        try:import pandas as pd
        except ImportError:self.skipTest('Optional raw-data check requires pandas')
        from src.prep import clean
        frame=pd.DataFrame(dict(price=['$100']*3,license=['']*3,property_type=['Entire condo']*3,
                                minimum_nights=[1]*3,last_review=pd.to_datetime(['2026-06-14','2026-06-16','2024-01-01'])))
        cleaned,_=clean(frame)
        self.assertEqual(cleaned.is_active.tolist(),[True,False,False])

    def test_pandas_exploration_matches_authoritative_engine(self):
        try:import pandas as pd
        except ImportError:self.skipTest('Optional cross-engine check requires pandas')
        from src.analysis import read_csv,price_segments,modelled_rows,key
        from src import portfolio
        raw=pd.read_csv(C.TABLES/'segments.csv',dtype={'bedrooms_grp':str})
        pandas_rows=portfolio.underwrite(portfolio.add_purchase_prices(raw))
        expected={key(r):r for r in modelled_rows(price_segments(read_csv(C.TABLES/'segments.csv')))}
        self.assertEqual(len(pandas_rows),len(expected))
        for r in pandas_rows.to_dict('records'):
            for field in ['price_cad','noi','cash_in','net_yield']:
                self.assertAlmostEqual(r[field],expected[key(r)][field])
        self.assertEqual(len(portfolio.build_portfolio(pandas_rows)),13)


if __name__ == "__main__":
    unittest.main()
