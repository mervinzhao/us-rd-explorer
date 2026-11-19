"""Compare IRIS NAICS 2005 values with SEI 2008 appendix tables 4-19/20/21 (UNT EOT 2008 copy).
Usage: python -I sird_hist_check_sei08.py <seind08 dir> <sird_hist_by_industry.csv>"""
import sys, csv, re, xlrd
d = {}
for x in csv.DictReader(open(sys.argv[2])):
    if x['year'] == '2005' and x['is_primary'] == '1' and x['classification'] == 'NAICS':
        d[(x['measure'], re.sub(r'\s', '', x['sic_code_native']))] = x['value_usd_millions_nominal'] or x['flag']
for t, m in (('at04-19', 'total'), ('at04-20', 'company_nonfederal'), ('at04-21', 'federal')):
    sh = xlrd.open_workbook('%s/%s.xls' % (sys.argv[1], t)).sheet_by_index(0)
    n = agree = 0
    diffs = []
    for r in range(5, sh.nrows):
        code = re.sub(r'\s', '', str(sh.cell_value(r, 1)).replace('–', '-'))
        v = sh.cell_value(r, 6)
        if not code or (m, code) not in d:
            continue
        sv = ('%d' % v) if isinstance(v, float) else str(v).split()[0]
        iv = d[(m, code)]
        n += 1
        if sv == iv:
            agree += 1
        else:
            diffs.append((code, sv, iv))
    print(t, m, 'compared', n, 'agree', agree, 'differ', diffs[:12])
