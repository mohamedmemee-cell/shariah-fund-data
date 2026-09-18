#!/usr/bin/env python3
import json,re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"discovery_candidates.json"
DOC=ROOT/"docs"/"discovery.json"
FEED=ROOT/"docs"/"shariah-funds.json"

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def norm(s):
    s=(s or "").lower().replace("shari'ah","shariah").replace("shari’ah","shariah")
    s=re.sub(r"\b(the|fund|portfolio|class|south africa|sa)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()
def dom(url):
    return (urlparse(url or "").hostname or "").lower().removeprefix("www.")
def sim(a,b):
    A=set(norm(a).split());B=set(norm(b).split())
    if not A or not B:return 0
    return len(A&B)/max(1,len(A|B))

if not DATA.exists(): raise SystemExit(0)
p=json.loads(DATA.read_text(encoding="utf-8"))
rows=p.get("candidates",[])
feed=json.loads(FEED.read_text(encoding="utf-8")) if FEED.exists() else {"funds":[]}
funds=feed.get("funds",[])

# Carry forward durable decisions by normalized identity even when the same fund
# is rediscovered through another website.
durable={}
for r in rows:
    if r.get("status") in ("rejected","not_now","already_tracked"):
        durable.setdefault(norm(r.get("title")),r)

# Auto-match existing Fund Explorer records.
for r in rows:
    best=None;bestscore=0
    for f in funds:
        sc=sim(r.get("title"),f.get("name"))
        if sc>bestscore:bestscore=sc;best=f
    if best and bestscore>=0.72:
        r["status"]="already_tracked"
        r["existing_fund_id"]=best.get("id")
        r["existing_fund_name"]=best.get("name")
        if best.get("manager"):
            r["manager"]=best.get("manager")
    key=norm(r.get("title"))
    d=durable.get(key)
    if d and d is not r and d.get("status") in ("rejected","not_now"):
        r["status"]=d.get("status")
        if d.get("rejection"):r["rejection"]=d["rejection"]
        if d.get("deferred"):r["deferred"]=d["deferred"]

# Merge duplicate identities while keeping all discovery sources.
groups={}
for r in rows: groups.setdefault(norm(r.get("title")) or r.get("id"),[]).append(r)
out=[]
for key,g in groups.items():
    g.sort(key=lambda x:int(x.get("confidence") or 0),reverse=True)
    base=dict(g[0])
    src=[]
    for x in g:
        u=x.get("url")
        if u and all(z.get("url")!=u for z in src):
            src.append({"url":u,"domain":x.get("domain") or dom(u),"query":x.get("query"),"confidence":x.get("confidence")})
    base["discovery_sources"]=src
    base["discovered_via"]=", ".join(sorted({z.get("domain") for z in src if z.get("domain")}))
    # Prefer durable status across duplicates.
    for x in g:
        if x.get("status")=="rejected":
            base["status"]="rejected";base["rejection"]=x.get("rejection");break
        if x.get("status")=="not_now":
            base["status"]="not_now";base["deferred"]=x.get("deferred")
        if x.get("status")=="already_tracked" and base.get("status") not in ("rejected","not_now"):
            base["status"]="already_tracked";base["existing_fund_id"]=x.get("existing_fund_id");base["existing_fund_name"]=x.get("existing_fund_name")
    out.append(base)
p["candidates"]=out
p["generated_at"]=now()
DATA.write_text(json.dumps(p,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
DOC.write_text(json.dumps(p,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("Reconciled",len(rows),"rows into",len(out),"candidate identities")
