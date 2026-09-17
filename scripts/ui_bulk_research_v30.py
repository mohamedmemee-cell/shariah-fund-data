#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'docs'/'index.html'
EXPLORER=ROOT/'docs'/'fund-explorer.html'
MARK='ui-bulk-research-v30'

# Move projection period slider above the maximum-funds box in Step 2.
s=INDEX.read_text(encoding='utf-8')
if MARK not in s:
    js=r'''
<script>
/* ui-bulk-research-v30 */
(function(){
 function moveProjection(){
   const inputs=document.querySelector('.inputs'), years=document.getElementById('years');
   if(!inputs||!years)return;
   const slider=years.closest('.sliderrow');
   const heading=slider?.previousElementSibling;
   const fund=document.querySelector('.fundLimitBox,#goalFundLimitV4');
   if(!slider||!heading||!fund)return;
   const wrap=document.createElement('div');wrap.id='projectionPeriodV30';
   fund.parentNode.insertBefore(wrap,fund);wrap.appendChild(heading);wrap.appendChild(slider);
 }
 moveProjection();setTimeout(moveProjection,60);
})();
</script>
'''
    s=s.replace('</body>',js+'\n<!-- '+MARK+' -->\n</body>',1)
    INDEX.write_text(s,encoding='utf-8')

# Add a visible bulk-research panel to Fund Explorer so the automatic job is observable.
t=EXPLORER.read_text(encoding='utf-8')
if MARK not in t:
    css=r'''
<style>
/* ui-bulk-research-v30 */
.bulkResearchV30{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:14px}.bulkStatV30{padding:11px 12px;border:1px solid var(--line);border-radius:11px;background:var(--soft)}.bulkStatV30 small{display:block;color:var(--muted);margin-bottom:4px}.bulkStatV30 b{font-size:18px}.bulkNoteV30{margin:10px 0 0;color:var(--muted);font-size:12px;line-height:1.45}@media(max-width:760px){.bulkResearchV30{grid-template-columns:1fr 1fr}}
</style>
'''
    t=t.replace('</head>',css+'\n</head>',1)
    panel='''<section class="card" id="bulkResearchPanelV30"><div class="sectiontitle"><h2 style="margin:0">Automatic Watchlist research</h2><span class="muted" id="bulkResearchDateV30">Loading…</span></div><div class="bulkResearchV30"><div class="bulkStatV30"><small>Watchlist researched</small><b id="bulkResearchedV30">—</b></div><div class="bulkStatV30"><small>Official sources found</small><b id="bulkSourcesV30">—</b></div><div class="bulkStatV30"><small>Fields auto-verified</small><b id="bulkFieldsV30">—</b></div><div class="bulkStatV30"><small>Still on Watchlist</small><b id="bulkStillV30">—</b></div></div><p class="bulkNoteV30">This runs automatically with the fund-data workflow. It searches official manager sites only, fills fields when the evidence is clear, then applies the normal activation gates. Funds with missing or ambiguous evidence remain on Watchlist for review.</p></section>'''
    needle='<section class="card"><div class="tableWrap">'
    if needle in t:t=t.replace(needle,panel+needle,1)
    js=r'''
<script>
/* ui-bulk-research-v30 */
(async function(){
 try{
   const [rr,vr]=await Promise.all([fetch('./bulk-research.json?ts='+Date.now(),{cache:'no-store'}),fetch('./bulk-verification.json?ts='+Date.now(),{cache:'no-store'})]);
   const r=rr.ok?await rr.json():{},v=vr.ok?await vr.json():{};
   const set=(id,x)=>{const e=document.getElementById(id);if(e)e.textContent=x??'—'};
   set('bulkResearchedV30',r.researched);set('bulkSourcesV30',r.official_source_found);set('bulkFieldsV30',r.fields_verified);set('bulkStillV30',v.still_watchlist);
   set('bulkResearchDateV30',r.generated_at?'Last run: '+r.generated_at:'Not run yet');
 }catch(e){const x=document.getElementById('bulkResearchDateV30');if(x)x.textContent='Status unavailable'}
})();
</script>
'''
    t=t.replace('</body>',js+'\n<!-- '+MARK+' -->\n</body>',1)
    EXPLORER.write_text(t,encoding='utf-8')
print('Applied V30 slider placement and bulk research status UI')
