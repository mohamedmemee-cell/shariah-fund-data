#!/usr/bin/env python3
import io
import json
import re
from pathlib import Path
from datetime import datetime, timezone

import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources" / "funds.json"
MANUAL = ROOT / "data" / "manual_values.json"
OUTPUT = ROOT / "docs" / "shariah-funds.json"
HISTORY = ROOT / "data" / "history"

HEADERS = {"User-Agent": "ShariahFundDataBot/1.0 (+GitHub Actions; public fund factsheet monitor)"}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def pdf_text(url):
    r = requests.get(url, headers=HEADERS, timeout=40)
    r.raise_for_status()
    reader = PdfReader(io.BytesIO(r.content))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def camissa_values(text, match_name):
    # Camissa consolidated performance sheet normally lists:
    # Fund | 1Y | 3Y | 5Y | 10Y | ... | TER ...
    # We deliberately parse conservatively and reject suspicious rows.
    flat = re.sub(r"[\t ]+", " ", text)
    pos = flat.lower().find(match_name.lower())
    if pos < 0:
        raise ValueError(f"Could not find {match_name!r} in Camissa document")
    snippet = flat[pos:pos + 700]
    nums = [float(x) for x in re.findall(r"(-?\d+(?:\.\d+)?)%", snippet)]
    if len(nums) < 3:
        raise ValueError(f"Not enough percentages found near {match_name!r}")
    one, three, five = nums[0], nums[1], nums[2]
    ten = nums[3] if len(nums) >= 4 and -50 <= nums[3] <= 100 else None
    # TER is often later in the row. Choose a plausible cost percentage from the tail.
    ter = None
    for n in nums[5:]:
        if 0 <= n <= 5:
            ter = n
            break
    for n in (one, three, five):
        if not -60 <= n <= 100:
            raise ValueError("Parsed return outside sanity bounds")
    return {"oneYear": one, "threeYear": three, "fiveYear": five, "tenYear": ten, "ter": ter}


def main():
    registry = load_json(SOURCES)
    manual = load_json(MANUAL)
    values = manual.get("values", {})
    now = datetime.now(timezone.utc)
    generated = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    cache = {}
    output_funds = []

    for f in registry["funds"]:
        base = dict(values.get(f["id"], {}))
        status = "manual"
        error = None
        if f.get("auto_type") == "camissa_performance_pdf":
            try:
                url = f["source_url"]
                if url not in cache:
                    cache[url] = pdf_text(url)
                auto = camissa_values(cache[url], f.get("match_name", f["name"]))
                # Only overwrite fields for which parser returned a value.
                for k, v in auto.items():
                    if v is not None:
                        base[k] = v
                status = "auto"
            except Exception as exc:
                status = "fallback_manual"
                error = str(exc)[:240]

        row = {
            "id": f["id"], "name": f["name"], "manager": f["manager"],
            "category": f["category"], "bucket": f["bucket"],
            "suggested_split": f.get("suggested_split", 0),
            "oneYear": base.get("oneYear"), "threeYear": base.get("threeYear"),
            "fiveYear": base.get("fiveYear"), "tenYear": base.get("tenYear"),
            "ter": base.get("ter"), "source_url": f.get("source_url"),
            "shariah_note": f.get("shariah_note"), "update_status": status,
            "updated": generated if status == "auto" else manual.get("as_of")
        }
        if error:
            row["update_error"] = error
        output_funds.append(row)

    feed = {
        "schema_version": 1,
        "generated_at": generated,
        "currency": "ZAR",
        "disclaimer": "Public fund information for research/planning. Past performance is not a guarantee of future returns. Verify figures against official fund documents before investing.",
        "funds": output_funds
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(feed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    HISTORY.mkdir(parents=True, exist_ok=True)
    snap = HISTORY / f"{now.date().isoformat()}.json"
    snap.write_text(json.dumps(feed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"Snapshot {snap}")
    for x in output_funds:
        print(f"{x['name']}: {x['update_status']}")

if __name__ == "__main__":
    main()
