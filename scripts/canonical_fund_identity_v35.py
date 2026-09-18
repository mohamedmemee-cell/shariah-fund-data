#!/usr/bin/env python3
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEED = ROOT / "docs" / "shariah-funds.json"
DISC_DATA = ROOT / "data" / "discovery_candidates.json"
DISC_DOC = ROOT / "docs" / "discovery.json"
ADD = ROOT / "docs" / "add-fund.html"

MARK = "canonical-fund-identity-v35"

def norm(s):
    s=(s or "").lower().replace("shari'ah","shariah").replace("shari’ah","shariah")
    s=re.sub(r"\b(the|fund|portfolio|class|south africa|sa)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def sim(a,b):
    A=set(norm(a).split()); B=set(norm(b).split())
    if not A or not B: return 0
    return len(A&B)/max(1,len(A|B))

if not FEED.exists():
    raise SystemExit("Missing docs/shariah-funds.json")

feed=json.loads(FEED.read_text(encoding="utf-8"))
funds=feed.get("funds",[])

def best_match(name):
    best=None; score=0
    for f in funds:
        sc=sim(name,f.get("name"))
        if sc>score:
            best=f; score=sc
    return best,score

# 1) Discovery is authoritative about whether a candidate is already tracked.
for path in (DISC_DATA, DISC_DOC):
    if not path.exists():
        continue
    payload=json.loads(path.read_text(encoding="utf-8"))
    changed=False
    for row in payload.get("candidates",[]):
        f,score=best_match(row.get("title") or row.get("name"))
        if f and score>=0.72:
            row["status"]="already_tracked"
            row["existing_fund_id"]=f.get("id")
            row["existing_fund_name"]=f.get("name")
            row["canonical_fund_id"]=f.get("id")
            changed=True
    if changed:
        path.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

# 2) Existing Add Fund candidate files are linked to the tracked fund instead of
#    becoming a second verification record.
data_candidates=ROOT/"data"/"candidates"
docs_candidates=ROOT/"docs"/"candidates"
for folder in (data_candidates, docs_candidates):
    if not folder.exists():
        continue
    for path in folder.glob("*.json"):
        if path.name=="index.json":
            continue
        try:
            row=json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        f,score=best_match(row.get("name"))
        if not f or score<0.72:
            continue
        row["status"]="already_tracked"
        row["existing_fund_id"]=f.get("id")
        row["existing_fund_name"]=f.get("name")
        row["canonical_fund_id"]=f.get("id")
        row["activation_ready"]=False
        row["notes"]=list(dict.fromkeys((row.get("notes") or [])+[
            "This candidate matches an existing Fund Explorer record. Verification is maintained on the tracked fund details page; do not duplicate verification in Add Fund."
        ]))
        path.write_text(json.dumps(row,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

# 3) Add Fund UI guardrails: prevent duplicate onboarding and route linked
#    candidates back to their canonical Fund Details record.
s=ADD.read_text(encoding="utf-8")
if MARK not in s:
    css = r'''
<style id="canonicalFundIdentityStylesV35">
.canonicalTrackedV35{margin:12px 0;padding:14px;border:1px solid var(--line);border-radius:12px;background:var(--soft)}
.canonicalTrackedV35 strong{display:block;margin-bottom:5px}
.canonicalTrackedV35 .actions{margin-top:10px}
</style>
'''
    js = r'''
<script id="canonicalFundIdentityV35">
/* canonical-fund-identity-v35 */
(function(){
 const byId=id=>document.getElementById(id);
 const normalise=s=>(s||'').toLowerCase().replaceAll("shari'ah",'shariah').replaceAll('shari’ah','shariah')
   .replace(/\b(the|fund|portfolio|class|south africa|sa)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim();
 function similarity(a,b){
   const A=new Set(normalise(a).split(' ').filter(Boolean)),B=new Set(normalise(b).split(' ').filter(Boolean));
   if(!A.size||!B.size)return 0;let n=0;A.forEach(x=>{if(B.has(x))n++});return n/Math.max(1,new Set([...A,...B]).size)
 }
 async function feed(){
   try{const r=await fetch('./shariah-funds.json?ts='+Date.now(),{cache:'no-store'});return r.ok?(await r.json()).funds||[]:[]}catch(e){return []}
 }
 async function matchTracked(name){
   const rows=await feed();let best=null,score=0;
   rows.forEach(f=>{const s=similarity(name,f.name);if(s>score){score=s;best=f}});
   return best&&score>=0.72?best:null;
 }
 function trackedNotice(f,message){
   if(!f)return;
   const entry=byId('entryCard');
   let box=byId('canonicalTrackedNoticeV35');
   if(!box){
     box=document.createElement('div');box.id='canonicalTrackedNoticeV35';box.className='canonicalTrackedV35';
     entry?.insertAdjacentElement('afterbegin',box);
   }
   box.innerHTML='<strong>Already tracked in Fund Explorer</strong><span>'+(message||'This fund already has one tracked record. Verification and updates belong on its Fund Details page, so you do not need to verify it again here.')+'</span><div class="actions"><a class="btn" href="./fund-details.html?id='+encodeURIComponent(f.id)+'">View tracked fund</a></div>';
   byId('submit')?.setAttribute('disabled','disabled');
 }
 async function linkedCandidate(){
   let t=null;try{t=JSON.parse(localStorage.getItem('candidateFundTracking')||'null')}catch(e){}
   if(!t?.id)return;
   try{
     const r=await fetch('./candidates/'+encodeURIComponent(t.id)+'.json?ts='+Date.now(),{cache:'no-store'});
     if(!r.ok)return;
     const row=await r.json();
     if(row.existing_fund_id||row.canonical_fund_id){
       const id=row.existing_fund_id||row.canonical_fund_id;
       const rows=await feed(),f=rows.find(x=>x.id===id)||{id,name:row.existing_fund_name||row.name};
       const card=byId('statusCard'); if(card)card.classList.add('hidden');
       document.getElementById('reviewWorkspaceV34')?.remove();
       trackedNotice(f,'This candidate matches a fund already tracked in Fund Explorer. Any manual verification already completed on Fund Details is authoritative; Add Fund will not create or request a second verification.');
       try{localStorage.removeItem('candidateFundTracking')}catch(e){}
     }
   }catch(e){}
 }
 async function discoveryGuard(){
   const p=new URLSearchParams(location.search),did=p.get('discovery');if(!did)return;
   try{
     const r=await fetch('./discovery.json?ts='+Date.now(),{cache:'no-store'});if(!r.ok)return;
     const j=await r.json(),row=(j.candidates||[]).find(x=>String(x.id||'')===String(did));
     if(row?.status==='already_tracked'&&row.existing_fund_id){
       location.replace('./fund-details.html?id='+encodeURIComponent(row.existing_fund_id));return;
     }
   }catch(e){}
 }
 function wrapSubmit(){
   const btn=byId('submit');if(!btn||btn.dataset.canonicalGuardV35)return;
   btn.dataset.canonicalGuardV35='1';
   const original=btn.onclick;
   btn.onclick=async function(ev){
     const name=(byId('name')?.value||'').trim();
     if(name){
       const f=await matchTracked(name);
       if(f){
         ev?.preventDefault?.();
         trackedNotice(f);
         return false;
       }
     }
     return original?original.call(this,ev):undefined;
   };
 }
 async function init(){
   await discoveryGuard();
   await linkedCandidate();
   wrapSubmit();
 }
 init();
 window.addEventListener('focus',()=>setTimeout(linkedCandidate,150));
})();
</script>
'''
    s=s.replace("</head>",css+"\n</head>",1)
    s=s.replace("</body>",js+"\n<!-- "+MARK+" -->\n</body>",1)
    ADD.write_text(s,encoding="utf-8")

print("Applied canonical fund identity and duplicate-onboarding guard V35")
