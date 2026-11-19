"""Build long-format CSVs from NCSES National Patterns of R&D Resources 2023-24 (NSF 26-313).

Run with:  python -I scripts/natpat_build.py <xlsx_dir> <out_dir>

Inputs: nsf26313-tab001.xlsx ... tab009.xlsx (Excel data tables).
Outputs:
  natpat_character_source_performer.csv   source x performer cells and published totals
  natpat_business_performer_funding_detail.csv  business-performer sub-sources (tables 2-5 only)
  natpat_deflator.csv                     GDP implicit price deflator from table 1
  natpat_checks.txt                       sum and cross-table checks
"""
import csv
import os
import re
import sys
from collections import defaultdict

import openpyxl

XLSX, OUT = sys.argv[1], sys.argv[2]
REL = "nsf26313"

CHAR_BY_SOURCE = {6: "total", 7: "basic", 8: "applied", 9: "development"}
CHAR_BY_PERF = {2: "total", 3: "basic", 4: "applied", 5: "development"}

SRC = {
    "All funding sources": "all_sources",
    "Federal": "federal",
    "Nonfederal government": "nonfederal_government",
    "Business": "business",
    "Higher education": "higher_education",
    "Nonprofit": "nonprofit",
}
PERF = {
    "All performers": "all_performers",
    "Total": "all_performers",
    "Federal intramural": "federal_intramural",
    "FFRDC": "ffrdc",
    "FFRDCs": "ffrdc",
    "Nonfederal government": "nonfederal_government",
    "Business": "business",
    "Higher education": "higher_education",
    "Nonprofit": "nonprofit",
    "All federal": "all_federal_performers",
}
# Table 2-5 business-performer sub-sources that tables 6-9 fold into broader sources.
BIZ_SUB = {
    "Own domestic": "business_own_domestic",
    "Other domestic business": "business_other_domestic",
    "Foreign business": "business_foreign",
    "Other": "other",
}

FOOTNOTE_LABELS = {
    "Federal intramurala": "Federal intramural",
    "FFRDCsb": "FFRDCs",
    "Nonfederal governmentc": "Nonfederal government",
    "Businessd": "Business",
    "Higher educatione": "Higher education",
    "Nonprofitf": "Nonprofit",
    "Totalg": "Total",
}


def clean(label):
    if label is None:
        return None
    label = str(label).strip()
    return FOOTNOTE_LABELS.get(label, label)


def read_table(n):
    path = os.path.join(XLSX, f"{REL}-tab{n:03d}.xlsx")
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    title = rows[1][0]
    top, sub = rows[3], rows[4]
    groups, g = [], None
    for v in top:
        if v is not None:
            g = clean(v)
        groups.append(g)
    cols = [(groups[i], clean(sub[i])) for i in range(len(sub))]
    section, data = None, []
    for r in rows[5:]:
        lab = r[0]
        if lab is None:
            continue
        if isinstance(lab, str) and "millions" in lab:
            section = "constant" if lab.startswith("Constant") else "current"
            continue
        m = re.match(r"^(\d{4})([a-z]?)$", str(lab).replace(".0", ""))
        if not m:
            raise ValueError(f"table {n}: unexpected row label {lab!r}")
        year, flag = int(m.group(1)), m.group(2)
        for i in range(1, len(cols)):
            data.append((section, year, flag, cols[i], r[i]))
    return title, data


def status(year):
    if year <= 2022:
        return "actual"
    if year == 2023:
        return "preliminary"
    return "estimated"


def num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if str(v).strip() == "NA":
        return "NA"
    raise ValueError(f"unexpected cell {v!r}")


def main():
    os.makedirs(OUT, exist_ok=True)
    cells = {}  # (year, char, src, perf) -> {current, constant, table}
    flags_seen = defaultdict(set)
    titles = {}

    # Tables 6-9: source x performer
    for t, ch in CHAR_BY_SOURCE.items():
        title, data = read_table(t)
        titles[t] = title
        for section, year, flag, (grp, sublab), v in data:
            flags_seen[t].add((year, flag))
            if grp == "All funding sources":
                src, perf = "all_sources", "all_performers"
            else:
                src, perf = SRC[grp], PERF[sublab]
            k = (year, ch, src, perf)
            cells.setdefault(k, {"table": f"T{t}"})[section] = num(v)

    # Tables 2-5: performer x source. Keep only what tables 6-9 lack:
    # performer totals (all_sources x performer) and the all-federal-performer group.
    # Everything else is used to cross-check.
    biz_detail = {}
    cross = []
    for t, ch in CHAR_BY_PERF.items():
        title, data = read_table(t)
        titles[t] = title
        for section, year, flag, (grp, sublab), v in data:
            flags_seen[t].add((year, flag))
            if grp == "All performers":
                perf, src = "all_performers", "all_sources"
            else:
                perf = PERF[grp]
                if sublab == "Total":
                    src = "all_sources"
                elif perf == "business" and sublab in BIZ_SUB:
                    k = (year, ch, BIZ_SUB[sublab], "business")
                    biz_detail.setdefault(k, {"table": f"T{t}"})[section] = num(v)
                    continue
                else:
                    src = SRC[sublab]
            k = (year, ch, src, perf)
            val = num(v)
            if k in cells and cells[k]["table"] in ("T6", "T7", "T8", "T9"):
                cross.append((k, section, cells[k].get(section), val, f"T{t}"))
                continue
            cells.setdefault(k, {"table": f"T{t}"})[section] = val

    # Table 1: deflator
    ws = openpyxl.load_workbook(os.path.join(XLSX, f"{REL}-tab001.xlsx"), data_only=True).worksheets[0]
    t1 = list(ws.iter_rows(values_only=True))
    titles[1] = t1[1][0]
    defl = []
    for r in t1[6:]:
        if r[0] is None:
            continue
        m = re.match(r"^(\d{4})([a-z]?)$", str(r[0]).replace(".0", ""))
        if not m:
            continue
        y = int(m.group(1))
        defl.append({
            "year": y, "deflator": r[3], "base_year": 2017,
            "gdp_usd_billions_nominal": r[1], "gdp_usd_billions_constant2017": r[2],
            "total_rd_usd_billions_nominal": r[4], "total_rd_usd_billions_constant2017": r[5],
            "status": status(y),
        })
    with open(os.path.join(OUT, "natpat_deflator.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(defl[0]))
        w.writeheader()
        w.writerows(defl)

    def fmt(x):
        if x is None or x == "NA":
            return ""
        return f"{x:.0f}" if float(x).is_integer() else str(x)

    order_c = {"basic": 0, "applied": 1, "development": 2, "total": 3}
    order_s = {s: i for i, s in enumerate(["all_sources", "federal", "nonfederal_government", "business", "higher_education", "nonprofit"])}
    order_p = {p: i for i, p in enumerate(["all_performers", "all_federal_performers", "federal_intramural", "ffrdc", "nonfederal_government", "business", "higher_education", "nonprofit"])}

    fields = ["year", "character", "source_of_funds", "performer", "value_usd_millions_nominal",
              "status", "value_usd_millions_constant2017", "not_available", "table_id"]
    na_count = 0
    with open(os.path.join(OUT, "natpat_character_source_performer.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for k in sorted(cells, key=lambda k: (k[0], order_c[k[1]], order_s[k[2]], order_p[k[3]])):
            c = cells[k]
            na = c.get("current") == "NA"
            na_count += na
            w.writerow([k[0], k[1], k[2], k[3], fmt(c.get("current")), status(k[0]),
                        fmt(c.get("constant")), "NA" if na else "", f"{REL}-tab{int(c['table'][1:]):03d}"])

    with open(os.path.join(OUT, "natpat_business_performer_funding_detail.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for k in sorted(biz_detail, key=lambda k: (k[0], order_c[k[1]], k[2])):
            c = biz_detail[k]
            na = c.get("current") == "NA"
            w.writerow([k[0], k[1], k[2], k[3], fmt(c.get("current")), status(k[0]),
                        fmt(c.get("constant")), "NA" if na else "", f"{REL}-tab{int(c['table'][1:]):03d}"])

    # ---- checks ----
    out = []
    P = lambda *a: out.append(" ".join(str(x) for x in a))
    P("Titles:")
    for t in sorted(titles):
        P(f"  table {t}: {titles[t]}")
    P("Year flags seen:", sorted({(y, f) for t in flags_seen for (y, f) in flags_seen[t] if f}))
    years = sorted({k[0] for k in cells})
    P("Years:", years[0], "-", years[-1], "count", len(years))
    P("Cells written:", len(cells), "NA cells:", na_count)

    def v(y, ch, s, p, sec="current"):
        x = cells.get((y, ch, s, p), {}).get(sec)
        return 0.0 if x in (None, "NA") else x

    srcs = ["federal", "nonfederal_government", "business", "higher_education", "nonprofit"]
    perfs = ["federal_intramural", "ffrdc", "nonfederal_government", "business", "higher_education", "nonprofit"]
    chars = ["basic", "applied", "development"]

    P("\nCross-table mismatches (T6-9 vs T2-5 at the same source x performer), |diff|>0:")
    mm = [(k, s, a, b, t) for (k, s, a, b, t) in cross if a != b and not (a == "NA" and b in ("NA", None))]
    P("  count:", len(mm), "of", len(cross))
    for k, s, a, b, t in mm[:40]:
        P("  ", k, s, "T6-9:", a, f"{t}:", b)

    for sec in ("current", "constant"):
        P(f"\n[{sec}] Max |sum - published total| by check, with the worst year:")
        checks = defaultdict(lambda: (0, None))

        def rec(name, y, diff):
            if abs(diff) > abs(checks[name][0]):
                checks[name] = (diff, y)
            elif name not in checks:
                checks[name] = (0, None)

        big = []
        for y in years:
            for ch in chars + ["total"]:
                tot = v(y, ch, "all_sources", "all_performers", sec)
                d = sum(v(y, ch, s, "all_performers", sec) for s in srcs) - tot
                rec(f"{ch}: sources sum to all-sources total", y, d)
                # federal intramural has no published all-sources total: use its federally funded cell
                perf_tot = lambda p: v(y, ch, "federal", p, sec) if p == "federal_intramural" else v(y, ch, "all_sources", p, sec)
                d = sum(perf_tot(p) for p in perfs) - tot
                rec(f"{ch}: performers sum to all-performers total (intramural = federally funded only)", y, d)
                for s in srcs:
                    d = sum(v(y, ch, s, p, sec) for p in perfs) - v(y, ch, s, "all_performers", sec)
                    rec(f"{ch}: {s} performers sum to {s} total", y, d)
                    if abs(d) > 5 and sec == "current":
                        big.append((y, ch, s, round(d)))
                for p in perfs:
                    if p == "federal_intramural":
                        continue  # no all-sources total is published for federal intramural
                    d = sum(v(y, ch, s, p, sec) for s in srcs) - v(y, ch, "all_sources", p, sec)
                    rec(f"{ch}: sources sum to {p} performer total", y, d)
                    if abs(d) > 5 and sec == "current":
                        big.append((y, ch, "perf:" + p, round(d)))
                d = v(y, ch, "federal", "federal_intramural", sec) + v(y, ch, "all_sources", "ffrdc", sec) - v(y, ch, "all_sources", "all_federal_performers", sec)
                rec(f"{ch}: federally funded intramural + FFRDC = all federal performers", y, d)
                if abs(d) > 5 and sec == "current":
                    big.append((y, ch, "all_federal_performers", round(d)))
            for s in ["all_sources"] + srcs:
                d = sum(v(y, c, s, "all_performers", sec) for c in chars) - v(y, "total", s, "all_performers", sec)
                rec(f"basic+applied+dev = total, source {s}", y, d)
        for name in sorted(checks):
            d, y = checks[name]
            P(f"  {name}: {d:+.0f} ({y})")
        if sec == "current":
            P("\n  Gaps larger than $5M (year, character, source or perf:performer, gap):")
            for b in big:
                P("   ", b)

    with open(os.path.join(OUT, "natpat_checks.txt"), "w") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
