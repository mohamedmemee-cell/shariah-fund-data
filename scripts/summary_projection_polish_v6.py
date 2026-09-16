#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'docs'/'index.html'
s=p.read_text(encoding='utf-8')
if 'summary-projection-polish-v6' in s:
    print('summary projection polish already present')
    raise SystemExit(0)
css=r'''
/* summary-projection-polish-v6 */
#summaryProjectionV4{margin-top:18px}
#summaryProjectionV4 h3{margin:0 0 10px;padding-bottom:8px;border-bottom:2px solid color-mix(in srgb,var(--brand) 45%,var(--line));color:var(--brand-strong)}
#summaryProjectionV4 .projectionGridV4{grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
#summaryProjectionV4 .projectionCardV4{display:flex;flex-direction:column;gap:5px;min-height:96px;padding:14px 16px;border-radius:12px;background:var(--card);border:1px solid var(--line);overflow:hidden}
#summaryProjectionV4 .projectionCardV4 small{font-size:12px;font-weight:750;color:var(--muted);line-height:1.25}
#summaryProjectionV4 .projectionCardV4 b{display:block;font-size:20px;line-height:1.15;letter-spacing:-.01em;white-space:nowrap}
#summaryProjectionV4 .projectionCardV4 span{display:block;margin-top:auto;font-size:12px;line-height:1.3;color:var(--muted);white-space:normal}
#summaryProjectionV4 .projectionCardV4:nth-child(1){border-top:4px solid #9aa5a8;background:color-mix(in srgb,var(--card) 88%,#eef1f2)}
#summaryProjectionV4 .projectionCardV4:nth-child(2){border-top:4px solid var(--blue);background:color-mix(in srgb,var(--card) 84%,var(--blue-soft))}
#summaryProjectionV4 .projectionCardV4:nth-child(3){border-top:4px solid var(--green);background:color-mix(in srgb,var(--card) 84%,var(--green-soft))}
#summaryProjectionV4 .projectionCardV4:nth-child(4){border-top:4px solid var(--amber);background:color-mix(in srgb,var(--card) 84%,var(--amber-soft))}
@media(max-width:820px){#summaryProjectionV4 .projectionGridV4{grid-template-columns:1fr 1fr}}
@media(max-width:480px){#summaryProjectionV4 .projectionGridV4{grid-template-columns:1fr}}
'''
s=s.replace('</style>',css+'\n</style>',1)
p.write_text(s,encoding='utf-8')
print('Applied summary projection polish V6')
