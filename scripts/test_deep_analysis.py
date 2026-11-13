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
        r=underwrite(fixture())
        self.assertAlmostEqual(r["cash_in"],586428.4)
        # Revenue 83,406 less 25,855.86 variable and 11,119.505 fixed.
        self.assertAlmostEqual(r["noi"],46430.635)
        fee=underwrite(fixture(),fee=.155)
        self.assertAlmostEqual(r["noi"]-fee["noi"],83406*.125)

    def test_strict_capacity_boundaries(self):
        for n,expected in ((5,0),(9,0),(10,1),(19,1),(20,2)):
            self.assertEqual(len(select([underwrite(fixture(n))])),expected)
        self.assertEqual(len(select([underwrite(fixture(7))],strict=False)),1)

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


if __name__ == "__main__":
    unittest.main()
