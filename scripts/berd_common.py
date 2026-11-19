"""Shared helpers for the BERD/BRDIS/SIRD industry R&D build.

Cell conventions captured in the long file:
  value_usd_millions_nominal  number, or blank when suppressed / range / '*'
  flag  D   = withheld to avoid disclosure
        i   = >50% of estimate from imputation/reweighting (BRDIS/BERD)
        r   = (single-year BERD tables) relative standard error > 50%
        *   = amount < $500,000 (value left blank)
        R   = published as a range "lo - hi" (value blank, range_low/high set)
        combos joined with '+', e.g. 'R+i'
"""
import re

NAICS_VINTAGE = [  # (first_year, last_year, label)  -- from BERD multi-year table notes
    (2008, 2008, 'NAICS2002'),
    (2009, 2013, 'NAICS2007'),
    (2014, 2019, 'NAICS2012'),
    (2020, 2099, 'NAICS2017'),
]


def naics_vintage(year):
    for a, b, lab in NAICS_VINTAGE:
        if a <= year <= b:
            return lab
    raise ValueError(year)


def norm_code(c):
    if c is None:
        return ''
    if isinstance(c, float):
        if c.is_integer():
            return str(int(c))
        return str(c)
    s = str(c).replace('\xa0', ' ').strip()
    s = re.sub(r'\s+', ' ', s)
    return s


def norm_label(s):
    if s is None:
        return ''
    s = str(s).replace('\xa0', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


RANGE_RE = re.compile(r'^\s*([\d,\.]+)\s*[-–]\s*([\d,\.]+)\s*$')


def parse_cell(v, f=None):
    """Return (value, flag, lo, hi) or None when the cell means 'not available'."""
    flags = []
    fl = '' if f is None else str(f).replace('\xa0', ' ').strip()
    for ch in fl.replace(',', ' ').split():
        if ch in ('i', 'r', 'D', '*'):
            flags.append(ch)
    lo = hi = ''
    val = ''
    if v is None:
        return None
    if isinstance(v, (int, float)):
        val = float(v)
    else:
        s = str(v).replace('\xa0', ' ').strip()
        if s == '' or s in ('NA', 'na', '(NA)', '–', '-', '—'):
            return None
        if s == 'D' or s == '(D)':
            flags.insert(0, 'D')
        elif s == '*':
            flags.insert(0, '*')
        else:
            m = RANGE_RE.match(s)
            if m:
                lo = float(m.group(1).replace(',', ''))
                hi = float(m.group(2).replace(',', ''))
                flags.insert(0, 'R')
            else:
                # numbers with trailing flags, e.g. '1,234 i' or '1234i'
                m2 = re.match(r'^([\d,\.]+)\s*([a-zA-Z\*]*)$', s)
                if m2:
                    val = float(m2.group(1).replace(',', ''))
                    if m2.group(2):
                        flags.append(m2.group(2))
                else:
                    raise ValueError('unparsed cell %r' % (v,))
    seen = []
    for x in flags:
        if x not in seen:
            seen.append(x)
    return val, '+'.join(seen), lo, hi


FIELDS = ['year', 'industry_code_native', 'industry_label_native', 'classification',
          'measure', 'value_usd_millions_nominal', 'flag', 'range_low', 'range_high',
          'is_primary', 'survey', 'source_table', 'source_url']


def fmt(x):
    if x == '' or x is None:
        return ''
    if isinstance(x, float):
        if x.is_integer():
            return str(int(x))
        return ('%.3f' % x).rstrip('0').rstrip('.')
    return str(x)
