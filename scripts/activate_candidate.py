#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data" / "candidates"
DOCS_CANDIDATES = ROOT / "docs" / "candidates"
FUNDS = ROOT / "sources" / "funds.json"
MANUAL = ROOT / "data" / "manual_values.json"


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")[:100]


def infer_category(name):
    n = (name or "").lower()
    if "income" in n or "yield" in n:
        return "Income"
    if "balanced" in n or "multi asset" in n or "multi-asset" in n:
        return "Balanced"
    if "equity" in n or "share" in n:
        return "Global Equity" if "global" in n or "world" in n else "Equity"
    return "Other"


def event_candidate_id():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).exists():
        return None
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    issue = event.get("issue") or {}
    title = issue.get("title") or ""
    if not title.lower().startswith("activate fund:"):
        return None
    body = issue.get("body") or ""
    m = re.search(r"^Candidate id:\s*(.+)$", body, re.I | re.M)
    if m:
        return clean(m.group(1))
    return slugify(title.split(":", 1)[1])


def main():
    cid = event_candidate_id()
    if not cid:
        raise SystemExit("No activation candidate id found in issue event")
    candidate_path = CANDIDATES / f"{cid}.json"
    if not candidate_path.exists():
        raise SystemExit(f"Candidate not found: {cid}")
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    if not candidate.get("activation_ready"):
        raise SystemExit("Candidate has not passed the automated activation threshold")

    registry = json.loads(FUNDS.read_text(encoding="utf-8"))
    if any(f.get("id") == cid for f in registry.get("funds", [])):
        print("Fund is already active in sources/funds.json")
    else:
        findings = candidate.get("findings") or {}
        factsheet = candidate.get("factsheet_url") or None
        registry.setdefault("funds", []).append({
            "id": cid,
            "name": candidate.get("name"),
            "manager": candidate.get("manager") or "Unknown",
            "category": infer_category(candidate.get("name")),
            "bucket": "Watchlist",
            "suggested_split": 0,
            "auto_type": "pdf_performance" if factsheet else "page_pdf",
            "source_url": candidate.get("source_url"),
            "factsheet_url": factsheet,
            "risk_level": findings.get("risk_level") or "Unknown",
            "shariah_note": findings.get("shariah_evidence") or "Shariah evidence captured during candidate onboarding; review the official source before investing."
        })
        FUNDS.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manual = json.loads(MANUAL.read_text(encoding="utf-8"))
    perf = (candidate.get("findings") or {}).get("performance") or {}
    manual.setdefault("values", {})[cid] = {
        "oneYear": perf.get("oneYear"),
        "threeYear": perf.get("threeYear"),
        "fiveYear": perf.get("fiveYear"),
        "tenYear": perf.get("tenYear"),
        "sinceInception": perf.get("sinceInception"),
        "ter": (candidate.get("findings") or {}).get("ter"),
        "dataAsOf": None
    }
    manual["as_of"] = datetime.now(timezone.utc).date().isoformat()
    MANUAL.write_text(json.dumps(manual, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    candidate["status"] = "active"
    candidate["activated_at"] = now_iso()
    candidate["updated_at"] = now_iso()
    candidate_path.write_text(json.dumps(candidate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DOCS_CANDIDATES.mkdir(parents=True, exist_ok=True)
    (DOCS_CANDIDATES / f"{cid}.json").write_text(json.dumps(candidate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Activated candidate: {candidate.get('name')}")


if __name__ == "__main__":
    main()
