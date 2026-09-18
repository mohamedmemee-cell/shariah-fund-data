#!/usr/bin/env python3
import json, os, re
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVENT=Path(os.environ.get("GITHUB_EVENT_PATH",""))
DATA=ROOT/"data"/"discovery_candidates.json"
DOC=ROOT/"docs"/"discovery.json"

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def field(body,name):
    m=re.search(r"^"+re.escape(name)+r":[ \t]*([^\r\n]*)$",body,re.I|re.M)
    return m.group(1).strip() if m else ""

if not EVENT.exists():
    raise SystemExit("Missing GitHub event")
ev=json.loads(EVENT.read_text(encoding="utf-8"))
issue=ev.get("issue") or {}
title=issue.get("title") or ""
if not title.startswith("Discovery decision:"):
    print("Not a discovery decision issue")
    raise SystemExit(0)
body=issue.get("body") or ""
cid=field(body,"Candidate id")
action=field(body,"Action").lower().replace(" ","_")
reason=field(body,"Reason")
existing_id=field(body,"Existing fund id")
if not cid or action not in {"reject","not_now","already_tracked","restore"}:
    raise SystemExit("Candidate id or valid Action missing")

payload=json.loads(DATA.read_text(encoding="utf-8"))
rows=payload.get("candidates",[])
row=next((x for x in rows if str(x.get("id"))==cid),None)
if row is None:
    raise SystemExit("Unknown discovery candidate: "+cid)

if action=="reject":
    row["status"]="rejected"
    row["rejection"]={"reason":reason or "Not specified","date":now(),"issue_number":issue.get("number")}
elif action=="not_now":
    row["status"]="not_now"
    row["deferred"]={"reason":reason or "Deferred by user","date":now(),"issue_number":issue.get("number")}
elif action=="already_tracked":
    row["status"]="already_tracked"
    row["existing_fund_id"]=existing_id or row.get("existing_fund_id")
    row["tracked_marked_at"]=now()
elif action=="restore":
    row["status"]="needs_verification"
    row.pop("rejection",None)
    row.pop("deferred",None)
row["decision_updated_at"]=now()
payload["generated_at"]=now()
DATA.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
DOC.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("Updated",cid,"to",row["status"])
