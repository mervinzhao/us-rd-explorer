"""Generic parser for single-year IRIS/SIRD tables by industry: basic/applied/development by industry (and source),
and NAICS 2005-2007 funds by industry. Usage: python -I sird_hist_parse_single.py <pages_dir> <out_csv> [--verbose]"""
import sys, os, re, csv, xlrd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sird_hist_common import *

# (relative path, publication id, classification) ; order = publication order (later wins on duplicates)
BAD = [
 ('nsf_56-16/a-12', 'SIC'), ('nsf_59-50/a-6', 'SIC'), ('nsf_60-049/a-6', 'SIC'), ('nsf_61-32/a-14', 'SIC'),
 ('nsf_62-3/a-14', 'SIC'), ('nsf_63-7/a-14', 'SIC'), ('nsf_64-9/a-16', 'SIC'), ('nsf_65-018/a-60', 'SIC'),
 ('nsf_66-15/a-65', 'SIC'), ('nsf_66-15/a-67', 'SIC'), ('nsf_66-28/63', 'SIC'), ('nsf_66-28/65', 'SIC'),
 ('nsf_67-012/67', 'SIC'), ('nsf_67-012/69', 'SIC'), ('nsf_68-020/68', 'SIC'), ('nsf_68-020/70', 'SIC'),
 ('nsf_69-028/45', 'SIC'), ('nsf_69-028/46', 'SIC'), ('nsf_70-029/44', 'SIC'), ('nsf_70-029/45', 'SIC'),
 ('nsf_71-018/b-29', 'SIC'), ('nsf_71-018/b-30', 'SIC'), ('nsf_72-309/b-47', 'SIC'), ('nsf_72-309/b-48', 'SIC'),
 ('nsf_73-305/b-46', 'SIC'), ('nsf_73-305/b-47', 'SIC'), ('nsf_74-312/b-43', 'SIC'), ('nsf_74-312/b-44', 'SIC'),
 ('nsf_75-315/b-41', 'SIC'), ('nsf_75-315/b-42', 'SIC'), ('nsf_76-322/b-45', 'SIC'), ('nsf_76-322/b-46', 'SIC'),
 ('nsf_77-324/b-45', 'SIC'), ('nsf_77-324/b-46', 'SIC'), ('nsf_78-314/b-44', 'SIC'), ('nsf_78-314/b-45', 'SIC'),
 ('nsf_79-313/b-44', 'SIC'), ('nsf_79-313/b-45', 'SIC'), ('nsf_81-324/b-29', 'SIC'), ('nsf_81-324/b-30', 'SIC'),
 ('nsf_83-325/b-28', 'SIC'), ('nsf_83-325/b-29', 'SIC'), ('nsf_85-325/b-28', 'SIC'), ('nsf_85-325/b-29', 'SIC'),
 ('nsf_1984/b-25', 'SIC'), ('nsf_1984/b-26', 'SIC'), ('nsf_89-316/b-27', 'SIC'), ('nsf_89-316/b-28', 'SIC'),
 ('nsf_95-324/a-23', 'SIC'), ('nsf_95-324/a-24', 'SIC'), ('nsf_95-324/a-25', 'SIC'), ('nsf_95-324/a-26', 'SIC'),
 ('nsf_95-324/a-27', 'SIC'), ('nsf_96-304/a-26', 'SIC'), ('nsf_96-304/a-27', 'SIC'), ('nsf_96-304/a-28', 'SIC'),
 ('nsf_97-331/a-23', 'SIC'), ('nsf_97-331/a-24', 'SIC'), ('nsf_97-331/a-25', 'SIC'),
 ('nsf_99-312/a-22a', 'SIC'), ('nsf_99-312/a-23a', 'SIC'), ('nsf_99-312/a-24a', 'SIC'),
 ('nsf_99-358/a-31', 'SIC'), ('nsf_01-305/a-29', 'SIC'),
 ('nsf_06-322/34', 'NAICS'), ('nsf_10-319/28', 'NAICS'), ('nsf_2006/24', 'NAICS'), ('nsf_2007/58', 'NAICS'),
]
FUNDS = [('nsf_10-319/1', 'NAICS'), ('nsf_2006/1', 'NAICS'), ('nsf_2007/30', 'NAICS')]

STOP = re.compile(r'(distribution by size|size of company$|company size|number of employees|^fewer than|^see explanatory|^key|^source|^note|^\*|^d = |^[a-z0-9]\s{1,3}[A-Z]|^[0-9]+\s*/)', re.I)
VALRE = re.compile(r'^\s*(\(?\s*[A-Za-z0-9]{1,2}\s*\)\s*)?[\d,]*\.?\d+\s*$|^\s*\(\s*[A-Za-z0-9]{1,2}\s*\)\s*$|^\s*[\.\*]\s*$|^\s*[DS]\s*$')

def is_val(v):
    if isinstance(v, float):
        return True
    return bool(VALRE.match(str(v))) and str(v).strip() != ''

def is_num(v):
    if isinstance(v, float):
        return True
    return bool(re.match(r'^\s*(\(\w\)\s*)?[\d,]*\.?\d+\s*$', str(v)))

def is_flagcell(v):
    s = str(v).strip()
    return s == '' or bool(re.fullmatch(r'\(?[A-Za-z\*]\)?', s))

def measure_of(h, verbose=False):
    h = h.lower().replace('develop- ment', 'development').replace('develop-ment', 'development').replace('develop-\nment', 'development')
    h = re.sub(r'develop-?\s*ment', 'development', h)
    if re.search(r'percent|number|companies|distribution|sales|employment|check|scientists|engineers|thousands', h):
        return None
    ch = 'basic' if 'basic' in h else 'applied' if 'applied' in h else 'development' if 'development' in h else 'total'
    if re.search(r'company,\s*federal', h):
        src = 'total'
    elif 'federal' in h:
        src = 'federal'
    elif 'company' in h or 'nonfederal' in h:
        src = 'company_nonfederal'
    else:
        src = 'total'
    if src == 'total':
        return ch
    return src if ch == 'total' else src + '_' + ch

HDRWORD = re.compile(r'basic|applied|develop|federal|company|total|research|number|r&d', re.I)
OVERRIDE = {'nsf_56-16/a-12': {1: 'total', 2: 'basic'}, 'nsf_59-50/a-6': {1: 'total', 2: 'basic', 3: 'applied', 4: 'development'}}

def is_year(v):
    return isinstance(v, float) and 1950 <= v <= 2010 and v == int(v)

def norm_sub(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())

def parse_table(path, cls, verbose=False, rel=''):
    b = xlrd.open_workbook(path)
    sh = b.sheet_by_index(0)
    fn = footnote_map(sh)
    rows = [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]
    ncol = sh.ncols
    title = ' '.join(str(rows[r][0]) for r in range(min(3, len(rows))) if str(rows[r][0]).strip())
    tyears = [int(y) for y in re.findall(r'(19[5-9]\d|200\d)', title)]
    # column blocks (side-by-side pages)
    bstarts = sorted({c for row in rows for c in range(ncol) if isinstance(row[c], str) and re.match(r'^\s*(Industry|Distribution by industry)', row[c])})
    if not bstarts or bstarts[0] != 0:
        bstarts = [0] + [c for c in bstarts if c != 0]
    out = []
    diag = []
    for bi, c0 in enumerate(bstarts):
        c1 = bstarts[bi + 1] if bi + 1 < len(bstarts) else ncol
        def lab(r): return str(rows[r][c0]).strip()
        def isdata(r):
            l = lab(r)
            if not l or re.match(r'^(industry|distribution by industry|table )', l, re.I):
                return False
            nums = [v for v in rows[r][c0 + 1:c1] if is_num(v)]
            return len(nums) >= 2 and not all(is_year(v) for v in nums if isinstance(v, float)) or (len(nums) >= 2 and any(not isinstance(v, float) for v in nums))
        def ishdr(r):
            cells = [str(v) for v in rows[r][c0 + 1:c1] if str(v).strip()]
            if any(is_num(v) and not is_year(v) for v in rows[r][c0 + 1:c1]):
                return False
            return sum(bool(HDRWORD.search(x)) for x in cells) >= 2 or (sum(is_year(v) for v in rows[r][c0 + 1:c1]) >= 2)
        # segments
        segs = []
        cur = 0
        seen_data = False
        for r in range(len(rows)):
            if ishdr(r) and seen_data:
                st = r
                while st - 1 > cur and any(str(v).strip() for v in rows[st - 1][c0:c1]) and not isdata(st - 1):
                    st -= 1
                segs.append((cur, st)); cur = st; seen_data = False
            if isdata(r):
                seen_data = True
        segs.append((cur, len(rows)))
        for s0, s1 in segs:
            data = [r for r in range(s0, s1) if isdata(r)]
            if not data:
                continue
            first = data[0]
            # code column
            codecol = None
            htxt = ' '.join(str(rows[r][c0 + 1]) for r in range(s0, first) if c0 + 1 < c1)
            if re.search(r'SIC|NAICS', htxt):
                codecol = c0 + 1
            elif c0 + 1 < c1:
                cc = [rows[r][c0 + 1] for r in data]
                if sum(isinstance(v, str) and v.strip() != '' and not is_val(v) for v in cc) > len(cc) / 3:
                    codecol = c0 + 1
            vstart = (codecol + 1) if codecol is not None else c0 + 1
            cand = [c for c in range(vstart, c1) if sum(is_val(rows[r][c]) for r in data) >= 2]
            hrows = []
            for r in range(s0, first):
                cells = [str(rows[r][c]).strip() for c in range(vstart, c1)]
                ne = [x for x in cells if x]
                if not ne:
                    continue
                txt = ' '.join(ne)
                if re.fullmatch(r'\s*(\[?(dollars in millions|millions of dollars|in millions of dollars)\]?|page \d+ of \d+|\(millions of dollars\)|\$millions|thousands|\$millions thousands)\s*', txt, re.I):
                    continue
                if lab(r).lower().startswith('table') and len(ne) <= 1 and not HDRWORD.search(txt):
                    continue
                hrows.append(r)
            ov = OVERRIDE.get(rel)
            def celltxt(r, c):
                v = rows[r][c]
                return ('%d' % v) if isinstance(v, float) else re.sub(r'\s+', ' ', str(v)).strip()
            # 1) header matrix, merging lowercase continuation rows into the row above
            mat = []
            for r in hrows:
                cells = {c: celltxt(r, c) for c in range(vstart, c1) if celltxt(r, c)}
                if mat and any(re.match(r'^[a-z]', t) for t in cells.values()):
                    prev = mat[-1]
                    for c, t in cells.items():
                        prev[c] = (prev.get(c, '') + ' ' + t).strip()
                else:
                    mat.append(cells)
            vcand = [c for c in range(vstart, c1) if sum(is_val(rows[r][c]) for r in data) >= 2]
            nv = max(1, len([c for c in vcand if not all(is_flagcell(rows[r][c]) for r in data)]))
            GW = re.compile(r'federal|company|total|basic|applied|develop|r&d|research|percent|millions|dollars|^(19[5-9]\d|200\d)$', re.I)
            groups, subs = [], []
            for cells in mat:
                labs = list(cells.values())
                if labs and len(labs) <= max(1, nv / 2) and len(set(labs)) == len(labs) and all(GW.search(t) for t in labs) \
                        and (len(labs) >= 2 or nv > 1):
                    groups.append(labs)
                else:
                    subs.append(cells)
            sub = {c: ' '.join(m.get(c, '') for m in subs).strip() for c in vcand}
            if subs:
                valcols = [c for c in vcand if sub[c] and not re.search(r'check', sub[c], re.I)]
            else:
                valcols = [c for c in vcand if not all(is_flagcell(rows[r][c]) for r in data)]
            if ov is not None:
                valcols = [c0 + k for k in sorted(ov)]
            colinfo = {}
            cyc = 0
            seen = set()
            for i, c in enumerate(valcols):
                k = norm_sub(sub.get(c, '')) if subs else str(i)
                if subs:
                    if k in seen:
                        cyc += 1; seen = set()
                    seen.add(k)
                else:
                    cyc = i
                g = ' '.join(gl[cyc] if cyc < len(gl) else '' for gl in groups)
                h = (g + ' ' + sub.get(c, '')).strip()
                h = re.sub(r'\[?(dollars in millions|millions of dollars)\]?', '', h, flags=re.I)
                m = measure_of(h)
                if ov is not None:
                    m = ov.get(c - c0)
                yrs = re.findall(r'(19[5-9]\d|200\d)', h)
                yr = int(yrs[0]) if yrs else (max(tyears) if tyears else None)
                colinfo[c] = (m, yr, h)
            cand = vcand
            flagcol = {}
            for c in valcols:
                if c + 1 < c1 and c + 1 not in valcols and c + 1 not in cand and all(is_flagcell(rows[r][c + 1]) for r in data):
                    flagcol[c] = c + 1
            if any(re.search(r'sales|employment|scientists', ' '.join(m.values()), re.I) for m in mat):
                continue
            diag.append((c0, s0, codecol, [(c, colinfo[c]) for c in valcols], flagcol))
            pending = ''
            last = None
            stopped = False
            dstart = (max(hrows) + 1) if hrows else first
            for r in range(min(dstart, first), s1):
                row = rows[r]
                if re.match(r'^\s*(table |\[|see explanatory)', str(row[c0]), re.I):
                    continue
                l = clean_label(row[c0]) if str(row[c0]).strip() else ''
                cv = row[codecol] if codecol is not None else ''
                if isinstance(cv, float):
                    cv = '{:,}'.format(int(cv)) if cv > 99999 else '%d' % cv
                code = norm_dash(str(cv)).strip()
                if code.strip('. ') == '':
                    code = ''
                if l and re.match(r'^industry', l, re.I):
                    continue
                if l and STOP.search(l):
                    if re.search(r'distribution by size|company size|size of company|number of employees|fewer than|^note|^source|^key|^[a-z0-9]\s{1,3}[A-Z]', l, re.I):
                        stopped = True
                    continue
                if stopped:
                    continue
                vals = [row[c] for c in valcols]
                has = any(is_val(v) for v in vals)
                if not has:
                    if l and re.match(r'^[a-z&]', l):
                        if pending:
                            pending = (pending + ' ' + l).strip()
                        elif last is not None:
                            last['label'] = (last['label'] + ' ' + l).strip()
                            if code:
                                last['code'] = (last['code'] + ',' + code) if last['code'] else code
                    elif l and code:
                        # complete row with all cells blank
                        last = {'label': (pending + ' ' + l).strip(), 'code': code, 'cells': [], 'blank': True}
                        pending = ''
                    elif l and not re.match(r'^(distribution by industry|industry)', l, re.I):
                        pending = (pending + ' ' + l).strip()
                    elif not l and code and last is not None:
                        last['code'] = (last['code'] + code) if last['code'].endswith((',', '-')) else last['code'] + ',' + code
                        last['code'] = re.sub(r',\s*', ',', last['code'])
                    continue
                full = (pending + ' ' + l).strip() if l else pending
                if not full and last is not None and last.get('blank'):
                    full = last['label']
                    code = (last['code'] + code) if last['code'].endswith((',', '-')) else last['code'] + ',' + code
                pending = ''
                full, _ = strip_label_footnote(full)
                if re.match(r'^(total|all industries)$', full, re.I):
                    full = 'All industries'
                rec = {'label': full, 'code': re.sub(r',\s*', ',', code), 'cells': []}
                for c in valcols:
                    m, yr, h = colinfo[c]
                    if m is None:
                        continue
                    val, flag, ok = parse_cell(row[c], fn)
                    if c in flagcol:
                        fl = str(row[flagcol[c]]).strip().strip('()')
                        if fl:
                            flag = (flag + '+' if flag else '') + fl
                    if flag == 'NA':
                        continue
                    rec['cells'].append((yr, m, val, flag))
                last = rec
                out.append(rec)
    if verbose:
        print('##', rel, '| title years', tyears)
        for c0, s0, codecol, cols, flagcol in diag:
            print('  block', c0, 'seg', s0, 'code', codecol, ' '.join('%d:%s/%s' % (c, ci[0], ci[1]) for c, ci in cols), 'flags', sorted(flagcol))
    return out, title

def main():
    pages, outp = sys.argv[1], sys.argv[2]
    verbose = '--verbose' in sys.argv
    allrows = []
    for kind, lst in (('bad', BAD), ('funds', FUNDS)):
        for order, (rel, cls) in enumerate(lst):
            relpath = 'excel-files/%s.xls' % rel
            path = os.path.join(pages, relpath.replace('/', '_'))
            recs, title = parse_table(path, cls, verbose, rel)
            pub = rel.split('/')[0].replace('nsf_', 'NSF ')
            for rec in recs:
                for yr, m, val, flag in rec['cells']:
                    allrows.append({'year': yr, 'sic_code_native': rec['code'], 'industry_label_native': rec['label'],
                        'measure': m, 'value_usd_millions_nominal': '' if val is None else ('%d' % val if val == int(val) else '%.3f' % val).rstrip('0').rstrip('.') if val is not None and val != int(val) else ('' if val is None else '%d' % val),
                        'flag': flag, 'source': 'IRIS_%s_%s' % (rel.split('/')[0].replace('nsf_', ''), rel.split('/')[1]),
                        'source_url': src_url(relpath), 'classification': cls, 'kind': kind, 'order': order,
                        'table_title': re.sub(r'\s+', ' ', title)[:200]})
    with open(outp, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(allrows[0].keys()))
        w.writeheader(); w.writerows(allrows)
    print(len(allrows), 'rows')

if __name__ == '__main__':
    main()
