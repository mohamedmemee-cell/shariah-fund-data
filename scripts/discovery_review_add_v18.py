#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DISC=ROOT/'docs'/'discovery.html'
ADD=ROOT/'docs'/'add-fund.html'

# Discovery Inbox: add Review source + Add this fund actions.
s=DISC.read_text(encoding='utf-8')
if 'discovery-review-add-v18' not in s:
    s=s.replace('.warn{color:var(--warn)}', '.warn{color:var(--warn)}.actionsV18{display:flex;gap:7px;flex-wrap:wrap}.actionV18{display:inline-flex;align-items:center;justify-content:center;padding:7px 9px;border:1px solid var(--line);border-radius:8px;text-decoration:none;font-weight:750;font-size:12px;white-space:nowrap}.actionV18.primary{background:var(--accent);color:#fff;border-color:var(--accent)}',1)
    s=s.replace('<th>Search source</th></tr>', '<th>Search source</th><th>Action</th></tr>',1)
    s=s.replace('<td colspan="6">Loading…</td>', '<td colspan="7">Loading…</td>',1)
    old="<td><small>${esc(x.query||'')}</small></td></tr>"
    new="<td><small>${esc(x.query||'')}</small></td><td><div class=\"actionsV18\"><a class=\"actionV18\" href=\"${esc(x.url)}\" target=\"_blank\" rel=\"noopener noreferrer\">Review source</a>${x.status==='needs_verification'?`<a class=\"actionV18 primary\" href=\"./add-fund.html?discovery=${encodeURIComponent(x.id||'')}&name=${encodeURIComponent(x.title||'')}&manager=${encodeURIComponent(x.manager||'')}&website=${encodeURIComponent(x.url||'')}\">Add this fund</a>`:''}</div></td></tr>"
    if old not in s:
        raise SystemExit('Discovery row anchor not found')
    s=s.replace(old,new,1)
    s=s.replace("'<tr><td colspan=\"6\">No candidates match these filters.</td></tr>'", "'<tr><td colspan=\"7\">No candidates match these filters.</td></tr>'",1)
    s=s.replace("'<tr><td colspan=\"6\" class=\"warn\">Discovery data is not available yet. Run the Discovery workflow in GitHub Actions.</td></tr>'", "'<tr><td colspan=\"7\" class=\"warn\">Discovery data is not available yet. Run the Discovery workflow in GitHub Actions.</td></tr>'",1)
    s=s.replace('</style></head>', '/* discovery-review-add-v18 */\n</style></head>',1)
    DISC.write_text(s,encoding='utf-8')

# Add Fund: accept Discovery Inbox values as safe prefills, while keeping confirmation/review gates.
a=ADD.read_text(encoding='utf-8')
if 'discovery-prefill-v18' not in a:
    banner='<div class="callout hidden" id="discoveryPrefill"><b>From Discovery Inbox</b><br><span id="discoveryPrefillText"></span> Review the official source before continuing. Discovery does not confirm Shariah compliance.</div>'
    anchor='<section class="card" id="entryCard">'
    if anchor not in a:
        raise SystemExit('Add Fund entry anchor not found')
    a=a.replace(anchor, anchor+banner,1)
    js=r'''
<script>
/* discovery-prefill-v18 */
(function(){
 const p=new URLSearchParams(location.search), id=p.get('discovery');
 if(!id)return;
 const set=(field,key)=>{const el=document.getElementById(field),v=p.get(key);if(el&&v)el.value=v};
 set('name','name');set('manager','manager');set('website','website');
 const box=document.getElementById('discoveryPrefill'),txt=document.getElementById('discoveryPrefillText');
 if(box){box.classList.remove('hidden');if(txt)txt.textContent='Candidate '+id+' has been prefilled from the automated discovery scan.'}
})();
</script>
'''
    a=a.replace('</body>',js+'\n</body>',1)
    ADD.write_text(a,encoding='utf-8')

print('Applied Discovery review/Add Fund handoff V18')
