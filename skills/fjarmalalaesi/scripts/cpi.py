#!/usr/bin/env python3
"""Fetch Icelandic CPI (vísitala neysluverðs) from Hagstofa's PX-Web API.

Two series matter for mortgage modeling:

  * VIS01000 — headline CPI, keyed by MEASUREMENT month, with YoY change.
  * VIS01004 — "vísitala til verðtryggingar", keyed by the month the value
    APPLIES to loan indexation. By law (14. gr. laga 38/2001) the index
    measured in month M governs verðtrygging from the 1st of month M+2;
    this series has that lag already applied. USE THIS ONE for loan models.

Stdlib only (urllib). Values in the tables are index points, May 1988 = 100.

CLI:
    python3 cpi.py latest            # current indexation value + YoY inflation
    python3 cpi.py indexation -n 24  # last 24 months of VNV til verðtryggingar
    python3 cpi.py headline -n 12    # last 12 months of headline CPI + YoY
    (--json on any subcommand)
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request

BASE = "https://px.hagstofa.is/pxis/api/v1/is/Efnahagur/visitolur/1_vnv/1_vnv"


def _query(table: str, query: list[dict]) -> list[dict]:
    body = json.dumps({"query": query, "response": {"format": "json"}}).encode()
    req = urllib.request.Request(
        f"{BASE}/{table}",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            # PX-Web returns JSON with a BOM sometimes; be tolerant
            return json.loads(resp.read().decode("utf-8-sig"))["data"]
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as e:
        raise SystemExit(
            f"Hagstofa PX-Web unreachable or schema changed ({e}) — see "
            f"references/icelandic-data.md for endpoint details, or read the "
            f"latest CPI release at hagstofa.is manually."
        )


def fetch_indexation(n: int = 24) -> list[dict]:
    """VNV til verðtryggingar — month = when the value governs indexation."""
    data = _query("VIS01004.px", [
        {"code": "Vísitala", "selection": {"filter": "item", "values": ["financial_indexation"]}},
        {"code": "Mánuður", "selection": {"filter": "top", "values": [str(n)]}},
    ])
    return [
        {"effective_month": d["key"][0], "index": float(d["values"][0])}
        for d in data
        if d["values"][0] not in (".", "..", "")
    ]


def fetch_headline(n: int = 12) -> list[dict]:
    """Headline CPI keyed by measurement month, with 12-month inflation."""
    data = _query("VIS01000.px", [
        {"code": "Vísitala", "selection": {"filter": "item", "values": ["CPI"]}},
        {"code": "Liður", "selection": {"filter": "item", "values": ["index", "change_A"]}},
        {"code": "Mánuður", "selection": {"filter": "top", "values": [str(n)]}},
    ])
    months: dict[str, dict] = {}
    for d in data:
        # key layout: [month, series, item] or [month, item] depending on table version
        month, item = d["key"][0], d["key"][-1]
        rec = months.setdefault(month, {"measurement_month": month})
        if d["values"][0] in (".", "..", ""):
            continue
        val = float(d["values"][0])
        if item == "index":
            rec["index"] = val
        elif item == "change_A":
            rec["yoy_inflation_pct"] = val
    return [months[k] for k in sorted(months)]


def cmd_latest(args: argparse.Namespace) -> None:
    idx = fetch_indexation(3)
    head = [m for m in fetch_headline(3) if "yoy_inflation_pct" in m]
    if not idx or not head:
        raise SystemExit("Hagstofa returned no usable data for the latest months — check the tables manually.")
    latest_idx = idx[-1]
    latest_head = head[-1]
    out = {
        "indexation": latest_idx,
        "headline": latest_head,
        "note": "indexation.effective_month is the month this value governs "
                "verðtrygging (measurement month + 2, per 14. gr. laga 38/2001)",
    }
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"VNV til verðtryggingar: {latest_idx['index']} (effective {latest_idx['effective_month']})")
    print(f"Headline CPI: {latest_head.get('index')} measured {latest_head['measurement_month']}, "
          f"YoY inflation {latest_head.get('yoy_inflation_pct')}%")


def cmd_indexation(args: argparse.Namespace) -> None:
    rows = fetch_indexation(args.n)
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    prev = None
    for r in rows:
        mom = f"  ({(r['index'] / prev - 1) * 100:+.3f}% m/m)" if prev else ""
        print(f"{r['effective_month']}: {r['index']}{mom}")
        prev = r["index"]


def cmd_headline(args: argparse.Namespace) -> None:
    rows = fetch_headline(args.n)
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    for r in rows:
        yoy = f"  YoY {r['yoy_inflation_pct']}%" if "yoy_inflation_pct" in r else ""
        print(f"{r['measurement_month']}: {r.get('index', '?')}{yoy}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("latest", help="current indexation value + YoY inflation")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_latest)

    sp = sub.add_parser("indexation", help="VNV til verðtryggingar series (use for loan models)")
    sp.add_argument("-n", type=int, default=24, help="months (default 24)")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_indexation)

    sp = sub.add_parser("headline", help="headline CPI by measurement month")
    sp.add_argument("-n", type=int, default=12, help="months (default 12)")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_headline)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
