#!/usr/bin/env python3
import json, os, re
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVENT=Path(os.environ.get("GITHUB_EVENT_PATH",""))
DATA_DIR=ROOT/"data"/"candidates"
DOCS_DIR=ROOT/"docs"/"candidates"

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def field(body,name):
    m=re.search(r"^"+re.escape(name)+r":[ \t]*([^\r\n]*)$",body,re.I|re.M)
    return m.group(1).strip() if m else ""
def num(v):
    if not v:return None
    m=re.search(r"-?\d+(?:\.\d+)?",v.replace(",",""))
    return float(m.group(0)) if m else None
def yesno(v):
    x=(v or "").strip().lower()
    if x in ("yes","true","y","eligible","verified"): return True
    if x in ("no","false","n","not eligible","not verified"): return False
    return None

if not EVENT.exists(): raise SystemExit("Missing event")
ev=json.loads(EVENT.read_text(encoding="utf-8"))
issue=ev.get("issue") or {}
title=issue.get("title") or ""
if not title.startswith("Review candidate data:"):
    print("Not a candidate review issue"); raise SystemExit(0)
body=issue.get("body") or ""
cid=field(body,"Candidate id")
if not cid: raise SystemExit("Candidate id missing")
path=DATA_DIR/f"{cid}.json"
if not path.exists(): raise SystemExit("Unknown candidate: "+cid)
row=json.loads(path.read_text(encoding="utf-8"))
f=row.setdefault("findings",{})
perf=f.setdefault("performance",{})

manager=field(body,"Fund manager")
official=field(body,"Official fund page")
factsheet=field(body,"Factsheet")
if manager: row["manager"]=manager
if official: row["source_url"]=official
if factsheet: row["factsheet_url"]=factsheet

risk=field(body,"Risk classification")
ter=num(field(body,"TER"))
minm=num(field(body,"Minimum monthly"))
minl=num(field(body,"Minimum lump sum"))
tfsa=yesno(field(body,"TFSA eligible"))
shariah=yesno(field(body,"Shariah governance verified"))
shsrc=field(body,"Shariah source")
if risk: f["risk_level"]=risk
if ter is not None: f["ter"]=ter
if minm is not None: f["minimum_monthly"]=minm
if minl is not None: f["minimum_lump_sum"]=minl
if tfsa is not None: f["tfsa_eligible"]=tfsa
if shariah is not None:
    f["shariah_language_found"]=shariah
    if shariah:
        f["shariah_evidence"]=field(body,"Shariah evidence") or shsrc or "Manually verified"
if shsrc: row["shariah_source"]=shsrc

for label,key in [("1Y return","oneYear"),("3Y return","threeYear"),("5Y return","fiveYear"),("10Y return","tenYear"),("Since inception return","sinceInception")]:
    v=num(field(body,label))
    if v is not None: perf[key]=v

st=row.setdefault("stages",{})
st["candidate"]="complete"
st["official_sources"]="complete" if row.get("source_url") else "needs_attention"
pc=sum(v is not None for v in perf.values())
st["performance_data"]="complete" if pc>=2 else ("partial" if pc else "needs_attention")
st["fees"]="complete" if f.get("ter") is not None else "needs_attention"
st["minimums"]="complete" if f.get("minimum_monthly") is not None or f.get("minimum_lump_sum") is not None else "needs_attention"
st["tfsa"]="complete" if f.get("tfsa_eligible") is not None else "needs_attention"
st["shariah"]="complete" if f.get("shariah_language_found") and f.get("shariah_evidence") else "needs_attention"
st["automation"]="complete" if row.get("source_url") else "needs_attention"
ready=(st["official_sources"]=="complete" and st["shariah"]=="complete" and st["performance_data"] in ("complete","partial") and st["fees"]=="complete" and st["minimums"]=="complete" and st["tfsa"]=="complete" and bool(f.get("risk_level")))
st["validation"]="ready_for_review" if ready else "needs_review"
row["activation_ready"]=bool(ready)
row["status"]="ready_for_review" if ready else "needs_review"
row["updated_at"]=now()
row.setdefault("manual_reviews",[]).append({"issue_number":issue.get("number"),"reviewed_at":now(),"source":field(body,"Verification source") or official or shsrc or "User supplied"})
text=json.dumps(row,indent=2,ensure_ascii=False)+"\n"
path.write_text(text,encoding="utf-8")
DOCS_DIR.mkdir(parents=True,exist_ok=True)
(DOCS_DIR/f"{cid}.json").write_text(text,encoding="utf-8")
print("Candidate",cid,"=>",row["status"])
