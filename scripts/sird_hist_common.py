"""Shared helpers for parsing NSF IRIS / SIRD Excel tables (sird_hist_*)."""
import re

IRIS_BASE = 'https://www.nsf.gov/statistics/iris/'
AIT = 'https://wayback.archive-it.org/5902/20181003221605/'
MIRROR = 'https://github.com/jivizcaino/nsf-iris-archive/blob/main/raw/pages/'

def src_url(relpath):
    """relpath like 'excel-files/historical_tables/h-25.xls'"""
    return AIT + IRIS_BASE + relpath

def norm_dash(s):
    return (s.replace('–', '-').replace('—', '-').replace('‒', '-')
             .replace('\xa0', ' '))

def clean_label(s):
    s = norm_dash(str(s))
    s = re.sub(r'[…\.]{2,}.*$', '', s)      # leader dots
    s = s.replace('…', '')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def strip_label_footnote(s):
    """'Food, kindred, and tobacco products1' -> ('Food, kindred, and tobacco products', '1')"""
    m = re.match(r'^(.*?[A-Za-z\)])(\d{1,2}(?:,\d{1,2})*)$', s)
    if m and not re.search(r'\d$', m.group(1)):
        return m.group(1).strip(), m.group(2)
    return s, ''

NUM = r'[\d,]*\.?\d+'

def parse_cell(v, fn_text=None):
    """Return (value or None, flag string, ok). ok=False -> unrecognised, needs review.
    flag vocabulary: D, S, T (as published), lt0.5 (less than $0.5m), e (NSF estimate),
    fnN:<text> for footnote-reference cells, '.' as published."""
    fn_text = fn_text or {}
    if isinstance(v, (int, float)):
        if v == -1:
            return None, fn_flag('1', fn_text.get('1', '')) + '(cell -1)', True
        return float(v), '', True
    s = norm_dash(str(v)).strip()
    s = re.sub(r'(\d),\s+(\d{3})', r'\1,\2', s)
    if s in ('D', 'S'):
        return None, s, True
    if re.fullmatch(r'\.{2,}', s):
        return None, 'NA', True
    s = re.sub(r'^\(\s*(\w+)\s*\)', r'(\1)', s)
    if s == '' or s.upper() in ('NA', 'N/A') or re.match(r'^Page \d+ of \d+$', s):
        return None, 'NA', True
    if re.fullmatch(NUM, s):
        return float(s.replace(',', '')), '', True
    m = re.fullmatch(r'\(([DSTX])\)', s)
    if m:
        return None, m.group(1), True
    m = re.fullmatch(r'\(([DSTX])\)\s*(' + NUM + ')', s)
    if m:
        return float(m.group(2).replace(',', '')), m.group(1), True
    m = re.fullmatch(r'(' + NUM + r')\s*\(([DSTX])\)', s)
    if m:
        return float(m.group(1).replace(',', '')), m.group(2), True
    if s in ('*', '(*)'):
        return None, 'lt0.5', True
    if s in ('.', '-', '--', '—'):
        return None, s, True
    m = re.fullmatch(r'\((\d{1,2}|[a-z])\)', s)
    if m:
        return None, fn_flag(m.group(1), fn_text.get(m.group(1), '')), True
    m = re.fullmatch(r'(\d{1,2})\s+(' + NUM + ')', s)
    if m:
        t = fn_text.get(m.group(1), '')
        fl = 'e' if 'estimated' in t.lower() else 'fn' + m.group(1)
        return float(m.group(2).replace(',', '')), fl, True
    return None, 'RAW:' + s, False

def fn_flag(key, t):
    tl = t.lower()
    if 'less than' in tl:
        return 'lt0.5'
    if 'imputation' in tl:
        return 'S'
    if 'withheld' in tl or 'disclos' in tl:
        return 'D'
    if 'not separately available' in tl or 'included in total' in tl or 'included in the total' in tl:
        return 'T'
    m = re.search(r'included (?:in|with) (?:the )?(.*?)(?: group)?[\.,]', tl)
    if m:
        return 'T:in ' + m.group(1)[:50]
    return 'fn%s:%s' % (key, t[:70]) if t else 'fn%s' % key

def footnote_map(sh):
    fn = {}
    for r in range(sh.nrows):
        for c in range(sh.ncols):
            v = sh.cell_value(r, c)
            if isinstance(v, str):
                m = re.match(r'^\s*\(?([a-z]|\d{1,2})\)?\s*([A-Z][^\n]{8,})', v)
                if m:
                    fn.setdefault(m.group(1), m.group(2).strip())
    return fn
