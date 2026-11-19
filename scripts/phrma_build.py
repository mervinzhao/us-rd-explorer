"""Build the preferred annual series and an edition-comparison file from the
long table written by phrma_parse.py. Run with python -I.

Usage: python -I phrma_build.py <long_csv> <out_series_csv> <out_by_edition_csv>
Rule: for each year take the most recent edition that reports it; list every
other edition's differing value in the note. No interpolation.
"""
import csv
import sys
from collections import defaultdict

# What the year marker means in each edition (read from each table's footnotes).
EST_MARK = {
    "p2002": "*", "p2003": "*", "p2004": "*", "p2005": "*", "p2006": "*",
    "p2007": "*", "p2008": "*", "p2009": "**", "p2010": "**", "p2011": "**",
    "p2012": "**", "p2013": "**", "p2014": "**",
}

KNOWN_SUM_ISSUES = {
    2001: "PhRMA's printed total for 2001 (29,772.7) exceeds domestic+abroad (29,722.6) by 50.1 in every edition from 2003 on",
}


def is_est(r):
    # Year-row asterisks only ever mark "Estimated" in these tables (the R&D-abroad
    # footnote star sits on the column header). The 2004 ed. writes *2003*;
    # the 2005-2006 eds. keep 2003 marked with a trailing *.
    return r["edition_key"] in EST_MARK and "*" in r["marker"]


def fmt(x):
    return f"{float(x):.1f}"


def main():
    src, out_series, out_long = sys.argv[1:4]
    rows = list(csv.DictReader(open(src)))
    for r in rows:
        r["pub_year"] = int(r["pub_year"])
        r["year"] = int(r["year"])
        r["estimated"] = is_est(r)
    by_year = defaultdict(list)
    for r in rows:
        by_year[r["year"]].append(r)

    with open(out_long, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "edition_pub_year", "source_edition", "domestic_rd_usd_millions",
                    "abroad_rd_usd_millions", "total_rd_usd_millions", "flagged_estimated_in_edition",
                    "source_url"])
        for y in sorted(by_year):
            for r in sorted(by_year[y], key=lambda r: r["pub_year"]):
                w.writerow([y, r["pub_year"], r["edition"], fmt(r["domestic"]), fmt(r["abroad"]),
                            fmt(r["total"]), "yes" if r["estimated"] else "", r["url"]])

    with open(out_series, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "domestic_rd_usd_millions", "abroad_rd_usd_millions", "source_edition",
                    "source_url", "note"])
        for y in sorted(by_year):
            eds = sorted(by_year[y], key=lambda r: r["pub_year"])
            best = eds[-1]
            notes = []
            if best["estimated"]:
                notes.append("flagged Estimated in this edition; no later edition found")
            if y == max(by_year):
                notes.append("latest year: first report, not flagged estimated but may be revised in the next survey")
            diffs = [r for r in eds[:-1] if fmt(r["domestic"]) != fmt(best["domestic"])
                     or fmt(r["abroad"]) != fmt(best["abroad"])]
            if diffs:
                parts = []
                for r in diffs:
                    tag = " est." if r["estimated"] else ""
                    parts.append(f"{r['pub_year']} ed.{tag} domestic {fmt(r['domestic'])} abroad {fmt(r['abroad'])}")
                notes.append("earlier editions differ: " + "; ".join(parts))
            same = [str(r["pub_year"]) for r in eds[:-1] if r not in diffs]
            if same:
                notes.append("same value in " + ", ".join(same) + " eds.")
            if y in KNOWN_SUM_ISSUES:
                notes.append(KNOWN_SUM_ISSUES[y])
            w.writerow([y, fmt(best["domestic"]), fmt(best["abroad"]), best["edition"], best["url"],
                        " | ".join(notes)])


if __name__ == "__main__":
    main()
