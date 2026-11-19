"""Checks for data/sird_hist_by_industry.csv. Usage: python -I sird_hist_check.py <csv>"""
import sys, csv, collections
rows = [x for x in csv.DictReader(open(sys.argv[1])) if x['is_primary'] == '1']
V = {}
for x in rows:
    if x['value_usd_millions_nominal'] != '':
        V[(int(x['year']), x['measure'], x['industry_label_native'], x['source'])] = float(x['value_usd_millions_nominal'])
def get(y, m, lab, src=None):
    for (yy, mm, ll, ss), v in V.items():
        if yy == y and mm == m and ll == lab and (src is None or ss == src):
            return v
    return None

print('## Coverage (primary rows with a value / all primary rows), by measure and year range')
cov = collections.defaultdict(lambda: [0, 0, set()])
for x in rows:
    k = (x['measure'], x['classification'])
    cov[k][1] += 1
    if x['value_usd_millions_nominal'] != '':
        cov[k][0] += 1
    cov[k][2].add(int(x['year']))
for k in sorted(cov):
    ys = sorted(cov[k][2])
    print('%-32s %-5s years %d-%d (%d distinct) cells %d/%d' % (k[0], k[1], ys[0], ys[-1], len(ys), cov[k][0], cov[k][1]))

print('\n## Check 1: IRIS h-tables, sum of top-level industries vs All industries (total, h-25)')
TOP = ['Food, kindred, and tobacco products', 'Textiles and apparel', 'Lumber, wood products, and furniture',
       'Paper and allied products', 'Chemicals and allied products', 'Petroleum refining and extraction',
       'Rubber products', 'Stone, clay, and glass products', 'Primary metals', 'Fabricated metal products',
       'Machinery', 'Electrical equipment', 'Professional and scientific instruments', 'Other manufacturing industries',
       'Nonmanufacturing']
TRANS = ['Motor vehicles and motor vehicles equipment', 'Other transportation equipment', 'Aircraft and missiles']
for meas, src in (('total', 'IRIS_h-25'), ('company_nonfederal', 'IRIS_h-3'), ('federal', 'IRIS_h-9')):
    ok = []
    for y in range(1953, 1999):
        allv = get(y, meas, 'All industries', src)
        if allv is None:
            continue
        parts = [get(y, meas, l, src) for l in TOP]
        t = get(y, meas, 'Transportation equipment', src)
        if t is None:
            tp = [get(y, meas, l, src) for l in TRANS]
            if any(v is None for v in tp):
                t = None
            else:
                t = sum(tp)
        if t is None or any(v is None for v in parts):
            continue
        s = sum(parts) + t
        ok.append((y, round(s, 1), allv, round(s - allv, 1)))
    print(meas, 'years where every top-level industry is published:', len(ok))
    for y, s, a, d in ok:
        print('   %d  sum %.1f  all-industries %.1f  diff %+.1f (%.2f%%)' % (y, s, a, d, 100 * d / a))

print('\n## Check 2: total = company_nonfederal + federal, same industry and year (h-tables)')
n = bad = 0
for (y, m, l, s), v in V.items():
    if m != 'total' or s != 'IRIS_h-25':
        continue
    c = get(y, 'company_nonfederal', l, 'IRIS_h-3'); f = get(y, 'federal', l, 'IRIS_h-9')
    if c is None or f is None:
        continue
    n += 1
    if abs(c + f - v) > max(2, 0.01 * v):
        bad += 1
        print('   mismatch', y, l, 'total', v, 'company', c, 'federal', f)
print('   checked', n, 'industry-years;', bad, 'differ by more than 1% / $2m')

print('\n## Check 3: basic + applied + development = total within each BAD table (same source)')
by = collections.defaultdict(dict)
allr = list(csv.DictReader(open(sys.argv[1])))
for x in allr:
    if x['value_usd_millions_nominal'] != '':
        by[(x['year'], x['source'], x['industry_label_native'])][x['measure']] = float(x['value_usd_millions_nominal'])
n = bad = 0
for k, d in sorted(by.items()):
    for pre in ('', 'federal_', 'company_nonfederal_'):
        tot = d.get(pre[:-1] if pre else 'total')
        parts = [d.get(pre + c) for c in ('basic', 'applied', 'development')]
        if tot is None or any(p is None for p in parts):
            continue
        n += 1
        if abs(sum(parts) - tot) > max(2, 0.01 * tot):
            bad += 1
            print('   mismatch', k, pre or 'total', tot, parts)
print('   checked', n, ';', bad, 'mismatches')
n = bad = 0
for k, d in sorted(by.items()):
    for c in ('total', 'basic', 'applied', 'development'):
        a = d.get(c); f = d.get('federal' if c == 'total' else 'federal_' + c); co = d.get('company_nonfederal' if c == 'total' else 'company_nonfederal_' + c)
        if None in (a, f, co):
            continue
        n += 1
        if abs(f + co - a) > max(2, 0.01 * a):
            bad += 1
            print('   source mismatch', k, c, a, f, co)
print('   federal + company = total by character: checked', n, ';', bad, 'mismatches')

print('\n## Check 4: NAICS 2005-2007 (IRIS single-year tables)')
for y in (2005, 2006, 2007):
    a = get(y, 'total', 'All industries'); f = get(y, 'federal', 'All industries'); c = get(y, 'company_nonfederal', 'All industries')
    m = get(y, 'total', 'Manufacturing industries'); nm = get(y, 'total', 'Nonmanufacturing industries')
    b = get(y, 'basic', 'All industries'); ap = get(y, 'applied', 'All industries'); dv = get(y, 'development', 'All industries')
    print('   %d all %s = fed %s + comp %s (%s); mfg %s + nonmfg %s = %s; B+A+D %s+%s+%s = %s' % (y, a, f, c, f + c, m, nm, m + nm, b, ap, dv, b + ap + dv))
