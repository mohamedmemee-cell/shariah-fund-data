#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'docs'/'discovery.html'
s=p.read_text(encoding='utf-8')
marker='manual-discovery-search-v19'
if marker in s:
    print('Manual Discovery Search V19 already present')
    raise SystemExit(0)

# Add styles.
css='''
/* manual-discovery-search-v19 */
.manualSearchV19{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:end}.manualSearchV19 label{display:block;font-size:13px;font-weight:750;color:var(--muted);margin-bottom:6px}.manualSearchV19 input{width:100%;padding:12px;border:1px solid var(--line);border-radius:10px;background:transparent;color:inherit;font-size:15px}.manualSearchV19 button{padding:12px 16px;border:1px solid var(--line);border-radius:10px;background:var(--accent);color:#fff;font-weight:800;cursor:pointer}.manualResultV19{margin-top:12px;padding:11px 13px;border-radius:10px;background:var(--soft);display:none}.manualResultV19.show{display:block}.manualResultV19.warn{background:color-mix(in srgb,var(--warn) 10%,var(--card));color:var(--warn)}@media(max-width:700px){.manualSearchV19{grid-template-columns:1fr}.manualSearchV19 button{width:100%}}
'''
s=s.replace('</style>',css+'\n</style>',1)

# Add the search card before the filter card.
anchor='<section class="card"><div class="filters">'
card='''<section class="card" id="manualSearchCardV19">
<h2 style="margin-top:0">Search For</h2>
<p class="muted">Enter specific words, a fund manager, product name, or a website. The system will run a focused web search and add any suitable findings to this Discovery Inbox. Discovery is still not Shariah verification.</p>
<div class="manualSearchV19"><div><label for="manualSearchForV19">Words or website</label><input id="manualSearchForV19" placeholder="e.g. Sentio Shariah fund or https://example.co.za"></div><button id="manualSearchBtnV19" type="button">Search the web</button></div>
<div id="manualSearchResultV19" class="manualResultV19" aria-live="polite"></div>
</section>'''
if anchor not in s: raise SystemExit('Discovery filter anchor not found')
s=s.replace(anchor,card+'\n'+anchor,1)

# Add JS before closing body. Static GitHub Pages cannot directly start Actions, so
# create a prefilled GitHub issue; the issues workflow performs the search and the
# page polls the token-specific result JSON.
js=r'''
<script>
/* manual-discovery-search-v19 */
(function(){
 const input=document.getElementById('manualSearchForV19'),btn=document.getElementById('manualSearchBtnV19'),box=document.getElementById('manualSearchResultV19');
 if(!input||!btn||!box)return;
 const repo='mohamedmemee-cell/shariah-fund-data';
 function token(){return 'ms-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8)}
 function show(t,warn=false){box.textContent=t;box.className='manualResultV19 show'+(warn?' warn':'')}
 async function poll(tok,tries=0){
   try{
     const r=await fetch('./manual-search-results/'+encodeURIComponent(tok)+'.json?ts='+Date.now(),{cache:'no-store'});
     if(r.ok){
       const x=await r.json();
       show(x.message||'Search complete.',Number(x.count||0)===0);
       if(Number(x.count||0)>0){setTimeout(()=>location.reload(),1300)}
       return;
     }
   }catch(e){}
   if(tries<40)setTimeout(()=>poll(tok,tries+1),5000);else show('Search request submitted, but the result has not appeared yet. Refresh this page shortly.',true)
 }
 btn.addEventListener('click',()=>{
   const q=(input.value||'').trim();if(!q){show('Enter words or a website to search for.',true);return}
   const tok=token();localStorage.setItem('manualDiscoveryTokenV19',tok);localStorage.setItem('manualDiscoveryQueryV19',q);
   const body=`Manual discovery search request\n\nSearch token: ${tok}\nSearch for: ${q}\n\nThis request only discovers possible investment products. Any result must still pass the normal Shariah and product verification process before activation.`;
   const u='https://github.com/'+repo+'/issues/new?title='+encodeURIComponent('Discovery search: '+tok)+'&body='+encodeURIComponent(body);
   show('A GitHub confirmation page is opening. Submit the pre-filled issue there, then return here; this page will check for the search result automatically.');
   window.open(u,'_blank','noopener');
   poll(tok,0);
 });
 const saved=localStorage.getItem('manualDiscoveryTokenV19');if(saved){const q=localStorage.getItem('manualDiscoveryQueryV19')||'';show('Checking latest manual search'+(q?' for “'+q+'”':'')+'…');poll(saved,0)}
})();
</script>
'''
s=s.replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied manual Discovery Search UI V19')
