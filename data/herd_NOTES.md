# US higher education R&D by field and source of funds, FY1972–FY2024

Built 2026-11-18 from NCSES institution-level public use microdata, then checked against NCSES published tables. All values are thousands of current (nominal) US dollars. Fiscal years are each institution's academic fiscal year, mostly July–June.

## Files

| File | What |
|---|---|
| `data/herd_by_field_source.csv` | Main output. Long format, FY1972–2024, field × source of funds |
| `data/herd_by_field_character.csv` | Type of R&D (basic, applied, development). National totals only, because no year collects it by field |
| `data/herd_federal_by_agency_field.csv` | Federal R&D by agency × field, FY2003–2024, detailed and broad fields |
| `data/herd_checks.txt` | Full output of the consistency checks and the published-table checks |
| `data/herd_item_inventory.csv` | Every questionnaire item, row and column in each year's file, with counts (taken from the full extracts) |
| `data/herd_excluded_not_collected.csv` | Rows present in the files for years before NCSES collected that subfield (see Gaps) |
| `scripts/herd_inventory.py`, `herd_slim.py`, `herd_build.py`, `herd_check.py` | Run in that order, each as `python -I scripts/<name>.py <project_root>`. herd_inventory takes a second argument, the output path |
| `raw/herd/` | `csv/*.csv.gz` holds the microdata cut down to the items used. `pub_fy2024/` holds the NSF 26-304 tables. `pub_hist/` holds SEI 2008 appendix table 5-4 and the FY2016 field-change list. `fy-2024-herd-dug-text-file-format.pdf` is the data users' guide |

### Columns in `herd_by_field_source.csv`

- `fiscal_year`
- `broad_field_native`: the text before the first comma in the native row label, for example `Life sciences` or `Engineering`. Grand-total rows use `All S&E fields` (FY1972–2009), `All fields (S&E + non-S&E)` (FY2003–09, derived), or `All` (FY2010+).
- `detailed_field_native`: the row label exactly as it appears in the microdata. Labels ending in `, all` are broad-field totals.
- `source_of_funds_native`: the source category for that year.
  - FY1972–2009, grand total: `Federal`, `State and local government`, `Industry`, `Institution funds`, `All other sources`, `Total`.
  - FY1973–2009, by field: `Total`, `Federal`, and `Nonfederal` (derived as Total minus Federal).
  - FY2010+: `Federal government`, `State and local government`, `Business`, `Nonprofit organizations`, `Institution funds`, `All other sources`, `Nonfederal, total`, `Total`.
- `taxonomy_version`: `ARD_1972`, `ARD_1973-1979`, `ARD_1980-1989`, `ARD_1990-1996`, `ARD_1997-2009`, `HERD_2010-2015` or `HERD_2016-`. ARD is the Academic R&D Expenditures Survey.
- `value_usd_thousands_nominal`
- `source`: the microdata file and item number. Values computed rather than reported are marked `(derived ...)`.
- `row_type`, one of:
  - `detail`
  - `broad_total`
  - `grand_total`
  - `grand_total_incl_nonSE` (FY2003–09 only)
- `finest_level`: True for rows that split the grand total without overlap. These are the detail rows, plus the broad-field total of any broad field that has no subfields in that year. Summing finest-level rows within a year, population and source gives the grand total.
- `population`:
  - `all surveyed institutions` (FY1972–2011)
  - `standard form` (FY2010+)
  - `short form (FY2012+, <$1M R&D)`

  For FY2012 on, add standard-form and short-form rows to get the national total. Short-form institutions report broad fields × federal and nonfederal only. Short-form R&D is about 0.1–0.2% of the total, for example $164 million of $117.7 billion in FY2024.

Two extra columns (`finest_level`, `population`) were added to the requested schema so that the file can be summed without double counting.

## Sources (exact URLs)

- Microdata landing page: https://ncses.nsf.gov/explore-data/microdata/higher-education-research-development
  - Files: `https://ncses.nsf.gov/821/assets/0/files/higher_education_r_and_d_{YYYY}.zip` for 1972–2024, and `..._{YYYY}_short.zip` for 2012–2024. All 66 files downloaded on 2026-11-18. CSVs were extracted and the zips deleted.
  - File layout guide: https://ncses.nsf.gov/821/assets/0/files/fy-2024-herd-dug-text-file-format.pdf (Guide for Public Use Data Files, FY2024, September 2025). Section 1.3 covers FY2010+ and section 2.3 covers FY1972–2009.
- Published tables, HERD FY2024 (report ncses26003, tables NSF 26-304): https://ncses.nsf.gov/pubs/ncses26003, and https://ncses.nsf.gov/pubs/nsf26304/assets/data-tables/nsf26304-data-tables-tables-excels.zip. Tables used:
  - Table 1: source of funds, FY1953–2024
  - Table 2: by population, FY2010–24
  - Table 7: type of R&D, FY1953–2024
  - Table 8: source × type, FY2010–24
  - Table 9: field, FY2010–24
  - Table 10: field × source, FY2024
  - Table 11: agency × field, FY2024
- Technical notes for the FY2024 cycle: https://ncses.nsf.gov/surveys/higher-education-research-development/2024 (Data Comparability section).
- Pre-2010 field check: Science and Engineering Indicators 2008, appendix table 5-4, "Expenditures for academic R&D, by field: Selected years, 1975–2006". Retrieved from the UNT web archive: https://webarchive.library.unt.edu/web/20090512212604id_/http://nsf.gov/statistics/seind08/append/c5/at05-04.pdf
- FY2016 field changes: "Fields of R&D for the FY 2016 Higher Education Research and Development Survey", an NCSES list with a "Changes from FY 2015" column, as reposted by Boise State: https://boisestate.edu/research-osp/wp-content/uploads/sites/233/2017/04/NSF-Survey-RD-Field-Codes-FY-2016.pdf. The FY2016 Technical Notes Appendix A (formerly ncsesdata.nsf.gov/herd/2016) now only exists on archive-it, which was rate-limiting this session.
- DataLumos mirror (https://doi.org/10.3886/E239710V1) was not used. It sits behind a Cloudflare JavaScript challenge, and the NCSES files were complete.

## File layouts used

Both eras are long format: one record per institution × questionnaire item × row × column, with values in `data` in $ thousands. Status codes are blank (reported), `e` (estimated by NCSES), `i` (imputed) and `n` (not available). Imputed and estimated values are included, which is how NCSES builds its national totals. Files are Latin-1 encoded.

**FY1972–2009** (`herd_YYYY.csv`). Columns used: `questionnaire_no`, `question`, `row`, `column`, `data`, `status`.
- Line references were restated in the FY2009 format.
- Every record is summed, including `fice_combined` records and the NCSES aggregate-estimate records (hdg_code 9). The sums reproduce Table 1 exactly, so nothing is double counted.

Items used:
- `01` Source (no `column`): Federal, State and local government, Industry, Institution funds (total), All other sources, Total. S&E only.
- `02` Expenditures by S&E field: rows are fields, columns `Total` and `Federal`.
- `02a` Non-S&E fields, FY2003–09: `Total` and `Federal`.
- `02b` Federal by S&E field × agency, FY2003–09: DOD, DOE, HHS, NASA, NSF, USDA, Other agencies.

**FY2010+** (`herdYYYY.csv`, standard form). Row and question numbers were restated in the FY2024 format (guide section 1.3), so FY2010–15 rows carry the post-2016 field names. Items used:
- `01.a`–`01.g`: source totals.
- `06.a`–`06.d`: type of R&D × Federal, Nonfederal, Total.
- `09A`–`09K`: federal by field × agency, plus a Total column.
- `11A`–`11K`: nonfederal by field × State and local government, Business, Nonprofit (misspelled `Nonprofit organziations` in the files), Institution funds, All other sources, Total.
- Field total = Q9 Total + Q11 Total (derived). It matches Table 9 exactly.

**FY2012+ short form** (`shortYYYY.csv`). Items used:
- `01.a`–`01.g`: sources.
- `02.a`–`02.k`: broad field × Federal, Nonfederal, Total.

## Taxonomy and population breaks

### Survey and population

| Years | Survey | Population and threshold |
|---|---|---|
| FY1972–1977, 1979–1997 | Academic R&D Expenditures Survey | Institutions with S&E doctoral programs, or at least $50K separately budgeted S&E R&D. FY1984–87, 1989–92 and 1994–97 were sample years, with non-sampled institutions imputed. The file has about 535–690 institutions |
| FY1978 | same | Only doctorate-granting institutions surveyed (317). NCSES estimated the rest, and the estimate is in the file as an aggregate record |
| FY1998–2003 | same | Bachelor's or higher in S&E and at least $150K separately budgeted R&D, plus all S&E doctorate-granting institutions and HBCUs |
| FY2004–2009 | same | Bachelor's or higher in S&E and at least $150K S&E R&D. 711 institutions in FY2009 |
| FY2010+ | HERD | Bachelor's or higher in any field and at least $150K R&D in any field. Each separate campus reports on its own instead of combined system reports (711 institutions in FY2009 to 742–744 in FY2010; the technical notes and the guide differ). Clinical trials and research training grants explicitly count as R&D. From FY2012, institutions under $1M receive the short form. 925 institutions in FY2024 |

The FY2009 to FY2010 jump in the national total is $57.3B to $61.3B. Of that, S&E alone goes from $54.9B to about $58.4B (science $49.1B plus engineering $9.3B). The rest is non-S&E coverage ($2.4B in FY2009, a lower bound because it was never imputed, to $2.9B in FY2010) and the broader R&D definition. FY2003–09 totals in Table 1 include the non-S&E item, which here is the `All fields (S&E + non-S&E)` row. Before FY2003 the totals are S&E only.

Source categories also change at FY2010:

| FY1972–2009 | FY2010+ |
|---|---|
| Federal | Federal government |
| State and local government | same |
| Industry | Business |
| Institution funds | Institution funds |
| All other sources (includes nonprofits) | split into Nonprofit organizations and All other sources |

Other FY2010+ instruction changes that affect source shares (from the technical notes):
- FY2012: the instructions spelled out what institutionally financed research covers, including 501(c)(3) foundation funds.
- FY2013: funds from foreign and US universities go to All other sources.
- FY2017: FFRDC funds are reported as federal.
- FY2018: research administration is excluded from institution funds.

Before FY2010, fields are collected as Total and Federal only, so the only cross-tab by field is federal versus nonfederal. The six-way source split exists only for the national total. Field × each nonfederal source starts in FY2010.

### Field taxonomy versions

- **ARD_1972**: no field item released. The guide states "Expenditures by fields of science are not available for FY 1972", so FY1972 has source totals only.
- **ARD_1973-1979**: these fields:
  - Engineering (total only)
  - Physical sciences: astronomy, chemistry, physics, other
  - Environmental sciences (total only)
  - Mathematical sciences
  - Computer sciences
  - Life sciences: agricultural, biological, medical, other
  - Psychology
  - Social sciences: economics, political science, sociology, other
  - Other sciences

  Life, physical and social sciences have no `, all` line before FY1979, so here they are derived as sums of their subfields. FY1973 biological sciences originally included agricultural sciences. NCSES split them back using FY1974 shares.
- **ARD_1980-1989**: adds engineering subfields (aeronautical and astronautical, chemical, civil, electrical, mechanical, other) and environmental subfields (atmospheric, earth sciences, oceanography, other).
- **ARD_1990-1996**: adds metallurgical and materials engineering, taken out of engineering "other", which falls from $867M in FY1989 to $663M in FY1990.
- **ARD_1997-2009**: adds bioengineering and biomedical engineering. Non-S&E fields (item 2A) start in FY2003: business and management; communications, journalism, library science; education; humanities; law; social work; visual and performing arts; other. FY2003–04 (and slightly FY2005, 2007, 2008) report part of non-S&E only as a total. A `Non-S&E, not allocated to a subfield (derived residual)` row makes the detail rows add up.
- **HERD_2010-2015**: the predecessor's fields, plus the same non-S&E list as a full part of the total. The microdata show these years under FY2016+ names. The FY2016 change list gives the old names that changed, and the rest are as in ARD:

  | FY2010–15 name (Academic R&D wording) | FY2016+ name |
  |---|---|
  | Environmental sciences | Geosciences, atmospheric, and ocean sciences |
  | Biological sciences | Biological and biomedical sciences |
  | Medical sciences | Health sciences |
  | Business and management | Business management and business administration |
  | Communication, journalism, and library science | Communication and communications technologies |

  The other FY2010–15 labels in the files (for example computer and information sciences, mathematics and statistics, atmospheric science and meteorology, political science and government) are NCSES's restated names. I could not confirm the original FY2010–15 questionnaire wording, because the FY2010–15 HERD tables only survive on archive-it, which was rate-limiting. Treat those FY2010–15 labels as NCSES restatements, not as the survey's own wording.
- **HERD_2016-**: four new fields, plus discipline moves. Main moves (old field to new field):
  - Metallurgical and materials engineering (materials science part) → Physical sciences, materials science (new). Metallurgical and materials engineering falls from $1,102M in FY2015 to $744M in FY2016, and materials science starts at $172M.
  - Other engineering (industrial, manufacturing and systems eng.) and Mathematics (operations research) → Engineering, industrial and manufacturing (new). It starts at $237M.
  - Agricultural sciences (forestry, fisheries, conservation, renewable resources) and Economics (natural resource economics) → Life sciences, natural resources and conservation (new). It starts at $693M, and agricultural sciences falls from $3,480M to $3,288M.
  - Sociology (cultural anthropology) and Biological sciences (physical anthropology) → Social sciences, anthropology (new). It starts at $96M.
  - Medical sciences (neuroscience, pharmacology) → Biological and biomedical sciences.
  - Other life sciences (nursing, therapy and rehabilitation, communication disorders, gerontology, lab technologies, health administration), plus all veterinary disciplines from agricultural and biological sciences → Health sciences. Life sciences other falls from $2,287M to $1,463M, and biological and biomedical rises from $11.7B to $13.0B.
  - Political science (public administration), Other social sciences (urban planning, history of science), Civil eng. (architecture), Agricultural sci. (landscape architecture), Communication (library science), Biological sci. (food and nutrition studies) → Non-S&E fields, mostly "Other non-S&E". Non-S&E other rises from $664M to $1,011M.
  - Computer sciences (management information systems) → Non-S&E, business.
  - Physics (chemical physics) → Chemistry. Chemistry (pharmaceutical chemistry) → Health sciences. Chemical eng. (petroleum eng.) and Mechanical eng. (engineering mechanics) → Other engineering. Chemical eng. (wood science) → Agricultural sciences. Geological and earth sciences (cartography) → Other social sciences.

  The technical notes also say Questions 9, 11 and 14 changed fields "for FY 2020". The FY2016–2024 microdata show no new or renamed field rows after FY2016, so I treat that as a repeated sentence, not a second break.

Old-to-new crosswalk at the FY2009/2010 break, broad level, native labels on both sides:

| FY1973–2009 | FY2010+ |
|---|---|
| Computer sciences | Computer and information sciences |
| Environmental sciences (atmospheric; earth; oceanography; other) | Geosciences, atmospheric sciences, and ocean sciences (atmospheric science and meteorology; geological and earth sciences; ocean sciences and marine sciences; other) |
| Life sciences: agricultural; biological; medical; other | Life sciences: agricultural; biological and biomedical; health; other (+ natural resources and conservation from FY2016) |
| Mathematical sciences | Mathematics and statistics |
| Physical sciences: astronomy; chemistry; physics; other | Physical sciences: astronomy and astrophysics; chemistry; physics; other (+ materials science from FY2016) |
| Psychology | Psychology |
| Social sciences: economics; political science; sociology; other | Social sciences: economics; political science and government; sociology, demography, and population studies; other (+ anthropology from FY2016) |
| Other sciences | Other sciences ("Sciences nec" in the tables) |
| Engineering: aeronautical and astronautical; bioengineering and biomedical; chemical; civil; electrical; mechanical; metallurgical and materials; other | Engineering: aerospace, aeronautical, and astronautical; bioengineering and biomedical engineering; chemical; civil; electrical, electronic, and communications; mechanical; metallurgical and materials; other (+ industrial and manufacturing from FY2016) |
| Non-S&E (item 2A, outside the total) | Non-S&E (inside the total) |

Labels are not harmonized beyond this table.

## Character of work (`herd_by_field_character.csv`)

- **FY2010–2024**: from microdata Q6. Basic, applied and development × Federal, Nonfederal and Total, standard form only, since the short form does not ask. Matches Table 8 exactly. There is no field breakdown.
- **FY1953–2009**: taken from published Table 7. It splits Total and Federal into basic research versus applied research plus development, S&E only. Amounts are in USD millions and stored ×1000. Before FY2010 these were institution-reported percentage estimates. The estimation method was revised in FY1998, so the series is not comparable across 1997/1998. FY1978 is blank (not collected). Federal basic research is not available before FY1972, and pre-1972 totals are NCSES interpolations between survey years.

## Federal agency × field (`herd_federal_by_agency_field.csv`)

- **FY2003–2009**: item 2B, S&E fields only.
- **FY2010+**: Q9, all fields, standard form only.

Agencies are DOD, DOE, HHS, NASA, NSF, USDA and Other agencies. Detailed and broad fields are both included. Agency × field does not exist before FY2003.

## Gaps

- **FY1972**: no field data, only the six source totals. Published field totals for FY1972 were not found online. SEI tables start at FY1975.
- **FY1978**: NCSES estimate built from doctorate-granting institutions only. National totals match Table 1, but treat field detail as lower quality.
- **Subfields before they were collected**: the files carry rows for engineering and environmental subfields in FY1973–79, metallurgical and materials engineering in FY1984–89, and bioengineering in FY1984–96, holding zeros or scattered values. In FY1979 they hold scattered retro-imputed values that sum to only a few percent of the broad field. These rows are left out (listed in `herd_excluded_not_collected.csv`), and the broad totals cover those years.
- **Field × nonfederal source** is only available from FY2010. Before that, only federal and nonfederal by field.
- **Short-form institutions (FY2012+)**: broad fields only, and nonfederal is not split by source within fields.
- **Federal by agency**: no agency detail before FY2003.
- **Institution-fund detail**: the split into institutionally financed research, cost sharing and unrecovered indirect costs (Table 2) is not in the public files, so it is not captured.

## Sanity checks (full output in `herd_checks.txt`)

Internal checks:
- Detail rows sum to their broad-field totals in every year and source (1,254 pairs, 0 over $2K, after the non-S&E residual).
- Broad fields sum to the grand total for every source.
- Item 2 'All' equals item 1 for Total and Federal in FY1973–2009 (asserted in the build).
- Q9 and Q11 'All' rows equal Q1 in FY2010–24.

National totals against NCSES Table 1, $ millions, as mine / published:

| FY | Total | Federal | Note |
|---|---|---|---|
| 1975 | 3,408.7 / 3,409 | 2,288.1 / 2,288 | |
| 1985 | 9,687.1 / 9,687 | 6,064.4 / 6,064 | sample year |
| 1995 | 22,179.0 / 22,179 | 13,337.4 / 13,337 | sample year |
| 2005 | 47,535.2 / 47,535 | 29,956.7 / 29,957 | S&E + non-S&E. S&E only is 45,774.0 / 29,186.5 |
| 2015 | 68,665.3 / 68,665 | 37,910.6 / 37,911 | standard + short |
| 2024 | 117,718.6 / 117,719 | 64,717.6 / 64,718 | standard + short |

Every year from FY1972 to FY2024 and every source in Table 1 matches within rounding (largest gap $0.5M).

Field checks:
- FY2010–24 standard-form field totals (666 field-year cells, all detailed and broad fields) match Table 9 exactly.
- FY2024 broad field × each source matches Table 10 exactly.
- FY2024 agency × broad field matches Table 11 (the cells inspected are identical).
- Type of R&D FY2010–24 matches Table 8 exactly.
- Standard + short form equals the Table 2 all-institution totals in every year.
- Pre-2010 fields against SEI 2008 appendix table 5-4 (current $M, 525 field-year cells for 1975, 1980, 1985, 1990, 1995–2006): 453 cells within $1M, largest gap 2.9% (FY2006 life sciences "other", $34M). The gaps come from revisions and retro-imputation since 2008, and grow toward 2006, as expected.

## Things to watch

- **Life sciences totals**: medical sciences (later health sciences) is the largest field. Its FY2009 to FY2010 rise ($18.2B to $19.3B) mixes real growth with the HERD definition change (clinical trials and training grants explicitly included).
- **Metallurgical and materials engineering**: jumps in FY2014 ($1,203M, from $812M in FY2013), then drops back in FY2016 when materials science moved out. The FY2014–15 level looks like a reporting change at one or a few institutions, not a national trend. It is worth checking at institution level before using it.
- **Mathematical sciences**: falls from $620M in FY2008 to $547M in FY2009, then reads $592M in FY2010 under the new survey.
- **Institution comparisons**: system-level combined reporting before FY2010 versus campus-level reporting from FY2010 changes institution counts, not national totals.
- **Data vintage**: NCSES revises earlier years through retro-imputation. Use these files (downloaded 2026-11-18, file dates 2023-09 for FY1972–2009 and 2025-09 for FY2010+) as one vintage.
