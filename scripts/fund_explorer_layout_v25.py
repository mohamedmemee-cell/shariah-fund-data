#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'docs'/'fund-explorer.html'
s=p.read_text(encoding='utf-8')
marker='fund-explorer-layout-v25'
if marker in s:
    print('Fund Explorer layout V25 already present')
    raise SystemExit(0)

css=r'''
/* fund-explorer-layout-v25 */
body main{max-width:1680px!important;padding-left:24px!important;padding-right:24px!important}
.fundCountV25{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:0 0 10px;color:var(--muted);font-size:13px}
.fundCountV25 strong{color:var(--text);font-size:14px}
.tableWrap{overflow-x:visible!important}
#fundExplorerTableV25{width:100%!important;min-width:0!important;table-layout:auto}
#fundExplorerTableV25 th,#fundExplorerTableV25 td{padding:10px 7px;font-size:13px}
#fundExplorerTableV25 th:nth-child(1),#fundExplorerTableV25 td:nth-child(1){width:42px;text-align:center;color:var(--muted)}
#fundExplorerTableV25 th:nth-child(2),#fundExplorerTableV25 td:nth-child(2){min-width:220px;text-align:left;white-space:normal}
#fundExplorerTableV25 th:nth-child(3),#fundExplorerTableV25 td:nth-child(3){min-width:135px;text-align:left;white-space:normal}
#fundExplorerTableV25 th:nth-child(4),#fundExplorerTableV25 td:nth-child(4){min-width:120px;white-space:normal}
#fundExplorerTableV25 th:nth-child(5),#fundExplorerTableV25 td:nth-child(5){min-width:90px;white-space:normal}
#fundExplorerTableV25 th:nth-child(6),#fundExplorerTableV25 td:nth-child(6){min-width:85px;white-space:normal}
#fundExplorerTableV25 th:nth-child(n+7),#fundExplorerTableV25 td:nth-child(n+7){white-space:nowrap}
@media(max-width:1100px){.tableWrap{overflow-x:auto!important}#fundExplorerTableV25{min-width:1180px!important}.fundCountV25{position:sticky;left:0}}
'''
s=s.replace('</style>',css+'\n</style>',1)

s=s.replace('<section class="card"><div class="tableWrap"><table>','<section class="card"><div class="fundCountV25"><strong id="fundCountV25">Loading funds…</strong><span id="fundTotalV25"></span></div><div class="tableWrap"><table id="fundExplorerTableV25">',1)
s=s.replace('<thead><tr><th>Fund</th>','<thead><tr><th>#</th><th>Fund</th>',1)
s=s.replace('<tbody id="rows"><tr><td colspan="12">Loading…</td></tr></tbody>','<tbody id="rows"><tr><td colspan="13">Loading…</td></tr></tbody>',1)

old="$('rows').innerHTML=arr.length?arr.map(f=>`<tr><td><a class=\"fund\" href=\"./fund-details.html?id=${encodeURIComponent(f.id)}\">${f.name}</a></td>"
new="$('fundCountV25').textContent=`Showing ${arr.length} of ${feed.funds.length} funds`;$('fundTotalV25').textContent=arr.length===feed.funds.length?'Full list':'Filtered list';$('rows').innerHTML=arr.length?arr.map((f,i)=>`<tr><td>${i+1}</td><td><a class=\"fund\" href=\"./fund-details.html?id=${encodeURIComponent(f.id)}\">${f.name}</a></td>"
if old not in s:
    raise SystemExit('Could not find Fund Explorer render anchor; refusing partial patch')
s=s.replace(old,new,1)
s=s.replace("'<tr><td colspan=\"12\">No funds match these filters.</td></tr>'","'<tr><td colspan=\"13\">No funds match these filters.</td></tr>'",1)

s=s.replace('</body>','<!-- '+marker+' -->\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied Fund Explorer layout V25')
