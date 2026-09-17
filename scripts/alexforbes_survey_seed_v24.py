#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'sources' / 'funds.json'
MANUAL = ROOT / 'data' / 'manual_values.json'

SURVEY_URL = 'https://invest.alexforbes.com/za/en/surveys/industry-surveys/shariah-manager-watch'
SURVEY_AS_OF = '2026-07-31'

# Source: Alexforbes Shari'ah Manager Watch Survey, month ending July 2026.
# Performance values below are the PORTFOLIO returns (not benchmark returns),
# expressed as percentages. 3Y/5Y/7Y/10Y figures are annualised in the survey.
SURVEY_FUNDS = [
    # Balanced Funds
    ('27four Shari\'ah Balanced Prescient FoF','27four','Balanced',17.41,12.80,10.71,8.96),
    ('27four Shari\'ah Multi-Managed Balanced Fund','27four','Balanced',17.78,13.40,11.32,9.42),
    ('27four Shari\'ah Wealth Builder Fund','27four','Balanced',18.92,13.91,11.62,9.69),
    ('Alexander Forbes Investments Shari’ah Medium Growth','Alexander Forbes Investments','Balanced',17.41,12.46,10.57,None),
    ('Alexander Forbes Investments Shari\'ah High Growth','Alexander Forbes Investments','Balanced',21.50,15.03,12.39,None),
    ('Camissa Islamic Balanced Fund','Camissa','Balanced',22.32,14.07,11.50,10.89),
    ('Element Islamic Balanced','Element Investment Managers','Balanced',6.20,7.49,6.83,8.45),
    ('Foord Shariah Balanced Fund','Foord','Balanced',12.49,None,None,None),
    ('Momentum Investments Shari’ah','Momentum Investments','Balanced',17.84,13.31,10.49,None),
    ('Oasis Crescent Balanced High Equity','Oasis','Balanced',18.98,12.41,11.63,9.02),
    ('Oasis Crescent Balanced Progressive','Oasis','Balanced',18.82,12.38,11.36,8.73),
    ('Oasis Crescent Balanced Stable','Oasis','Balanced',14.82,10.65,9.76,8.02),
    ('Old Mutual Shari\'ah Balanced','Old Mutual Investment Group','Balanced',19.15,13.60,11.85,9.56),
    ('Sentio SCI Hikma Shari\'ah Balanced','Sentio Capital','Balanced',6.43,9.97,8.28,7.43),
    ('SMM Nur Balanced Portfolio','Sanlam Multi-Managers','Balanced',18.00,13.06,10.93,9.53),
    ('STANLIB Multi-Manager Shari\'ah Balanced','STANLIB Multi-Manager','Balanced',14.47,12.34,10.61,9.75),
    # Domestic Equity
    ('Element Islamic Equity','Element Investment Managers','Domestic Equity',11.93,9.88,9.49,10.08),
    ('Mazi Shari\'ah Equity Fund','Mazi Asset Management','Domestic Equity',30.80,17.96,14.18,None),
    ('Mianzo Islamic Domestic Equity 27Four Fund','Mianzo Asset Management','Domestic Equity',27.99,None,None,None),
    ('Old Mutual Shari\'ah Equity','Old Mutual Investment Group','Domestic Equity',27.07,16.85,14.18,10.19),
    # Global Equity
    ('Element Islamic Global Equity','Element Investment Managers','Global Equity',6.98,12.43,11.91,10.15),
    ('Old Mutual Global Islamic Equity','Old Mutual Investment Group','Global Equity',21.01,18.43,16.03,15.08),
    # Domestic & Global Equity Exposure
    ('27four Shari\'ah Active Equity','27four','Domestic & Global Equity',20.52,14.53,11.26,9.64),
    ('Camissa Islamic Equity Fund','Camissa','Domestic & Global Equity',30.36,17.71,13.28,12.48),
    ('Oasis Crescent Equity Fund','Oasis','Domestic & Global Equity',19.08,12.70,12.42,9.35),
    ('Sentio SCI Hikma Shari\'ah General Equity','Sentio Capital','Domestic & Global Equity',10.13,12.43,9.67,7.11),
    ('Visio BCI Shari’ah Equity fund','Visio Fund Management','Domestic & Global Equity',9.20,10.20,8.83,8.21),
    ('Wealthvest Shariah Equity 27Four Fund','Wealthvest Asset Management','Domestic & Global Equity',14.21,None,None,None),
    # Income Funds
    ('Camissa Islamic High Yield Fund','Camissa','Income',13.45,12.09,9.79,None),
    ('Oasis Crescent Income Fund','Oasis','Income',9.57,8.47,7.68,7.37),
    ('Sentio SCI Hikma Shari’ah Income Fund','Sentio Capital','Income',8.33,None,None,None),
]

def slugify(name):
    s = name.lower().replace('’', "'")
    s = re.sub(r"shari['’]?ah", 'shariah', s)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return 'alexforbes-' + s[:90]

sources = json.loads(SOURCES.read_text(encoding='utf-8'))
manual = json.loads(MANUAL.read_text(encoding='utf-8'))
funds = sources.setdefault('funds', [])
values = manual.setdefault('values', {})

# Exact source-name matches use the existing record/id; otherwise create a Watchlist
# record using the exact Alexforbes survey name. This avoids silently merging near-
# duplicate product names that still need manager-level verification.
by_name = {f.get('name'): f for f in funds}
added = 0
updated = 0
for name, manager, category, one, three, five, ten in SURVEY_FUNDS:
    f = by_name.get(name)
    if f is None:
        fid = slugify(name)
        # Keep IDs unique even if a future source has the same slug.
        used = {x.get('id') for x in funds}
        base = fid
        n = 2
        while fid in used:
            fid = f'{base}-{n}'; n += 1
        f = {
            'id': fid,
            'name': name,
            'manager': manager,
            'category': category,
            'bucket': 'Watchlist',
            'suggested_split': 0,
            'auto_type': 'manual',
            'source_url': SURVEY_URL,
            'risk_level': None,
            'shariah_note': "Included in the Alexforbes Shari'ah Manager Watch Survey for July 2026. Keep on Watchlist until manager/fund-level verification is complete.",
            'discovery_source': 'Alexforbes Shari\'ah Manager Watch Survey',
            'survey_as_of': SURVEY_AS_OF,
        }
        funds.append(f)
        by_name[name] = f
        added += 1
    else:
        # Preserve existing manager URLs/automation and only record the survey metadata.
        f['discovery_source'] = 'Alexforbes Shari\'ah Manager Watch Survey'
        f['survey_as_of'] = SURVEY_AS_OF
        updated += 1

    rec = values.setdefault(f['id'], {})
    survey_perf = {
        'oneYear': one,
        'threeYear': three,
        'fiveYear': five,
        'tenYear': ten,
        'dataAsOf': SURVEY_AS_OF,
    }
    # Seed only missing fallback values. Existing manager/manual values stay intact.
    for k, v in survey_perf.items():
        if v is not None and rec.get(k) is None:
            rec[k] = v
    if not rec.get('dataAsOf'):
        rec['dataAsOf'] = SURVEY_AS_OF

manual['as_of'] = max(str(manual.get('as_of') or ''), '2026-09-17')
manual['note'] = (manual.get('note') or '') + ' Alexforbes July 2026 Shari\'ah Manager Watch values seed missing fallbacks only; manager/manual verified figures remain authoritative.'

SOURCES.write_text(json.dumps(sources, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
MANUAL.write_text(json.dumps(manual, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'Alexforbes survey universe applied: {added} added, {updated} existing exact-name records enriched, {len(SURVEY_FUNDS)} survey portfolios represented.')
