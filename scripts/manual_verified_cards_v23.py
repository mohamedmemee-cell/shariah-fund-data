#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEED = ROOT / 'docs' / 'shariah-funds.json'
DIRECTORY = ROOT / 'docs' / 'fund-directory.json'

feed = json.loads(FEED.read_text(encoding='utf-8'))
directory = json.loads(DIRECTORY.read_text(encoding='utf-8'))
fund_dir = directory.get('funds') or {}

# Any value explicitly marked Manual verified is authoritative for the UI/feed
# until it is deliberately changed or re-verified. Automated collectors must not
# silently overwrite these values in the cards.
field_map = {
    'risk_level': 'risk_level',
    'ter': 'ter',
    'oneYear': 'oneYear',
    'threeYear': 'threeYear',
    'fiveYear': 'fiveYear',
    'tenYear': 'tenYear',
    'sinceInception': 'sinceInception',
}

changed = []
for row in feed.get('funds', []):
    d = fund_dir.get(row.get('id')) or {}
    verification = d.get('verification') or {}
    for verification_key, feed_key in field_map.items():
        rec = verification.get(verification_key) or {}
        if rec.get('status') != 'verified' or rec.get('method') != 'manual':
            continue
        value = rec.get('value')
        if value in (None, ''):
            continue
        if row.get(feed_key) != value:
            row[feed_key] = value
            changed.append(f"{row.get('id')}:{feed_key}")

    # Keep the performance date aligned with the manually verified performance
    # values when a manual date was captured.
    manual_perf_keys = ('oneYear', 'threeYear', 'fiveYear', 'tenYear', 'sinceInception')
    if any((verification.get(k) or {}).get('status') == 'verified' and
           (verification.get(k) or {}).get('method') == 'manual'
           for k in manual_perf_keys):
        dates = [
            (verification.get(k) or {}).get('verified_at')
            for k in manual_perf_keys
            if (verification.get(k) or {}).get('verified_at')
        ]
        # Prefer an explicit manually stored data-as-of from manual_values if the
        # updater has already placed it in the feed; otherwise retain existing.
        if dates and not row.get('updated'):
            row['updated'] = max(dates)

FEED.write_text(json.dumps(feed, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('Applied manual verified card overrides' + (': ' + ', '.join(changed) if changed else ': no changes'))
