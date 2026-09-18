#!/usr/bin/env python3
import json,re
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"candidates"
DOCS=ROOT/"docs"/"candidates"
THIRD={"moneyweb.co.za","invest.alexforbes.com","alexforbes.com"}
HINTS={"27four":"27four","camissa":"Camissa","satrix":"Satrix","old mutual":"Old Mutual","al baraka":"Al Baraka","oasis":"Oasis","stanlib":"STANLIB","sentio":"Sentio","element":"Element Investment Managers","mazi":"Mazi","foord":"Foord","wealthvest":"Wealthvest"}

def host(u): return (urlparse(u or "").hostname or "").lower().removeprefix("www.")
def manager(name,old):
    low=(name or "").lower()
    for k,v in HINTS.items():
        if k in low:return v
    return old if (old or "").lower() not in ("moneyweb","unknown") else "Unknown"

changed=0
for p in DATA.glob("*.json"):
    try:r=json.loads(p.read_text(encoding="utf-8"))
    except Exception:continue
    src=r.get("source_url") or ""
    h=host(src)
    if h in THIRD:
        r["discovery_url"]=r.get("discovery_url") or src
        r["discovered_via"]=r.get("discovered_via") or h
        r["source_url"]=""
        r["manager"]=manager(r.get("name"),r.get("manager"))
        r["status"]="queued"
        r["activation_ready"]=False
        r.setdefault("notes",[]).append("V34: third-party discovery URL separated from official fund source; official source research queued.")
        text=json.dumps(r,indent=2,ensure_ascii=False)+"\n"
        p.write_text(text,encoding="utf-8")
        DOCS.mkdir(parents=True,exist_ok=True)
        (DOCS/p.name).write_text(text,encoding="utf-8")
        changed+=1
print("Requeued",changed,"candidate(s) with third-party discovery sources")
