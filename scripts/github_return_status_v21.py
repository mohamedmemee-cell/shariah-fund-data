#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
MARKER='github-return-status-v21'

CSS=r'''
/* github-return-status-v21 */
.returnStatusV21{margin-top:12px;padding:13px 14px;border:1px solid var(--line);border-radius:11px;background:var(--soft);line-height:1.45}.returnStatusV21 strong{display:block;margin-bottom:3px}.returnStatusV21.ok{border-color:color-mix(in srgb,var(--accent) 45%,var(--line))}.returnStatusV21.warn{border-color:color-mix(in srgb,var(--warn) 45%,var(--line));background:color-mix(in srgb,var(--warn) 8%,var(--card))}.returnStatusV21 a{font-weight:750}.returnStatusV21 .miniActions{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}.returnStatusV21 .miniActions a,.returnStatusV21 .miniActions button{padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--text);text-decoration:none;font:inherit;font-weight:750;cursor:pointer}
'''

DISC_JS=r'''
<script>
/* github-return-status-v21-discovery */
(function(){
 const repo='mohamedmemee-cell/shariah-fund-data', api='https://api.github.com/repos/'+repo;
 const input=document.getElementById('manualSearchForV19'), oldBtn=document.getElementById('manualSearchBtnV19'), box=document.getElementById('manualSearchResultV19');
 if(!input||!oldBtn||!box)return;
 const btn=oldBtn.cloneNode(true);oldBtn.replaceWith(btn);
 function token(){return 'ms-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8)}
 function state(){try{return JSON.parse(localStorage.getItem('manualDiscoveryStateV21')||'null')}catch(e){return null}}
 function save(v){localStorage.setItem('manualDiscoveryStateV21',JSON.stringify(v));localStorage.setItem('manualDiscoveryTokenV19',v.token||'');localStorage.setItem('manualDiscoveryQueryV19',v.query||'')}
 function show(title,text,kind='',issueUrl=''){
   box.className='manualResultV19 show';box.innerHTML=`<div class="returnStatusV21 ${kind}"><strong>${title}</strong><span>${text}</span>${issueUrl?`<div class="miniActions"><a href="${issueUrl}" target="_blank" rel="noopener">Open GitHub request</a></div>`:''}</div>`;
 }
 async function issueFor(tok){
   try{const r=await fetch(api+'/issues?state=all&per_page=100&ts='+Date.now(),{cache:'no-store'});if(!r.ok)return null;const rows=await r.json();return rows.find(x=>x.title==='Discovery search: '+tok)||null}catch(e){return null}
 }
 async function resultFor(tok){try{const r=await fetch('./manual-search-results/'+encodeURIComponent(tok)+'.json?ts='+Date.now(),{cache:'no-store'});return r.ok?await r.json():null}catch(e){return null}}
 async function check(){const s=state();if(!s?.token)return;const result=await resultFor(s.token);if(result){const n=Number(result.count||0);show('Search complete',result.message||`${n} possible investment${n===1?'':'s'} found.`,n?'ok':'');if(n){setTimeout(()=>location.reload(),900)}return}const issue=await issueFor(s.token);if(!issue){show('Waiting for GitHub confirmation',`Search for “${s.query}” has not been submitted yet. Complete the green Create button in GitHub, then return here.`);return}const issueUrl=issue.html_url||('https://github.com/'+repo+'/issues/'+issue.number);if(issue.state==='open'){show('Request received — searching',`GitHub issue #${issue.number} was accepted. The focused search for “${s.query}” is running now.`,'ok',issueUrl);return}show('Search request finished, but no result was published','GitHub completed the request, but the result file is missing. Use Try again below rather than submitting duplicate requests.','warn',issueUrl)}
 btn.addEventListener('click',()=>{const q=(input.value||'').trim();if(!q){show('Enter something to search for','Type a fund name, manager or website first.','warn');return}const tok=token(),body=`Manual discovery search request\n\nSearch token: ${tok}\nSearch for: ${q}\n\nThis request only discovers possible investment products. Any result must still pass the normal Shariah and product verification process before activation.`;save({token:tok,query:q,startedAt:new Date().toISOString()});show('Confirm this search in GitHub',`A GitHub page is opening for “${q}”. Click the green Create button once, then close that tab and return here.`);window.open('https://github.com/'+repo+'/issues/new?title='+encodeURIComponent('Discovery search: '+tok)+'&body='+encodeURIComponent(body),'_blank','noopener');setTimeout(check,1200)});
 window.addEventListener('focus',()=>setTimeout(check,250));document.addEventListener('visibilitychange',()=>{if(!document.hidden)setTimeout(check,250)});if(state()?.token)setTimeout(check,200);
})();
</script>
'''

ADD_JS=r'''
<script>
/* github-return-status-v21-add-fund */
(function(){
 const repo='mohamedmemee-cell/shariah-fund-data', api='https://api.github.com/repos/'+repo;
 const byId=id=>document.getElementById(id), slug=s=>(s||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,100);
 const oldBtn=byId('submit');if(!oldBtn)return;const btn=oldBtn.cloneNode(true);oldBtn.replaceWith(btn);
 let statusBox=document.getElementById('githubReturnAddV21');if(!statusBox){statusBox=document.createElement('div');statusBox.id='githubReturnAddV21';statusBox.className='returnStatusV21 hidden';btn.insertAdjacentElement('afterend',statusBox)}
 function tracked(){try{return JSON.parse(localStorage.getItem('candidateFundTracking')||'null')}catch(e){return null}}
 function save(v){localStorage.setItem('candidateFundTracking',JSON.stringify(v))}
 function show(title,text,kind='',issueUrl=''){statusBox.className='returnStatusV21 '+kind;statusBox.innerHTML=`<strong>${title}</strong><span>${text}</span>${issueUrl?`<div class="miniActions"><a href="${issueUrl}" target="_blank" rel="noopener">Open GitHub request</a></div>`:''}`}
 async function issueFor(name){try{const r=await fetch(api+'/issues?state=all&per_page=100&ts='+Date.now(),{cache:'no-store'});if(!r.ok)return null;const rows=await r.json();return rows.find(x=>x.title==='Candidate fund: '+name)||null}catch(e){return null}}
 async function candidateFor(id){try{const r=await fetch('./candidates/'+encodeURIComponent(id)+'.json?ts='+Date.now(),{cache:'no-store'});return r.ok?await r.json():null}catch(e){return null}}
 async function check(){const t=tracked();if(!t?.name)return;byId('statusCard')?.classList.remove('hidden');byId('statusName').textContent=t.name;byId('statusManager').textContent=t.manager||'Manager not supplied';const row=await candidateFor(t.id||slug(t.name));if(row){show('Onboarding accepted',`Research has started for ${row.name}. Current status: ${(row.status||'researching').replaceAll('_',' ')}.`,'ok');if(typeof poll==='function')try{poll()}catch(e){}return}const issue=await issueFor(t.name);if(!issue){show('Waiting for GitHub confirmation','The onboarding request is prepared but GitHub has not created it yet. Click Continue, then the green Create button in GitHub, close that tab and return here.');return}const issueUrl=issue.html_url||('https://github.com/'+repo+'/issues/'+issue.number);if(issue.state==='open'){show('Request accepted — research queued',`GitHub issue #${issue.number} was created successfully. The automated research workflow is processing this fund now.`,'ok',issueUrl);return}show('GitHub request is closed','The request exists, but no candidate research file was published. Reopen the GitHub issue or start onboarding again only if you intend to retry.','warn',issueUrl)}
 btn.addEventListener('click',()=>{const name=(byId('name')?.value||'').trim();if(!name){alert('Please enter the fund name.');return}const manager=(byId('manager')?.value||'').trim()||'Unknown',website=(byId('website')?.value||'').trim()||'Not supplied',factsheet=(byId('factsheet')?.value||'').trim()||'Not supplied',id=slug(name);save({id,name,manager,website,factsheet,createdAt:new Date().toISOString()});const body=['Candidate fund onboarding request','','Fund name: '+name,'Fund manager: '+manager,'Official fund page: '+website,'Factsheet: '+factsheet].join('\n');show('Confirm this fund in GitHub','A GitHub page will open. Click the green Create button once, then close that tab and return here.');window.open('https://github.com/'+repo+'/issues/new?title='+encodeURIComponent('Candidate fund: '+name)+'&body='+encodeURIComponent(body),'_blank','noopener');setTimeout(check,1200)});
 byId('continueConfirm')?.addEventListener('click',()=>setTimeout(check,1200));byId('refresh')?.addEventListener('click',check);window.addEventListener('focus',()=>setTimeout(check,250));document.addEventListener('visibilitychange',()=>{if(!document.hidden)setTimeout(check,250)});if(tracked()?.name)setTimeout(check,250);
})();
</script>
'''

for filename,js in [('discovery.html',DISC_JS),('add-fund.html',ADD_JS)]:
    p=DOCS/filename
    s=p.read_text(encoding='utf-8')
    if MARKER in s:
        print(filename+': V21 already present')
        continue
    if '</style>' in s:s=s.replace('</style>',CSS+'\n</style>',1)
    s=s.replace('</body>',js+'\n<!-- '+MARKER+' -->\n</body>',1)
    p.write_text(s,encoding='utf-8')
    print(filename+': GitHub return status added')
