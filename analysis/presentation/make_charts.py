"""Altair charts for the simple deck, from outputs/final/ (run scripts/final_allocation.py first).
Writes analysis/presentation/charts/*.png. Run: python analysis/presentation/make_charts.py"""
import json
from pathlib import Path

import altair as alt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "outputs" / "final"
OUT = Path(__file__).with_name("charts")
OUT.mkdir(exist_ok=True)

TEAL, GREY, INK, QUIET = "#1F7A8C", "#A3ACB1", "#1B1F24", "#6B757B"
FONT = "Arial"
MIN_N = json.loads((FINAL / "summary.json").read_text())["rules"]["min_listings"]
bed = lambda b: "3+ bed" if str(b) == "3+" else f"{b}-bed"


def save(chart, name, w_in, h_in, label_w=0):
    """Size the chart so 1 px = 1 pt at its slide box (inches); label_w = room taken by axis labels. Saved at 4x."""
    chart = (chart.properties(width=w_in * 72 - label_w - 40, height=h_in * 72 - 40)
             .configure(font=FONT, background="white")
             .configure_view(stroke=None)
             .configure_axis(labelColor=INK, labelFontSize=12, titleColor=QUIET, titleFontSize=12, grid=False, domain=False, ticks=False)
             .configure_legend(labelFontSize=12, labelColor=INK, title=None, orient="bottom", symbolType="square"))
    chart.save(str(OUT / f"{name}.png"), scale_factor=4)


opts = pd.read_csv(FINAL / "options.csv", dtype={"bedrooms_grp": str})
alloc = pd.read_csv(FINAL / "allocation.csv", dtype={"bedrooms_grp": str})
condos = opts[(opts.bucket == "condo") & (opts.n >= MIN_N)].copy()
houses = opts[(opts.bucket == "house") & (opts.n >= MIN_N)].copy()
opts["label"] = opts.neighbourhood_cleansed + " " + opts.bedrooms_grp.map(bed)
condos["label"] = condos.neighbourhood_cleansed + " " + condos.bedrooms_grp.map(bed)
houses["label"] = houses.neighbourhood_cleansed + " " + houses.bedrooms_grp.map(bed)


def hbar(df, x, y, color, fmt, order, legend=True, colors=None):
    base = alt.Chart(df).encode(
        y=alt.Y(f"{y}:N", sort=order, title=None, axis=alt.Axis(labelLimit=320)),
        x=alt.X(f"{x}:Q", axis=None, scale=alt.Scale(domain=[0, df[x].max() * 1.15])))
    bars = base.mark_bar(cornerRadiusEnd=3, height={"band": 0.7}).encode(
        color=alt.Color(f"{color}:N", scale=alt.Scale(domain=colors[0], range=colors[1]), legend=alt.Legend() if legend else None))
    text = base.mark_text(align="left", dx=5, fontSize=12, color=INK).encode(text=alt.Text(f"{x}:Q", format=fmt))
    return bars + text


# 1. Revenue per ~$1.1M: one big unit vs two cheaper units
big = condos[(condos.neighbourhood_cleansed == "Downtown") & (condos.bedrooms_grp == "3+")].iloc[0]
small = condos[(condos.neighbourhood_cleansed == "Downtown Eastside") & (condos.bedrooms_grp == "1")].iloc[0]
ex = pd.DataFrame([
    {"choice": f"1 × 3+ bed|Downtown|${big.price_cad / 1e6:.2f}M", "revenue": big.rev_median, "kind": "Bigger unit"},
    {"choice": f"2 × 1-bed|Downtown Eastside|${2 * small.price_cad / 1e6:.2f}M", "revenue": 2 * small.rev_median, "kind": "Two cheaper units"}])
eb = alt.Chart(ex).encode(x=alt.X("choice:N", sort=list(ex.choice), title=None, axis=alt.Axis(labelAngle=0, labelExpr="split(datum.label, '|')", labelLimit=200)),
                          y=alt.Y("revenue:Q", axis=None, scale=alt.Scale(domain=[0, ex.revenue.max() * 1.18])))
example = (eb.mark_bar(cornerRadiusEnd=3, width={"band": 0.55}).encode(color=alt.Color("kind:N", scale=alt.Scale(domain=["Bigger unit", "Two cheaper units"], range=[GREY, TEAL]), legend=None))
           + eb.mark_text(dy=-10, fontSize=14, fontWeight="bold", color=INK).encode(text=alt.Text("revenue:Q", format="$,.0f")))
save(example, "example", 4.5, 2.6, 0)

# 2. Funnel
fn = pd.read_csv(FINAL / "funnel.csv"); fn["kind"] = ["step"] * (len(fn) - 1) + ["final"]
save(hbar(fn, "listings", "stage", "kind", ",.0f", list(fn.stage), legend=False, colors=(["step", "final"], [GREY, TEAL])), "funnel", 5.3, 3.3, 215)

# 3. Condos vs houses
cv = pd.concat([condos.assign(type="Condo"), houses.head(4).assign(type="House")])
save(hbar(cv, "gross_yield", "label", "type", ".1%", list(cv.label), colors=(["Condo", "House"], [TEAL, GREY])), "condo_vs_house", 6.4, 3.85, 190)

# 4. Ranking: bought vs not
units = {(r.neighbourhood_cleansed, r.bedrooms_grp): r.units for r in alloc.itertuples()}
condos["units"] = [units.get((r.neighbourhood_cleansed, r.bedrooms_grp), 0) for r in condos.itertuples()]
condos["status"] = condos.units.map(lambda u: "Bought" if u else "Not bought")
condos["label2"] = [f"{l} · {u} bought" if u else l for l, u in zip(condos.label, condos.units)]
save(hbar(condos, "gross_yield", "label2", "status", ".1%", list(condos.label2), colors=(["Bought", "Not bought"], [TEAL, GREY])), "ranking", 5.1, 3.85, 205)

# 5. Sample size test
ss = pd.read_csv(FINAL / "sample_size_test.csv").melt("listings", var_name="measure", value_name="error")
ss["measure"] = ss.measure.map({"typical_error": "Typical error", "error_90pct": "90% of samples within"})
enc = dict(x=alt.X("listings:O", title="Listings in the sample", axis=alt.Axis(labelAngle=0)),
           y=alt.Y("error:Q", axis=None), color=alt.Color("measure:N", scale=alt.Scale(domain=["Typical error", "90% of samples within"], range=[TEAL, GREY])))
line = alt.Chart(ss).mark_line(point=alt.OverlayMarkDef(size=60), strokeWidth=3).encode(**enc)
lab = alt.Chart(ss).mark_text(dy=-12, fontSize=12, color=INK).encode(x=enc["x"], y=enc["y"], text=alt.Text("error:Q", format=".0%"))
rule = alt.Chart(pd.DataFrame({"listings": [MIN_N]})).mark_rule(strokeDash=[4, 4], color=QUIET).encode(x="listings:O")
save(alt.layer(rule, line, lab), "sample_size", 5.7, 3.85, 0)

# 6. Condo occupancy
oc = pd.read_csv(FINAL / "condo_occupancy.csv")
oc["label"] = oc.neighbourhood_cleansed + " (" + oc.listings.astype(str) + " listings)"
oc["kind"] = ["top"] + ["rest"] * (len(oc) - 1)
save(hbar(oc, "occupancy", "label", "kind", ".0%", list(oc.label), legend=False, colors=(["top", "rest"], [TEAL, GREY])), "occupancy", 5.9, 3.85, 205)
print("charts written to", OUT)

# 7. 2027 scenarios
sc = json.loads((FINAL / "summary.json").read_text())["scenarios_2027"]
sd = pd.DataFrame([{"case": "Revenue −20%", "revenue": sc["revenue_minus20"]["revenue"], "kind": "alt"},
                   {"case": "Expected (median)", "revenue": sc["base"]["revenue"], "kind": "base"},
                   {"case": "Revenue +10%", "revenue": sc["revenue_plus10"]["revenue"], "kind": "alt"}])
sd["label"] = sd.revenue.map(lambda v: f"${v / 1e3:,.0f}K")
sb = alt.Chart(sd).encode(x=alt.X("case:N", sort=list(sd.case), title=None, axis=alt.Axis(labelAngle=0)),
                          y=alt.Y("revenue:Q", axis=None, scale=alt.Scale(domain=[0, sd.revenue.max() * 1.2])))
scen = (sb.mark_bar(cornerRadiusEnd=3, width={"band": 0.55}).encode(color=alt.Color("kind:N", scale=alt.Scale(domain=["base", "alt"], range=[TEAL, GREY]), legend=None))
        + sb.mark_text(dy=-9, fontSize=14, fontWeight="bold", color=INK).encode(text="label:N"))
save(scen, "scenarios_2027", 4.7, 2.0, 0)
print("scenario chart written")
