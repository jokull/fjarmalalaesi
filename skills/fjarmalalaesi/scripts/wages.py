#!/usr/bin/env python3
"""Salary benchmarking from Hagstofa's launarannsókn (wage survey) PX-Web API.

The "know your worth" tool: median and percentile wages for full-time
employees by occupation group, plus fine-grained lookup by ÍSTARF95
occupation code. Data lags ~5 months (published each May for the prior
year) — uprate by the Jan 1 contractual raise (kjarasamningar; +3.5% for
2026) when comparing against a current offer.

Wage concepts (compare the right one — differences exceed 20%):
  * grunnlaun         — base day-work salary only
  * regluleg laun     — contracted hours incl. fixed overtime/vaktaálag;
                        compare a plain monthly offer against THIS
  * heildarlaun       — everything incl. occasional overtime and bonuses;
                        compare "total comp" claims against THIS

Stdlib only.

CLI:
    python3 wages.py groups                    # median heildarlaun by occupation group
    python3 wages.py groups --measure regular  # regluleg laun instead
    python3 wages.py percentiles --group 2     # P10/P25/P50/P75/P90 for sérfræðingar
    python3 wages.py occupation 213            # fine-grained ÍSTARF95 code (tölvusérfræðingar)
    python3 wages.py occupation --list         # list ÍSTARF95 codes and names
"""

from __future__ import annotations

import argparse
import json
import urllib.request

BASE = "https://px.hagstofa.is/pxis/api/v1/is/Samfelag/launogtekjur/1_laun/1_laun"

GROUP_NAMES = {
    "0": "Alls (all employees)",
    "1": "Stjórnendur (managers)",
    "2": "Sérfræðingar (professionals)",
    "3": "Tæknar og sérmenntað starfsfólk",
    "4": "Skrifstofufólk",
    "5": "Þjónustu-, sölu- og afgreiðslufólk",
    "6": "Iðnaðarmenn",
    "7": "Véla- og vélgæslufólk",
    "8": "Ósérhæft starfsfólk",
}

# Measure codes differ per table (check each table's metadata before reuse)
MEASURES_VIN02002 = {"total": "7", "regular": "5"}  # heildarlaun / regluleg laun (fullvinnandi)
MEASURES_VIN02004 = {"total": "3", "regular": "1"}  # 0=grunnlaun 1=regluleg 2=regl.heildar 3=heildarlaun

# "Eining" codes in VIN02004: 1=P10, 3=P25, 6=P50, 9=P75, 11=P90
PERCENTILE_CODES = {"P10": "1", "P25": "3", "P50": "6", "P75": "9", "P90": "11"}
MEDIAN_CODE = "2"  # miðgildi in VIN02002


def _query(table: str, query: list[dict]) -> dict:
    body = json.dumps({"query": query, "response": {"format": "json"}}).encode()
    req = urllib.request.Request(
        f"{BASE}/{table}", data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8-sig"))


def _metadata(table: str) -> dict:
    req = urllib.request.Request(f"{BASE}/{table}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8-sig"))


def latest_year(table: str) -> str:
    meta = _metadata(table)
    for var in meta["variables"]:
        if var["code"] == "Ár":
            return var["values"][-1]
    raise RuntimeError("no year variable found")


def cmd_groups(args: argparse.Namespace) -> None:
    year = args.year or latest_year("VIN02002.px")
    data = _query("VIN02002.px", [
        {"code": "Ár", "selection": {"filter": "item", "values": [year]}},
        {"code": "Launþegahópur", "selection": {"filter": "item", "values": ["0"]}},  # almennur + opinber
        {"code": "Starfsstétt", "selection": {"filter": "item", "values": list(GROUP_NAMES)}},
        {"code": "Kyn", "selection": {"filter": "item", "values": ["0"]}},
        {"code": "Laun og vinnutími", "selection": {"filter": "item", "values": [MEASURES_VIN02002[args.measure]]}},
        {"code": "Eining", "selection": {"filter": "item", "values": [MEDIAN_CODE]}},
    ])
    rows = []
    for d in data["data"]:
        group = d["key"][2]
        val = d["values"][0]
        if val not in (".", "..", ""):
            rows.append({"group": GROUP_NAMES.get(group, group), "median_thous_kr": float(val)})
    out = {"year": year, "measure": args.measure, "unit": "þús. kr/mánuði, miðgildi, fullvinnandi", "rows": rows}
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"Median {'heildarlaun' if args.measure == 'total' else 'regluleg laun'}, full-time, {year} (þús. kr/mo):")
    for r in rows:
        print(f"  {r['group']:<42} {r['median_thous_kr']:>7,.0f}")


def cmd_percentiles(args: argparse.Namespace) -> None:
    year = args.year or latest_year("VIN02004.px")
    data = _query("VIN02004.px", [
        {"code": "Ár", "selection": {"filter": "item", "values": [year]}},
        {"code": "Launþegahópur", "selection": {"filter": "item", "values": ["0"]}},
        {"code": "Starfsstétt", "selection": {"filter": "item", "values": [args.group]}},
        {"code": "Kyn", "selection": {"filter": "item", "values": ["0"]}},
        {"code": "Laun og vinnutími", "selection": {"filter": "item", "values": [MEASURES_VIN02004[args.measure]]}},
        {"code": "Eining", "selection": {"filter": "item", "values": list(PERCENTILE_CODES.values())}},
    ])
    code_to_name = {v: k for k, v in PERCENTILE_CODES.items()}
    pcts = {}
    for d in data["data"]:
        eining = d["key"][-1]
        val = d["values"][0]
        if eining in code_to_name and val not in (".", "..", ""):
            pcts[code_to_name[eining]] = float(val)
    out = {"year": year, "group": GROUP_NAMES.get(args.group, args.group),
           "measure": args.measure, "unit": "þús. kr/mánuði, fullvinnandi", "percentiles": pcts}
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"{out['group']}, {year}, {'heildarlaun' if args.measure == 'total' else 'regluleg laun'} (þús. kr/mo):")
    for p in ["P10", "P25", "P50", "P75", "P90"]:
        if p in pcts:
            print(f"  {p}: {pcts[p]:>7,.0f}")


def cmd_occupation(args: argparse.Namespace) -> None:
    meta = _metadata("VIN02001.px")
    starfsstett = next(v for v in meta["variables"] if v["code"] == "Starf")
    if args.list:
        for code, text in zip(starfsstett["values"], starfsstett["valueTexts"]):
            print(f"{code.strip():<8} {text}")
        return
    if not args.code:
        raise SystemExit("give an ÍSTARF95 code (see --list), e.g. 213")
    # Codes in the table carry significant whitespace/asterisks — match by stripped prefix
    matches = [v for v in starfsstett["values"] if v.strip().rstrip("*").strip() == args.code]
    if not matches:
        raise SystemExit(f"code {args.code!r} not found — run with --list to see codes")
    year = args.year or latest_year("VIN02001.px")
    meta_measures = next(v for v in meta["variables"] if v["code"] == "Laun og vinnutími")
    meta_eining = next(v for v in meta["variables"] if v["code"] == "Eining")
    data = _query("VIN02001.px", [
        {"code": "Ár", "selection": {"filter": "item", "values": [year]}},
        {"code": "Starf", "selection": {"filter": "item", "values": matches}},
        {"code": "Kyn", "selection": {"filter": "item", "values": ["0"]}},
    ])
    # Group values by (measure, eining) text for readability
    m_names = dict(zip(meta_measures["values"], meta_measures["valueTexts"]))
    e_names = dict(zip(meta_eining["values"], meta_eining["valueTexts"]))
    label = next(t for v, t in zip(starfsstett["values"], starfsstett["valueTexts"]) if v in matches)
    rows = []
    for d in data["data"]:
        # key: [year, starfsstett, kyn, measure, eining] (order per metadata)
        measure, eining = d["key"][-2], d["key"][-1]
        val = d["values"][0]
        if val not in (".", "..", ""):
            rows.append({"measure": m_names.get(measure, measure), "statistic": e_names.get(eining, eining), "value": float(val)})
    out = {"year": year, "occupation": label, "unit": "þús. kr/mánuði, fullvinnandi", "rows": rows}
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"{label} — {year} (þús. kr/mo, full-time):")
    for r in rows:
        print(f"  {r['measure']:<28} {r['statistic']:<12} {r['value']:>8,.0f}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("groups", help="median wages by 1-digit occupation group")
    sp.add_argument("--measure", choices=["total", "regular"], default="total")
    sp.add_argument("--year", help="default: latest available")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_groups)

    sp = sub.add_parser("percentiles", help="P10–P90 for one occupation group")
    sp.add_argument("--group", default="2", choices=list(GROUP_NAMES),
                    help="0=alls 1=stjórnendur 2=sérfræðingar 4=skrifstofufólk 6=iðnaðarmenn 8=ósérhæft")
    sp.add_argument("--measure", choices=["total", "regular"], default="total")
    sp.add_argument("--year", help="default: latest available")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_percentiles)

    sp = sub.add_parser("occupation", help="fine-grained stats by ÍSTARF95 code")
    sp.add_argument("code", nargs="?", help="ÍSTARF95 code, e.g. 213 (tölvusérfræðingar)")
    sp.add_argument("--list", action="store_true", help="list available codes")
    sp.add_argument("--year", help="default: latest available")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_occupation)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
