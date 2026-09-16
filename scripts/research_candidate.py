#!/usr/bin/env python3
import io
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "candidates"
DOCS_DIR = ROOT / "docs" / "candidates"
SOURCE_DIR = ROOT / "sources" / "candidates"
INDEX = DOCS_DIR / "index.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ShariahFundCandidateBot/1.0; +GitHub Actions)",
    "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.8",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def slugify(value):
    value = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return value[:100] or "candidate-fund"


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def money_value(text, patterns):
    for pat in patterns:
        m = re.search(pat, text, re.I | re.S)
        if m:
            raw = m.group(1).replace(",", "").replace(" ", "")
            try:
                return float(raw)
            except ValueError:
                pass
    return None


def percent_value(text, patterns):
    for pat in patterns:
        m = re.search(pat, text, re.I | re.S)
        if m:
            try:
                value = float(m.group(1))
                if -100 <= value <= 100:
                    return value
            except ValueError:
                pass
    return None


def get(url):
    r = requests.get(url, headers=HEADERS, timeout=35, allow_redirects=True)
    r.raise_for_status()
    return r


def pdf_text(url):
    r = get(url)
    if not r.content.startswith(b"%PDF"):
        raise ValueError("URL did not return a PDF")
    reader = PdfReader(io.BytesIO(r.content))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def discover_factsheet(page_url, soup, fund_name):
    words = [w for w in re.findall(r"[a-z0-9]+", fund_name.lower()) if len(w) > 3]
    best = None
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"])
        label = clean(" ".join(a.stripped_strings)).lower()
        href_l = href.lower()
        if ".pdf" not in href_l:
            continue
        score = 0
        if any(k in label for k in ("factsheet", "fact sheet", "fund fact", "mdd", "minimum disclosure", "monthly")):
            score += 8
        score += sum(2 for w in words if w in label or w in href_l)
        if best is None or score > best[0]:
            best = (score, href)
    return best[1] if best and best[0] >= 4 else None


def extract_board_snippet(text):
    flat = clean(text)
    patterns = [
        r"(.{0,180}(?:shari['’]?ah|shariah)\s+(?:supervisory\s+)?(?:board|committee).{0,360})",
        r"(.{0,180}(?:shari['’]?ah|shariah)\s+(?:advisor|adviser|scholar).{0,360})",
    ]
    for pat in patterns:
        m = re.search(pat, flat, re.I)
        if m:
            return clean(m.group(1))[:520]
    return None


def extract_risk(text):
    flat = clean(text)
    for label in (
        "Aggressive", "High", "Medium High", "Moderate to High", "Moderate-High",
        "Moderate", "Medium", "Low-Medium", "Low to Moderate", "Low"
    ):
        if re.search(rf"\b{re.escape(label)}\b", flat, re.I):
            return label
    return None


def extract_performance(text):
    flat = clean(text)
    specs = {
        "oneYear": [r"(?:1\s*year|1[-\s]*yr|one\s*year)[^\d-]{0,90}(-?\d+(?:\.\d+)?)\s*%"],
        "threeYear": [r"(?:3\s*year|3[-\s]*yr|three\s*year)[^\d-]{0,90}(-?\d+(?:\.\d+)?)\s*%"],
        "fiveYear": [r"(?:5\s*year|5[-\s]*yr|five\s*year)[^\d-]{0,90}(-?\d+(?:\.\d+)?)\s*%"],
        "tenYear": [r"(?:10\s*year|10[-\s]*yr|ten\s*year)[^\d-]{0,90}(-?\d+(?:\.\d+)?)\s*%"],
        "sinceInception": [r"(?:since\s+inception|inception)[^\d-]{0,90}(-?\d+(?:\.\d+)?)\s*%"],
    }
    return {k: percent_value(flat, pats) for k, pats in specs.items()}


def extract_fields(text):
    flat = clean(text)
    ter = percent_value(flat, [
        r"(?:total\s+expense\s+ratio|\bTER\b)[^\d]{0,60}(\d+(?:\.\d+)?)\s*%",
    ])
    min_monthly = money_value(flat, [
        r"(?:minimum\s+(?:monthly|recurring|debit\s+order)[^R\d]{0,80}(?:R|ZAR)\s*)([\d ,]+(?:\.\d+)?)",
        r"(?:monthly\s+minimum[^R\d]{0,80}(?:R|ZAR)\s*)([\d ,]+(?:\.\d+)?)",
    ])
    min_lump = money_value(flat, [
        r"(?:minimum\s+(?:initial|lump\s*sum|once[-\s]*off)[^R\d]{0,80}(?:R|ZAR)\s*)([\d ,]+(?:\.\d+)?)",
        r"(?:lump\s*sum\s+minimum[^R\d]{0,80}(?:R|ZAR)\s*)([\d ,]+(?:\.\d+)?)",
    ])
    tfsa = None
    if re.search(r"(?:tax[-\s]*free\s+savings\s+account|\bTFSA\b)", flat, re.I):
        tfsa = not bool(re.search(r"(?:not\s+(?:available|eligible)|ineligible)[^\.]{0,60}(?:tax[-\s]*free|TFSA)", flat, re.I))
    shariah = bool(re.search(r"\b(?:shari['’]?ah|shariah|islamic)\b", flat, re.I))
    return {
        "ter": ter,
        "minimum_monthly": min_monthly,
        "minimum_lump_sum": min_lump,
        "tfsa_eligible": tfsa,
        "risk_level": extract_risk(flat),
        "shariah_evidence": extract_board_snippet(flat),
        "shariah_language_found": shariah,
        "performance": extract_performance(flat),
    }


def parse_issue_candidate():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).exists():
        return None
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    issue = event.get("issue") or {}
    title = issue.get("title") or ""
    if not title.lower().startswith("candidate fund:"):
        return None
    body = issue.get("body") or ""

    def value(label):
        m = re.search(rf"^{re.escape(label)}:\s*(.+)$", body, re.I | re.M)
        return clean(m.group(1)) if m else ""

    name = clean(title.split(":", 1)[1]) or value("Fund name")
    return {
        "id": slugify(name),
        "name": name,
        "manager": value("Fund manager") or "Unknown",
        "source_url": value("Official fund page") if value("Official fund page") != "Not supplied" else "",
        "factsheet_url": value("Factsheet") if value("Factsheet") != "Not supplied" else "",
        "issue_number": issue.get("number"),
        "status": "queued",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }


def research(candidate):
    candidate = dict(candidate)
    candidate["status"] = "researching"
    candidate["updated_at"] = now_iso()
    notes = []
    source_url = candidate.get("source_url") or ""
    factsheet_url = candidate.get("factsheet_url") or ""
    combined = ""
    resolved_source = source_url
    page_ok = False
    factsheet_ok = False

    if source_url:
        try:
            response = get(source_url)
            page_ok = True
            resolved_source = response.url
            soup = BeautifulSoup(response.text, "html.parser")
            combined += "\n" + soup.get_text(" ", strip=True)
            if not factsheet_url:
                factsheet_url = discover_factsheet(response.url, soup, candidate.get("name", "")) or ""
        except Exception as exc:
            notes.append(f"Official fund page could not be read automatically: {str(exc)[:180]}")
    else:
        notes.append("No official fund page was supplied.")

    if factsheet_url:
        try:
            combined += "\n" + pdf_text(factsheet_url)
            factsheet_ok = True
        except Exception as exc:
            notes.append(f"Factsheet could not be parsed automatically: {str(exc)[:180]}")

    findings = extract_fields(combined) if combined else {
        "ter": None, "minimum_monthly": None, "minimum_lump_sum": None,
        "tfsa_eligible": None, "risk_level": None, "shariah_evidence": None,
        "shariah_language_found": False,
        "performance": {"oneYear": None, "threeYear": None, "fiveYear": None, "tenYear": None, "sinceInception": None},
    }

    performance_found = sum(v is not None for v in findings["performance"].values())
    stages = {
        "candidate": "complete",
        "official_sources": "complete" if page_ok else "needs_attention",
        "performance_data": "complete" if performance_found >= 2 else ("partial" if performance_found else "needs_attention"),
        "fees": "complete" if findings.get("ter") is not None else "needs_attention",
        "minimums": "complete" if findings.get("minimum_monthly") is not None or findings.get("minimum_lump_sum") is not None else "needs_attention",
        "tfsa": "complete" if findings.get("tfsa_eligible") is not None else "needs_attention",
        "shariah": "complete" if findings.get("shariah_language_found") and findings.get("shariah_evidence") else ("partial" if findings.get("shariah_language_found") else "needs_attention"),
        "automation": "complete" if page_ok else "needs_attention",
    }

    activation_ready = (
        stages["official_sources"] == "complete"
        and stages["shariah"] == "complete"
        and stages["performance_data"] in ("complete", "partial")
        and stages["fees"] == "complete"
    )
    stages["validation"] = "ready_for_review" if activation_ready else "needs_review"

    candidate.update({
        "source_url": resolved_source or source_url,
        "factsheet_url": factsheet_url,
        "findings": findings,
        "stages": stages,
        "activation_ready": activation_ready,
        "status": "ready_for_review" if activation_ready else "needs_review",
        "notes": notes,
        "updated_at": now_iso(),
    })

    config = {
        "id": candidate["id"],
        "name": candidate["name"],
        "manager": candidate.get("manager"),
        "source_url": candidate.get("source_url"),
        "factsheet_url": candidate.get("factsheet_url"),
        "extractor": "generic_official_source_v1",
        "status": "configured" if page_ok else "needs_source",
        "configured_at": now_iso(),
    }
    return candidate, config


def write_candidate(candidate, config=None):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(candidate, indent=2, ensure_ascii=False) + "\n"
    (DATA_DIR / f"{candidate['id']}.json").write_text(payload, encoding="utf-8")
    (DOCS_DIR / f"{candidate['id']}.json").write_text(payload, encoding="utf-8")
    if config:
        (SOURCE_DIR / f"{candidate['id']}.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rebuild_index():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(DATA_DIR.glob("*.json")):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
            rows.append({
                "id": row.get("id"), "name": row.get("name"), "manager": row.get("manager"),
                "status": row.get("status"), "activation_ready": row.get("activation_ready", False),
                "updated_at": row.get("updated_at"), "issue_number": row.get("issue_number"),
            })
        except Exception:
            continue
    INDEX.write_text(json.dumps({"generated_at": now_iso(), "candidates": rows}, indent=2) + "\n", encoding="utf-8")


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    candidate = parse_issue_candidate()
    if candidate:
        write_candidate(candidate)
        targets = [DATA_DIR / f"{candidate['id']}.json"]
    else:
        targets = []
        for path in DATA_DIR.glob("*.json"):
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
                if row.get("status") == "queued":
                    targets.append(path)
            except Exception:
                pass

    if not targets:
        rebuild_index()
        print("No queued candidate funds to research.")
        return

    for path in targets:
        row = json.loads(path.read_text(encoding="utf-8"))
        print(f"Researching candidate: {row.get('name')}")
        researched, config = research(row)
        write_candidate(researched, config)
        print(f"Candidate status: {researched.get('status')}")

    rebuild_index()


if __name__ == "__main__":
    main()
