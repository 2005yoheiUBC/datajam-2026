import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const ROOT=path.resolve(HERE,'../..');
const SKILL='/Users/yukiko/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
const RUNTIME='/Users/yukiko/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=process.env.RUNTIME_NODE_MODULES||path.join(RUNTIME,'node/node_modules');
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const d=JSON.parse(await fs.readFile(path.join(ROOT,'analysis/current/results.json'),'utf8'));
const b=d.performance,h=d.recommendation,t=d.tables,r=d.raw_validation;
const cases=Object.fromEntries(t.performance_scenarios.map(x=>[x.scenario,x]));
const money=v=>'$'+Math.round(v).toLocaleString('en-CA');
const m=v=>'$'+(v/1e6).toFixed(2)+'m';
const k=v=>(v<0?'−$':'$')+Math.round(Math.abs(v)/1000)+'k';
const pct=v=>(v*100).toFixed(2)+'%';
const FONT='Arial',INK='#162B40',BLUE='#176B88',ORANGE='#C77538',MUTED='#536471';
const pres=Presentation.create({slideSize:{width:1280,height:720}});
const notes=[];
const source='Sources: analysis/current/results.json and corresponding CSVs; src/analysis.py; Business Case (updated) - DataJam 2026.pdf. Public pricing: https://opendata.vancouver.ca/explore/dataset/property-tax-report/ and property-parcel-polygons. Platform fee: https://www.airbnb.com/help/article/1857, checked 2026-11-13.';
function text(s,content,x,y,w,ht,size=24,bold=false,color=INK){
 const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:ht},fill:'none',line:{fill:'none',width:0}});
 q.text=content;q.text.style={fontSize:size,typeface:FONT,bold,color};q.text.insets=0;return q;
}
function slide(title,note,appendix=false){
 const s=pres.slides.add();s.background.fill='#FFFFFF';
 text(s,title,64,42,1152,110,44,true);
 text(s,`${appendix?'Appendix':'DDD investment committee'}    ${pres.slides.items.length}`,64,680,1000,20,15,false,MUTED);
 s.speakerNotes.text=note+'\n\n'+source;
 notes.push({slide:pres.slides.items.length,title,notes:note});return s;
}
function table(s,headers,rows,{x=64,y=170,w=1152,ht=360,widths=null,size=24}={}){
 const vals=[headers,...rows];const tab=s.tables.add({rows:vals.length,columns:headers.length,left:x,top:y,width:w,height:ht,values:vals,...(widths?{columnWidths:widths}:{})});
 tab.borders.assign({fill:'#D7E0E5',style:'solid',width:.6});
 tab.cells.block({row:0,column:0,rowCount:vals.length,columnCount:headers.length}).assign({fill:'#FFFFFF',textStyle:{typeface:FONT,fontSize:size,color:INK},margins:{left:12,right:12,top:10,bottom:10}});
 tab.cells.block({row:0,column:0,rowCount:1,columnCount:headers.length}).assign({fill:INK,textStyle:{typeface:FONT,fontSize:size,color:'#FFFFFF',bold:true}});
 return tab;
}
function chart(s,cats,values,{x=64,y=180,w=800,ht=390,title='',format='0.0%',color=BLUE}={}){
 values=values.map(v=>Number(v.toPrecision(12))); // Portable Excel precision; exact calculations stay in results.json.
 const ch=s.charts.add('bar',{position:{left:x,top:y,width:w,height:ht},title,titleTextStyle:{fontSize:22,fill:INK},categories:cats,series:[{name:title||'Modelled return',values,fill:color}],hasLegend:false,
 barOptions:{direction:'bar',grouping:'clustered',gapWidth:85},
 xAxis:{textStyle:{fontSize:21,fill:INK},majorGridlines:null},
 yAxis:{numberFormatCode:format,textStyle:{fontSize:20,fill:MUTED},majorGridlines:{fill:'#D7E0E5',width:.5,style:'solid'}},
 dataLabels:{showValue:true,position:'outEnd',numberFormatCode:format,textStyle:{fontSize:23,fill:INK,bold:true}},chartFill:'none',plotAreaFill:'none'});
 applyPresentationChartFont(ch,{fontFamily:FONT});return ch;
}
let s;
s=slide(`Recommend ${b.units} condos across three Vancouver areas`,
`TARGET 0:45. We recommend seven one-bedroom condos in Downtown Eastside, four two-bedroom condos in Downtown, and two two-bedroom condos in West End. The plan deploys ${m(b.cash_deployed)} and leaves ${k(b.idle_cash)} unallocated. At historical estimated revenue carried forward into a full 2027 operating year, the model produces ${k(b.noi)} of operating income, a ${pct(b.yield_on_deployed)} return on deployed cash. This is a scenario, not a forecast guarantee. It includes modelled platform, management and cleaning costs but excludes income tax and major capital repairs. We will explain both the allocation and what could change it.`);
// Recommendation is the opening slide, rather than a separate decorative cover.
table(s,['Location','Condo type','Units','Capital'],h.map(x=>[x.neighbourhood_cleansed,x.bedrooms_grp+' bedroom',String(x.units),m(x.cash_total)]),{y:206,w:780,ht:270,widths:[310,180,100,190],size:24});
text(s,k(b.noi),900,210,300,85,64,true,BLUE);
text(s,'Modelled 2027 operating income',900,300,300,85,25);
text(s,pct(b.yield_on_deployed),900,409,300,70,52,true,BLUE);
text(s,'on '+m(b.cash_deployed)+' deployed',900,481,300,50,23);
text(s,`Planning range: ${k(cases.revenue_minus20.noi)} to ${k(cases.revenue_plus10.noi)} income at revenue −20% / +10%`,64,556,1152,46,26,true);
text(s,'Full-year historical run-rate scenario. Before income tax and capital repairs. No debt.',64,615,1152,40,21,false,MUTED);

s=slide('Public data, with explicit limits',
`TARGET 0:45. We use the supplied Inside Airbnb Vancouver file, labelled June 15, 2026, and public Vancouver tax and parcel data. We rebuilt both sources. Of 6,509 listings, 4,447 pass the price and minimum-stay filters, and 3,137 active entire-home observations enter segment analysis. Revenue and occupancy are estimates, not receipts. We found mixed June and July scrape dates and 132 review dates after the nominal snapshot. We exclude those reviews from active status and disclose residual date uncertainty. Purchase prices are neighbourhood assessed-value proxies adjusted by bedroom assumptions. They require validation against actual acquisition opportunities.`);
table(s,['Listing population','Count'],[['Raw listings',r.raw_rows.toLocaleString()],['After price and stay filters',r.clean_rows.toLocaleString()],['Active entire-home observations',r.active_entire_home_rows.toLocaleString()]],{y:190,w:640,ht:278,widths:[500,140]});
text(s,'What the data can support',760,190,450,42,29,true);
text(s,'Estimated revenue by segment\nLocal assessed-value price proxies\nConditional investment comparisons',760,250,450,155,25);
text(s,'What it cannot establish',760,425,450,42,29,true);
text(s,'Actual bookings or available purchases\nAn unbiased 2027 forecast',760,485,450,90,25);
text(s,'132 post-snapshot review dates excluded from active status. Mixed scrape dates remain a limitation.',64,540,640,85,22,false,MUTED);
text(s,'Data: Inside Airbnb, Vancouver, 15 June 2026, CC BY 4.0.',64,638,1152,30,19,false,MUTED);

s=slide('Returns and constraints determine the mix',
`TARGET 1:30. Our metric divides modelled annual operating income by purchase, closing and furnishing cash. We rank neighbourhood/type/bedroom segments, then buy whole units within the budget. At least 20 comparables are required, no segment can exceed ten percent of its listing sample, and a neighbourhood cannot consume more than forty percent of the full budget. These are team assumptions, not requirements from the brief. Downtown Eastside reaches its regional limit at seven units. Downtown adds four two-bedroom units. West End adds two, its segment supply limit. We tested the threshold and cap instead of asserting they are correct. Without the cap, annual income rises, but almost eighty percent of the budget enters one neighbourhood. This is a feasible greedy allocation, not a mathematical proof of the best possible portfolio.`);
chart(s,h.map(x=>`${x.neighbourhood_cleansed} / ${x.bedrooms_grp} bed`),h.map(x=>x.modelled_operating_income/x.cash_total),{w:835,ht:370,title:'Operating income / acquisition and setup cash'});
text(s,'Selection rules',950,185,270,42,29,true);
text(s,'20+ comparables\n\n40% of budget per area\n\n10% of segment supply',950,245,270,250,25);
text(s,'Sample sizes: '+h.map(x=>`${x.neighbourhood_cleansed} ${x.comparables}`).join(', '),64,580,1152,55,23);
text(s,'Team assumptions. Greedy selection; global optimality is not established.',64,632,1152,30,20,false,MUTED);

const alt=t.few_vs_many;
s=slide('Modest properties outperform the high-value alternative',
`TARGET 1:00. The brief asks us to compare a few expensive properties with many modest ones. We split buyable segments at their median assumed purchase price, then apply the same budget, sample and concentration rules. The modest-property strategy selects ${alt[2].units} units and produces ${k(alt[2].noi)}, versus ${alt[1].units} high-value properties and ${k(alt[1].noi)}. We compare income against the full ten-million mandate, so unused cash does not artificially improve the result. Unused cash earns zero here. This comparison supports the modest-property choice under our price and cost assumptions. It does not establish a general causal relationship between smaller properties and better returns.`);
chart(s,[`${alt[2].units} modest properties`,`${alt[1].units} high-value properties`],[alt[2].yield_on_budget,alt[1].yield_on_budget],{w:1152,ht:310,title:'Annual operating income / full CAD 10m budget'});
text(s,`Modest: ${m(alt[2].cash_deployed)} deployed, ${k(alt[2].noi)} income`,64,530,1152,42,27,true);
text(s,`High-value: ${m(alt[1].cash_deployed)} deployed, ${k(alt[1].noi)} income`,64,578,1152,42,27);
text(s,`Split at segment-median purchase price ${money(d.property_price_median_cutoff)}. Idle cash earns zero.`,64,632,1152,32,20,false,MUTED);

s=slide('2027 income depends on revenue and acquisition prices',
`TARGET 1:30. Our base assumes a full year of operations at historical estimated revenue. Revenue of ${k(b.revenue)} less modelled variable costs and fixed costs gives ${k(b.noi)} of operating income. We do not claim that historical listing estimates predict 2027. The planning range uses a revenue decrease of twenty percent and an increase of ten percent. Adding a repairs reserve reduces base income to ${k(cases.repairs_reserve5.noi)}. Combining twenty-percent lower revenue with that reserve leaves ${k(cases.revenue_minus20_reserve5.noi)}. The listing twenty-fifth percentile case is near break-even; it is a cross-sectional stress, not a forecast confidence bound. Acquisition-price shocks reselect the portfolio within the same budget. These cases tell us which assumptions to verify before committing capital, not the probability of success.`);
table(s,['Annual income bridge','CAD'],[['Estimated revenue',k(b.revenue)],['Variable costs, 43.5%',k(-b.revenue*.435)],['Fixed costs',k(-b.fixed_costs)],['Operating income',k(b.noi)],['After 5% repairs reserve',k(cases.repairs_reserve5.noi)]],{y:181,w:550,ht:350,widths:[390,160],size:23});
chart(s,['Revenue −20%','Base run-rate','Revenue +10%'],[cases.revenue_minus20.noi/1000,b.noi/1000,cases.revenue_plus10.noi/1000],{x:656,y:181,w:560,ht:350,title:'Operating income (CAD thousands)',format:'0'});
text(s,`Revenue −20% plus 5% repairs reserve: ${k(cases.revenue_minus20_reserve5.noi)} income`,64,558,1152,50,28,true,ORANGE);
text(s,'Chosen scenarios, not forecast probabilities. Income tax and major capital works excluded.',64,626,1152,42,20,false,MUTED);

s=slide('Validation before offers, monitoring after launch',
`TARGET 1:00. The largest practical uncertainty is whether assessed values represent properties we can actually buy. Before offers, obtain property-level prices, condition reports and strata approvals, then rerun the allocation. Validate costs with operators and size the repairs and working-capital reserve. Confirm licensing and registration under the simulation rules: the brief explicitly waives principal residence, but other rules remain. After launch, compare monthly booked revenue and costs with the plan and investigate persistent variance. Our data-date and active-listing assumptions remain limitations. AI assisted code, analysis and slide drafting. We checked important outputs by rebuilding public source data, independent arithmetic and selection constraints. Our recommendation is a shortlist to validate, not a claim that these specific units are already available.`);
table(s,['Risk','First action'],[['Assessed values differ from purchase prices','Verify available prices and condition; rerun +10% / +20% cases.'],['Estimated revenue and operating costs','Obtain operator quotes; size repairs and cash reserves.'],['Concentration and operational permissions','Check strata, licences and registration under case rules.'],['Performance differs from the scenario','Track monthly booked revenue and costs against the plan.']],{y:182,ht:355,widths:[430,722],size:24});
text(s,'AI assistance: code, analysis and slides. Checked by source rebuilds, independent arithmetic and constraint tests.',64,578,1152,76,23,false,MUTED);

s=slide('Three decisions with measured consequences',
`APPENDIX. Each decision records what, why and its measured effect. Pricing counterfactual holds the matched segment universe fixed. Minimum sample tests hold costs and caps fixed. Cap tests hold pricing, costs and minimum sample fixed. Sources: current/pricing_method_comparison.csv, sample_size_sensitivity.csv, concentration_sensitivity.csv.`,true);
const g=t.pricing_method_comparison[0],sm=t.sample_size_sensitivity[0],nc=t.concentration_sensitivity.at(-1);
table(s,['Decision','Reason','Measured effect'],[
 ['Neighbourhood assessment prices','Local price variation; retain acquisition-proxy caveat.',`GVR: ${g.units} units, ${pct(g.yield_on_deployed)}. Local: ${b.units} units, ${pct(b.yield_on_deployed)}.`],
 ['Minimum 20 comparables','Screen tiny samples; test 5, 10, 20 and 30.',`Minimum 5: ${sm.units} units, ${k(sm.noi)}. Minimum 20: ${b.units} units, ${k(b.noi)}.`],
 ['40% neighbourhood cap','Limit exposure while measuring sacrificed income.',`No cap: ${k(nc.noi)}, largest area ${pct(nc.max_hood_budget_share)}. Cap: ${k(b.noi)}, largest ${pct(b.max_hood_budget_share)}.`]
],{y:178,ht:405,widths:[270,385,497],size:24});
text(s,'All comparisons use modelled operating costs. These rules are team choices, not brief requirements.',64,619,1152,42,21,false,MUTED);

const ex=h[0];const exFixed=ex.purchase_price_each*.003+9500;const exVariable=ex.revenue_each*.435;
s=slide('One-unit calculation: Downtown Eastside',
`APPENDIX. One-bedroom purchase proxy is ${money(ex.purchase_price_each)}. Closing costs are four percent, plus furnishing of twenty-five thousand. Total setup cash is ${money(ex.cash_each)}. Revenue is the segment median ${money(ex.revenue_each)}, not verified receipts. Platform, management and cleaning assumptions total forty-three point five percent. Fixed costs include property tax, strata, insurance and licensing. All numbers are calculated before displayed rounding. Seven units cost ${money(ex.cash_total)}; an eighth would exceed four million.`,true);
table(s,['Item','Calculation','CAD per unit'],[['Purchase price','Assessed condo median × 0.85',money(ex.purchase_price_each)],['Acquisition and setup','Price × 1.04 + 25,000',money(ex.cash_each)],['Estimated annual revenue','Median of 146 active segment listings',money(ex.revenue_each)],['Variable operating costs','Revenue × 43.5%',money(exVariable)],['Fixed operating costs','Tax + strata + insurance + registration',money(exFixed)],['Operating income','Revenue − variable costs − fixed costs',money(ex.revenue_each-exVariable-exFixed)]],{y:172,ht:402,widths:[285,620,247],size:23});
text(s,`Annual income / setup cash = ${pct(ex.modelled_operating_income/ex.cash_total)}`,64,607,1152,48,29,true,BLUE);

s=slide('Sensitivity to prices, samples and concentration',
`APPENDIX. All rows reselect units under the stated changed assumption; all other assumptions are held fixed. Price shocks include both closing costs and property tax. Condo bedroom multipliers also have a separate ±10 percent sensitivity in current/bedroom_multiplier_sensitivity.csv. Do not confuse reselection cases with fixed-holdings revenue stresses.`,true);
table(s,['Purchase price','Units','Income'],t.purchase_price_sensitivity.map((x,i)=>[['Base','+10%','+20%'][i],String(x.units),k(x.noi)]),{x:64,y:190,w:550,ht:235,widths:[240,110,200],size:24});
table(s,['Minimum comparables','Units','Income'],t.sample_size_sensitivity.map((x,i)=>[String([5,10,20,30][i]),String(x.units),k(x.noi)]),{x:666,y:190,w:550,ht:290,widths:[275,100,175],size:24});
text(s,`No neighbourhood cap: ${nc.units} units and ${k(nc.noi)} income; ${pct(nc.max_hood_budget_share)} of budget in one area.`,64,536,1152,65,26,true);
text(s,'The 40% cap lowers modelled income but limits single-area exposure. It does not remove common risks.',64,614,1152,45,22,false,MUTED);

const study=t.selection_objective_comparison[0];
s=slide('Fee-excluded allocation and investment recommendation',
`APPENDIX. The requested allocation study deliberately excludes platform, management and cleaning costs in selection. It selects fourteen condos. Evaluated with costs restored it produces ${money(study.noi)}. Cost-aware selection changes Downtown's bedroom mix and produces ${money(b.noi)}, using ${money(b.cash_deployed-study.cash_deployed)} more capital. Neither is a global optimum. The extra capital has opportunity cost; we show the trade-off rather than claiming strict dominance. Earlier November 12 figures used older inputs and are archived.`,true);
table(s,['Measure','Requested allocation study','Cost-aware pitch'],[['Selection basis','Before the three operating costs','After modelled operating costs'],['Units / neighbourhoods',`${study.units} / ${study.neighbourhoods}`,`${b.units} / ${b.neighbourhoods}`],['Downtown mix','5 one-bedroom condos','4 two-bedroom condos'],['Capital deployed',m(study.cash_deployed),m(b.cash_deployed)],['Income with costs restored',k(study.noi),k(b.noi)],['Return with costs restored',pct(study.yield_on_deployed),pct(b.yield_on_deployed)]],{y:176,ht:405,widths:[355,400,397],size:23});
text(s,`Cost-aware alternative: ${money(b.noi-study.noi)} more annual income for ${money(b.cash_deployed-study.cash_deployed)} more capital.`,64,615,1152,45,23,true);

const rawRows=await fs.readFile(path.join(ROOT,'analysis/current/raw_filter_sensitivity.csv'),'utf8');
const csvLines=rawRows.trim().split(/\r?\n/);const heads=csvLines[0].split(',');const rawCases=csvLines.slice(1).map(l=>Object.fromEntries(l.split(',').map((v,i)=>[heads[i],v])));
s=slide('Data-quality checks and remaining limits',
`APPENDIX. Source labelled June 15 contains June 15, June 16 and July 6 scrape dates. Excluding later review dates removes known look-ahead in the active flag, but later prices and trailing estimates remain possible. The comparison rows rebuild affected segment populations and reselect. Missing bedrooms are imputed to one in base; excluding them is a sensitivity. Including inactive listings reduces modelled income. Assessment joins use parcel centroids and residential proxies, not validated sale opportunities. We have not done out-of-time forecast validation. Public raw source hashes and assessment reconstruction metadata are recorded.`,true);
const labels={allow_future_reviews:'Allow later last-review dates',minimum_stay_under30:'Use minimum stay under 30 nights',include_inactive:'Include inactive listings',exclude_missing_bedrooms:'Exclude missing bedrooms',no_price_outlier_filter:'Remove price-range filter'};
table(s,['Population treatment','Units','Operating income'],[['Base',String(b.units),k(b.noi)],...rawCases.map(x=>[labels[x.scenario],x.units,k(Number(x.noi))])],{y:173,ht:370,widths:[720,150,282],size:23});
text(s,'Active-only selection can be optimistic. Mixed scrape dates prevent a clean June 15 information set.',64,583,1152,66,24,false,MUTED);

await fs.mkdir(path.join(HERE,'.build'),{recursive:true});
await fs.writeFile(path.join(HERE,'speaker_notes.md'),notes.map(n=>`## ${n.slide}. ${n.title}\n\n${n.notes}\n`).join('\n'));
for(let i=0;i<pres.slides.items.length;i++){
 const png=await pres.export({slide:pres.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(HERE,'.build',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const candidate=path.join(HERE,'.build/candidate.pptx');
await (await PresentationFile.exportPptx(pres)).save(candidate);
await fs.mkdir(path.join(ROOT,'.codex-finalizer'),{recursive:true});
await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:path.join(HERE,'ddd_investment_pitch.pptx'),
 pythonExecutable:path.join(RUNTIME,'python/bin/python'),integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[1,2,5,6,7,8,9,10,11].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[1,2,5,6,7,8,9,10,11],requiredNativeChartOwnerSlides:[3,4,5],materializeLiteralChartWorkbooks:true,
 fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(ROOT,'.codex-finalizer/ddd.validation.json')});
console.log('Created 11-slide presentation, speaker notes, editable tables and charts.');
