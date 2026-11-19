# US business R&D by industry: NSF/NCSES SIRD, BRDIS, BRDS, BERD

Built 2026-11-18. Files:

- `data/berd_by_industry.csv`: long format, one row per year x industry x measure x source table.
- `data/berd_concordance.csv`: suggested mapping of native codes to the 21 analysis groups, by era.
- Scripts: `scripts/berd_parse_ncses.py` (BRDIS/BRDS/BERD Excel), `scripts/berd_sird_pdf.py` (SIRD PDF volumes), `scripts/berd_parse_sei.py` (SEI table), `scripts/berd_merge.py`, `scripts/berd_check.py`, `scripts/berd_common.py`.
- Raw downloads: `raw/berd/` (one folder per release).

## Columns

| column | meaning |
|---|---|
| year | calendar year of R&D performance |
| industry_code_native, industry_label_native | exactly as published (labels whitespace-normalized; footnote letters dropped) |
| classification | `NAICS1997`, `NAICS2002`, `NAICS2007`, `NAICS2012`, `NAICS2017` (the NAICS vintage NCSES states for that survey year), or `NAICS2002_SIRD_pre2004_method` (bridge rows, see breaks) |
| measure | `total`, `basic`, `applied`, `development`, `company_funded`, `other_funded`, `federal_funded`, `nonfederal_funded` (SIRD: company + other nonfederal), plus funder x type cells such as `federal_funded_basic`, `company_funded_applied`, `nonfederal_funded_development` |
| value_usd_millions_nominal | millions of current US dollars; blank when the cell is suppressed, a range, or under $0.5m |
| flag | `D` withheld (disclosure); `i` >50% imputed/reweighted (BRDIS/BERD); `S` >50% imputed (SIRD); `r` RSE >50% (BERD single-year tables); `*` < $0.5 million; `R` published as a range; combinations joined with `+` |
| range_low, range_high | bounds when flag contains `R` (NCSES now prints ranges instead of D for some cells) |
| is_primary | 1 = the row to use. 0 = duplicate of the same year/industry/measure from another table (kept so both vintages are visible) |
| survey | SIRD, BRDIS, BRDS, BERD |
| source_table, source_url | release ID and table number; URL of the Excel/PDF |

All values are R&D performed by the company inside the 50 states and DC ("domestic"), from all sources of funds. Worldwide and foreign R&D were not captured.

Use `is_primary == 1`. For a given year and industry the `total` comes from a different table than the funding and type splits, so splits will not add exactly to the total (see sanity checks).

## Sources (exact URLs)

BERD / BRDS / BRDIS (Excel, ncses.nsf.gov). Pattern for every table: `https://ncses.nsf.gov/pubs/<id>/assets/data-tables/tables/<file>.xlsx`; zips at `https://ncses.nsf.gov/pubs/<id>/assets/data-tables/<id>-data-tables-tables-excels.zip` (2020+) or `...-data-tables-tables.zip`.

| year | release | page |
|---|---|---|
| 2024 | NSF 27-300 | https://ncses.nsf.gov/pubs/nsf27300 (released 29 Oct 2026; InfoBrief NSF 27-301) |
| 2023 | NSF 25-354 | https://ncses.nsf.gov/pubs/nsf25354 (InfoBrief NSF 25-353) |
| 2022 | NSF 24-335 | https://ncses.nsf.gov/pubs/nsf24335 |
| 2021 | NSF 23-351 | https://ncses.nsf.gov/pubs/nsf23351 |
| 2020 | NSF 23-314 | https://ncses.nsf.gov/pubs/nsf23314 |
| 2019 | NSF 22-329 | https://ncses.nsf.gov/pubs/nsf22329 |
| 2018 (BRDS) | NSF 21-312 | https://ncses.nsf.gov/pubs/nsf21312 |
| 2017 (BRDS) | NSF 20-311 | https://ncses.nsf.gov/pubs/nsf20311 |
| 2016 (BRDIS) | NSF 19-318 | https://ncses.nsf.gov/pubs/nsf19318 |
| 2015 (BRDIS) | NSF 18-313 | https://ncses.nsf.gov/pubs/nsf18313 |

Tables used per release (numbers shift between releases; the parser matches on titles):

- Multi-year total by industry, 2008-2024: NSF 27-300 Table 58 "Domestic R&D paid for by the company and others and performed by the company, by industry and company size: 2008-24". Primary `total` for 2008-2024. It carries NCSES's revised values ("Most statistics for years prior to 2024 have been revised since original publication").
- Type of R&D (total): "Domestic R&D paid for by the company and others and performed by the company, by type of R&D, industry, and company size" (Table 12 every year). Gives `basic`, `applied`, `development`; its total is kept with `is_primary=0`.
- Funder x type: "Domestic R&D paid for and performed by the company, by type of R&D ..." (`company_funded_*`), "... paid for by others ... by type of R&D ..." (`other_funded_*`), "... paid for by the U.S. federal government ... by type of R&D ..." (`federal_funded_*`).
- Company vs others at full industry detail: "Domestic R&D performance (,) by performer (and) source of funds, industry, and company size" (columns Performed by the company: Paid for by the company, Paid for by others).
- Federal at full industry detail: "Domestic R&D paid for by others and performed by the company, by source of funds, industry, and company size" (column U.S. federal government agencies).

SIRD, NAICS basis (born-digital PDFs from the University of North Texas End of Term 2008 web archive):

- Research and Development in Industry: 2003 (NSF 07-314): https://webarchive.library.unt.edu/eot2008/20090514051234/http://www.nsf.gov/statistics/nsf07314/pdf/nsf07314.pdf . Tables 3 (total, 1999-2003), 12 (company and other nonfederal, 1999-2003), 20 (federal, 1999-2003), 34 (basic/applied/development by industry and source, 2003). 1999-2002 values here are the revised ones.
- Research and Development in Industry: 2004 (NSF 09-301): https://webarchive.library.unt.edu/eot2008/20090514044938/http://www.nsf.gov/statistics/nsf09301/pdf/nsf09301.pdf . Table 28 (total, federal, nonfederal, basic/applied/development x source, 2004) and Table A-9 (2004 by original vs revised industry classification method).

Science & Engineering Indicators 2022, NSB 2022-5, Table SRD-4 (type of R&D by select industry, 2010-19): https://ncses.nsf.gov/pubs/nsb20225/assets/nsb20225-supplemental-materials.zip . Used only for 2010-2014 basic/applied/development, at the 31-33, 325, 334, 336, 21-23/42-81, 51, 54 level.

Survey methodology and comparability text: https://ncses.nsf.gov/surveys/business-enterprise-research-development/2024 (and /2023).

## Coverage of what is in the file (is_primary = 1)

| measure | years | industry detail |
|---|---|---|
| total | 1999-2004 (SIRD NAICS), 2008-2024 (BRDIS/BERD) | full published detail (about 60-73 rows) |
| company_funded, other_funded | 2015-2024 | full detail |
| federal_funded | 1999-2004, 2015-2024 | full detail |
| nonfederal_funded | 1999-2004 | full detail (SIRD concept = company + other nonfederal) |
| basic, applied, development | 2003-2004; 2010-2014 (coarse, SEI); 2015-2024 | 2015-18 about 40 rows; 2019+ about 73 rows |
| funder x type cells | 2003-2004 (federal / nonfederal), 2015-2024 (company / others / federal) | as above |

## Gaps

1. SIRD 1953-1998 (SIC basis) by industry: NOT in the file. The source is NSF's Industrial Research and Development Information System (IRIS, `https://www.nsf.gov/statistics/iris/`, about 2,500 historical tables; its menu lists "Total R&D by Industry [1953-2007]", "Company R&D by Industry [1953-2007]", "Federal R&D by Industry [1953-2007]", "B,A,D by Industry and Source [1953-2007]"). nsf.gov now redirects it to NSF's Archive-It collection (`https://wayback.archive-it.org/5902/20181003221605/https://www.nsf.gov/statistics/iris/`), which returned "Rate limit reached" throughout; web.archive.org was not reachable when this was built; the UNT End of Term archive holds only the IRIS menu pages, not the `search_hist.cfm` table pages or the Excel files. Scanned SIRD volumes for 1969-1999 exist on archive.org (e.g. `ns-reports_ns-122in-2-995-96`, `ns-reports_ns-122in-2-985-86`, `ERIC_ED186278`, `ERIC_ED463163`), but their OCR of numeric tables is too poor to parse without hand checking (e.g. "10,6%", "(0)" for "(D)"). SIC-basis industry detail for 1956-96 was later hand-transcribed from the scanned volumes: see `sird_scan_by_industry.csv` and `sird_scan_NOTES.md`.
2. SIRD 2005-2007 (NSF 10-319 and the 2006-07 volume) and BRDIS 2008-2014 single-year releases (source of funds and type of R&D by industry): same Archive-It problem. For 2008-2014 the file has totals by industry (revised, from the 2024 multi-year table) and coarse basic/applied/development for 2010-14 (SEI). Company/federal splits by industry for 2005-2014 are missing.
3. 1997-1998 on NAICS (published in R&D in Industry: 1999, NSF 02-312, table A-2) not captured (only an OCR'd ERIC copy is available: `https://archive.org/download/ERIC_ED463163/ERIC_ED463163.pdf`).
4. Computers and peripherals (3341) is never published separately in BRDIS/BERD.
5. Many SIRD NAICS cells are D (pharma total 1999, 2000, 2002, 2003; motor vehicles 1999-2003; software 2003-04). For pharma, nonfederal funds are published even when the total is D, and federal funds there are tiny, so nonfederal is a good proxy.

## Breaks and how to bridge them

1. SIC to NAICS (SIRD 1999 survey). IRIS SIC series end in 1998; NAICS series start in 1999 (NSF also republished 1997-98 on NAICS in NSF 02-312). Use `berd_concordance.csv` for the group mapping. Biggest differences: SIC 35 contains computers (357) and NAICS 333 does not; SIC 38 instruments splits into NAICS 3345, 3391 and others; software, computer services and R&D services (SIC 737, 871, 873) map to NAICS 5112, 5415, 5413, 5417 only approximately. Bridge with the 1997-98 overlap where available; otherwise splice on group shares.
2. SIRD industry classification method, 2004. Before 2004 SIRD coded each company by the industry with the largest payroll, and electronically assigned codes put much R&D in wholesale trade (42, notably 4222 drugs) and management of companies (55). For 2004 NSF hand-reviewed codes. Table A-9 of NSF 09-301 gives 2004 under both methods (rows with classification `NAICS2002_SIRD_pre2004_method`): pharma 3254 = 15,935 (old) vs 31,477 (new); 4222 = 12,931 (old); manufacturing 109,455 vs 147,288. Splice 1999-2003 to 2004+ with the A-9 ratios, or add 4222 to 3254 before 2004.
3. SIRD to BRDIS (2008). BRDIS assigns industry by the business code with the largest domestic R&D (BERD notes: "Industry classification is based on the dominant business code for domestic R&D performance"), collects worldwide R&D, and uses a modular questionnaire. NCSES says no conclusive break in the aggregate, but industry levels jump: aerospace 13.1bn (SIRD 2004) vs 36.9bn (BRDIS 2008); pharma 31.5bn vs 48.1bn; total 208.3bn (2004) vs 290.7bn (2008). The SIRD 2005-2007 years that would show the size of the jump are in gap 2.
4. NAICS vintage: 2002 (2008), 2007 (2009-13), 2012 (2014-19), 2017 (2020-24). Small effects except 5417 detail codes (541711/541712 in 2012 NAICS, 541713/541714/541715 in 2017 NAICS) and 51 (5112 software publishers moves to 513210 only in NAICS 2022, which BERD has not adopted).
5. "Other nonmanufacturing" composition changes in 2011 (NCSES note), and table-specific scopes: in the 2015-18 single-year type-of-R&D tables, "other 334" includes 3341 and 3342, "other 336" includes motor vehicles, and "Miscellaneous manufacturing" is coded "322, 324, 339". In the multi-year and 2019+ tables, "other 334" includes 3341 only. Same code string, different scope: read with `source_table`.
6. Employment threshold: SIRD and BRDIS cover companies with 5+ employees; BRDS/BERD (2017+) 10+ employees (the 5-9 class was 1.6bn in 2016).
7. $50,000 threshold: from 2018, companies that performed or funded less than $50,000 of R&D are excluded (about $70 million in 2024).
8. 2023 reporting-practice change. During the 2023 collection some respondents dropped expenditures that do not meet the BERD R&D definition, which lowers 2023 relative to what 2022 practice would have produced. NCSES states that "no revisions will be made to the R&D expenditure estimates published for the 2022 or earlier BERD Surveys" (2023 and 2024 survey pages; same wording in National Patterns 2023-24). So no revised (lower) 2022-and-earlier series exists, and none is quantified; 2022->2023 growth (+4.5% revised, 691,987 -> 723,206) understates the like-for-like change. The only revisions to earlier years are NCSES's routine ones, which the 2024 multi-year table carries (`is_primary=1`); first-published values are kept with `is_primary=0`.
9. Type of R&D: NSF revised the business basic/applied/development estimation method for 1998 onward (National Patterns technical notes), so SIC-era basic research shares are not comparable with 1998+.
10. SIRD federal funds are reported by performers and differ from agency-reported obligations (Federal Funds survey); SIRD 2001+ excludes FFRDCs.
11. Concepts: SIRD splits funds into federal and "company and other nonfederal"; BRDIS/BERD split into "paid for by the company" and "paid for by others" (federal is one part of others, along with other companies, foreign parents, etc.). For a federal vs nonfederal series across the 2008 break use `federal_funded` and `total - federal_funded`.

## Retail trade and Amazon

BERD shows only "Electronic shopping and electronic auctions" (454111-12) separately; the rest of retail is inside "Other nonmanufacturing". Its values are small or suppressed (1.4bn 2014, 11.7bn 2018 (i), range 0-17.2bn 2019, range 14.5-20.9bn 2020, D 2021-22, 8.0bn 2023, 7.9bn 2024). Amazon alone reports tens of billions of "technology and infrastructure" spending, so after 2019 it is almost certainly coded to another industry under the dominant-R&D-business-code rule. Data processing and hosting (518, 6.6bn 2008 to 58.8bn 2024) and "other 51" (1.0bn to 102.5bn) are the likely homes. This is an inference from magnitudes; NCSES does not name companies.

## Concordance for the analysis groups

See `data/berd_concordance.csv` (group, era, native codes, relation, note). In short:

| group | SIC (IRIS, 1953-98) | NAICS (SIRD 1999-2004; BRDIS/BERD 2008+) |
|---|---|---|
| Pharmaceuticals | 283 | 3254 (+4222 before 2004) |
| Other chemicals | 28 - 283 | 325 - 3254 |
| Semiconductors | 367 | 3344 |
| Computers and peripherals | 357 | 3341 (SIRD only; in "other 334" from 2008) |
| Communications equipment | 366 | 3342 |
| Instruments (nav, measuring, electromedical) | 381-382 (+3845) | 3345 |
| Other computer and electronic | 365, 369 parts | other 334 |
| Electrical equipment | 361-364, 369 | 335 |
| Machinery | 35 - 357 | 333 |
| Motor vehicles and parts | 371 | 3361-63 |
| Aerospace | 372, 376 | 3364 |
| Other transportation | 373-375, 379 | other 336 |
| Other manufacturing | rest of 20-39 | rest of 31-33 |
| Software publishers | 7372 (in 737) | 5112 |
| Other information | 48 communications, 27 publishing parts | 51 - 5112 |
| Computer systems design | 7371, 7373, 7379 | 5415 |
| Scientific R&D services | 873 | 5417 |
| Architectural and engineering | 871 | 5413 |
| Health care | 80 | 621-623 |
| Retail trade | 52-59 | 44-45 (BERD: only 454111-12) |
| Other nonmanufacturing | rest | rest |

## Sanity checks

Output of `scripts/berd_check.py` for selected years (USD millions). "total" is the primary total for that year.

| year | classification | check | values (USD m) | diff |
|---|---|---|---|---|
| 1999 | NAICS1997 | nonfederal + federal | 161594 + 22535 = 184129 vs total 184129 | +0 |
| 1999 | NAICS1997 | manufacturing + nonmanufacturing | 118339 + 65790 = 184129 vs total 184129 | +0 |
| 2003 | NAICS2002 | nonfederal + federal | 183305 + 20699 = 204004 vs total 204004 | +0 |
| 2003 | NAICS2002 | manufacturing + nonmanufacturing | 123384 + 80620 = 204004 vs total 204004 | +0 |
| 2003 | NAICS2002 | basic + applied + development | 204004 vs total 204004 | +0 |
| 2003 | NAICS2002 | total: nsf07314 Table 34 vs nsf07314 Table 3 | 204004 vs 204004 | +0 |
| 2003 | NAICS2002 | published headline 204,004 m (SIRD 2003, NSF 07-314 Table 1) | 204004 | +0 |
| 2004 | NAICS2002 | nonfederal + federal | 188035 + 20266 = 208301 vs total 208301 | +0 |
| 2004 | NAICS2002 | manufacturing + nonmanufacturing | 147288 + 61013 = 208301 vs total 208301 | +0 |
| 2004 | NAICS2002 | basic + applied + development | 208301 vs total 208301 | +0 |
| 2004 | NAICS2002_SIRD_pre2004_method | nonfederal + federal | 188035 + 20266 = 208301 vs total 208301 | +0 |
| 2004 | NAICS2002_SIRD_pre2004_method | manufacturing + nonmanufacturing | 109455 + 98846 = 208301 vs total 208301 | +0 |
| 2008 | NAICS2002 | manufacturing + nonmanufacturing | 203755 + 86926 = 290681 vs total 290680 | +1 |
| 2015 | NAICS2012 | company + other | 296677 + 59144 = 355821 vs total 355671 | +150 |
| 2015 | NAICS2012 | manufacturing + nonmanufacturing | 236170 + 119501 = 355671 vs total 355671 | +0 |
| 2015 | NAICS2012 | basic + applied + development | 355822 vs total 355671 | +151 |
| 2015 | NAICS2012 | total: nsf18313 Table 12 vs nsf27300 Table 58 (multi-year, revised) | 355821 vs 355671 | +150 |
| 2018 | NAICS2012 | company + other | 377806 + 63230 = 441036 vs total 443633 | -2597 |
| 2018 | NAICS2012 | manufacturing + nonmanufacturing | 274315 + 169318 = 443633 vs total 443633 | +0 |
| 2018 | NAICS2012 | basic + applied + development | 441036 vs total 443633 | -2597 |
| 2018 | NAICS2012 | total: nsf21312 Table 12 vs nsf27300 Table 58 (multi-year, revised) | 441036 vs 443633 | -2597 |
| 2021 | NAICS2017 | company + other | 527804 + 74695 = 602499 vs total 608429 | -5930 |
| 2021 | NAICS2017 | manufacturing + nonmanufacturing | 333362 + 275067 = 608429 vs total 608429 | +0 |
| 2021 | NAICS2017 | basic + applied + development | 602499 vs total 608429 | -5930 |
| 2021 | NAICS2017 | total: nsf23351 Table 12 vs nsf27300 Table 58 (multi-year, revised) | 602499 vs 608429 | -5930 |
| 2022 | NAICS2017 | company + other | 608058 + 83489 = 691547 vs total 691987 | -440 |
| 2022 | NAICS2017 | manufacturing + nonmanufacturing | 377701 + 314286 = 691987 vs total 691987 | +0 |
| 2022 | NAICS2017 | basic + applied + development | 691546 vs total 691987 | -441 |
| 2022 | NAICS2017 | total: nsf24335 Table 12 vs nsf27300 Table 58 (multi-year, revised) | 691547 vs 691987 | -440 |
| 2023 | NAICS2017 | company + other | 635478 + 86314 = 721792 vs total 723206 | -1414 |
| 2023 | NAICS2017 | manufacturing + nonmanufacturing | 394260 + 328946 = 723206 vs total 723206 | +0 |
| 2023 | NAICS2017 | basic + applied + development | 721793 vs total 723206 | -1413 |
| 2023 | NAICS2017 | total: nsf25354 Table 12 vs nsf27300 Table 58 (multi-year, revised) | 721792 vs 723206 | -1414 |
| 2023 | NAICS2017 | published headline 722 bn (InfoBrief NSF 25-353) | 723206 | +1206 |
| 2024 | NAICS2017 | company + other | 679371 + 85711 = 765082 vs total 765082 | +0 |
| 2024 | NAICS2017 | manufacturing + nonmanufacturing | 405092 + 359990 = 765082 vs total 765082 | +0 |
| 2024 | NAICS2017 | basic + applied + development | 765082 vs total 765082 | +0 |
| 2024 | NAICS2017 | total: nsf27300 Table 12 vs nsf27300 Table 58 (multi-year, revised) | 765082 vs 765082 | +0 |
| 2024 | NAICS2017 | published headline 765 bn (InfoBrief NSF 27-301) | 765082 | +82 |

Notes on the checks: manufacturing + nonmanufacturing equals the total in every year (within rounding). 2015-2023 splits come from first-published single-year tables and the total from the revised 2024 multi-year table, so splits differ from the total by up to 1% (largest: 2021, -5.9bn; 2016, -3.9bn). 2024 splits are exact. SEI 2022's 2010-14 totals differ from the 2024 vintage by up to 1.3% (2011). The 2023 and 2024 totals match the InfoBrief headlines ($722bn, $765bn); the revised 2023 total in the 2024 release is 723,206. SIRD 1999 total: 182,823 as first published (NSF 02-312 Table A-1) vs 184,129 revised (NSF 07-314).
