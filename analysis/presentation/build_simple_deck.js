// Simple pitch deck: decisions first, then why. Every number is read from outputs/final/ (scripts/final_allocation.py).
// Run: python scripts/final_allocation.py && NODE_PATH=<folder with pptxgenjs> node analysis/presentation/build_simple_deck.js
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..", "..");
const FINAL = path.join(ROOT, "outputs", "final");
const OUT = path.join(__dirname, "ddd_pitch_simple.pptx");
const APPLY_THEME = process.env.APPLY_THEME;

// ---------- data ----------
function readCsv(file) {
  const text = fs.readFileSync(path.join(FINAL, file), "utf8").trim();
  const parseLine = (line) => {
    const out = []; let cur = "", q = false;
    for (const ch of line) {
      if (ch === '"') q = !q;
      else if (ch === "," && !q) { out.push(cur); cur = ""; }
      else cur += ch;
    }
    out.push(cur); return out;
  };
  const [head, ...rows] = text.split(/\r?\n/).map(parseLine);
  const TEXT = new Set(["bedrooms_grp", "neighbourhood_cleansed", "bucket", "stage"]);
  return rows.map((r) => Object.fromEntries(head.map((h, i) => [h, TEXT.has(h) || isNaN(Number(r[i])) || r[i] === "" ? r[i] : Number(r[i])])));
}
const alloc = readCsv("allocation.csv");
const options = readCsv("options.csv");
const funnel = readCsv("funnel.csv");
const sample = readCsv("sample_size_test.csv");
const occ = readCsv("condo_occupancy.csv");
const summary = JSON.parse(fs.readFileSync(path.join(FINAL, "summary.json"), "utf8"));

const MIN_N = summary.rules.min_listings;
const OLD = summary.old_cost_based_model;
const SC = summary.scenarios_2027;
const money = (v) => (v >= 1e6 ? `$${(v / 1e6).toFixed(2)}M` : `$${Math.round(v / 1e3)}K`);
const pct = (v, d = 1) => `${(v * 100).toFixed(d)}%`;
const bed = (b) => (b === "3+" ? "3+ bed" : `${b}-bed`);
const condos = options.filter((o) => o.bucket === "condo" && o.n >= MIN_N);
const houses = options.filter((o) => o.bucket === "house" && o.n >= MIN_N);
const bestHouse = houses[0];
const err = (n) => sample.find((s) => s.listings === n).typical_error;

// ---------- theme ----------
const THEME = {
  name: "Harbour",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1F24", lt1: "FFFFFF", dk2: "0E3B43", lt2: "EDF2F3",
    accent1: "1F7A8C", accent2: "E07A5F", accent3: "A3ACB1", accent4: "F2CC8F",
    accent5: "3D405B", accent6: "81B29A", hlink: "1F7A8C", folHlink: "3D405B",
  },
};
const HEX = THEME.colors;
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "DDD Vancouver $10M: recommendation";
const C = pres.SchemeColor;
const CREDIT = "Data: Inside Airbnb, Vancouver, 15 June 2026, CC BY 4.0 · City of Vancouver Open Data, property tax report 2026";

pres.defineSlideMaster({
  title: "DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.0, w: 8.8, h: 1.0, fontSize: 36, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 2.1, w: 8.8, h: 0.5, fontSize: 16, color: C.background2, margin: 0 }, text: "" } },
    { text: { text: CREDIT, options: { x: 0.6, y: 5.2, w: 8.8, h: 0.25, fontSize: 9, color: C.accent3, margin: 0 } } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  margin: [0.5, 0.5, 0.5, 0.5],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontSize: 26, bold: true, color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: CREDIT, options: { x: 0.5, y: 5.25, w: 8.2, h: 0.25, fontSize: 9, color: C.accent3, margin: 0 } } },
  ],
  slideNumber: { x: 9.1, y: 5.22, w: 0.4, h: 0.3, fontSize: 9, color: C.accent3, align: "right" },
});

const chartText = { catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt", titleFontFace: "+mn-lt" };
const quietAxes = (o) => Object.assign({
  catAxisLabelColor: HEX.dk1, valAxisLabelColor: "6B757B", catAxisLabelFontSize: 12, valAxisLabelFontSize: 10,
  valGridLine: { style: "none" }, catGridLine: { style: "none" }, catAxisLineShow: false,
  dataLabelFontSize: 12, dataLabelColor: HEX.dk1, showTitle: false,
}, chartText, o);


// Altair PNG (analysis/presentation/make_charts.py), fitted inside a box, keeping its aspect.
const CHARTS = path.join(__dirname, "charts");
function img(slide, name, x, y, w, h) {
  const buf = fs.readFileSync(path.join(CHARTS, `${name}.png`));
  const pw = buf.readUInt32BE(16), ph = buf.readUInt32BE(20);
  const k = Math.min(w / pw, h / ph), iw = pw * k, ih = ph * k;
  slide.addImage({ path: path.join(CHARTS, `${name}.png`), x: x + (w - iw) / 2, y: y + (h - ih) / 2, w: iw, h: ih, objectName: `${name}-chart`, altText: name.replace(/_/g, " ") + " chart" });
}

// ---------- Section 1: the decision ----------
pres.addSection({ title: "Decision" });

// 1. Title + answer
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Decision" });
  s.addText(`Buy ${summary.units} condos in ${summary.neighbourhoods} Vancouver neighbourhoods`, { placeholder: "title" });
  s.addText("DDD's $10M short-term rental portfolio · DataJam 2026", { placeholder: "body" });
  const stats = [
    [money(summary.money_spent), "invested of the $10M"],
    [`${summary.units}`, "condos, all bought outright"],
    [money(summary.revenue), "revenue per year"],
    [pct(summary.gross_yield, 1), "revenue ÷ purchase price"],
  ];
  stats.forEach(([big, label], i) => {
    const x = 0.6 + i * 2.25;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.1, w: 2.0, h: 1.5, rectRadius: 0.08, fill: { color: C.background1, transparency: 88 }, line: { type: "none" }, objectName: `stat-card-${i + 1}` });
    s.addText(big, { x: x + 0.15, y: 3.25, w: 1.7, h: 0.7, fontSize: 30, bold: true, color: C.background1, margin: 0, isTextBox: true, objectName: `stat-value-${i + 1}` });
    s.addText(label, { x: x + 0.15, y: 3.95, w: 1.7, h: 0.5, fontSize: 12, color: C.background2, margin: 0, valign: "top", isTextBox: true, objectName: `stat-label-${i + 1}` });
  });
  s.addNotes(`[0:40] Our answer first. With the $10M we buy ${summary.units} condos in ${summary.neighbourhoods} neighbourhoods: Downtown Eastside, Downtown and Kitsilano. We spend ${money(summary.money_spent)} and expect about ${money(summary.revenue)} of revenue a year, which is ${pct(summary.gross_yield, 1)} of what we pay. The rest of the talk shows the decisions behind this and why we made them.`);
}

// 2. Where the money goes
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Decision" });
  s.addText(`Where the $10M goes: ${summary.units} condos in ${summary.neighbourhoods} neighbourhoods`, { placeholder: "title" });
  const hoods = [...new Set(alloc.map((a) => a.neighbourhood_cleansed))];
  hoods.forEach((h, i) => {
    const rows = alloc.filter((a) => a.neighbourhood_cleansed === h);
    const m = rows.reduce((t, r) => t + r.money, 0), rev = rows.reduce((t, r) => t + r.revenue, 0);
    const x = 0.5 + i * 3.08, w = 2.84;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.25, w, h: 2.75, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: `hood-card-${i + 1}` });
    s.addText(h, { x: x + 0.2, y: 1.4, w: w - 0.4, h: 0.4, fontSize: 18, bold: true, color: C.text2, margin: 0, isTextBox: true, objectName: `hood-name-${i + 1}` });
    s.addText(rows.map((r, j) => ({ text: `${r.units} × ${bed(r.bedrooms_grp)}`, options: { breakLine: j < rows.length - 1 } })),
      { x: x + 0.2, y: 1.85, w: w - 0.4, h: 0.8, fontSize: 22, bold: true, color: C.accent1, margin: 0, valign: "top", isTextBox: true, objectName: `hood-units-${i + 1}` });
    s.addText([
      { text: `${money(m)} · ${pct(m / 1e7, 0)} of budget`, options: { breakLine: true } },
      { text: `${money(rev)} revenue / yr`, options: { breakLine: true } },
      { text: `${pct(rev / m)} revenue ÷ price`, options: {} },
    ], { x: x + 0.2, y: 2.75, w: w - 0.4, h: 1.1, fontSize: 14, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 4, isTextBox: true, objectName: `hood-stats-${i + 1}` });
  });
  s.addText([
    { text: "Total  ", options: { bold: true, color: C.text2 } },
    { text: `${summary.units} condos · ${money(summary.money_spent)} spent (${money(summary.unspent)} left) · ${money(summary.revenue)} revenue a year · ${pct(summary.gross_yield, 1)} revenue ÷ price`, options: { color: C.text1 } },
  ], { x: 0.5, y: 4.3, w: 9.0, h: 0.4, fontSize: 14, margin: 0, isTextBox: true, objectName: "total-line" });
  s.addText("Revenue = median of comparable listings, last 12 months, assumed for 2027. Price = 2026 assessed value. Operating costs not included.",
    { x: 0.5, y: 4.7, w: 9.0, h: 0.35, fontSize: 10, color: C.accent3, margin: 0, isTextBox: true, objectName: "basis-note" });
  s.addNotes("[1:00] Downtown Eastside gets 7 one-bed condos. It stops at 7 because an 8th would pass our 40% cap. Downtown gets 3 one-beds and 2 two-beds. Kitsilano gets 3 one-beds, and then the money runs out. Every number here is a median of real comparable listings.");
}

// 3. Decision log
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Decision" });
  s.addText("Three decisions shaped the portfolio", { placeholder: "title" });
  const condoLow = Math.min(...condos.map((c) => c.gross_yield)), condoHigh = Math.max(...condos.map((c) => c.gross_yield));
  const H = { bold: true, color: C.background1, fill: { color: C.text2 }, fontSize: 14, valign: "middle" };
  const cell = (t, o = {}) => ({ text: t, options: Object.assign({ fontSize: 14, color: C.text1, valign: "middle" }, o) });
  const rows = [
    [cell("Decision", H), cell("Why", H), cell("Impact", H)],
    [cell("1  Condos only, no houses", { bold: true, color: C.text2 }), cell("Similar revenue, but houses cost 2‑3× more"),
      cell(`Every condo option ${pct(condoLow)}+ vs best house ${pct(bestHouse.gross_yield)} (revenue ÷ price)`)],
    [cell(`2  Trust only options with ${MIN_N}+ listings`, { bold: true, color: C.text2 }), cell(`A median from 20 listings is ±${pct(err(20), 0)} off; from ${MIN_N}, ±${pct(err(MIN_N), 0)}`),
      cell("West End 2-bed (23 listings) out; Kitsilano 1-bed (31) in")],
    [cell("3  Rank by revenue ÷ price", { bold: true, color: C.text2 }), cell("Revenue alone favours big, expensive units; net yield needs costs the brief doesn't give"),
      cell(`${summary.units} units, ${money(summary.revenue)}/yr vs ${OLD.units} units, ${money(OLD.revenue)}/yr in our earlier cost-based model`)],
  ];
  s.addTable(rows, { x: 0.5, y: 1.25, w: 9.0, colW: [2.9, 3.05, 3.05], rowH: [0.45, 0.95, 0.95, 0.95], border: { type: "solid", pt: 0.75, color: "D5DDE0" }, margin: [0.06, 0.12, 0.06, 0.12], objectName: "decision-log" });
  s.addNotes("[1:30] These are our three main decisions. One: condos only, because houses earn similar revenue but cost two to three times more. Two: we only trust a number if at least 30 listings stand behind it. Below that, a typical listing's revenue can be off by 15 to 20 percent. Three: we rank by revenue divided by price. Our earlier model ranked after assumed costs and bought 13 units; switching brought in more Downtown 1-beds and raised revenue to about 765 thousand.");
}

// ---------- Section 2: why ----------
pres.addSection({ title: "Why" });

// 4. Metric
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Why" });
  s.addText("We rank by revenue ÷ price: what each dollar earns", { placeholder: "title" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.25, w: 4.2, h: 1.1, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: "metric-card" });
  s.addText([
    { text: "Revenue ÷ price", options: { fontSize: 26, bold: true, color: C.accent1, breakLine: true } },
    { text: "median yearly revenue ÷ estimated purchase price", options: { fontSize: 13, color: C.text1 } },
  ], { x: 0.7, y: 1.35, w: 3.8, h: 0.9, margin: 0, valign: "middle", isTextBox: true, objectName: "metric-formula" });
  s.addText([
    { text: "Budget is fixed: cheaper units mean more units", options: { bullet: true, breakLine: true } },
    { text: "Operating costs are not given, so we leave them out", options: { bullet: true, breakLine: true } },
    { text: "Occupancy shows demand, not return", options: { bullet: true } },
  ], { x: 0.5, y: 2.6, w: 4.2, h: 1.6, fontSize: 14, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0, isTextBox: true, objectName: "metric-reasons" });
  const big = condos.find((c) => c.neighbourhood_cleansed === "Downtown" && c.bedrooms_grp === "3+");
  const small = condos.find((c) => c.neighbourhood_cleansed === "Downtown Eastside" && c.bedrooms_grp === "1");
  const labels = [`1 × Downtown 3+ bed (${money(big.price_cad)})`, `2 × Downtown Eastside 1-bed (${money(2 * small.price_cad)})`];
  s.addText("Same ~$1.1M, two choices: revenue per year", { x: 5.0, y: 1.25, w: 4.5, h: 0.35, fontSize: 14, bold: true, color: C.text2, margin: 0, isTextBox: true, objectName: "example-title" });
  img(s, "example", 5.0, 1.65, 4.5, 2.6);
  s.addText(`The cheaper option earns ${pct(2 * small.rev_median / big.rev_median - 1, 0)} more for the same money.`, { x: 5.0, y: 4.35, w: 4.5, h: 0.35, fontSize: 13, color: C.text1, margin: 0, isTextBox: true, objectName: "example-takeaway" });
  s.addNotes("[1:00] Our one metric is revenue divided by price. The budget is fixed, so the question is how much revenue each dollar buys. For example, about 1.1 million buys either one big Downtown 3-bed or two Downtown Eastside 1-beds, and the two 1-beds earn about 30% more. The brief gives no operating costs, so we leave them out rather than guess.");
}

// 5. Data & assumptions
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Why" });
  s.addText("Two public datasets, stated assumptions and limits", { placeholder: "title" });
  s.addText("From 6,509 listings to the ones we can trust", { x: 0.5, y: 1.2, w: 5.2, h: 0.35, fontSize: 14, bold: true, color: C.text2, margin: 0, isTextBox: true, objectName: "funnel-title" });
  img(s, "funnel", 0.5, 1.55, 5.3, 2.95);
  s.addText("Checks: dropped no-price and $30–$2,000 outliers; 132 reviews dated after the snapshot ignored; 386 listings with no bedroom count treated as 1-bed.",
    { x: 0.5, y: 4.5, w: 5.3, h: 0.5, fontSize: 10, color: "6B757B", margin: 0, valign: "top", isTextBox: true, objectName: "data-checks" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.0, y: 1.2, w: 3.5, h: 3.6, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: "assumption-card" });
  s.addText([
    { text: "Assumptions", options: { bold: true, color: C.text2, breakLine: true } },
    { text: "2027 revenue = last 12 months", options: { bullet: true, breakLine: true } },
    { text: "Price = 2026 assessed value", options: { bullet: true, breakLine: true } },
    { text: "Condo price × bedrooms: 0.85 / 1.15 / 1.5", options: { bullet: true, breakLine: true } },
    { text: "No operating costs (not given)", options: { bullet: true, breakLine: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "Limitations", options: { bold: true, color: C.text2, breakLine: true } },
    { text: "Bookings estimated from reviews", options: { bullet: true, breakLine: true } },
    { text: "Nightly prices from one day in June", options: { bullet: true, breakLine: true } },
    { text: "Assessed value ≠ asking price", options: { bullet: true } },
  ], { x: 6.2, y: 1.35, w: 3.15, h: 3.35, fontSize: 13, color: C.text1, paraSpaceAfter: 3, valign: "top", margin: 0, isTextBox: true, objectName: "assumption-list" });
  s.addNotes("[1:00] We use two public datasets: Inside Airbnb for revenue and bookings, and the City of Vancouver's 2026 tax data for purchase prices. We keep short-term, active, whole-home listings DDD could actually copy, which leaves 1,120 condo listings we can trust. Our main assumptions: 2027 looks like the last 12 months; bookings are estimated from reviews; prices are assessed values; and because the tax data has no bedroom counts, we scale condo prices by bedrooms. The main limits: bookings are estimated from reviews, and prices come from one June day. [7-min version: say only the two sources, the bedroom assumption and the review-based estimate.]");
}

// 6. Condos vs houses
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Why" });
  s.addText("Every trusted condo option beats every house option", { placeholder: "title" });
  const show = [...condos, ...houses.slice(0, 4)];
  const labels = show.map((o) => `${o.neighbourhood_cleansed} ${bed(o.bedrooms_grp)}`);
  img(s, "condo_vs_house", 0.5, 1.15, 6.4, 3.85);
  s.addText([
    { text: "Similar revenue", options: { bold: true, color: C.text2, breakLine: true } },
    { text: `Best house: ${money(bestHouse.rev_median)}/yr`, options: { breakLine: true } },
    { text: `Condos: ${money(Math.min(...condos.map((c) => c.rev_median)))}–${money(Math.max(...condos.map((c) => c.rev_median)))}/yr`, options: { breakLine: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "Much higher price", options: { bold: true, color: C.text2, breakLine: true } },
    { text: `Best house: ${money(bestHouse.price_cad)}`, options: { breakLine: true } },
    { text: `Condos: ${money(Math.min(...condos.map((c) => c.price_cad)))}–${money(Math.max(...condos.map((c) => c.price_cad)))}`, options: {} },
  ], { x: 7.1, y: 1.4, w: 2.4, h: 2.6, fontSize: 14, color: C.text1, valign: "top", margin: 0, isTextBox: true, objectName: "condo-house-facts" });
  s.addText(`All ${condos.length} condo options and the top 4 of ${houses.length} house options with ${MIN_N}+ listings.`, { x: 7.1, y: 4.2, w: 2.4, h: 0.6, fontSize: 10, color: C.accent3, margin: 0, valign: "top", isTextBox: true, objectName: "condo-house-note" });
  s.addNotes(`[0:45] This is why we buy condos only. Houses earn about the same revenue but cost two to three times more. The best house option returns ${pct(bestHouse.gross_yield)}; every condo option we trust returns more than that.`);
}

// 7. Process
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Why" });
  s.addText("We buy from the top until the money or a limit runs out", { placeholder: "title" });
  const steps = [
    ["1", `Rank the ${condos.length} trusted condo options by revenue ÷ price`],
    ["2", "Buy from the top, at most 40% ($4M) per neighbourhood"],
    ["3", "Sizes within 1 point of an area's best share the money"],
    ["4", "Leftover money goes to the next option"],
  ];
  steps.forEach(([n, t], i) => {
    const y = 1.3 + i * 0.85;
    s.addShape(pres.shapes.OVAL, { x: 0.5, y, w: 0.45, h: 0.45, fill: { color: C.accent1 }, line: { type: "none" }, objectName: `step-dot-${n}` });
    s.addText(n, { x: 0.5, y, w: 0.45, h: 0.45, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `step-num-${n}` });
    s.addText(t, { x: 1.1, y: y - 0.08, w: 3.1, h: 0.62, fontSize: 14, color: C.text1, valign: "middle", margin: 0, isTextBox: true, objectName: `step-text-${n}` });
  });
  const units = (o) => { const a = alloc.find((x) => x.neighbourhood_cleansed === o.neighbourhood_cleansed && x.bedrooms_grp === o.bedrooms_grp); return a ? a.units : 0; };
  const labels = condos.map((o) => `${o.neighbourhood_cleansed} ${bed(o.bedrooms_grp)}${units(o) ? ` · ${units(o)} bought` : ""}`);
  img(s, "ranking", 4.4, 1.15, 5.1, 3.85);
  s.addNotes("[1:00] Here's how the allocation works. We rank the eight condo options we trust. We buy from the top: Downtown Eastside 1-beds until the 40% cap. Then Downtown, where 1-beds and 2-beds are nearly tied, so we alternate. Then Kitsilano until the money runs out. Downtown 3-beds and Downtown Eastside 2-beds are skipped because they're clearly worse than the best size in their own area.");
}

// ---------- Section 3: outlook ----------
pres.addSection({ title: "Outlook" });

// 8. 2027 performance
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Outlook" });
  s.addText(`We expect about ${money(SC.base.revenue)} of revenue in 2027`, { placeholder: "title" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.2, w: 3.6, h: 1.85, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: "expected-card" });
  s.addText([
    { text: money(SC.base.revenue), options: { fontSize: 36, bold: true, color: C.accent1, breakLine: true } },
    { text: `${pct(SC.base.gross_yield)} of the purchase price`, options: { fontSize: 14, color: C.text1, breakLine: true } },
    { text: `Range: ${money(SC.revenue_minus20.revenue)} (revenue −20%) to ${money(SC.revenue_plus10.revenue)} (+10%)`, options: { fontSize: 12, color: C.text1 } },
  ], { x: 0.7, y: 1.3, w: 3.25, h: 1.65, margin: 0, valign: "middle", isTextBox: true, objectName: "expected-value" });
  img(s, "scenarios_2027", 4.4, 1.15, 5.1, 1.95);
  const card = (x, head, items, key) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.25, w: 4.4, h: 1.8, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: `${key}-card` });
    s.addText([{ text: head, options: { bold: true, color: C.text2, breakLine: true } },
      ...items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } }))],
    { x: x + 0.2, y: 3.35, w: 4.0, h: 1.6, fontSize: 13, color: C.text1, paraSpaceAfter: 3, valign: "top", margin: 0, isTextBox: true, objectName: `${key}-list` });
  };
  card(0.5, "Could push it down", ["Slow start: new listings have no reviews; January is low season", "Licence or registration delays: listing removed", "Tourism dip hits all units at once"], "down");
  card(5.1, "Could push it up", ["Fewer unlicensed competitors (3,248 licences for 4,969 listings, Apr 2026)", "Professional management beats the median listing", "Conventions and cruise season downtown"], "up");
  s.addNotes(`[1:00] For 2027 we expect about ${money(SC.base.revenue)} of revenue, ${pct(SC.base.gross_yield)} of what we pay. That's the median comparable listing, carried forward. If revenue is 20% lower we still get about ${money(SC.revenue_minus20.revenue)}; 10% higher gives about ${money(SC.revenue_plus10.revenue)}. What could push it down: a slow start, licence delays, or a tourism dip. What could push it up: fewer unlicensed competitors, good management, and big events downtown.`);
}

// 9. Caveats and risks
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Outlook" });
  s.addText("Caveats and risks, and how we reduce them", { placeholder: "title" });
  const H = { bold: true, color: C.background1, fill: { color: C.text2 }, fontSize: 14, valign: "middle" };
  const cell = (t, o = {}) => ({ text: t, options: Object.assign({ fontSize: 14, color: C.text1, valign: "middle" }, o) });
  const tag = (t) => cell(t, { bold: true, color: C.accent1 });
  const minRev = Math.min(...alloc.map((a) => a.revenue_each)), maxRev = Math.max(...alloc.map((a) => a.revenue_each));
  const rows = [
    [cell("", H), cell("What", H), cell("Mitigation", H)],
    [tag("Caveat"), cell(`Each unit earns modest revenue (${money(minRev)}–${money(maxRev)}/yr), and there are ${summary.units} units to manage`),
      cell("Per dollar it earns more; one management company runs all units")],
    [tag("Caveat"), cell("Revenue and bookings are estimates; June prices may run high"),
      cell(`Use the median, not the average; plan for the −20% case (${money(SC.revenue_minus20.revenue)}); track revenue monthly`)],
    [tag("Risk"), cell(`${pct(summary.concentration_downtown_core, 0)} of the money is in Downtown + Downtown Eastside`),
      cell("Max 40% per neighbourhood; Kitsilano adds spread")],
  ];
  s.addTable(rows, { x: 0.5, y: 1.25, w: 9.0, colW: [1.2, 3.9, 3.9], rowH: [0.42, 0.85, 0.85, 0.85], border: { type: "solid", pt: 0.75, color: "D5DDE0" }, margin: [0.06, 0.12, 0.06, 0.12], objectName: "risk-table" });
  s.addText("Opt-out: unlikely for Vancouver, which needs 3%+ rental vacancy for two years. If it happened (from 1 June 2027), it would add competitors, not change our own rules.",
    { x: 0.5, y: 4.7, w: 9.0, h: 0.45, fontSize: 11, color: "6B757B", margin: 0, valign: "top", isTextBox: true, objectName: "optout-note" });
  s.addNotes(`[1:00] Two caveats and one risk. Caveat one: each unit earns modest revenue, and 15 units is more to manage. That's the few-versus-many trade-off; per dollar, many modest units earn more, and one manager runs them all. Caveat two: our revenue is an estimate, so we use the median and plan for a 20% lower case. The main risk is concentration: ${pct(summary.concentration_downtown_core, 0)} of the money is downtown, which our 40% cap and Kitsilano units partly offset.`);
}

// 10. Implementation
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Outlook" });
  s.addText("Next steps: three things before 1 January 2027", { placeholder: "title" });
  const steps = [
    ["1", "Before buying", "Check the building's rules allow short-term rentals"],
    ["2", "Before 1 Jan 2027", "City business licence and provincial registration for every unit"],
    ["3", "1 Jan 2027", `All ${summary.units} units go live`],
  ];
  steps.forEach(([n, when, what], i) => {
    const x = 0.5 + i * 3.08, w = 2.84;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.25, w, h: 1.75, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: `next-card-${n}` });
    s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: 1.4, w: 0.45, h: 0.45, fill: { color: C.accent1 }, line: { type: "none" }, objectName: `next-dot-${n}` });
    s.addText(n, { x: x + 0.2, y: 1.4, w: 0.45, h: 0.45, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `next-num-${n}` });
    s.addText(when, { x: x + 0.8, y: 1.4, w: w - 1.0, h: 0.45, fontSize: 14, bold: true, color: C.text2, valign: "middle", margin: 0, isTextBox: true, objectName: `next-when-${n}` });
    s.addText(what, { x: x + 0.2, y: 2.0, w: w - 0.4, h: 0.9, fontSize: 14, color: C.text1, valign: "top", margin: 0, isTextBox: true, objectName: `next-what-${n}` });
  });
  s.addText([
    { text: "How we know it's working  ", options: { bold: true, color: C.text2 } },
    { text: `monthly revenue on track for about ${money(SC.base.revenue)} a year; if behind, adjust prices first.`, options: { color: C.text1 } },
  ], { x: 0.5, y: 3.25, w: 9.0, h: 0.45, fontSize: 14, margin: 0, isTextBox: true, objectName: "monitoring" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 3.9, w: 9.0, h: 1.1, rectRadius: 0.08, fill: { color: C.background1 }, line: { color: "D5DDE0", width: 0.75 }, objectName: "ai-card" });
  s.addText([
    { text: "AI use  ", options: { bold: true, color: C.text2 } },
    { text: "We used Claude to help write code, run analysis and draft slides. We checked it by re-running every number from code in our GitHub repo, hand-checking the allocation ($10M budget, 40% cap), and testing key choices against alternatives.", options: { color: C.text1 } },
  ], { x: 0.7, y: 3.98, w: 8.6, h: 0.95, fontSize: 12, margin: 0, valign: "middle", isTextBox: true, objectName: "ai-disclosure" });
  s.addNotes("[0:45] Three steps before launch. Before buying each condo, check the building allows short-term rentals. Before January 1, get the City licence and provincial registration for every unit, because without them the listing is removed. Then all 15 go live. We'll know it's working if monthly revenue tracks our plan; if not, we adjust prices first. We used AI to help with code and slides, and checked it by re-running every number from our repo.");
}

// ---------- Appendix ----------
pres.addSection({ title: "Appendix" });
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Appendix" });
  s.addText("Decision log", { placeholder: "title" });
  const H = { bold: true, color: C.background1, fill: { color: C.text2 }, fontSize: 12, valign: "middle" };
  const cell = (t, o = {}) => ({ text: t, options: Object.assign({ fontSize: 12, color: C.text1, valign: "middle" }, o) });
  const condoLow = Math.min(...condos.map((c) => c.gross_yield));
  const rows = [
    [cell("Decision", H), cell("Alternatives compared", H), cell("Evidence", H), cell("What changed", H)],
    [cell("1  Condos only", { bold: true, color: C.text2 }), cell("Condos and houses together"),
      cell(`Similar revenue; houses cost 2‑3× more. Every condo option ${pct(condoLow)}+ vs best house ${pct(bestHouse.gross_yield)}`),
      cell(`All ${summary.units} units are condos; no houses`)],
    [cell(`2  Trust options with ${MIN_N}+ listings`, { bold: true, color: C.text2 }), cell("5, 10, 20, 50 listings"),
      cell(`Resampling: a median from 20 listings is ±${pct(err(20), 0)} off; from ${MIN_N}, ±${pct(err(MIN_N), 0)}; from 50, ±${pct(err(50), 0)}`),
      cell("West End 2-bed (23 listings) dropped; Kitsilano 1-bed (31) came in")],
    [cell("3  Rank by revenue ÷ price", { bold: true, color: C.text2 }), cell("Revenue alone; net yield after assumed costs"),
      cell("Revenue alone favours expensive units (1 Downtown 3+ bed earns less than 2 Downtown Eastside 1-beds); costs not given in the brief"),
      cell(`${OLD.units} → ${summary.units} units; ${money(OLD.revenue)} → ${money(summary.revenue)} revenue/yr; more Downtown 1-beds`)],
  ];
  s.addTable(rows, { x: 0.5, y: 1.2, w: 9.0, colW: [1.9, 1.9, 2.9, 2.3], rowH: [0.38, 0.95, 0.95, 1.05], border: { type: "solid", pt: 0.75, color: "D5DDE0" }, margin: [0.05, 0.1, 0.05, 0.1], objectName: "decision-log-full" });
  s.addText("Also: max 40% of $10M per neighbourhood; sizes within 1 point of an area's best share the money; max 10% of an option's listings.",
    { x: 0.5, y: 4.85, w: 9.0, h: 0.3, fontSize: 10, color: "6B757B", margin: 0, isTextBox: true, objectName: "other-rules" });
  s.addNotes("Decision log for the judges: each decision with the alternatives we compared, the evidence, and what changed.");
}
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Appendix" });
  s.addText(`Backup: ${MIN_N} listings keep a typical error near ±${pct(err(MIN_N), 0)}`, { placeholder: "title" });
  img(s, "sample_size", 0.5, 1.15, 5.7, 3.85);
  s.addText([
    { text: "How we tested", options: { bold: true, color: C.text2, breakLine: true } },
    { text: "5,000 random samples from the 374 Downtown 1-bed condos; each sample's median revenue vs the full median.", options: { breakLine: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "Small groups mislead", options: { bold: true, color: C.text2, breakLine: true } },
    { text: "South Cambie condos show 66% occupancy, from 1 listing.", options: {} },
  ], { x: 6.4, y: 1.3, w: 3.1, h: 3.4, fontSize: 13, color: C.text1, valign: "top", margin: 0, isTextBox: true, objectName: "sample-notes" });
  s.addNotes("Backup for Q&A: why 30 listings.");
}
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Appendix" });
  s.addText("Backup: Downtown condos book the most nights", { placeholder: "title" });
  img(s, "occupancy", 0.5, 1.15, 5.9, 3.85);
  s.addText([
    { text: "Demand supports, price decides", options: { bold: true, color: C.text2, breakLine: true } },
    { text: "Occupancy = median nights booked ÷ 365, condos only, areas with 30+ listings.", options: { breakLine: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "Downtown Eastside books less than Downtown but costs less, so it returns more per dollar.", options: {} },
  ], { x: 6.6, y: 1.3, w: 2.9, h: 3.4, fontSize: 13, color: C.text1, valign: "top", margin: 0, isTextBox: true, objectName: "occupancy-notes" });
  s.addNotes("Backup for Q&A: demand by neighbourhood.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  if (APPLY_THEME) await require(APPLY_THEME).applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
