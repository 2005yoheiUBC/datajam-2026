"""Generate the team reports and presentation content from current/results.json."""
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'analsis';OUT=BASE/'current'
sys.path.insert(0,str(ROOT))
from src.analysis import C,read_csv,price_segments,underwrite

def money(v):return f'${v:,.0f}'
def percent(v):return f'{v:.2%}'
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(v) for v in r)+' |' for r in rows])

def main():
 d=json.loads((OUT/'results.json').read_text());b=d['performance'];h=d['recommendation'];t=d['tables'];r=d['raw_validation'];cases={x['scenario']:x for x in t['performance_scenarios']}
 if not r:raise SystemExit('Run raw validation once before preparing presentation materials.')
 allocation=t['selection_objective_comparison'][0];concentration=t['concentration_sensitivity'][-1];sample=t['sample_size_sensitivity'][0]
 before=sum(x['contribution_before_three_costs'] for x in h);variable=b['revenue']*(C.PLATFORM_FEE+C.MANAGEMENT_FEE+C.CLEANING_AND_SUPPLIES)
 decisions=[
 ['Pricing','Use neighbourhood assessed values instead of two-region GVR benchmarks.','More local price variation; both are acquisition proxies. Same matched listing universe in both cases.',f"GVR: {t['pricing_method_comparison'][0]['units']} units, {percent(t['pricing_method_comparison'][0]['yield_on_deployed'])}; assessments: {b['units']} units, {percent(b['yield_on_deployed'])}.",'pricing_method_comparison.csv'],
 ['Sample size','Require at least 20 comparables per segment.','Avoid choosing segments supported by only a handful of listings; test 5/10/20/30, not a claim of statistical sufficiency.',f"At 5: {sample['units']} units and {money(sample['noi'])} income. At 20: {b['units']} units and {money(b['noi'])}.",'sample_size_sensitivity.csv'],
 ['Concentration','Limit one neighbourhood to 40% of the full budget.','Accept a measured income cost to limit a single-neighbourhood exposure. Shared citywide and condo risks remain.',f"No cap: {concentration['units']} units, {money(concentration['noi'])}, largest exposure {percent(concentration['max_hood_budget_share'])} of budget. At 40%: {b['units']} units, {money(b['noi'])}, {percent(b['max_hood_budget_share'])} largest exposure.",'concentration_sensitivity.csv']]
 allocationtable=table(['Neighbourhood','Condo bedrooms','Units','Comparables','Cash deployed','Modelled annual income'],[[x['neighbourhood_cleansed'],x['bedrooms_grp'],x['units'],x['comparables'],money(x['cash_total']),money(x['modelled_operating_income'])] for x in h])
 scenario_table=table(['Case, same selected holdings','Annual operating income','Return on deployed cash'],[[x['scenario'],money(x['noi']),percent(x['yield_on_deployed'])] for x in t['performance_scenarios']])
 report=f'''# Presentation recommendation and analysis

Updated November 13, 2026. CAD throughout. **This report supersedes the November 12 allocation.**

## Decision

For the investment-committee pitch, recommend **{b['units']} condos in {b['neighbourhoods']} Vancouver neighbourhoods**, deploying **{money(b['cash_deployed'])}** and leaving **{money(b['idle_cash'])}** unallocated. Modelled 2027 operating income is **{money(b['noi'])}**, equivalent to **{percent(b['yield_on_deployed'])} on deployed cash**, or **{percent(b['yield_on_budget'])} on the full mandate**. This is a historical-revenue run-rate scenario, not a calibrated 2027 forecast or guaranteed return.

{allocationtable}

All units are condos. The two largest neighbourhood allocations represent {percent(sum(sorted([x['cash_total'] for x in h],reverse=True)[:2])/b['cash_deployed'])} of deployed cash. Geographical limits do not diversify citywide rules or property-type risk. Unallocated cash is a buffer to size explicitly, not a demonstrated adequate reserve.

## Preserve the requested fee-excluded allocation study

The user requested ignoring platform, management, and cleaning/supplies costs when selecting locations. That analysis is retained in [current/fee_excluded_holdings.csv](current/fee_excluded_holdings.csv): **{allocation['units']} units**, with 7 one-bedroom units in Downtown Eastside, 5 one-bedroom units in Downtown, and 2 two-bedroom units in West End. It deploys {money(allocation['cash_deployed'])}.

Evaluating those same holdings with modelled operating costs gives {money(allocation['noi'])} income and {percent(allocation['yield_on_deployed'])} return. Cost-aware selection instead uses four two-bedroom units in Downtown, producing {money(b['noi']-allocation['noi'])} more annual modelled income while committing {money(b['cash_deployed']-allocation['cash_deployed'])} more capital. The final pitch uses this cost-aware alternative because its mandate is investment value. The requested allocation study remains a separately labelled comparison.

## Calculation and meaning of the return

```text
Total cash = purchase price × 1.04 + furnishing of 25,000 per unit
Operating income = estimated annual revenue × (1 − 15.5% − 20% − 8%) − fixed costs
Fixed costs = purchase price × 0.3% + strata + insurance + licence/registration
Return on deployed cash = operating income / total cash
```

Strata is 500/month for condos, insurance 2,000/year, and licence/registration 1,500/year per unit. These, management at 20%, cleaning/supplies at 8%, closing at 4%, and furnishing at 25,000 are modelling assumptions, not property quotes. Platform 15.5% is a single-fee scenario supported by [Airbnb's official explanation](https://www.airbnb.com/help/article/1857), checked November 13, 2026. The historical revenue input is held fixed when changing fees; repricing and guest-demand responses are not estimated.

| Annual bridge | CAD |
| --- | ---: |
| Sum of selected segment-median revenues | {money(b['revenue'])} |
| Modelled variable operating costs, 43.5% | ({money(variable)}) |
| Modelled fixed operating costs | ({money(b['fixed_costs'])}) |
| Operating income before income tax/capital repairs | {money(b['noi'])} |
| After an additional assumed 5% of revenue for repairs reserve | {money(cases['repairs_reserve5']['noi'])} |

No debt, income tax, resale gain/loss, or major capital expenditure is included. A repairs reserve is shown separately. The return is not IRR. Summed segment medians are neither an estimated portfolio expectation nor its statistical median.

## Selection and alternatives

Active entire-home listings are grouped by neighbourhood, property bucket, and bedrooms. Eligible segments have at least {C.MIN_COMPARABLES} listing comparables. Rank by modelled operating income / purchase-plus-setup cash, then buy integer units while respecting the 10 million budget, 40% of budget per neighbourhood, and floor(10% of segment comparables) capacity. Skip nonpositive operating income. This is yield-first greedy selection, not proven global optimisation or an exhaustive maximisation of annual income. The limits and minimum sample are team assumptions, not brief requirements.

The price split for few-high-value versus many-modest uses the median price across eligible buyable **segments** ({money(d['property_price_median_cutoff'])}), not a transaction-weighted market median. Under identical selection rules:

{table(['Alternative','Units','Cash deployed','Annual operating income','Return on full budget'],[[x['scenario'],x['units'],money(x['cash_deployed']),money(x['noi']),percent(x['yield_on_budget'])] for x in t['few_vs_many']])}

Uninvested cash earns zero in this comparison. Property-count-specific overhead has not been estimated. The low-cost portfolio is more efficient under the model; this is not a causal statement about smaller properties generally.

## 2027 scenarios and validation

Properties are assumed operational January 1, 2027 for a full year. Base revenue equals historical estimated revenue, with no assumed trend or World Cup uplift. Revenue −20% / +10% gives a conditional operating-income range of {money(cases['revenue_minus20']['noi'])} to {money(cases['revenue_plus10']['noi'])}. This is a chosen planning range, not a prediction interval. Two months offline assumes uniformly distributed revenue; seasonal closure could be worse.

{scenario_table}

p25/p75 are cross-sectional differences between listings, simultaneously applied to holdings; they are not future confidence bounds. The p25 case is near break-even, so the portfolio is not robust to every stress. Revenue −20% plus an extra 5% repairs reserve gives {money(cases['revenue_minus20_reserve5']['noi'])}. Revenue shocks keep holdings fixed. Purchase-price shocks reselect within budget; +20% purchase prices gives {t['purchase_price_sensitivity'][2]['units']} units and {percent(t['purchase_price_sensitivity'][2]['yield_on_deployed'])}. Condo bedroom-price multipliers are also tested ±10%.

Raw listings were downloaded from the public Inside Airbnb snapshot URL and rebuilt: {r['raw_rows']:,} listings, {r['clean_rows']:,} after price/stay filters, {r['active_entire_home_rows']:,} active entire-home listings, {r['segments']} segments. There are {r['future_review_rows']} review dates after the nominal snapshot date; these are excluded from active status. The file's scrape dates are mixed: {json.dumps(r['last_scraped_counts'])}. Later scrape observations can still influence prices and trailing estimates, so this is not a reconstructed clean June 15 information set.

External property prices were rebuilt from public tax and parcel data: 229,095 matched rows and 191,840 selected residential-proxy rows. Tax coordinate joins, parcel centroids, zoning, legal type and value bounds are proxies, not verified acquisition opportunities. Polygon holes are respected. Assessment values are not transaction prices. Townhouses use strata/condo assessment proxies; they are not selected in this recommendation. See [property-value provenance](../data/external/property_values_provenance.json).

Missing bedrooms remain imputed to one in the base pipeline, but excluding them is tested. Including inactive listings reduces the selected strategy's modelled income; active-only selection may be optimistic. Outlier filters and the 30-versus-90-night threshold are tested, with all results in [current/raw_filter_sensitivity.csv](current/raw_filter_sensitivity.csv). A listing's minimum stay classifies its advertised policy, not every realised booking.

## Three decisions to defend

{table(['Decision','What','Why','Measured effect','Evidence'],decisions)}

## Risks and actions

1. Acquisition-price proxy: obtain property-level price, condition and strata checks, and rerun +10%/+20% cases before offers.
2. Demand and estimated revenue: track actual booked revenue and costs against these assumptions monthly; investigate a sustained shortfall rather than treating reviews as bookings.
3. Concentration: keep the explicit cap and report the income sacrificed; recognise common condo/city shocks remain.
4. Data dates and sample selection: disclose mixed scrape dates, exclude known post-snapshot reviews, and use an earlier independent snapshot for a future out-of-time validation. That validation is not yet performed.
5. Operational permissions: the brief explicitly waives principal-residence requirements for the simulation. Licences, registration, safety and strata approvals still need checking. Do not pitch a solution to the waived restriction.

## Reproduction and traceability

From the repository root, `python3 run.py` recreates current numbers using committed, privacy-safe aggregates and the standard library. For the raw route, create a virtual environment, install requirements, run `bash scripts/download_data.sh`, optionally rebuild assessed prices using `python scripts/build_property_values.py`, then run `python run.py --source raw`. Both routes were checked. To refresh this report and the presentation content, run `python3 scripts/prepare_materials.py` after the analysis.

Source of truth: [current/results.json](current/results.json). Exact holdings, each experiment, and raw-source hashes are adjacent. Calculation code: [src/analysis.py](../src/analysis.py). Tests: [scripts/test_deep_analysis.py](../scripts/test_deep_analysis.py). Sources: Inside Airbnb (snapshot labelled June 15, 2026, CC BY 4.0), City of Vancouver property tax and parcel datasets, GVR October 2026 for the controlled pricing counterfactual, and the local business-case PDF.

AI assistance: code, analysis and presentation drafting. Checked by public raw-data reconstruction, assessed-value reconstruction, independent arithmetic, capacity/budget tests, and slide-data reconciliation. The team must understand and defend assumptions. No individual hosts or licence identifiers appear in these outputs.
'''
 (BASE/'recommendation_en.md').write_text(report)
 ja=f'''# 最新の推奨と計算の説明

2026年11月13日更新。前の14戸案・8戸案とは、価格データ・日付処理・費用条件が異なります。

## 発表の推奨

**13戸：Downtown Eastsideの1寝室7戸、Downtownの2寝室4戸、West Endの2寝室2戸。** 必要資金は{money(b['cash_deployed'])}、残額は{money(b['idle_cash'])}。運営費を入れた年間営業利益は{money(b['noi'])}、投入資金への比率は{percent(b['yield_on_deployed'])}です。修繕積立を売上の5%追加すると{money(cases['repairs_reserve5']['noi'])}となります。

## 費用を除いた比較も残しています

指定の3費用を除いて選ぶと14戸（Downtown Eastsideの1寝室7戸、Downtownの1寝室5戸、West Endの2寝室2戸）。この14戸に運営費を戻すと営業利益は{money(allocation['noi'])}。費用を考慮して選んだ13戸では{money(b['noi']-allocation['noi'])}多く、必要資金も{money(b['cash_deployed']-allocation['cash_deployed'])}増えます。発表では投資判断として13戸を推奨し、14戸は別条件の比較にします。

## 計算式

```text
1戸の必要資金 = 購入価格 × 1.04 + 家具代25,000
1戸の固定費 = 購入価格 × 0.003 + 管理組合費6,000 + 保険2,000 + 登録等1,500
1戸の営業利益 = 推定売上 × (1 − 0.155 − 0.20 − 0.08) − 固定費
利回り = 営業利益 ÷ 必要資金
```

管理組合費と管理会社の運営代行費は別です。税金（所得税）、大規模修繕、借入、売却益を含まないので、投資全体のIRRではありません。

## どの数字を使ったか

{allocationtable}

売上はInside Airbnbの推定値の区分中央値、価格は市の住宅評価額を地域別に集計して寝室倍率を掛けたものです。評価額と実際の購入価格は同じではありません。

## 比較対象とは

同じ地域・種別・寝室数に属する、過去1年にレビューがある住戸全体の掲載数です。購入できる売出物件の数ではありません。日付の処理を修正したため、Downtown Eastsideの1寝室は以前の152件から146件になっています。最低20件は分析上の仮定です。

## 上限40%の根拠

[src/portfolio.py](../src/portfolio.py) と [決定ログ](../docs/decision_log.md) にあるチーム独自ルールで、課題や法律の必須条件ではありません。総予算1,000万の40%、つまり400万を1地域の上限とします。同一区分は比較対象数の10%以下、端数切り捨て。高利回り順の貪欲法であり、全体最適の証明はしていません。

## 2027年の見通し

過去の推定売上を2027年にも継続すると置くシナリオです。売上20%減では{money(cases['revenue_minus20']['noi'])}、10%増では{money(cases['revenue_plus10']['noi'])}。確率的な予測区間ではありません。p25は物件間の売上差で、将来の不況予測ではありません。

原データには nominal 6月15日より後のレビュー{r['future_review_rows']}件と、6月・7月に混在する取得日があります。後日のレビューをactive判定から除き、影響を測定しました。ただし価格や過去推定売上を完全な6月15日時点へ戻せるわけではありません。

英語の詳細：[recommendation_en.md](recommendation_en.md)。数値：[current/results.json](current/results.json)。AI支援で整理し、原データの再集計、別計算、制約テストで照合しました。
'''
 (BASE/'reasoning_ja.md').write_text(ja)
 decision_doc='# Decision log\n\nThree presentation decisions, with controlled comparisons. All returns below restore modelled operating costs.\n\n'+table(['Decision','What','Why','What changed','Evidence'],decisions)+'\n\nSources: [current results](../analsis/current/results.json). The 40% cap and minimum 20 comparables are team choices, not brief requirements.\n'
 (ROOT/'docs/decision_log.md').write_text(decision_doc)
 qa=f'''# Presentation preparation and Q&A

## Seven-minute pitch

Use six main slides and stop at 6:30 to leave a 30-second buffer. The brief allows 3 minutes of Q&A. Final-round timing is 10 minutes plus 5 minutes of Q&A.

| Slide | Message | Target time |
| --- | --- | --- |
| 1 | Recommend {b['units']} units, show capital and operating income | 0:45 |
| 2 | Explain data coverage, date anomaly and selection | 0:45 |
| 3 | Show allocation, pricing and three constraints | 1:30 |
| 4 | Compare few expensive versus many modest properties | 1:00 |
| 5 | Explain 2027 run-rate and downside cases | 1:30 |
| 6 | Give risks, first actions and AI disclosure | 1:00 |

## Q&A answers

**Why not the earlier 14-unit recommendation?** It excluded three costs in selection. Rebuilding date handling and using local prices changed the inputs. We retain the requested 14-unit comparison; including modelled costs changes Downtown from five one-bedroom to four two-bedroom units and produces {money(b['noi']-allocation['noi'])} more income for {money(b['cash_deployed']-allocation['cash_deployed'])} more capital.

**Why this return metric?** Modelled annual operating income / cash deployed captures operating costs and acquisition/furnishing cash. We also show income / full budget so idle cash is visible. Neither is IRR.

**Is this an optimal portfolio?** No. It is a feasible yield-first greedy selection. We tested alternatives and constraints but did not prove global optimality or maximise income across every integer combination.

**What is a comparable?** An active entire-home Airbnb listing in the same neighbourhood/type/bedroom segment, not an available-for-sale property or a fully matched physical comparable.

**Where does 40% come from?** A team concentration assumption. Removing it raises income from {money(b['noi'])} to {money(concentration['noi'])} but puts {percent(concentration['max_hood_budget_share'])} of the budget into one neighbourhood. Citywide risks remain even with the cap.

**Why minimum 20 listings?** Screening against tiny groups; we compared 5, 10, 20 and 30. It is not a statistical guarantee. West End has only 23 comparables, so that estimate needs particular scrutiny.

**Why trust assessed values?** They are consistent public local proxies. We do not equate consistency with unbiased market prices. We rebuilt the source join, compared broad benchmarks, and tested purchase prices +10/+20%. Validate property-specific prices before offers.

**What does 2027 mean?** A full operational year starting January 1, with historical estimated revenue carried forward unchanged. −20/+10% are chosen planning scenarios, not fitted probabilities or a forecast interval.

**What is the downside?** Revenue −20% gives {money(cases['revenue_minus20']['noi'])}; adding a repairs reserve of 5% of stressed revenue gives {money(cases['revenue_minus20_reserve5']['noi'])}. The listing p25 case is near break-even. There is no guarantee of positive income.

**Are repairs and tax included?** Property tax is included. Repairs reserve is a separate scenario. Income tax, major capital works, debt and resale are excluded. The base income number is before these items.

**Why exclude future reviews?** The downloaded file is labelled June 15 but includes later scrape dates and 132 later last-review dates. We exclude known later reviews from active status and disclose that other fields may also contain later information.

**Can DDD own STR investment units?** For this simulation the brief explicitly waives principal-residence requirements. Other operating permissions remain relevant. We apply the simulation rule rather than claiming a real-world exemption.

**Are unavailable calendar nights bookings?** No, booked and blocked nights cannot be distinguished. We do not use unavailability as occupancy. Reviews and Inside Airbnb estimates are not booking receipts.

**What did AI do?** It helped with code, scenarios and slides. We downloaded public inputs, rebuilt aggregations and price joins, independently checked arithmetic and constraints, and reviewed slide numbers. Each presenter must explain the logic.

## Rehearsal

1. Assign a speaker and a backup for each slide. Use speaker notes as prompts, not text to read aloud.
2. Give a timed 6:30 run. Cut detail from the main slides before cutting important assumptions.
3. Have a teammate challenge three numbers and trace each to current/results.json, its CSV and src/analysis.py.
4. Run a strict three-minute Q&A with 20–30 second answers. Keep decisions and calculation examples in the appendix.
5. Rehearse the final action: validate actual acquisition opportunities, obtain operating/strata approvals under the case rules, price repairs, and track monthly revenue/cost variance.

## Submission checklist

- Export the PPTX and open it locally in PowerPoint or Slides before presenting; generated previews do not establish target-application behaviour.
- Show Inside Airbnb attribution exactly as required by the brief.
- Make material AI use and the checks visible in the pitch.
- Explain three decisions and their measured effects; keep the compiled log in the appendix.
- Do not show hosts, listing URLs or licence numbers.
- Run the README commands in a fresh checkout and keep one authoritative set of figures.
'''
 (BASE/'presentation/preparation_and_qa.md').write_text(qa)
 (ROOT/'docs/qa_notes.md').write_text('# Q&A notes\n\nThe current, checked Q&A and rehearsal guide is [analsis/presentation/preparation_and_qa.md](../analsis/presentation/preparation_and_qa.md). Older unverified statements about equal cost effects and ranking agreement have been removed.\n')
 (ROOT/'docs/assumptions.md').write_text(f'''# Current assumptions

Updated November 13, 2026. Authoritative values are in src/config.py and analsis/current/results.json.

| Assumption | Value / status |
| --- | --- |
| Revenue | Inside Airbnb trailing-year estimates, carried forward unchanged for 2027; not booking receipts |
| Acquisition price | Neighbourhood median assessed value × assumed condo bedroom multiplier; not market-price quotes |
| Condo bedroom factors | Studio .7, 1-bed .85, 2-bed 1.15, 3+ 1.5; tested ±10% |
| Platform | 15.5% scenario; Airbnb help/article/1857, checked November 13, 2026 |
| Management / cleaning | 20% / 8% of revenue, project assumptions |
| Property tax | 0.3% of purchase price, project assumption |
| Condo strata / insurance / licence | 6,000 / 2,000 / 1,500 annually per unit, project assumptions |
| Closing / furniture | 4% of purchase price / 25,000 per unit |
| Financing / income tax / resale | No debt; income tax and resale changes excluded |
| Repairs | Separate 5%-of-revenue reserve scenario; major works excluded |
| Selection constraints | At least 20 segment comparables, floor(10% of supply), 40% of total budget per neighbourhood; team choices |
| Simulation rule | Principal residence requirement explicitly waived by business brief; other permissions remain |
| Missing bedrooms | Impute one; alternative excluding missing tested |
| Dates | Mixed scrape dates; last-review dates after nominal snapshot excluded from active flag; residual date uncertainty remains |

External data: public City of Vancouver property tax and parcel datasets. Source reconstruction hashes are in data/external/property_values_provenance.json. GVR October 2026 is used only as a controlled counterfactual.

AI assistance: code, analytical comparisons and presentation drafting. Important outputs were checked through raw reconstruction, source-join reconstruction, independent arithmetic, budget/capacity tests and slide review.
''')
 (BASE/'presentation/decision_log.json').write_text(json.dumps(decisions,indent=2))
 print('Updated English/Japanese reports, decision log, assumptions and presentation preparation guide.')

if __name__=='__main__':main()
