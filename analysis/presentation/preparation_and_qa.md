# Presentation preparation and Q&A

## Seven-minute pitch

Use six main slides and stop at 6:30 to leave a 30-second buffer. The brief allows 3 minutes of Q&A. Final-round timing is 10 minutes plus 5 minutes of Q&A.

| Slide | Message | Target time |
| --- | --- | --- |
| 1 | Recommend 13 units, show capital and operating income | 0:45 |
| 2 | Explain data coverage, date anomaly and selection | 0:45 |
| 3 | Show allocation, pricing and three constraints | 1:30 |
| 4 | Compare few expensive versus many modest properties | 1:00 |
| 5 | Explain 2027 run-rate and downside cases | 1:30 |
| 6 | Give risks, first actions and AI disclosure | 1:00 |

## Q&A answers

**Why not the earlier 14-unit recommendation?** It excluded three costs in selection. Rebuilding date handling and using local prices changed the inputs. We retain the requested 14-unit comparison; including modelled costs changes Downtown from five one-bedroom to four two-bedroom units and produces $7,894 more income for $250,985 more capital.

**Why this return metric?** Modelled annual operating income / cash deployed captures operating costs and acquisition/furnishing cash. We also show income / full budget so idle cash is visible. Neither is IRR.

**Is this an optimal portfolio?** No. It is a feasible yield-first greedy selection. We tested alternatives and constraints but did not prove global optimality or maximise income across every integer combination.

**What is a comparable?** An active entire-home Airbnb listing in the same neighbourhood/type/bedroom segment, not an available-for-sale property or a fully matched physical comparable.

**Where does 40% come from?** A team concentration assumption. Removing it raises income from $246,987 to $280,714 but puts 79.92% of the budget into one neighbourhood. Citywide risks remain even with the cap.

**Why minimum 20 listings?** Screening against tiny groups; we compared 5, 10, 20 and 30. It is not a statistical guarantee. West End has only 23 comparables, so that estimate needs particular scrutiny.

**Why trust assessed values?** They are consistent public local proxies. We do not equate consistency with unbiased market prices. We rebuilt the source join, compared broad benchmarks, and tested purchase prices +10/+20%. Validate property-specific prices before offers.

**What does 2027 mean?** A full operational year starting January 1, with historical estimated revenue carried forward unchanged. −20/+10% are chosen planning scenarios, not fitted probabilities or a forecast interval.

**What is the downside?** Revenue −20% gives $167,517; adding a repairs reserve of 5% of stressed revenue gives $139,386. The listing p25 case is near break-even. There is no guarantee of positive income.

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
