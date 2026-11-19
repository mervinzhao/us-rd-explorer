"""Build data/sird_scan_by_industry.csv from the hand transcriptions in raw/sird_scan/tx/.
usage: python -I sird_scan_build.py RDFIELDS_DIR"""
import sys, os, re, csv, glob
base = sys.argv[1]
tx = os.path.join(base, 'raw/sird_scan/tx')
RANK = {'v1999': 6, 'v1996': 5, 'v1995': 5, 'v1988': 4, 'v1986': 3.5, 'v1977': 3, 'v1972': 2, 'v1969': 1}
SKIP = {'COMB', 'SPLIT', 'NOT_TABULATED'}
CODE = {'D': ('', 'D'), 'S': ('', 'S'), 'NA': ('', 'NA_included_in_total'), 'LT0.5': ('', 'lt_0.5'),
        'NONE': ('', 'none'), 'INC_OTHER_ELEC': ('', 'included_in_other_electrical'),
        'INC_OTHER_MFG': ('', 'included_in_other_manufacturing'), 'INC_NONMFG_FN3': ('', 'included_in_nonmanufacturing'),
        'ILLEGIBLE': ('', 'illegible'), 'DOTS': ('', 'printed_dots')}
FLAGS = {'E': 'E_estimated_by_NSF', 'S': 'S', 'U': 'U_uncertain_reading', 'X': 'X_from_other_table'}
def cell(c):
    c = c.strip()
    m = re.match(r'^(-?\d+(?:\.\d+)?)(?:\^([A-Z]+))?$', c)
    if m:
        return m.group(1), FLAGS.get(m.group(2), m.group(2) or '')
    if c in CODE: return CODE[c]
    raise ValueError(c)
def meta_and_rows(fn):
    meta, rows, hdr = {}, [], None
    for line in open(fn):
        line = line.rstrip('\n')
        if not line.strip(): continue
        if line.startswith('#'):
            k, _, v = line[1:].partition(':'); meta[k.strip()] = v.strip(); continue
        p = line.split('|')
        if hdr is None: hdr = p; continue
        rows.append(dict(zip(hdr, p)))
    return meta, hdr, rows
out = []
splits = []  # (year, key, measure, rank): a volume that shows this combined line split into components
for fn in sorted(glob.glob(os.path.join(tx, 'v*.txt'))):
    tag = os.path.basename(fn)[:5]
    meta, hdr, rows = meta_and_rows(fn)
    src, page, title = meta['source_item'], meta['page'], meta['table_title']
    if hdr[0] == 'year':  # 1999 trend tables: all-industry only
        for r in rows:
            for m in hdr[1:]:
                out.append(dict(year=int(r['year']), key='total', sic_code_native='all', industry_label_native='All industries',
                                measure=m, value=r[m], flag='', source_item=src, page=page, table_title=title, rank=RANK[tag]))
        continue
    if meta.get('layout') == 'measures':
        year = int(meta['year']); cols = [(year, m) for m in hdr[4:]]
    else:
        cols = [(int(y), meta['measure']) for y in hdr[4:]]
    for r in rows:
        for (y, m), h in zip(cols, hdr[4:]):
            c = r[h].strip()
            if c == 'SPLIT': splits.append((y, r['key'], m, RANK[tag]))
            if c in SKIP: continue
            v, f = cell(c)
            out.append(dict(year=y, key=r['key'], sic_code_native=r['sic'], industry_label_native=r['label'], measure=m,
                            value=v, flag=f, source_item=src, page=page, table_title=title, rank=RANK[tag]))
# drop NA cells for nonmanufacturing sub-industries in years they were not collected (pre-1995)
NONMFG_SUB = {'transutil','commun','telephone','othcommun','elecgas','othtransutil','trade','fire','services','bizserv','compserv',
              'othbizserv','health','medoffices','othhealth','engmgmt','engarch','rdtest','othengmgmt','othserv','othnonmfg'}
out = [o for o in out if not (o['key'] in NONMFG_SUB and o['year'] < 1995 and o['value'] == '')]
# preferred: most recent volume for each (year, key, measure)
best = {}
for o in out:
    k = (o['year'], o['key'], o['measure'])
    if o['flag'] == 'illegible': continue  # fall back to an older volume's reading when the latest is illegible
    if k not in best or o['rank'] > best[k]: best[k] = o['rank']
for o in out:
    k = (o['year'], o['key'], o['measure'])
    if k not in best: best[k] = o['rank']
for y, k, m, rk in splits:
    if (y, k, m) in best and rk > best[(y, k, m)]: best[(y, k, m)] = rk  # a later volume replaced the combined line by its split
for o in out:
    o['preferred'] = 1 if o['rank'] == best[(o['year'], o['key'], o['measure'])] else 0
out.sort(key=lambda o: (o['year'], o['measure'], o['key'], -o['rank']))
cols = ['year', 'sic_code_native', 'industry_label_native', 'measure', 'value_usd_millions_nominal', 'flag', 'source_item', 'page', 'table_title', 'industry_key', 'preferred']
with open(os.path.join(base, 'data/sird_scan_by_industry.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(cols)
    for o in out:
        w.writerow([o['year'], o['sic_code_native'], o['industry_label_native'], o['measure'], o['value'], o['flag'],
                    o['source_item'], o['page'], o['table_title'], o['key'], o['preferred']])
print(len(out), 'rows;', sum(o['preferred'] for o in out), 'preferred')
