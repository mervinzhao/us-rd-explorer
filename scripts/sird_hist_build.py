"""Assemble data/sird_hist_by_industry.csv from the parsed IRIS tables.
Usage: python -I sird_hist_build.py <work_h.csv> <work_single.csv> <out.csv>"""
import sys, csv, re, collections

def clean_label(s):
    s = s.strip().rstrip('.').strip()
    s = re.sub(r'\s+\d{1,2}/?$', '', s)
    s = re.sub(r'(nonmanufacturing)[ab]$', r'\1', s)
    s = re.sub(r'n\.e\.c\.\s*(a|2)$', 'n.e.c.', s)
    return s.strip()

def norm_flag(f):
    if f.startswith('RAW:'):
        f = f[4:]
    f = f.replace('(cell -1)', '')
    if f.startswith('fn') and 'not available' in f.lower():
        return 'NA'
    return f

def main():
    hpath, spath, outp = sys.argv[1:4]
    out = []
    for x in csv.DictReader(open(hpath)):
        x['classification'] = 'SIC'
        x['is_primary'] = '1'
        x['industry_label_native'] = clean_label(x['industry_label_native'])
        x['flag'] = norm_flag(x['flag'])
        if x['year'] == '1953' and x['measure'] == 'total' and x['sic_code_native'] == '13,29' and x['value_usd_millions_nominal'] == '4146':
            x['value_usd_millions_nominal'] = '146'
            x['flag'] = 'footnote marker 4 removed (cell reads 4146; NSF 56-16 table A-12 gives 145.9)'
        if x['year'] == '1986' and x['measure'] == 'total' and x['industry_label_native'] == 'Manufacturing':
            x['flag'] = 'suspect: equals all-industries total in source'
        if x['flag'] == 'NA':
            continue
        out.append(x)
    url25 = [x['source_url'] for x in out if x['source'] == 'IRIS_h-25'][0]
    for lab, v in (('Telecommunications and broadcasting', '113'), ('Construction', '29')):
        out.append({'year': '1953', 'sic_code_native': '', 'industry_label_native': lab, 'measure': 'total',
                    'value_usd_millions_nominal': v, 'flag': 'from table footnote 3', 'source': 'IRIS_h-25',
                    'source_url': url25, 'classification': 'SIC', 'is_primary': '1'})
    single = list(csv.DictReader(open(spath)))
    for x in single:
        x['industry_label_native'] = clean_label(x['industry_label_native'])
        x['flag'] = norm_flag(x['flag'])
    single = [x for x in single if x['flag'] != 'NA']
    # primary selection
    def key(x):
        k = x['sic_code_native'].replace(' ', '') or x['industry_label_native'].lower()
        if x['industry_label_native'] in ('All industries',):
            k = 'ALL'
        return (x['year'], x['measure'], x['classification'], k)
    best = {}
    for x in single:
        rank = (1 if x['kind'] == 'funds' else 0, int(x['order']))
        base = x['measure'] in ('total', 'federal', 'company_nonfederal')
        if base and x['kind'] == 'bad' and (x['classification'] == 'SIC' or x['year'] in ('2004', '2005', '2006', '2007')):
            continue
        k = key(x)
        if k not in best or rank > best[k]:
            best[k] = rank
    for x in single:
        rank = (1 if x['kind'] == 'funds' else 0, int(x['order']))
        x['is_primary'] = '1' if best.get(key(x)) == rank else '0'
    cols = ['year', 'sic_code_native', 'industry_label_native', 'measure', 'value_usd_millions_nominal', 'flag',
            'source', 'source_url', 'classification', 'is_primary']
    allrows = out + single
    allrows.sort(key=lambda x: (int(x['year']), x['classification'], x['is_primary'] == '0', x['measure'], x['source']))
    with open(outp, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader(); w.writerows(allrows)
    c = collections.Counter((x['measure'], x['classification'], x['is_primary']) for x in allrows)
    print(len(allrows), 'rows')
    for k, v in sorted(c.items()):
        print(k, v)

if __name__ == '__main__':
    main()
