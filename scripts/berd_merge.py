"""Merge the per-source work files into data/berd_by_industry.csv and print a coverage summary.

usage: python -I berd_merge.py <data dir>
Inputs: <data>/work/*.csv (written by berd_parse_ncses.py, berd_sird_pdf.py, berd_parse_sei.py,
        berd_parse_iris.py when available)
"""
import csv, glob, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from berd_common import FIELDS

ORDER = ['total', 'basic', 'applied', 'development', 'company_funded', 'nonfederal_funded',
         'other_funded', 'federal_funded']


def main():
    d = sys.argv[1]
    rows = []
    for f in sorted(glob.glob(os.path.join(d, 'work', '*.csv'))):
        rows += list(csv.DictReader(open(f, encoding='utf-8')))

    def key(r):
        m = r['measure']
        base = m.split('_')[0] if m.split('_')[0] in ('basic', 'applied', 'development') else m
        return (int(r['year']), r['classification'], r['industry_code_native'], m, -int(r['is_primary']), r['source_table'])
    rows.sort(key=key)
    # sanity: at most one primary row per (year, classification, code, label, measure)
    seen = defaultdict(list)
    for r in rows:
        if r['is_primary'] == '1':
            seen[(r['year'], r['classification'], r['industry_code_native'], r['industry_label_native'], r['measure'])].append(r['source_table'])
    dup = {k: v for k, v in seen.items() if len(v) > 1}
    if dup:
        print('DUPLICATE primaries:', len(dup))
        for k, v in list(dup.items())[:20]:
            print('  ', k, v)
    out = os.path.join(d, 'berd_by_industry.csv')
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, FIELDS)
        w.writeheader()
        w.writerows(rows)
    print('wrote', out, len(rows), 'rows')
    cov = defaultdict(set)
    for r in rows:
        if r['is_primary'] == '1':
            cov[(r['survey'], r['classification'], r['measure'])].add(int(r['year']))
    for k in sorted(cov):
        ys = sorted(cov[k])
        print('%-6s %-30s %-32s %d-%d (%d yrs)' % (k[0], k[1], k[2], ys[0], ys[-1], len(ys)))


if __name__ == '__main__':
    main()
