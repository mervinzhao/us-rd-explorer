"""Parse Science & Engineering Indicators 2022 (NSB 2022-5) Table SRD-4: type of R&D by
select industry, 2010-19. Only 2010-2014 rows are kept as primary (2015+ come from the
single-year BRDIS/BERD tables).

usage: python -I berd_parse_sei.py <xlsx> <out.csv>
"""
import csv, os, re, sys, warnings
warnings.filterwarnings('ignore')
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from berd_common import parse_cell, naics_vintage, FIELDS, fmt, norm_label

SECTIONS = {'all business r&d': 'total', 'basic research': 'basic', 'applied research': 'applied',
            'experimental development': 'development'}
URL = 'https://ncses.nsf.gov/pubs/nsb20225/assets/nsb20225-supplemental-materials.zip (nsb20225-tabsrd-004.xlsx)'


def main():
    f, outp = sys.argv[1], sys.argv[2]
    ws = openpyxl.load_workbook(f, data_only=True).worksheets[0]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    hdr = rows[3]
    years = [(j, int(float(h))) for j, h in enumerate(hdr) if j >= 1 and isinstance(h, (int, float))]
    out, sect = [], None
    for r in rows[4:]:
        lab = norm_label(r[0])
        if not lab:
            continue
        low = lab.lower()
        if low.startswith('industry share'):
            break
        if low in SECTIONS:
            sect = SECTIONS[low]
            continue
        if sect is None or ',' not in lab:
            continue
        m = re.match(r'^(.*?),\s*(\d.*)$', lab)
        if not m:
            continue
        name, code = m.group(1), m.group(2).strip()
        if name.startswith('All industries'):
            code = '21–23, 31–33, 42–81'
        for j, y in years:
            if y > 2014:
                continue
            p = parse_cell(r[j], r[j + 1] if j + 1 < len(r) else None)
            if p is None:
                continue
            v, fl, lo, hi = p
            out.append(dict(year=y, industry_code_native=code, industry_label_native=name.strip(),
                            classification=naics_vintage(y), measure=sect, value_usd_millions_nominal=fmt(v),
                            flag=fl, range_low=fmt(lo), range_high=fmt(hi),
                            is_primary=0 if sect == 'total' else 1, survey='BRDIS',
                            source_table='SEI 2022 (NSB 2022-5) Table SRD-4', source_url=URL))
    with open(outp, 'w', newline='') as fh:
        w = csv.DictWriter(fh, FIELDS)
        w.writeheader()
        w.writerows(out)
    print(len(out), 'rows')


if __name__ == '__main__':
    main()
