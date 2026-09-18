#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DISC=ROOT/'docs'/'discovery.html'
ADD=ROOT/'docs'/'add-fund.html'
MARK='discovery-review-workspace-v34'

# Discovery Inbox UI
s=DISC.read_text(encoding='utf-8')
if MARK not in s:
    css=r'''
/* discovery-review-workspace-v34 */
.actionV34{display:inline-flex;align-items:center;justify-content:center;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--text);font-weight:750;font-size:12px;cursor:pointer;text-decoration:none}.actionV34.primary{background:var(--accent);color:#fff;border-color:var(--accent)}.actionV34.warn{border-color:color-mix(in srgb,var(--warn) 45%,var(--line));color:var(--warn)}.reviewPanelV34{display:none;margin-top:8px;padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--soft);font-size:12px;line-height:1.45}.reviewPanelV34.show{display:block}.reviewGridV34{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.reviewGridV34 div{padding:8px;border:1px solid var(--line);border-radius:8px;background:var(--card)}.reviewGridV34 small{display:block;color:var(--muted);margin-bottom:3px}.decisionReasonV34{margin-top:8px;width:100%;padding:8px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--text)}@media(max-width:720px){.reviewGridV34{grid-template-columns:1fr}}
'''
    s=s.replace('</style>',css+'\n</style>',1)
    # add not_now status option
    s=s.replace('<option value="rejected">Rejected</option>','<option value="rejected">Rejected</option><option value="not_now">Not now</option>',1)
    js=r'''
<script>
/* discovery-review-workspace-v34 */
(function(){
 const repo='mohamedmemee-cell/shariah-fund-data';
 const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 function decisionUrl(x,action,reason=''){
   const body=['Discovery candidate decision','',
     'Candidate id: '+(x.id||''),
     'Candidate name: '+(x.title||''),
     'Action: '+action,
     'Reason: '+reason,
     'Existing fund id: '+(x.existing_fund_id||'')
   ].join('\n');
   return 'https://github.com/'+repo+'/issues/new?title='+encodeURIComponent('Discovery decision: '+(x.id||''))+'&body='+encodeURIComponent(body);
 }
 function addFundUrl(x){
   const via=(x.discovered_via||x.domain||'').trim();
   return './add-fund.html?discovery='+encodeURIComponent(x.id||'')+
     '&name='+encodeURIComponent(x.title||'')+
     '&discovered_via='+encodeURIComponent(via)+
     '&discovery_url='+encodeURIComponent(x.url||'');
 }
 function rowActions(x){
   const st=x.status||'needs_verification';
   if(st==='rejected'||st==='not_now'){
     return '<button class="actionV34" data-act="review" data-id="'+esc(x.id)+'">Review</button>'+
       '<a class="actionV34 primary" href="'+decisionUrl(x,'restore')+'">Restore candidate</a>';
   }
   if(st==='already_tracked'){
     const link=x.existing_fund_id?'./fund-details.html?id='+encodeURIComponent(x.existing_fund_id):'./fund-explorer.html';
     return '<a class="actionV34" href="'+link+'">View tracked fund</a>'+
       '<button class="actionV34" data-act="review" data-id="'+esc(x.id)+'">Review</button>';
   }
   return '<button class="actionV34" data-act="review" data-id="'+esc(x.id)+'">Review</button>'+
     '<a class="actionV34 primary" href="'+addFundUrl(x)+'">Add this fund</a>'+
     '<button class="actionV34" data-act="tracked" data-id="'+esc(x.id)+'">Already tracked</button>'+
     '<button class="actionV34" data-act="later" data-id="'+esc(x.id)+'">Not now</button>'+
     '<button class="actionV34 warn" data-act="reject" data-id="'+esc(x.id)+'">Reject</button>';
 }
 function reviewHtml(x){
   const srcs=(x.discovery_sources||[{url:x.url,domain:x.domain,query:x.query,confidence:x.confidence}]).filter(Boolean);
   return '<div class="reviewPanelV34" id="review-'+esc(x.id)+'"><div class="reviewGridV34">'+
     '<div><small>Discovered via</small><b>'+esc(x.discovered_via||x.domain||'—')+'</b></div>'+
     '<div><small>Probable manager</small><b>'+esc(x.manager||'Unverified')+'</b></div>'+
     '<div><small>Discovery confidence</small><b>'+Number(x.confidence||0)+'%</b></div>'+
     '<div><small>Status</small><b>'+esc((x.status||'').replaceAll('_',' '))+'</b></div>'+
     '</div><div style="margin-top:8px"><small class="muted">Discovery sources</small>'+
     srcs.map(z=>'<div><a href="'+esc(z.url||'#')+'" target="_blank" rel="noopener">'+esc(z.domain||z.url||'source')+'</a> · '+Number(z.confidence||0)+'% · '+esc(z.query||'')+'</div>').join('')+
     '</div><p class="muted">Discovery sources are leads only. Add Fund will research the actual manager and official fund/factsheet source before activation.</p></div>';
 }
 const oldRender=window.render;
 window.render=function(){
   const q=document.getElementById('q').value.toLowerCase(),st=document.getElementById('status').value,min=+document.getElementById('confidence').value;
   let a=data.candidates.filter(x=>(!q||(String(x.title)+' '+String(x.manager)+' '+String(x.domain)).toLowerCase().includes(q))&&(!st||x.status===st)&&Number(x.confidence||0)>=min);
   a.sort((x,y)=>Number(y.confidence||0)-Number(x.confidence||0));
   document.getElementById('rows').innerHTML=a.length?a.map(x=>'<tr><td><b>'+esc(x.title)+'</b><br><small class="muted">'+esc(x.domain||'')+'</small>'+reviewHtml(x)+'</td><td>'+esc(x.manager||'Unverified')+'</td><td><span class="pill">'+esc((x.status||'').replaceAll('_',' '))+'</span></td><td class="score">'+Number(x.confidence||0)+'%</td><td>'+esc((x.reasons||[]).join(' · '))+'</td><td><small>'+esc(x.query||'')+'</small></td><td><div class="actionsV18">'+rowActions(x)+'</div></td></tr>').join(''):'<tr><td colspan="7">No candidates match these filters.</td></tr>';
   const all=data.candidates;document.getElementById('count').textContent=all.length;document.getElementById('review').textContent=all.filter(x=>x.status==='needs_verification').length;document.getElementById('tracked').textContent=all.filter(x=>x.status==='already_tracked').length;document.getElementById('scan').textContent=data.generated_at||'—';
 };
 document.addEventListener('click',e=>{
   const b=e.target.closest('[data-act]');if(!b)return;
   const x=data.candidates.find(z=>String(z.id)===String(b.dataset.id));if(!x)return;
   const act=b.dataset.act;
   if(act==='review'){document.getElementById('review-'+x.id)?.classList.toggle('show');return}
   if(act==='tracked'){
     const id=prompt('Optional: enter the existing Fund Explorer id, or leave blank.');
     window.open(decisionUrl({...x,existing_fund_id:id||''},'already_tracked'),'_blank','noopener');return;
   }
   if(act==='later'){
     const reason=prompt('Optional note for “Not now”:')||'Deferred by user';
     window.open(decisionUrl(x,'not_now',reason),'_blank','noopener');return;
   }
   if(act==='reject'){
     const reason=prompt('Why reject this candidate? Examples: Not Shariah compliant, Duplicate, Not an investment fund, Not relevant, Outside scope, Other.');
     if(reason===null)return;
     window.open(decisionUrl(x,'reject',reason||'Other'),'_blank','noopener');return;
   }
 });
 setTimeout(()=>{if(typeof render==='function')render()},350);
})();
</script>
'''
    s=s.replace('</body>',js+'\n<!-- '+MARK+' -->\n</body>',1)
    DISC.write_text(s,encoding='utf-8')

# Add Fund review workspace + discovery source separation
a=ADD.read_text(encoding='utf-8')
if MARK not in a:
    css=r'''
/* discovery-review-workspace-v34 */
.discoverySourceV34{margin:12px 0;padding:12px;border:1px solid var(--line);border-radius:11px;background:var(--soft)}.reviewWorkspaceV34{margin-top:16px;padding:16px;border:1px solid var(--line);border-radius:14px;background:color-mix(in srgb,var(--soft) 45%,var(--card))}.reviewFieldsV34{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.reviewFieldsV34 label{display:block;color:var(--muted);font-size:12px;font-weight:750}.reviewFieldsV34 input,.reviewFieldsV34 select{width:100%;margin-top:5px;padding:10px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--text)}.missingV34{color:var(--red);font-weight:750}.verifiedV34{color:var(--accent);font-weight:750}@media(max-width:720px){.reviewFieldsV34{grid-template-columns:1fr}}
'''
    a=a.replace('</style>',css+'\n</style>',1)
    js=r'''
<script>
/* discovery-review-workspace-v34 */
(function(){
 const repo='mohamedmemee-cell/shariah-fund-data',byId=id=>document.getElementById(id);
 const p=new URLSearchParams(location.search),disc=p.get('discovery');
 const via=p.get('discovered_via')||'',durl=p.get('discovery_url')||'';
 if(disc){
   // Discovery is a lead, not the official source. Do not treat a third-party site
   // as the fund manager or official page.
   if(byId('manager'))byId('manager').value='';
   if(byId('website'))byId('website').value='';
   const box=byId('discoveryPrefill');
   if(box){
     box.classList.remove('hidden');
     box.innerHTML='<b>From Discovery Inbox</b><br>Discovered via <b>'+(via||'web search')+'</b>. This source is a lead only; onboarding will identify the actual fund manager and official source.'+(durl?' <a href="'+durl+'" target="_blank" rel="noopener">Open discovery source</a>':'');
   }
 }
 function val(x){return x==null?'':String(x)}
 function createWorkspace(row){
   let w=byId('candidateReviewV34');if(!w){w=document.createElement('div');w.id='candidateReviewV34';w.className='reviewWorkspaceV34';byId('statusCard')?.appendChild(w)}
   const f=row.findings||{},perf=f.performance||{},st=row.stages||{};
   const status=(k)=>st[k]==='complete'||st[k]==='ready_for_review'?'<span class="verifiedV34">Verified</span>':'<span class="missingV34">Needs review</span>';
   w.innerHTML='<h3 style="margin-top:0">Review & verify candidate information</h3><p class="muted">Items marked “Needs review” are the pieces automation could not verify. You can correct or complete them below, then save one verification request.</p>'+
   '<div class="reviewFieldsV34">'+
   '<label>Fund manager '+status('official_sources')+'<input id="rvManagerV34" value="'+val(row.manager||'')+'"></label>'+
   '<label>Official fund page '+status('official_sources')+'<input id="rvOfficialV34" value="'+val(row.source_url||'')+'"></label>'+
   '<label>Factsheet<input id="rvFactsheetV34" value="'+val(row.factsheet_url||'')+'"></label>'+
   '<label>Risk classification '+(f.risk_level?'<span class="verifiedV34">Verified</span>':'<span class="missingV34">Needs review</span>')+'<input id="rvRiskV34" value="'+val(f.risk_level||'')+'"></label>'+
   '<label>TER % '+status('fees')+'<input id="rvTerV34" value="'+val(f.ter??'')+'"></label>'+
   '<label>Minimum monthly (R) '+status('minimums')+'<input id="rvMinMV34" value="'+val(f.minimum_monthly??'')+'"></label>'+
   '<label>Minimum lump sum (R)<input id="rvMinLV34" value="'+val(f.minimum_lump_sum??'')+'"></label>'+
   '<label>TFSA eligible '+status('tfsa')+'<select id="rvTfsaV34"><option value="">Not verified</option><option value="Yes">Yes</option><option value="No">No</option></select></label>'+
   '<label>1Y return %<input id="rv1V34" value="'+val(perf.oneYear??'')+'"></label>'+
   '<label>3Y return %<input id="rv3V34" value="'+val(perf.threeYear??'')+'"></label>'+
   '<label>5Y return %<input id="rv5V34" value="'+val(perf.fiveYear??'')+'"></label>'+
   '<label>10Y return %<input id="rv10V34" value="'+val(perf.tenYear??'')+'"></label>'+
   '<label>Shariah governance verified '+status('shariah')+'<select id="rvShariahV34"><option value="">Not verified</option><option value="Yes">Yes</option><option value="No">No</option></select></label>'+
   '<label>Shariah source<input id="rvShariahSrcV34" value="'+val(row.shariah_source||'')+'"></label>'+
   '</div><div class="actions"><button class="btn" id="saveReviewV34" type="button">Save verification</button></div>';
   if(f.tfsa_eligible===true)byId('rvTfsaV34').value='Yes';if(f.tfsa_eligible===false)byId('rvTfsaV34').value='No';
   if(f.shariah_language_found&&f.shariah_evidence)byId('rvShariahV34').value='Yes';
   byId('saveReviewV34').onclick=()=>{
     const g=id=>(byId(id)?.value||'').trim();
     const body=['Candidate review','',
       'Candidate id: '+row.id,
       'Fund manager: '+g('rvManagerV34'),
       'Official fund page: '+g('rvOfficialV34'),
       'Factsheet: '+g('rvFactsheetV34'),
       'Risk classification: '+g('rvRiskV34'),
       'TER: '+g('rvTerV34'),
       'Minimum monthly: '+g('rvMinMV34'),
       'Minimum lump sum: '+g('rvMinLV34'),
       'TFSA eligible: '+g('rvTfsaV34'),
       '1Y return: '+g('rv1V34'),
       '3Y return: '+g('rv3V34'),
       '5Y return: '+g('rv5V34'),
       '10Y return: '+g('rv10V34'),
       'Shariah governance verified: '+g('rvShariahV34'),
       'Shariah source: '+g('rvShariahSrcV34'),
       'Shariah evidence: '+(f.shariah_evidence||''),
       'Verification source: '+(g('rvOfficialV34')||g('rvShariahSrcV34')||'User supplied')
     ].join('\n');
     window.open('https://github.com/'+repo+'/issues/new?title='+encodeURIComponent('Review candidate data: '+row.name)+'&body='+encodeURIComponent(body),'_blank','noopener');
   };
 }
 async function sync(){
   let t=null;try{t=JSON.parse(localStorage.getItem('candidateFundTracking')||'null')}catch(e){}
   if(!t?.id)return;
   try{const r=await fetch('./candidates/'+encodeURIComponent(t.id)+'.json?ts='+Date.now(),{cache:'no-store'});if(r.ok)createWorkspace(await r.json())}catch(e){}
 }
 byId('refresh')?.addEventListener('click',()=>setTimeout(sync,80));
 window.addEventListener('focus',()=>setTimeout(sync,200));
 setTimeout(sync,350);
})();
</script>
'''
    a=a.replace('</body>',js+'\n<!-- '+MARK+' -->\n</body>',1)
    ADD.write_text(a,encoding='utf-8')
print('Applied Discovery decisions and candidate review workspace V34')
