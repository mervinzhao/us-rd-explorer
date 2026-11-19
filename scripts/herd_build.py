"""Build national HERD / Academic R&D time series by field x source, character of work,
and federal agency x field from NCSES institution-level public use microdata.

Usage: python -I scripts/herd_build.py <project_root>

Inputs : raw/herd/csv/herd_YYYY.csv.gz (FY1972-2009, Academic R&D Expenditures Survey)
         raw/herd/csv/herdYYYY.csv.gz  (FY2010+, HERD standard form)
         raw/herd/csv/shortYYYY.csv.gz (FY2012+, HERD short form)
         raw/herd/pub_fy2024/nsf26304-tab007.xlsx (published type-of-R&D series, pre-2010)
Outputs: data/herd_by_field_source.csv
         data/herd_by_field_character.csv
         data/herd_federal_by_agency_field.csv
All values: thousands of current (nominal) US dollars.
"""
import os
import re
import sys
import glob

import pandas as pd

ROOT = sys.argv[1]
CSV = os.path.join(ROOT, 'raw', 'herd', 'csv')
OUT = os.path.join(ROOT, 'data')

ENC = 'latin-1'
USECOLS = ['questionnaire_no', 'question', 'row', 'column', 'data', 'status']


def read(path):
    df = pd.read_csv(path, dtype=str, encoding=ENC, usecols=lambda c: c in USECOLS,
                     low_memory=False)
    df['v'] = pd.to_numeric(df['data'], errors='coerce')
    return df


def broad_of(label):
    if label == 'All':
        return 'All'
    return label.split(',')[0].strip()


def tax_version_old(year):
    if year == 1972:
        return 'ARD_1972'          # sources only, no field item released
    if year <= 1979:
        return 'ARD_1973-1979'     # broad + some subfields; no eng/env subfields
    if year <= 1989:
        return 'ARD_1980-1989'     # + engineering and environmental subfields
    if year <= 1996:
        return 'ARD_1990-1996'     # + metallurgical & materials engineering
    return 'ARD_1997-2009'         # + bioengineering/biomedical eng (non-S&E item 2A from FY2003)


def tax_version_new(year):
    return 'HERD_2010-2015' if year <= 2015 else 'HERD_2016-'


# First fiscal year each predecessor-survey subfield was actually collected (guide section 2.1.6).
# Rows exist in the files before these years but hold zeros or scattered retro-imputed values.
FIRST_YEAR = {
    'Engineering, aeronautical and astronautical': 1980,
    'Engineering, chemical': 1980,
    'Engineering, civil': 1980,
    'Engineering, electrical': 1980,
    'Engineering, mechanical': 1980,
    'Engineering, other': 1980,
    'Engineering, metallurgical and materials': 1990,
    'Engineering, bioengineering and biomedical': 1997,
    'Environmental sciences, atmospheric sciences': 1980,
    'Environmental sciences, earth sciences': 1980,
    'Environmental sciences, oceanography': 1980,
    'Environmental sciences, other': 1980,
}

OLD_SOURCES = {
    'Federal': 'Federal',
    'State and local government': 'State and local government',
    'Industry': 'Industry',
    'Institution funds, total': 'Institution funds',
    'All other sources': 'All other sources',
    'Total': 'Total',
}

recs = []        # field x source
agency = []      # federal agency x field
character = []   # type of R&D
excluded = []    # rows dropped as not-collected


def add(year, broad, detail, src_funds, value, tv, source, row_type):
    recs.append(dict(fiscal_year=year, broad_field_native=broad, detailed_field_native=detail,
                     source_of_funds_native=src_funds, taxonomy_version=tv,
                     value_usd_thousands_nominal=value, source=source, row_type=row_type))


# ---------------------------------------------------------------- FY1972-2009
for year in range(1972, 2010):
    df = read(os.path.join(CSV, f'herd_{year}.csv.gz'))
    tv = tax_version_old(year)
    src = f'microdata:herd_{year}.csv'

    # Item 1: national S&E total by source of funds
    q1 = df[df.questionnaire_no == '01'].groupby('row').v.sum()
    for r, lab in OLD_SOURCES.items():
        add(year, 'All S&E fields', 'All S&E fields', lab, q1.get(r, 0.0), tv,
            src + ' item 1', 'grand_total')

    if year == 1972:
        continue  # no field item in the public file

    # Item 2: S&E field x (Total, Federal)
    q2 = df[df.questionnaire_no == '02'].groupby(['row', 'column']).v.sum().unstack()
    q2 = q2.drop(index='All', errors='ignore')  # identical to Item 1 total/federal (checked below)
    for lab, r in q2.iterrows():
        fy = FIRST_YEAR.get(lab)
        if fy and year < fy:
            excluded.append((year, lab, r.get('Total'), r.get('Federal')))
            continue
        rt = 'broad_total' if lab.endswith(', all') else 'detail'
        broad = broad_of(lab)
        tot, fed = r.get('Total', 0.0), r.get('Federal', 0.0)
        add(year, broad, lab, 'Total', tot, tv, src + ' item 2', rt)
        add(year, broad, lab, 'Federal', fed, tv, src + ' item 2', rt)
        add(year, broad, lab, 'Nonfederal', tot - fed, tv,
            src + ' item 2 (derived)', rt)

    # broad totals missing in early years (Life, Physical, Social sciences 'all' lines start FY1979)
    have = set(q2.index)
    kept = [x for x in recs if x['fiscal_year'] == year and x['row_type'] == 'detail']
    for broad in sorted({x['broad_field_native'] for x in kept}):
        lab = f'{broad}, all'
        if lab in have:
            continue
        for sf in ('Total', 'Federal', 'Nonfederal'):
            val = sum(x['value_usd_thousands_nominal'] for x in kept
                      if x['broad_field_native'] == broad and x['source_of_funds_native'] == sf)
            add(year, broad, lab, sf, val, tv, src + ' item 2 (derived: sum of subfields)',
                'broad_total')

    # Item 2A: non-S&E fields (FY2003-2009), outside the Item 1 total
    q2a = df[df.questionnaire_no == '02a'].groupby(['row', 'column']).v.sum().unstack()
    for lab, r in q2a.iterrows():
        rt = 'broad_total' if lab.endswith(', all') else 'detail'
        tot, fed = r.get('Total', 0.0), r.get('Federal', 0.0)
        add(year, 'Non-S&E', lab, 'Total', tot, tv, src + ' item 2A', rt)
        add(year, 'Non-S&E', lab, 'Federal', fed, tv, src + ' item 2A', rt)
        add(year, 'Non-S&E', lab, 'Nonfederal', tot - fed, tv,
            src + ' item 2A (derived)', rt)
    if len(q2a):
        # some institutions reported only the non-S&E total in FY2003-09: add a residual row so
        # detail rows sum to 'Non-S&E, all'
        det = q2a.drop(index='Non-S&E, all')
        res_t = q2a.loc['Non-S&E, all'].get('Total', 0.0) - det['Total'].sum()
        res_f = q2a.loc['Non-S&E, all'].get('Federal', 0.0) - det['Federal'].sum()
        if abs(res_t) > 0.5 or abs(res_f) > 0.5:
            lab = 'Non-S&E, not allocated to a subfield (derived residual)'
            add(year, 'Non-S&E', lab, 'Total', res_t, tv, src + ' item 2A (derived residual)', 'detail')
            add(year, 'Non-S&E', lab, 'Federal', res_f, tv, src + ' item 2A (derived residual)', 'detail')
            add(year, 'Non-S&E', lab, 'Nonfederal', res_t - res_f, tv,
                src + ' item 2A (derived residual)', 'detail')
        a = q2a.loc['Non-S&E, all']
        tot = q1.get('Total') + a.get('Total', 0.0)
        fed = q1.get('Federal') + a.get('Federal', 0.0)
        for sf, val in (('Total', tot), ('Federal', fed),
                        ('Nonfederal', tot - fed)):
            add(year, 'All fields (S&E + non-S&E)', 'All fields (S&E + non-S&E)', sf, val, tv,
                src + ' items 1+2A (derived)', 'grand_total_incl_nonSE')

    # Item 2B: federal by field x agency (FY2003-2009)
    q2b = df[df.questionnaire_no == '02b'].groupby(['row', 'column']).v.sum()
    for (lab, ag), val in q2b.items():
        agency.append(dict(fiscal_year=year, broad_field_native=broad_of(lab) if lab != 'All' else 'All S&E fields',
                           detailed_field_native=lab if lab != 'All' else 'All S&E fields',
                           agency_native=ag, taxonomy_version=tv,
                           value_usd_thousands_nominal=val, source=src + ' item 2B',
                           row_type='grand_total' if lab == 'All' else ('broad_total' if lab.endswith(', all') else 'detail')))

    # consistency check: item 2 'All' equals item 1
    a2 = df[(df.questionnaire_no == '02') & (df.row == 'All')].groupby('column').v.sum()
    if len(a2):
        assert abs(a2['Total'] - q1['Total']) < 1 and abs(a2['Federal'] - q1['Federal']) < 1, year


# ---------------------------------------------------------------- FY2010+
NEW_SOURCES_Q1 = {
    '01.a': 'Federal government', '01.b': 'State and local government', '01.c': 'Business',
    '01.d': 'Nonprofit organizations', '01.e': 'Institution funds', '01.f': 'All other sources',
    '01.g': 'Total',
}
NONFED_COLS = {
    'State and local government': 'State and local government',
    'Business': 'Business',
    'Nonprofit organziations': 'Nonprofit organizations',   # sic in the files
    'Nonprofit organizations': 'Nonprofit organizations',
    'Institution funds': 'Institution funds',
    'All other sources': 'All other sources',
    'Total': 'Nonfederal, total',
}

years_new = sorted(int(re.search(r'herd(\d{4})', f).group(1))
                   for f in glob.glob(os.path.join(CSV, 'herd2*.csv.gz')))
for year in years_new:
    tv = tax_version_new(year)
    df = read(os.path.join(CSV, f'herd{year}.csv.gz'))
    src = f'microdata:herd{year}.csv (standard form)'

    # Q1 national totals by source
    q1 = df[df.questionnaire_no.isin(NEW_SOURCES_Q1)].groupby('questionnaire_no').v.sum()
    for qn, lab in NEW_SOURCES_Q1.items():
        add(year, 'All', 'All', lab, q1.get(qn, 0.0), tv, src + ' Q1', 'grand_total')

    fed = df[df.questionnaire_no.str.match(r'^09[A-K]')]
    nonfed = df[df.questionnaire_no.str.match(r'^11[A-K]')]
    fedt = fed.groupby(['row', 'column']).v.sum().unstack()
    nft = nonfed.groupby(['row', 'column']).v.sum().unstack()
    for lab in sorted(set(fedt.index) | set(nft.index)):
        if lab == 'All':
            rt, broad = 'grand_total', 'All'
        else:
            rt = 'broad_total' if lab.endswith(', all') else 'detail'
            broad = broad_of(lab)
        f_tot = fedt.loc[lab].get('Total', 0.0) if lab in fedt.index else 0.0
        if lab != 'All':
            add(year, broad, lab, 'Federal government', f_tot, tv, src + ' Q9', rt)
        nf = nft.loc[lab] if lab in nft.index else pd.Series(dtype=float)
        if lab != 'All':
            for col, sl in NONFED_COLS.items():
                if col in nf.index:
                    add(year, broad, lab, sl, 0.0 if pd.isna(nf[col]) else nf[col], tv, src + ' Q11', rt)
            add(year, broad, lab, 'Total',
                f_tot + (0.0 if pd.isna(nf.get('Total')) else nf.get('Total', 0.0)), tv,
                src + ' Q9+Q11 (derived)', rt)
        else:
            # grand-total consistency: Q9/Q11 'All' rows vs Q1
            nf_tot = nf.get('Total', 0.0)
            add(year, 'All', 'All', 'Nonfederal, total', nf_tot, tv, src + ' Q11', 'grand_total')
            if abs(f_tot - q1['01.a']) > 1 or abs(f_tot + nf_tot - q1['01.g']) > 1:
                print(f'WARN {year}: Q9/Q11 All ({f_tot:.0f}+{nf_tot:.0f}) vs Q1 '
                      f'({q1["01.a"]:.0f}, {q1["01.g"]:.0f})', file=sys.stderr)
        # agency detail
        if lab in fedt.index:
            for ag, val in fedt.loc[lab].items():
                if ag == 'Total':
                    continue
                agency.append(dict(fiscal_year=year, broad_field_native=broad,
                                   detailed_field_native=lab, agency_native=ag,
                                   taxonomy_version=tv,
                                   value_usd_thousands_nominal=0.0 if pd.isna(val) else val,
                                   source=src + ' Q9', row_type=rt))

    # Q6 type of R&D (totals only; not collected by field)
    q6 = df[df.questionnaire_no.str.startswith('06.')].groupby(['row', 'column']).v.sum()
    for (r, c), val in q6.items():
        character.append(dict(fiscal_year=year, broad_field_native='All', detailed_field_native='All',
                              character_of_work_native=r, source_of_funds_native=c,
                              taxonomy_version=tv, value_usd_thousands_nominal=val,
                              source=src + ' Q6', population='standard form'))

    # short form (FY2012+): broad fields x federal/nonfederal, and Q1 sources
    sp = os.path.join(CSV, f'short{year}.csv.gz')
    if os.path.exists(sp):
        sdf = read(sp)
        ssrc = f'microdata:short{year}.csv (short form)'
        sq1 = sdf[sdf.questionnaire_no.isin(NEW_SOURCES_Q1)].groupby('questionnaire_no').v.sum()
        for qn, lab in NEW_SOURCES_Q1.items():
            add(year, 'All', 'All', lab, sq1.get(qn, 0.0), tv, ssrc + ' Q1', 'grand_total')
        sq2 = sdf[sdf.questionnaire_no.str.startswith('02.')].groupby(['row', 'column']).v.sum()
        for (lab, c), val in sq2.items():
            if lab == 'All':
                if c == 'Nonfederal':
                    add(year, 'All', 'All', 'Nonfederal, total', val, tv, ssrc + ' Q2', 'grand_total')
                continue  # Total/Federal already in Q1
            lab_out = {'Federal': 'Federal government', 'Nonfederal': 'Nonfederal, total',
                       'Total': 'Total'}[c]
            add(year, broad_of(lab), lab, lab_out, val, tv, ssrc + ' Q2', 'broad_total')

out = pd.DataFrame(recs)
out['population'] = out['source'].map(
    lambda s: 'short form (FY2012+, <$1M R&D)' if 'short form' in s else
    ('standard form' if 'standard form' in s else 'all surveyed institutions'))

# ---------------------------------------------------------------- pre-2010 type of R&D (published)
t7 = os.path.join(ROOT, 'raw', 'herd', 'pub_fy2024', 'nsf26304-tab007.xlsx')
if os.path.exists(t7):
    import warnings
    warnings.simplefilter('ignore')
    raw = pd.read_excel(t7, header=None)
    for _, r in raw.iterrows():
        y = str(r[0]).strip()
        m = re.match(r'^(\d{4})', y)
        if not m:
            continue
        year = int(m.group(1))
        if year < 1953 or year > 2009:
            continue
        vals = dict(tot=r[1], tot_basic=r[2], tot_appdev=r[4], fed=r[6], fed_basic=r[7], fed_appdev=r[9])
        for (cw, sf), key in {
            ('All', 'Total'): 'tot', ('Basic research', 'Total'): 'tot_basic',
            ('Applied research and experimental development', 'Total'): 'tot_appdev',
            ('All', 'Federal'): 'fed', ('Basic research', 'Federal'): 'fed_basic',
            ('Applied research and experimental development', 'Federal'): 'fed_appdev'}.items():
            v = vals[key]
            if isinstance(v, str) or pd.isna(v):
                continue
            character.append(dict(fiscal_year=year, broad_field_native='All S&E fields',
                                  detailed_field_native='All S&E fields',
                                  character_of_work_native=cw, source_of_funds_native=sf,
                                  taxonomy_version='ARD (published series)',
                                  value_usd_thousands_nominal=float(v) * 1000.0,
                                  source='NSF 26-304 Table 7 (USD millions x 1000)',
                                  population='all surveyed institutions'))

# finest_level: rows that partition the grand total without overlap (per year x population x source):
# detail rows, plus the broad-field total of any broad field that has no detail rows that year.
has_det = set(map(tuple, out[out.row_type == 'detail'][['fiscal_year', 'population', 'broad_field_native']].values))
out['finest_level'] = out.apply(
    lambda r: r.row_type == 'detail' or (r.row_type == 'broad_total' and
                                         (r.fiscal_year, r.population, r.broad_field_native) not in has_det),
    axis=1)

cols = ['fiscal_year', 'broad_field_native', 'detailed_field_native', 'source_of_funds_native',
        'taxonomy_version', 'value_usd_thousands_nominal', 'source', 'row_type', 'finest_level',
        'population']
out = out[cols].sort_values(['fiscal_year', 'population', 'broad_field_native',
                             'detailed_field_native', 'source_of_funds_native'])
out['value_usd_thousands_nominal'] = out['value_usd_thousands_nominal'].round(0).astype('int64')
out.to_csv(os.path.join(OUT, 'herd_by_field_source.csv'), index=False)

ch = pd.DataFrame(character).sort_values(['fiscal_year', 'source_of_funds_native', 'character_of_work_native'])
ch['value_usd_thousands_nominal'] = ch['value_usd_thousands_nominal'].round(0).astype('int64')
ch.to_csv(os.path.join(OUT, 'herd_by_field_character.csv'), index=False)

ag = pd.DataFrame(agency).sort_values(['fiscal_year', 'broad_field_native', 'detailed_field_native', 'agency_native'])
ag['value_usd_thousands_nominal'] = ag['value_usd_thousands_nominal'].round(0).astype('int64')
ag.to_csv(os.path.join(OUT, 'herd_federal_by_agency_field.csv'), index=False)

ex = pd.DataFrame(excluded, columns=['fiscal_year', 'row', 'total', 'federal'])
ex.to_csv(os.path.join(OUT, 'herd_excluded_not_collected.csv'), index=False)
print(len(out), len(ch), len(ag), len(ex))
