"""Cross-check IRIS h-tables (GitHub mirror of Archive-It) against NSF 96-304 born-digital PDF text (UNT EOT 2008)."""
import sys, re, csv
txt = open(sys.argv[1], encoding='utf-8', errors='replace').read().split('\n')
hcsv = sys.argv[2]
def grab(title_pat, years):
    out = {}
    on = False
    for ln in txt:
        if re.search(title_pat, ln):
            on = True; continue
        if on and re.search(r'^\s*Table A-\d+\.', ln) and not re.search(title_pat, ln):
            on = False
        if not on: continue
        toks = ln.split()
        if len(toks) >= len(years) + 1:
            vals = toks[-len(years):]
            if all(re.fullmatch(r'\$?[\d,]+|\(D\)|\(S\)|N/A', v) for v in vals):
                code = toks[-len(years) - 1]
                if re.fullmatch(r'[\d,\-]+', code):
                    out[code.rstrip(',')] = vals
    return out
years = list(range(1983, 1994))
d = {}
for x in csv.DictReader(open(hcsv)):
    d[(x['measure'], x['sic_code_native'], int(x['year']))] = x['value_usd_millions_nominal'] or x['flag']
for meas, pat in [('total', r'Table A-3\. Total'), ('company_nonfederal', r'Table A-7\. Company'), ('federal', r'Table A-12\. Federal')]:
    g = grab(pat, years)
    n = agree = 0
    for code, vals in g.items():
        for y, v in zip(years, vals):
            h = d.get((meas, code, y))
            if h is None: continue
            pv = v.replace('$', '').replace(',', '').strip('()')
            hv = h
            try:
                hv = str(round(float(h)))
            except ValueError: pass
            n += 1
            if pv == hv or (pv.isdigit() and hv.lstrip('-').isdigit() and abs(int(pv) - int(hv)) <= 1):
                agree += 1
            else:
                print(meas, code, y, 'pdf', v, 'iris', h)
    print(meas, 'codes', len(g), 'cells compared', n, 'agree', agree)
