"""Authoritative analysis. Cost-aware selection plus a separate fee-excluded study.
Monetary units are CAD. The aggregate workflow needs only the Python standard library.
"""
import csv
import hashlib
import json
import math
from collections import Counter,defaultdict
from pathlib import Path
from statistics import median
from . import config as C

OUT=C.ROOT/'analysis/current'
TEXT=set(C.SEGMENT_KEYS)|{'prop_type','step','why'}

def read_csv(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        return [{k:v if k in TEXT else float(v) for k,v in r.items()} for r in csv.DictReader(f)]

def write_csv(path,rows):
    if not rows:raise ValueError(f'No rows: {path}')
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def key(r):return tuple(r[k] for k in C.SEGMENT_KEYS)

def price_segments(segments,price_factor=1,bedroom_factors=None):
    source=read_csv(C.PROPERTY_VALUES_FILE)
    prices={(r['neighbourhood_cleansed'],r['prop_type']):r for r in source}
    if len(prices)!=len(source):raise ValueError('Duplicate assessment keys')
    result=[]
    for r in segments:
        category=C.BUCKET_TO_PROP_TYPE.get(r['bucket']);p=prices.get((r['neighbourhood_cleansed'],category))
        if p is None:continue
        factors=bedroom_factors or C.CONDO_BEDROOM_MULTIPLIER
        mult=factors[r['bedrooms_grp']] if r['bucket']=='condo' else 1
        result.append(dict(r,prop_type=category,median_value=p['median_value'],assessment_properties=p['properties'],price_cad=p['median_value']*mult*price_factor))
    return result

def underwrite(r,revenue_factor=1,price_factor=1,fee=None,management=None,cleaning=None,offline=0,reserve=0,rev_col='rev_median'):
    fee=C.PLATFORM_FEE if fee is None else fee
    management=C.MANAGEMENT_FEE if management is None else management
    cleaning=C.CLEANING_AND_SUPPLIES if cleaning is None else cleaning
    price=r['price_cad']*price_factor;gross=r[rev_col]*revenue_factor*(1-offline/12)
    fixed=C.LICENCE_AND_REGISTRATION_CAD+C.INSURANCE_CAD_YEAR+12*C.STRATA_FEES_CAD_MONTH[r['bucket']]+price*C.PROPERTY_TAX_RATE
    cash=price*(1+C.CLOSING_COSTS)+C.FURNISHING_CAD
    noi=gross*(1-fee-management-cleaning-reserve)-fixed
    return dict(r,gross=gross,fixed=fixed,cash_in=cash,noi=noi,net_yield=noi/cash)

def modelled_rows(rows):return [underwrite(r) for r in rows]

def selection_rows(rows):return [underwrite(r,fee=0,management=0,cleaning=0) for r in rows]

def select(rows,min_n=C.MIN_COMPARABLES,cap=C.MAX_NEIGHBOURHOOD_SHARE,strict=True,score='net_yield',legacy=False):
    spent=0;hoods=defaultdict(float);picks=[]
    for r in sorted([r for r in rows if r['n']>=min_n and (legacy or r['noi']>0)],key=lambda r:r[score],reverse=True):
        capacity=int(r['n']*C.MAX_SEGMENT_SHARE)
        if not strict:capacity=max(1,capacity)
        for _ in range(capacity):
            h=r[C.SEGMENT_KEYS[0]]
            if spent+r['cash_in']>C.BUDGET_CAD+1e-7 or hoods[h]+r['cash_in']>C.BUDGET_CAD*cap+1e-7:break
            picks.append(r);spent+=r['cash_in'];hoods[h]+=r['cash_in']
    return picks

def summary(port,label):
    cash=sum(r['cash_in'] for r in port);noi=sum(r['noi'] for r in port);hoods=defaultdict(float)
    for r in port:hoods[r[C.SEGMENT_KEYS[0]]]+=r['cash_in']
    return dict(scenario=label,units=len(port),cash_deployed=cash,idle_cash=C.BUDGET_CAD-cash,revenue=sum(r['gross'] for r in port),fixed_costs=sum(r['fixed'] for r in port),noi=noi,yield_on_deployed=noi/cash if cash else None,yield_on_budget=noi/C.BUDGET_CAD,neighbourhoods=len(hoods),max_hood_budget_share=max(hoods.values(),default=0)/C.BUDGET_CAD)

def evaluate(port,label,**kwargs):return summary([underwrite(r,**kwargs) for r in port],label)

def holdings(port):
    counts=Counter(key(r) for r in port);lookup={key(r):r for r in port};result=[]
    for k,n in counts.items():
        r=lookup[k];costed=underwrite(r)
        result.append(dict(**{f:r[f] for f in C.SEGMENT_KEYS},units=n,comparables=int(r['n']),purchase_price_each=r['price_cad'],cash_each=r['cash_in'],cash_total=n*r['cash_in'],revenue_each=r['rev_median'],contribution_before_three_costs=n*underwrite(r,fee=0,management=0,cleaning=0)['noi'],modelled_operating_income=n*costed['noi']))
    return result

def rebuild_raw():
    from . import prep
    import pandas as pd
    raw=prep.load_listings();clean,filters=prep.clean(raw);clean=prep.add_revenue(clean);seg=prep.segments(clean)
    C.PROCESSED.mkdir(parents=True,exist_ok=True)
    public_columns=['id','neighbourhood_cleansed','room_type','bucket','bedrooms','price_num',
                    'number_of_reviews_ltm','is_active','occupancy','revenue','review_scores_rating',
                    'licence_status','is_commercial_host']
    clean[public_columns].to_csv(C.PROCESSED/'listings_clean.csv',index=False)
    seg.to_csv(C.TABLES/'segments.csv',index=False);filters.to_csv(C.TABLES/'filters_applied.csv',index=False)
    old=clean.copy();old['is_active']=(pd.Timestamp(C.SNAPSHOT_DATE)-old['last_review']).dt.days.le(C.ACTIVE_REVIEW_WINDOW_DAYS)
    thirty,_=prep.clean(raw[raw.minimum_nights<30]);thirty=prep.add_revenue(thirty)
    inactive=clean.copy();inactive['is_active']=True
    variants={'allow_future_reviews':prep.segments(old),'minimum_stay_under30':prep.segments(thirty),'include_inactive':prep.segments(inactive),'exclude_missing_bedrooms':prep.segments(clean[clean.bedrooms.notna()])}
    a,b=C.MIN_NIGHTLY_PRICE,C.MAX_NIGHTLY_PRICE
    try:
        C.MIN_NIGHTLY_PRICE=0;C.MAX_NIGHTLY_PRICE=float('inf');broad,_=prep.clean(raw)
    finally:C.MIN_NIGHTLY_PRICE,C.MAX_NIGHTLY_PRICE=a,b
    variants['no_price_outlier_filter']=prep.segments(prep.add_revenue(broad))
    evidence=[]
    for name,df in variants.items():
        records=df.to_dict('records');write_csv(OUT/f'segments_{name}.csv',records)
        evidence.append(evaluate(select(modelled_rows(price_segments(records))),name))
    write_csv(OUT/'raw_filter_sensitivity.csv',evidence)
    stats=dict(raw_rows=len(raw),clean_rows=len(clean),active_entire_home_rows=int(seg.n.sum()),segments=len(seg),future_review_rows=int((raw.last_review>C.SNAPSHOT_DATE).sum()),missing_bedrooms_clean=int(clean.bedrooms.isna().sum()),last_scraped_counts=raw.last_scraped.value_counts().to_dict(),raw_sha256=hashlib.sha256((C.RAW/'listings.csv.gz').read_bytes()).hexdigest(),segments_sha256=hashlib.sha256((C.TABLES/'segments.csv').read_bytes()).hexdigest())
    (OUT/'raw_validation.json').write_text(json.dumps(stats,indent=2));return stats

def run(source='aggregates'):
    OUT.mkdir(parents=True,exist_ok=True);C.TABLES.mkdir(parents=True,exist_ok=True)
    stats=rebuild_raw() if source=='raw' else None
    segments=read_csv(C.TABLES/'segments.csv');priced=price_segments(segments)
    assert len({key(r) for r in segments})==len(segments)
    assert all(math.isfinite(r['rev_median']) and 0<=r['rev_p25']<=r['rev_median']<=r['rev_p75'] for r in segments)
    chosen=select(modelled_rows(priced));assert chosen,'No eligible units'
    base=evaluate(chosen,'modelled_cost_base');pre=summary(selection_rows(chosen),'before_three_excluded_costs')
    cases=[base,evaluate(chosen,'revenue_plus10',revenue_factor=1.1),evaluate(chosen,'revenue_minus10',revenue_factor=.9),evaluate(chosen,'revenue_minus20',revenue_factor=.8),evaluate(chosen,'revenue_minus30',revenue_factor=.7),evaluate(chosen,'two_months_offline',offline=2),evaluate(chosen,'revenue_minus20_reserve5',revenue_factor=.8,reserve=.05),evaluate(chosen,'repairs_reserve5',reserve=.05),evaluate(chosen,'platform_fee3',fee=.03),evaluate(chosen,'cross_section_p25',rev_col='rev_p25'),evaluate(chosen,'cross_section_p75',rev_col='rev_p75')]
    sample=[evaluate(select(modelled_rows(priced),min_n=n),f'min_n_{n}') for n in (5,10,20,30)]
    caps=[evaluate(select(modelled_rows(priced),cap=cap),f'cap_{cap}') for cap in (.2,.3,.4,.5,1)]
    pricing=[evaluate(select(modelled_rows(price_segments(segments,price_factor=f))),f'purchase_factor_{f}') for f in (1,1.1,1.2)]
    # Frozen public GVR counterfactual, same matched segment universe as assessments.
    benchmarks={'East':{'condo':635100,'townhouse':1055800,'house':1610700},'West':{'condo':751400,'townhouse':1285000,'house':2899700}}
    west={'Arbutus Ridge','Downtown','Dunbar Southlands','Fairview','Kerrisdale','Kitsilano','Marpole','Oakridge','Shaughnessy','South Cambie','West End','West Point Grey'}
    gvr=[]
    for r in priced:
        side='West' if r['neighbourhood_cleansed'] in west else 'East';typ=r['bucket']
        mult=C.CONDO_BEDROOM_MULTIPLIER[r['bedrooms_grp']] if typ=='condo' else 1
        gvr.append(dict(r,price_cad=benchmarks[side][typ]*mult))
    methods=[evaluate(select(modelled_rows(gvr)),'gvr_same_segment_universe'),base]
    bedrooms=[evaluate(select(modelled_rows(price_segments(segments,bedroom_factors={k:v*f for k,v in C.CONDO_BEDROOM_MULTIPLIER.items()}))),f'condo_multiplier_factor_{f}') for f in (.9,1,1.1)]
    cutoff=median(r['price_cad'] for r in priced);alternatives=[base]
    for name,pool in [('few_high_value',[r for r in priced if r['price_cad']>=cutoff]),('many_modest',[r for r in priced if r['price_cad']<cutoff])]:alternatives.append(evaluate(select(modelled_rows(pool)),name))
    allocation_study=select(selection_rows(priced));rank_comparison=[evaluate(allocation_study,'fee_excluded_selection_evaluated_with_costs'),base]
    owned=holdings(chosen);hoods=defaultdict(float)
    for r in owned:hoods[r['neighbourhood_cleansed']]+=r['cash_total']
    assert base['cash_deployed']<=C.BUDGET_CAD+1e-7
    assert all(v<=C.BUDGET_CAD*C.MAX_NEIGHBOURHOOD_SHARE+1e-7 for v in hoods.values())
    assert all(r['units']<=int(r['comparables']*C.MAX_SEGMENT_SHARE) and r['comparables']>=C.MIN_COMPARABLES for r in owned)
    tables={'holdings':owned,'performance_scenarios':cases,'sample_size_sensitivity':sample,'concentration_sensitivity':caps,'purchase_price_sensitivity':pricing,'pricing_method_comparison':methods,'bedroom_multiplier_sensitivity':bedrooms,'few_vs_many':alternatives,'selection_objective_comparison':rank_comparison,'fee_excluded_holdings':holdings(allocation_study)}
    for name,t in tables.items():write_csv(OUT/f'{name}.csv',t)
    write_csv(C.TABLES/'segments_underwritten.csv',[underwrite(r) for r in priced]);write_csv(C.TABLES/'recommended_portfolio.csv',[underwrite(r) for r in chosen]);write_csv(C.TABLES/'sensitivity.csv',cases);write_csv(C.TABLES/'few_vs_many.csv',alternatives)
    raw_evidence=OUT/'raw_validation.json';segment_hash=hashlib.sha256((C.TABLES/'segments.csv').read_bytes()).hexdigest()
    if raw_evidence.exists():
        evidence=json.loads(raw_evidence.read_text())
        if evidence.get('segments_sha256')==segment_hash:stats=evidence
    inputs=[C.TABLES/'segments.csv',C.PROPERTY_VALUES_FILE,C.ROOT/'src/config.py',Path(__file__)]
    data=dict(analysis_date='2026-11-13',input_mode=source,selection_metric='modelled operating income divided by cash deployed; fee-excluded allocation separately reported',projection_basis='2027 constant historical estimated revenue run-rate; not calibrated forecast',recommendation=owned,selection_summary=pre,performance=base,tables=tables,comparables_min=C.MIN_COMPARABLES,neighbourhood_cap=C.MAX_NEIGHBOURHOOD_SHARE,property_price_median_cutoff=cutoff,raw_validation=stats,sources={'airbnb_fees':'https://www.airbnb.com/help/article/1857','assessments':'https://opendata.vancouver.ca/explore/dataset/property-tax-report/','parcel_geometry':'https://opendata.vancouver.ca/explore/dataset/property-parcel-polygons/','gvr_counterfactual':'https://members.gvrealtors.ca/news/GVR-Stats-Package-October-2026.pdf'},input_sha256={str(p.relative_to(C.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    (OUT/'results.json').write_text(json.dumps(data,indent=2))
    (C.OUTPUTS/'key_numbers.json').write_text(json.dumps(dict(units=base['units'],cash_deployed_cad=round(base['cash_deployed'],-3),noi_2027_cad=round(base['noi'],-3),net_yield_base=round(base['yield_on_deployed'],3),neighbourhoods=base['neighbourhoods'],scenario='15.5% platform + 20% management + 8% cleaning; constant historical revenue; no repair reserve'),indent=2))
    print(json.dumps(dict(selection=pre,performance=base,holdings=owned,source=source),indent=2));return data
