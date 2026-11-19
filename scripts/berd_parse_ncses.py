"""Parse NCSES BRDIS/BRDS/BERD Excel data tables (releases on ncses.nsf.gov, 2015-2024)
into long rows.

usage: python -I berd_parse_ncses.py <raw/berd dir> <out.csv>
"""
import csv, glob, os, re, sys, warnings
warnings.filterwarnings('ignore')
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from berd_common import parse_cell, norm_code, norm_label, naics_vintage, FIELDS, fmt

RELEASES = ['nsf18313', 'nsf19318', 'nsf20311', 'nsf21312', 'nsf22329',
            'nsf23314', 'nsf23351', 'nsf24335', 'nsf25354', 'nsf27300']
LATEST = 'nsf27300'

SINGLE = [  # (title regex, measure prefix)
    (r'^Domestic R&D paid for by the company and others and performed by the company, by type of R&D, industry, and company size: (\d{4})$', ''),
    (r'^Domestic R&D paid for and performed by the company, by type of R&D, industry, and company size: (\d{4})$', 'company_funded'),
    (r'^Domestic R&D paid for by others and performed by the company, by type of R&D, industry, and company size: (\d{4})$', 'other_funded'),
    (r'^Domestic R&D paid for by the U\.S\. federal government and performed by the company, by type of R&D, industry, and company size: (\d{4})$', 'federal_funded'),
]
PERF = r'^Domestic R&D performance,? by performer,? (?:and )?source of funds, (?:by )?industry,? and company size: (\d{4})$'
BYSRC = r'^Domestic R&D paid for by others and performed by the company, by source of funds, industry, and company size: (\d{4})$'
MULTI = r'^Domestic R&D paid for by the company and others and performed by the company, by industry and company size: 2008[–-](\d{2})$'

TYPE_COL = {'total': 'total', 'basic research': 'basic', 'applied research': 'applied', 'development': 'development'}


def survey_name(y):
    return 'BRDIS' if y <= 2016 else ('BRDS' if y <= 2018 else 'BERD')


def measure_name(prefix, col):
    t = TYPE_COL[col]
    if prefix == '':
        return t
    return prefix if t == 'total' else prefix + '_' + t


def read_rows(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.worksheets[0]
    return [list(r) for r in ws.iter_rows(values_only=True)]


def table_title(rows):
    tno = norm_label(rows[0][0])
    title = norm_label(rows[1][0])
    return tno, title


def header_index(rows):
    for i, r in enumerate(rows[:10]):
        if len(r) > 1 and isinstance(r[1], str) and r[1].strip().lower() == 'naics code':
            return i
    raise ValueError('no header')


def data_rows(rows, start):
    for r in rows[start:]:
        lab = norm_label(r[0])
        code = norm_code(r[1])
        if not lab or code in ('', '–', '-'):
            continue
        yield lab, code, r


def parse_release(rel_dir, rel, out):
    for f in sorted(glob.glob(os.path.join(rel_dir, '*.xlsx'))):
        rows = read_rows(f)
        tno, title = table_title(rows)
        url = 'https://ncses.nsf.gov/pubs/%s/assets/data-tables/tables/%s' % (rel, os.path.basename(f))
        src = '%s %s' % (rel, tno)
        if not (any(re.match(rx, title) for rx, _ in SINGLE) or re.match(MULTI, title)
                or re.match(PERF, title) or re.match(BYSRC, title)):
            continue
        hi = header_index(rows)
        hdr = rows[hi]
        for rx, prefix in SINGLE:
            m = re.match(rx, title)
            if not m:
                continue
            year = int(m.group(1))
            cols = [(j, norm_label(h).lower()) for j, h in enumerate(hdr) if j >= 2 and h not in (None, '') and norm_label(h)]
            assert [c for _, c in cols] == ['total', 'basic research', 'applied research', 'development'], (f, cols)
            for lab, code, r in data_rows(rows, hi + 1):
                for j, c in cols:
                    p = parse_cell(r[j], r[j + 1] if j + 1 < len(r) else None)
                    if p is None:
                        continue
                    v, fl, lo, hi_ = p
                    meas = measure_name(prefix, c)
                    out.append(dict(year=year, industry_code_native=code, industry_label_native=lab,
                                    classification=naics_vintage(year), measure=meas,
                                    value_usd_millions_nominal=fmt(v), flag=fl, range_low=fmt(lo), range_high=fmt(hi_),
                                    # single-year totals are as first published; the latest multi-year table is primary
                                    is_primary=0 if meas in ('total', 'company_funded', 'other_funded', 'federal_funded') else 1,
                                    survey=survey_name(year), source_table=src, source_url=url))
        m = re.match(PERF, title) or re.match(BYSRC, title)
        if m:
            year = int(m.group(1))
            if re.match(PERF, title):
                sub = [norm_label(x) for x in rows[hi + 1]]
                want = {'Total': 'total_perf', 'Paid for by the company': 'company_funded', 'Paid for by others': 'other_funded'}
                cols = []
                for j, x in enumerate(sub):
                    if x in want and want[x] not in [c for _, c in cols]:
                        cols.append((j, want[x]))
                cols = [c for c in cols if c[1] != 'total_perf']
            else:
                h = [norm_label(x) for x in hdr]
                cols = [(h.index('Total'), 'other_funded')] + [(j, 'federal_funded') for j, x in enumerate(h) if 'federal' in x.lower()]
            assert len(cols) == 2, (f, cols)
            for lab, code, r in data_rows(rows, hi + 1):
                for j, meas in cols:
                    p = parse_cell(r[j], r[j + 1] if j + 1 < len(r) else None)
                    if p is None:
                        continue
                    v, fl, lo, hi_ = p
                    out.append(dict(year=year, industry_code_native=code, industry_label_native=lab,
                                    classification=naics_vintage(year), measure=meas,
                                    value_usd_millions_nominal=fmt(v), flag=fl, range_low=fmt(lo), range_high=fmt(hi_),
                                    is_primary=0 if (meas == 'other_funded' and re.match(BYSRC, title)) else 1,
                                    survey=survey_name(year), source_table=src, source_url=url))
        m = re.match(MULTI, title)
        if m and rel == LATEST:
            years = [(j, int(float(h))) for j, h in enumerate(hdr) if j >= 2 and isinstance(h, (int, float))]
            for lab, code, r in data_rows(rows, hi + 1):
                for j, y in years:
                    p = parse_cell(r[j], r[j + 1] if j + 1 < len(r) else None)
                    if p is None:
                        continue
                    v, fl, lo, hi_ = p
                    out.append(dict(year=y, industry_code_native=code, industry_label_native=lab,
                                    classification=naics_vintage(y), measure='total',
                                    value_usd_millions_nominal=fmt(v), flag=fl, range_low=fmt(lo), range_high=fmt(hi_),
                                    is_primary=1, survey=survey_name(y), source_table=src + ' (multi-year, revised)', source_url=url))


def main():
    base, outp = sys.argv[1], sys.argv[2]
    out = []
    for rel in RELEASES:
        parse_release(os.path.join(base, rel, 'x'), rel, out)
    with open(outp, 'w', newline='') as fh:
        w = csv.DictWriter(fh, FIELDS)
        w.writeheader()
        for r in out:
            w.writerow(r)
    from collections import Counter
    c = Counter((r['measure'], r['source_table'].split()[0]) for r in out)
    for k in sorted(c):
        print(k, c[k])


if __name__ == '__main__':
    main()
