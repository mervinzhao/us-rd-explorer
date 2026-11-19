"""Parse IRIS longitudinal tables h-25 (total), h-3 (company and other nonfederal), h-9 (federal), 1953-98, SIC.
Usage: python -I sird_hist_parse_h.py <pages_dir> <out_csv>"""
import sys, os, re, csv, xlrd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sird_hist_common import *

TABLES = [('h-25', 'total'), ('h-3', 'company_nonfederal'), ('h-9', 'federal')]

def footnotes(sh):
    fn = {}
    for r in range(sh.nrows):
        for c in range(sh.ncols):
            v = sh.cell_value(r, c)
            if isinstance(v, str):
                m = re.match(r'^\s*(\d{1,2})\s+([A-Z].*)$', v)
                if m and len(v) > 15:
                    fn[m.group(1)] = m.group(2).strip()
    return fn

def year_of(v):
    s = str(int(v)) if isinstance(v, float) else str(v).strip()
    m = re.match(r'^(19[5-9]\d|200\d)', s)
    return int(m.group(1)) if m else None

def parse(path, tid, measure, review):
    b = xlrd.open_workbook(path)
    sh = b.sheet_by_index(0)
    fn = footnotes(sh)
    out = []
    blocks = None
    in_size = False
    pending = {}
    last = {}
    for r in range(sh.nrows):
        row = [sh.cell_value(r, c) for c in range(sh.ncols)]
        starts = [c for c, v in enumerate(row) if isinstance(v, str) and v.strip().startswith('Industry and size of company')]
        if starts:
            blocks = []
            for i, c0 in enumerate(starts):
                c1 = starts[i + 1] if i + 1 < len(starts) else sh.ncols
                yrs = [(c, year_of(row[c])) for c in range(c0 + 2, c1) if row[c] != '' and year_of(row[c])]
                blocks.append((c0, yrs))
            in_size = False
            pending = {}
            continue
        if blocks is None:
            continue
        for c0, yrs in blocks:
            lab = row[c0] if isinstance(row[c0], str) else str(row[c0])
            if lab.strip().startswith('Distribution by size'):
                in_size = True
            if in_size:
                continue
            sic = norm_dash(str(row[c0 + 1])).strip() if c0 + 1 < len(row) else ''
            if sic == '.':
                sic = ''
            vals = [(y, row[c]) for c, y in yrs]
            has_vals = any(str(v).strip() != '' and not re.match(r'^Page \d+ of', str(v).strip()) for y, v in vals)
            labc = clean_label(lab)
            if not has_vals:
                if labc and not sic and not labc.startswith(('See explanatory', 'Distribution by', 'Total (company', 'Federal funds', 'Company and other', '[In millions')):
                    pending[c0] = (pending.get(c0, '') + ' ' + labc).strip()
                elif not labc and sic and c0 in last:
                    last[c0]['sic'] = (last[c0]['sic'] + sic) if last[c0]['sic'].endswith((',', '-')) else last[c0]['sic'] + ',' + sic
                continue
            full = (pending.pop(c0, '') + ' ' + labc).strip()
            full, lfn = strip_label_footnote(full)
            rec = {'label': full, 'sic': sic, 'cells': []}
            for y, v in vals:
                val, flag, ok = parse_cell(v, fn)
                if not ok:
                    review.append((tid, r, full, y, v))
                if flag == 'NA':
                    continue
                rec['cells'].append((y, val, flag))
            rec['label_fn'] = lfn
            last[c0] = rec
            out.append(rec)
    return out, fn

def main():
    pages, outp = sys.argv[1], sys.argv[2]
    review = []
    rows = []
    for tid, measure in TABLES:
        rel = 'excel-files/historical_tables/%s.xls' % tid
        recs, fn = parse(os.path.join(pages, rel.replace('/', '_')), tid, measure, review)
        for rec in recs:
            for y, val, flag in rec['cells']:
                rows.append({'year': y, 'sic_code_native': rec['sic'], 'industry_label_native': rec['label'],
                             'measure': measure, 'value_usd_millions_nominal': '' if val is None else ('%g' % val if val != int(val) else '%d' % val),
                             'flag': flag, 'source': 'IRIS_%s' % tid, 'source_url': src_url(rel)})
    with open(outp, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(len(rows), 'rows')
    for x in review:
        print('REVIEW', x)

if __name__ == '__main__':
    main()
