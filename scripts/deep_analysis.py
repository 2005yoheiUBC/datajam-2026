"""Audit saved aggregates and generate a Japanese analysis; standard library only.

Run: python3 scripts/deep_analysis.py
Does not download data or overwrite the original pipeline's outputs.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import config as C

OUT = ROOT / "analsis" / "deep_analysis"
KEYS = tuple(C.SEGMENT_KEYS)
TEXT = set(KEYS) | {"side", "gvr_type", "scenario", "case", "step", "why"}
SOURCES = {
    "city": "https://vancouver.ca/doing-business/short-term-rentals.aspx",
    "definition": "https://bylaws.vancouver.ca/consolidated/14131.PDF",
    "airbnb": "https://www.airbnb.com/help/article/1857",
    "gvr": "https://members.gvrealtors.ca/news/GVR-Stats-Package-October-2026.pdf",
}


def read(name):
    with (C.TABLES / f"{name}.csv").open(newline="") as f:
        return [{k: v if k in TEXT else float(v) for k, v in r.items()}
                for r in csv.DictReader(f)]


def key(r):
    return tuple(r[k] for k in KEYS)


def write(name, rows):
    assert rows, name
    with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def underwrite(r, revenue_factor=1.0, price_factor=1.0, fee=C.PLATFORM_FEE,
               management=C.MANAGEMENT_FEE, offline=0, reserve=0, rev_col="rev_median"):
    price = r["price_cad"] * price_factor
    gross = r[rev_col] * revenue_factor * (1 - offline / 12)
    fixed = (C.LICENCE_AND_REGISTRATION_CAD + C.INSURANCE_CAD_YEAR
             + C.STRATA_FEES_CAD_MONTH[r["bucket"]] * 12
             + C.PROPERTY_TAX_RATE * price)
    cash = price * (1 + C.CLOSING_COSTS) + C.FURNISHING_CAD
    noi = gross * (1 - fee - management - C.CLEANING_AND_SUPPLIES - reserve) - fixed
    return dict(r, gross=gross, fixed=fixed, cash_in=cash, noi=noi, net_yield=noi / cash)


def summary(port, label):
    cash = sum(r["cash_in"] for r in port)
    noi = sum(r["noi"] for r in port)
    hood = defaultdict(float)
    for r in port:
        hood[r[KEYS[0]]] += r["cash_in"]
    return dict(scenario=label, units=len(port), cash_deployed=cash,
                idle_cash=C.BUDGET_CAD-cash, noi=noi,
                yield_on_deployed=noi/cash if cash else None,
                yield_on_budget=noi/C.BUDGET_CAD,
                neighbourhoods=len(hood), max_hood_budget_share=max(hood.values(), default=0)/C.BUDGET_CAD)


def select(rows, min_n=5, cap=.4, strict=True, score="net_yield", legacy=False):
    # Same yield-first heuristic as the repository; not a global optimiser.
    candidates = [r for r in rows if r["n"] >= min_n and (legacy or r["noi"] > 0)]
    candidates.sort(key=lambda r: r[score], reverse=True)
    selected, spent, by_hood = [], 0, defaultdict(float)
    for r in candidates:
        capacity = int(r["n"] // 10)
        if not strict:
            capacity = max(1, capacity)
        for _ in range(capacity):
            hood = r[KEYS[0]]
            if spent + r["cash_in"] > C.BUDGET_CAD + 1e-6:
                break
            if by_hood[hood] + r["cash_in"] > C.BUDGET_CAD * cap + 1e-6:
                break
            selected.append(r)
            spent += r["cash_in"]
            by_hood[hood] += r["cash_in"]
    return selected


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |",
                       "| " + " | ".join("---" for _ in headers) + " |"]
                      + ["| " + " | ".join(str(v) for v in row) + " |" for row in rows])


def pct(n):
    return f"{n:.2%}" if n is not None else "算定不可"


def money(n):
    return f"{n:,.0f}"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    seg, saved, original = read("segments"), read("segments_underwritten"), read("recommended_portfolio")
    rows = [underwrite(r) for r in saved]
    by_key = {key(r): r for r in rows}
    checks = []

    def check(name, passed, detail):
        checks.append(dict(check=name, status="PASS" if passed else "FAIL", detail=detail))

    check("unique_segment_keys", len(by_key) == len(rows), f"{len(rows)} buyable segments")
    check("finite_numeric_inputs", all(math.isfinite(v) for r in saved for v in r.values() if isinstance(v, float)), "saved numeric cells")
    check("segment_counts_positive_integer", all(r["n"] > 0 and r["n"].is_integer() for r in seg), "aggregate sample counts")
    check("occupancy_in_range", all(0 <= r["occ_median"] <= 1 for r in seg), "0 <= median occupancy <= 1")
    check("revenue_quantiles_ordered", all(0 <= r["rev_p25"] <= r["rev_median"] <= r["rev_p75"] for r in seg), "p25 <= median <= p75")
    with C.GVR_FILE.open(newline="") as f:
        benchmarks = {(r["side"],r["gvr_type"]):float(r["benchmark_price_cad"]) for r in csv.DictReader(f)}
    pricing_error = []
    for r in saved:
        benchmark = benchmarks[(r["side"],r["gvr_type"])]
        multiplier = C.CONDO_BEDROOM_MULTIPLIER[r["bedrooms_grp"]] if r["bucket"] == "condo" else 1
        pricing_error.append(abs(r["price_cad"]-benchmark*multiplier))
    check("benchmark_and_bedroom_pricing", max(pricing_error) < 1e-7, "all 121 saved prices versus external CSV and config multipliers")
    segment_lookup = {key(r):r for r in seg}
    shared_numeric = [f for f in seg[0] if f not in TEXT]
    check("aggregate_join_consistency", all(key(r) in segment_lookup and all(abs(r[f]-segment_lookup[key(r)][f]) < 1e-7 for f in shared_numeric) for r in saved), "counts, occupancy, revenue quantiles, ratings and shares")
    for field in ("cash_in", "noi", "net_yield"):
        error = max(abs(a[field]-b[field]) for a, b in zip(rows, saved))
        check(f"recomputed_{field}", error < 1e-7, f"max absolute difference {error:.12g}")
    base_port = [by_key[key(r)] for r in original]
    replica = select(rows, strict=False, legacy=True)
    check("reproduces_original_selection", Counter(map(key, replica)) == Counter(map(key, original)), "legacy max(1, floor(n/10)) capacity")
    base = summary(base_port, "保存済み購入案")
    check("original_budget", base["cash_deployed"] <= C.BUDGET_CAD, money(base["cash_deployed"]))
    check("original_neighbourhood_cap", base["max_hood_budget_share"] <= .4 + 1e-8, pct(base["max_hood_budget_share"]))
    quantities = Counter(map(key, original))
    violations = [(k, count, by_key[k]["n"]) for k, count in quantities.items() if count > by_key[k]["n"]*.1 + 1e-8]
    check("original_supply_cap", not violations, str(violations))
    for r in original:
        check_name = None
        if any(abs(r[f]-by_key[key(r)][f]) > 1e-7 for f in ("noi", "cash_in", "net_yield")):
            check_name = str(key(r))
            raise ValueError(f"Saved portfolio differs from segment inputs: {check_name}")
    for s in read("sensitivity"):
        col = "rev_p25" if s["case"].startswith("low") else "rev_p75" if s["case"].startswith("high") else "rev_median"
        off = 2 if "offline" in s["case"] else 0
        value = summary([underwrite(r, rev_col=col, offline=off) for r in base_port], s["case"])
        check("sensitivity_"+s["case"], abs(value["noi"]-s["noi"]) < .01 and abs(value["yield_on_deployed"]-s["net_yield"]) < 1e-10, "independent recalculation")
    key_numbers = json.loads((C.OUTPUTS / "key_numbers.json").read_text())
    check("headline_rounding", key_numbers["units"] == len(base_port)
          and abs(key_numbers["noi_2027_cad"]-base["noi"]) <= 500
          and abs(key_numbers["net_yield_base"]-base["yield_on_deployed"]) <= .0005,
          "headline NOI within CAD 500; yield within 0.0005")
    write("audit", checks)
    unexpected=[c for c in checks if c["status"]=="FAIL" and c["check"]!="original_supply_cap"]
    if unexpected:
        raise SystemExit("Numerical reconciliation failed; inspect audit.csv. No report regenerated.")

    # Fixed holdings: these do not reselect units or force cash back under budget.
    scenario_args = [("base", {})]
    scenario_args += [(f"revenue_minus_{d}", dict(revenue_factor=1-d/100)) for d in (10,20,30)]
    scenario_args += [(f"purchase_plus_{d}", dict(price_factor=1+d/100)) for d in (10,20)]
    scenario_args += [(f"management_{m}", dict(management=m/100)) for m in (15,25)]
    scenario_args += [(f"offline_{m}_months", dict(offline=m)) for m in (2,4)]
    scenario_args += [("platform_15_5", dict(fee=.155)),
                      ("platform_15_5_revenue_minus_20", dict(fee=.155,revenue_factor=.8)),
                      ("platform_15_5_revenue_minus_20_reserve_5", dict(fee=.155,revenue_factor=.8,reserve=.05)),
                      ("cross_section_p25", dict(rev_col="rev_p25")),
                      ("cross_section_p75", dict(rev_col="rev_p75"))]
    scenarios = [summary([underwrite(r, **args) for r in base_port], name) for name,args in scenario_args]
    write("fixed_portfolio_scenarios", scenarios)
    grid = []
    for fee in (.03,.155):
        for price in (.8,.9,1,1.1,1.2):
            for rev in (.6,.7,.8,.9,1,1.1):
                s = summary([underwrite(r, fee=fee, price_factor=price, revenue_factor=rev) for r in base_port], "fixed holdings")
                grid.append(dict(platform_fee=fee, purchase_price_factor=price,revenue_factor=rev,**s))
    write("price_revenue_grid", grid)

    thresholds, selected_ports = [], {}
    for strict in (False, True):
        for min_n in (5,10,20,30):
            name = f"{'strict' if strict else 'legacy'}_n{min_n}"
            port = select(rows,min_n=min_n,strict=strict)
            s = summary(port,name)
            s["original_units_retained"] = sum((Counter(map(key, port)) & quantities).values())
            thresholds.append(s)
            selected_ports[name] = port
    write("sample_size_sensitivity", thresholds)
    caps = [summary(select(rows,min_n=20,cap=cap),f"n20_strict_cap_{cap}") for cap in (.2,.3,.4,.5,1)]
    write("concentration_cap_sensitivity",caps)
    # Stress-aware ranking: p25 is a cross-sectional scenario, not a forecast.
    prudent_rows = [underwrite(r,fee=.155) for r in rows]
    for r in prudent_rows:
        r["stress_score"] = underwrite(r,fee=.155,rev_col="rev_p25")["net_yield"]
    stress_port = select(prudent_rows,min_n=20,score="stress_score")
    comparison_ports = {"original":base_port,"strict_n20":selected_ports["strict_n20"],
                        "fee_15_5_n20":select(prudent_rows,min_n=20),
                        "p25_ranking_fee_15_5_n20":stress_port}
    comparisons = []
    for name,port in comparison_ports.items():
        for label,args in [("legacy_fee_base",{}),("fee15_5",dict(fee=.155)),
                           ("fee15_5_revenue80_reserve5",dict(fee=.155,revenue_factor=.8,reserve=.05)),
                           ("fee15_5_cross_section_p25",dict(fee=.155,rev_col="rev_p25"))]:
            comparisons.append(dict(selection=name,**summary([underwrite(r,**args) for r in port],label)))
        assert sum(r["cash_in"] for r in port) <= C.BUDGET_CAD+1e-6
        if name != "original":
            assert all(count <= by_key[k]["n"]*.1+1e-8 for k,count in Counter(map(key,port)).items())
            assert summary(port,name)["max_hood_budget_share"] <= .4+1e-8
    write("portfolio_comparison",comparisons)
    holdings = []
    for name,port in comparison_ports.items():
        counts = Counter(map(key,port))
        for k,count in counts.items():
            r=by_key[k]
            holdings.append(dict(selection=name,**{f:r[f] for f in KEYS},units=count,comparables=r["n"],
                                 cash_deployed=count*r["cash_in"],base_noi=count*r["noi"]))
    write("portfolio_holdings",holdings)

    neighbourhoods=[]
    for hood in sorted({r[KEYS[0]] for r in base_port}):
        port=[r for r in base_port if r[KEYS[0]]==hood]
        n=summary(port,hood)
        loss=sum(r["rev_median"]*.69 for r in port)  # all local revenue lost; fixed costs remain
        neighbourhoods.append(dict(neighbourhood=hood,units=len(port),capital_share=n["cash_deployed"]/base["cash_deployed"],
                                   noi_share=n["noi"]/base["noi"],noi=n["noi"],
                                   annual_noi_if_hood_offline=base["noi"]-loss))
    neighbourhoods.sort(key=lambda r:r["capital_share"],reverse=True)
    write("neighbourhood_concentration",neighbourhoods)

    diagnostics=[]
    for r in rows:
        fixed=r["fixed"]
        fee15=underwrite(r,fee=.155)
        required_revenue=fixed/.69
        max_price_4pct=(.69*r["rev_median"]-(fixed-C.PROPERTY_TAX_RATE*r["price_cad"])-.04*C.FURNISHING_CAD)/(C.PROPERTY_TAX_RATE+.04*(1+C.CLOSING_COSTS))
        diagnostics.append(dict(**{k:r[k] for k in KEYS},n=r["n"],price_cad=r["price_cad"],
                                revenue=r["rev_median"],net_yield=r["net_yield"],fee15_5_yield=fee15["net_yield"],
                                p25_yield=underwrite(r,rev_col="rev_p25")["net_yield"],
                                break_even_revenue=required_revenue,revenue_decline_to_zero=1-required_revenue/r["rev_median"] if r["rev_median"] else None,
                                max_purchase_price_for_4pct=max_price_4pct,
                                quantile_spread_over_median=(r["rev_p75"]-r["rev_p25"])/r["rev_median"] if r["rev_median"] else None))
    diagnostics.sort(key=lambda r:r["net_yield"],reverse=True)
    write("segment_diagnostics",diagnostics)

    cut=median(r["price_cad"] for r in rows)
    fewmany=[]
    for name,pool in [("all",rows),("few_high_value",[r for r in rows if r["price_cad"]>=cut]),
                      ("many_modest",[r for r in rows if r["price_cad"]<cut])]:
        fewmany.append(summary(select(pool,strict=False,legacy=True),name))
    for name,pool in [("few_high_value_n20_strict",[r for r in rows if r["price_cad"]>=cut]),
                      ("many_modest_n20_strict",[r for r in rows if r["price_cad"]<cut])]:
        fewmany.append(summary(select(pool,min_n=20),name))
    write("few_vs_many_budget_basis",fewmany)
    assert abs(fewmany[0]["noi"]-base["noi"]) < .01
    filters=read("filters_applied")
    gross=sum(r["rev_median"] for r in base_port)
    fixed=sum(r["fixed"] for r in base_port)
    b15=next(s for s in scenarios if s["scenario"]=="platform_15_5")
    break_even=1-fixed/(gross*.69)
    break_even15=1-fixed/(gross*.565)
    diagnostics_selected=[r for r in diagnostics if r["n"]>=5][:10]
    n20=next(s for s in thresholds if s["scenario"]=="strict_n20")
    concentration_2=sum(n["capital_share"] for n in neighbourhoods[:2])
    low_n_cash=sum(r["cash_in"] for r in base_port if r["n"]<20)/base["cash_deployed"]
    count_buyable=sum(r["n"] for r in rows)
    total_count=sum(r["n"] for r in seg)
    comp={(r['selection'],r['scenario']):r for r in comparisons}
    strict_p25=comp['strict_n20','fee15_5_cross_section_p25']
    ranked_p25=comp['p25_ranking_fee_15_5_n20','fee15_5_cross_section_p25']
    ranked_base=comp['p25_ranking_fee_15_5_n20','fee15_5']
    report=f'''# Vancouver Airbnb：既存データの深掘り分析

分析日：2026年11月12日。通貨：CAD。対象は課題用の架空ファンドDDD。

現状の結論は「小型コンドミニアム中心の構成が、保存済みの価格・費用仮定では高収益」。ただし、**約4%という数字は、手数料・比較件数・購入価格の仮定に依存する**。まず分析対象の定義を修正し、運営手数料と比較件数に対する頑健性を発表の中心に置くべきである。

## 1. 何を確認できたか

保存済みの{len(seg)}区分（地域×物件種別×寝室数）、購入可能と分類された{len(rows)}区分、{len(base_port)}戸の購入案を使用。区分の比較件数合計は{total_count:,.0f}件、購入可能区分では{count_buyable:,.0f}件。元データ・レビュー・カレンダーはフォルダにないため、集計表からの再計算に限定した。

価格・費用から営業利益を独立に再計算し、既存購入案、感度分析4ケース、見出し数値との整合性を検証した。数値の再現と、元データ自体の正しさは別である。欠損・非稼働物件・価格外れ値・レビュー推定の妥当性は再検証できない。

クリーニングは6,509件から4,401件へ。価格欠損664件、価格範囲外399件、最低宿泊日数30泊以上1,045件を順に除外している。除外理由・非稼働物件を外した影響・欠損寝室を1とする影響は、元データ復元後の検証課題。

## 2. 元の購入案の収益構造

| 指標 | 値 |
| --- | ---: |
| 戸数／地域数 | {base['units']}戸／{base['neighbourhoods']}地域 |
| 投入資金 | {money(base['cash_deployed'])} |
| 未使用資金 | {money(base['idle_cash'])} |
| 年間推定売上の合計 | {money(gross)} |
| 売上連動費用（31%） | {money(gross*.31)} |
| 年間固定費 | {money(fixed)} |
| 年間営業利益 | {money(base['noi'])} |
| 投入資金に対する営業利回り | {pct(base['yield_on_deployed'])} |
| 予算1,000万に対する営業利回り | {pct(base['yield_on_budget'])} |

営業利益 = 売上 × (1 − プラットフォーム手数料 − 管理手数料 − 清掃等費用) − 固定費。
投入資金 = 購入価格 × 1.04 + 家具25,000／戸。借入なし。売却益・所得税・減価償却は含めない。修繕積立や大規模修繕、運転資金も基準ケースに含まれず、投資全体のIRRではない。

全15戸がコンドミニアムであり、「6地域」は物件種別の分散を意味しない。また、区分ごとの売上中央値を合計しており、ポートフォリオ全体の売上中央値や期待値と同じではない。

## 3. 地域ランキングと比較件数

{table(['地域','種別','寝室','比較件数','元の利回り','手数料15.5%','売上p25時'],[[r[KEYS[0]],r['bucket'],r['bedrooms_grp'],int(r['n']),pct(r['net_yield']),pct(r['fee15_5_yield']),pct(r['p25_yield'])] for r in diagnostics_selected])}

Strathconaの1寝室は高収益だが比較対象10件、Riley Parkの2寝室は7件。購入案の資金の{pct(low_n_cash)}が比較対象20件未満の区分に配分されている。件数の多さだけで偏りは消えないが、5件以上だけで上位を選ぶ方法の依存度を確認する必要がある。

{table(['選定条件','戸数','営業利益','投入資金利回り','元の15戸から残った戸数'],[[r['scenario'],r['units'],money(r['noi']),pct(r['yield_on_deployed']),r['original_units_retained']] for r in thresholds])}

legacyは元コードと同じ「最低1戸可」、strictはfloor(比較件数×10%)を厳守する。strict_n20では{n20['units']}戸、利回り{pct(n20['yield_on_deployed'])}。条件変更で再選定しており、同じ15戸のストレス試算とは区別する。最低件数20は感度分析用の選択であり、統計的に保証された閾値ではない。

## 4. 売上・購入価格・費用への感度

{table(['固定した15戸のケース','営業利益','投入資金利回り','未使用資金／追加必要資金'],[[r['scenario'],money(r['noi']),pct(r['yield_on_deployed']),money(r['idle_cash'])] for r in scenarios])}

購入価格上昇ケースでは元の15戸を固定し、投入資金を増額する。未使用資金が負なら予算超過で、そのまま実行可能な購入案ではない。固定資産税と取得費用も価格に連動させた。管理料・清掃費等は売上比例、営業停止中も固定費は継続する。

元の費用率では売上が基準から{pct(break_even)}落ちると営業利益がゼロ。手数料15.5%では{pct(break_even15)}。これは全物件の売上を同じ比率で変える計算で、赤字確率ではない。

プラットフォーム手数料を3%から15.5%へ変えると、営業利益は{money(base['noi']-b15['noi'])}減り、利回りは{pct(b15['yield_on_deployed'])}となる。Airbnb公式は単一手数料では多くのホストが15.5%、物件管理ソフト利用者等には必須と説明している。全対象への適用と2027年の条件は運営形態ごとに確認が必要。[Airbnb公式]({SOURCES['airbnb']})

このケースは掲載売上を固定した費用感度である。ゲスト手数料の廃止に伴う価格調整や需要反応を織り込んだ将来予測ではない。修繕積立5%も外部相場ではなく、未計上費用への感度をみる追加仮定。

p25/p75ケースは区分内の物件間の売上差を全保有戸に同時適用したもの。予測区間・信頼区間・発生確率として使わない。集計表からブートストラップや地域間相関の推定はできない。

## 5. どの程度分散しているか

{table(['地域','戸数','投入資金構成比','営業利益構成比','当該地域が通年停止した場合の全体利益'],[[r['neighbourhood'],r['units'],pct(r['capital_share']),pct(r['noi_share']),money(r['annual_noi_if_hood_offline'])] for r in neighbourhoods])}

上位2地域で投入資金の{pct(concentration_2)}を占める。市全体の共通ショックに対して、地域を分けるだけでは保護にならない。通年停止試算はその地域の売上だけゼロ、固定費を維持。他地域への需要移転・資産売却・長期賃貸転換は仮定しない。

最低比較件数20件・厳格な供給制限で、地域ごとの上限を変えた結果：

{table(['地域上限（総予算比）','戸数','投入資金','営業利益','投入資金利回り'],[[r['scenario'].split('_')[-1],r['units'],money(r['cash_deployed']),money(r['noi']),pct(r['yield_on_deployed'])] for r in caps])}

## 6. 「少数高額」と「多数低額」

{table(['ケース','戸数','投入資金','未使用資金','投入資金利回り','予算全体利回り'],[[r['scenario'],r['units'],money(r['cash_deployed']),money(r['idle_cash']),pct(r['yield_on_deployed']),pct(r['yield_on_budget'])] for r in fewmany])}

高額／低額の境界は購入可能区分の価格中央値{money(cut)}。各区分を等重みにした境界で、実際の販売物件の中央値ではない。未使用現金の利息はゼロとした。両案の投資額が異なるため、予算全体の利回りで比較する。多数保有による追加人員・調整時間はデータがなく未計上。

## 7. 保守的な選定案も比較する

{table(['選定方法','評価ケース','戸数','投入資金','営業利益','投入資金利回り'],[[r['selection'],r['scenario'],r['units'],money(r['cash_deployed']),money(r['noi']),pct(r['yield_on_deployed'])] for r in comparisons])}

strict_n20は比較20件以上と供給10%制限。fee_15_5_n20はさらに手数料15.5%で再順位付け。p25_rankingは手数料15.5%・売上p25時の利回りで順位付けする。ただし購入を許すのは中央値売上時の営業利益が正の候補であり、p25で黒字になる保証はない。購入構成はportfolio_holdings.csvで追跡できる。

どの案も利回り順に購入する貪欲法で、全体最適性は保証しない。「optimised」という既存ラベルは数学的な最適解の証明ではない。次段階で、整数戸数・予算・地域上限・供給上限を制約にした年間営業利益最大化と比較する価値がある。

**比較から分かったこと：比較件数を増やすだけで下振れ耐性が改善するとは限らない。** strict_n20は、手数料15.5%・売上p25の同時適用で年間営業利益{money(strict_p25['noi'])}となる。一方、p25時の利回りで順位付けした案は{ranked_p25['units']}戸・{ranked_p25['neighbourhoods']}地域となり、同じケースで年間営業利益{money(ranked_p25['noi'])}。その代わり、中央値売上・手数料15.5%の利回りは{pct(ranked_base['yield_on_deployed'])}となる。利益水準と下振れ耐性の交換条件として提示できる。ただしp25順位を同じデータで評価しているので、別時点のデータでの検証は未実施。

## 8. 解釈を変える監査上の問題

1. **短期賃貸の定義。** コードの30泊閾値を「BCの法的定義」と説明するのは誤り。バンクーバー市は90泊未満と定義している。30泊未満に限定する分析設計自体は可能だが、その場合は対象市場の定義として明示する。元データがないため、除外1,045件のうち30〜89泊の件数・収益影響は算定できない。[市条例（2024年10月8日施行）]({SOURCES['definition']})
2. **居住要件は分析の成立条件。** docs/assumptions.mdは課題の仮定として主たる住居要件を無視すると記すが、元の課題文自体は未収録。市は主たる住居を要件とし、複数物件の短期運営を認めていないと説明している。この15戸モデルは課題上の例外を置いた収益シミュレーションとして扱い、実行可能性は確認できていない。[市の運営条件]({SOURCES['city']})
3. **供給上限の不一致。** 元コードは比較対象5〜9件でも最低1戸を買えるため、10%以下という説明と食い違う。今回の購入案では{len(violations)}区分が違反。上限の厳格化は別案で検証し、既存コードと結果は保存した。
4. **地域価格の粒度。** 同じ東西・種別・寝室数なら同じ購入価格。地域の利回り差の多くは売上差から生まれる。GVRの東西×3種別の6価格はPDFの掲載値と照合したが、寝室倍率0.7/0.85/1.15/1.5はプロジェクト独自仮定である。戸建て・タウンハウスは寝室数で価格調整していない。[GVR資料、PDFの3〜4ページ]({SOURCES['gvr']})
5. **推定値の独立性。** 宿泊単価・稼働・売上が同じ推定モデルに由来するなら、それらの相関は独立した需要検証にならない。レビューゼロ等の物件を外す設計は収益を上方に偏らせる可能性がある。ノートの「World Cup価格」という説明も、実際の価格対象日・推定売上の算出方法を確認するまでは仮説とする。
6. **2027年予測は未構築。** 2026年6月時点の過去推定売上と2026年10月の購入価格を組み合わせている。時点の不一致を明記し、2027年の成長率やイベント効果を自動的に付与しない。

## 9. 発表で使う結論と次の分析

発表の主張は「現在の価格モデルでは小型コンドが優位。ただし、推定利回り約4%は運営手数料・比較件数の設定で変わる。単一の購入案より、前提変更後の収益と残る候補を示す」とする。

- 1枚目：売上→変動費→固定費→営業利益の表。収益指標を定義する。
- 2枚目：最低比較件数5/10/20/30で構成と利回りが変わる表。高利回り候補のデータ量を示す。
- 3枚目：3%と15.5%の手数料、売上20%減、修繕費を組み合わせたケース比較。
- 4枚目：地域集中と購入可能性の条件。実際の投資提案と課題上の仮定を明示する。

次の実データ作業は、元スナップショットを復元し、①30泊未満と90泊未満を比較、②欠損寝室を独立区分として再集計、③非稼働を含む／除く収益差を検証、④対象候補の実売価格・管理組合条件を補完すること。時系列はレビュー月次を同じ月同士で比較し、観測途中の2026年と2025年通年を直接比較しない。レビュー件数は宿泊需要の代理指標で、宿泊数そのものではない。カレンダーの予約不可はホストによるブロックを含む。

## 再現方法・出力

`python3 scripts/deep_analysis.py`。追加パッケージ不要。元CSVとsrc/config.pyを読み、analsis/deep_analysis/にのみ出力する。変更した仮定を反映するには元のrun.pyで集計を再生成してから実行する。既存集計と現在のconfigが一致しないと監査で検出される。

audit.csvに再計算と制約検証、segment_diagnostics.csvに損益分岐売上・4%利回りを満たす購入価格上限、price_revenue_grid.csvに価格×売上×手数料の60ケース、その他CSVに購入案と感度結果を保存。manifest.jsonには入力ファイルのSHA-256を記録。市場価格・法制度・手数料の外部参照は2026年11月12日に確認。将来の公式ページ更新はこのレポートへ自動反映されない。

AI支援：コード作成、集計監査、ケース計算、日本語の解釈に使用。数値は保存済み集計表から独立再計算し照合。元データおよび課題原文の検証は未実施。
'''
    (OUT / "report_ja.md").write_text(report,encoding="utf-8")
    inputs=list(C.TABLES.glob("*.csv"))+[ROOT/"src/config.py",C.GVR_FILE,C.OUTPUTS/"key_numbers.json",Path(__file__).resolve()]
    manifest={"analysis_date":"2026-11-12","method":"aggregate audit and deterministic scenarios; yield-first greedy selection",
              "sources":SOURCES,"inputs":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
              "checks":checks,"limitations":["raw data absent","no forecast probabilities","no global optimisation","principal residence requirement relaxed only as project assumption"]}
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"baseline":base,"fee15_5":b15,"strict_n20":n20,"checks":len(checks),
                      "failed_checks":[c for c in checks if c["status"]=="FAIL"],"report":str(OUT/"report_ja.md")},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
