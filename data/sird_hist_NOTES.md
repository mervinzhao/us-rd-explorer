# Industrial R&D by industry, 1953-2007 (NSF SIRD via IRIS)

Built 2026-11-19. File: `data/sird_hist_by_industry.csv` (23,958 rows; 16,731 with `is_primary = 1`, of which 10,406 carry a number and the rest are published suppression or "included elsewhere" cells).

## Columns

| column | meaning |
|---|---|
| year | survey year (calendar year of R&D performance) |
| sic_code_native | industry code exactly as printed in the table (SIC through 1998, NAICS for 2002-2007 rows); dashes normalized to `-`; blank where the table prints none (pre-1967 BAD tables, aggregates) |
| industry_label_native | label as printed, leader dots and footnote markers removed; multi-line labels joined |
| measure | `total`, `company_nonfederal` (NSF "company and other (except Federal)"; older tables say "Company"), `federal`, `basic`, `applied`, `development`, and source x character cells `federal_basic`, `company_nonfederal_applied`, etc. |
| value_usd_millions_nominal | millions of current dollars, as published (some IRIS cells carry unrounded decimals, e.g. 5529.84). Blank when the cell is suppressed or not separately available |
| flag | as published: `D` withheld (disclosure); `S` more than 50% imputed (blank value before 1993, value shown from 1993); `T` not separately available but included in total (IRIS key; also the 1960s-80s footnote "Not separately available but included in total"); `T:in <group>` included in a named group; `lt0.5` less than $0.5 million; `e` estimated by NSF; `i` more than 50% imputed (NAICS tables); `-` zero or rounds to zero (2002 table key); `.` as printed in some 1960s-70s tables (no key; probably zero); `**`, `fnz` unexplained marks kept as printed; plus three editorial flags explained under "Source quirks" |
| source | `IRIS_h-25`, `IRIS_h-3`, `IRIS_h-9` (longitudinal tables) or `IRIS_<publication>_<table>` (single-year tables, e.g. `IRIS_99-358_a-31` = NSF 99-358 table A-31) |
| source_url | original IRIS Excel URL inside the Archive-It snapshot of 3 Oct 2018 |
| classification | `SIC` or `NAICS` |
| is_primary | 1 = the row to use. 0 = same year/industry/measure from another table or vintage (kept for comparison) |

Rule for `is_primary`: total, company_nonfederal and federal for 1953-1998 come from the longitudinal tables h-25, h-3 and h-9 (latest revised values); for 2004-2007 from the funds tables (latest volume wins: 2005 from the 2006 volume, 2006 and 2007 from the 2007 volume). Character-of-work measures come from the single-year BAD tables, the latest publication winning when a year appears in two volumes (e.g. 1992 in NSF 95-324, 96-304 and 97-331: 97-331 wins). The totals printed inside BAD tables are kept with `is_primary = 0`.

## Coverage (primary rows, years with at least one value)

| measure | SIC years | NAICS years |
|---|---|---|
| total, company_nonfederal, federal | 1953, 1956-1998 (no survey 1954-55) | 2002 (from the 2002 BAD table), 2004-2007 |
| basic | 1953, 1956-1977, 1979, 1981, 1983-1985, 1988-1998 | 2002, 2005-2007 |
| applied, development | 1956-1977, 1979, 1981, 1983-1985, 1988-1998 | 2005-2007 |
| federal_* and company_nonfederal_* by character | 1963-1977, 1979, 1981, 1983-1985, 1988-1998 | basic 2002; all three 2005-2007 |

Industry detail: SIC tables give the standard SIRD breakdown (food 20-21; textiles 22-23; lumber 24-25; paper 26; chemicals 28 with industrial chemicals 281-82,286, drugs 283, other chemicals; petroleum 13,29; rubber 30; stone/clay/glass 32; primary metals 33 with ferrous/nonferrous; fabricated metals 34; machinery 35 with office/computing 357 and other; electrical 36 with radio-TV 365, communication equipment 366, electronic components 367, other; transportation 37 with motor vehicles 371, other transportation, aircraft and missiles 372,376; instruments 38 with measuring 381-82 and optical/surgical/photographic 384-87; other manufacturing; nonmanufacturing). Nonmanufacturing detail (communications 48 and telephone 481, utilities 49, trade, FIRE, business services 73 with computer and data processing 737, health 80, engineering and management services 87 with 871 and 873) exists only for 1995-1998. In h-25, office/computing 357 has values 1972-1980, 1993-1994 and 1997-1998 (D or T in between); electronic components 367 has values from 1972 (D in 1986, 1991 and 1995-1998). The 1969-1971 BAD tables cover "selected industries" only (15-18 rows). NAICS 2005-2007 tables have about 60 rows (3-4 digit NAICS, information and professional services detail).

Suppression is heavy: in primary SIC rows about a third of the cells are D or T, more after 1980 (for example drugs 283 total is T or D in 1981-1985, 1987 and 1989-1991; motor vehicles 371 is D every year from 1986 except 1993; communication equipment 366 is D from 1992). Company and other funds are suppressed less often than totals because federal funds drive the disclosure risk; for industries with negligible federal funding (drugs, food, motor vehicles) company_nonfederal is a close proxy for total.

## Sources and how they were obtained

1. NSF IRIS (Industrial Research and Development Information System). nsf.gov now forwards to `ncses.nsf.gov/archived`; the live copy is Archive-It collection 5902, snapshot 2018-10-03. Archive-It answered "Rate limit reached" to every request when this was built (40 tries at 60-second spacing over 40 minutes, with `id_` raw URLs, other timestamps and the CDX endpoint; log in `raw/sird_hist/ait/poll.log`). The UNT End of Term 2008/2012 archives hold only the IRIS menu pages (no `search_hist.cfm` pages, no Excel files).

   The IRIS Excel files were instead taken from a public GitHub mirror of that same Archive-It snapshot: `https://github.com/jivizcaino/nsf-iris-archive` (commit 57e2cbb, 29 Oct 2026), which holds about 2,600 IRIS files downloaded from `wayback.archive-it.org/5902/20181003221605/...` with a crawl log giving each file's original URL. Cloned to `raw/sird_hist/gh_iris/`. `source_url` in the CSV is the original Archive-It URL of each file, not the mirror.

   Verification of the mirror against independent NSF copies:
   - NSF 96-304, Research and Development in Industry: 1993 (born-digital PDF, UNT EOT 2008: `https://webarchive.library.unt.edu/eot2008/20081107075122/http://www.nsf.gov/statistics/nsf96304/part1.pdf`), tables A-3, A-7 and A-12, 1983-1993 by industry: every 1983-1992 cell agrees with h-25/h-3/h-9 (341 cells per measure compared; total 325 agree, company 314, federal 328). All disagreements are 1993, which the IRIS longitudinal tables carry in the revised form printed one year later in the 1994 volume (checked against ERIC ED416096, R&D in Industry: 1994, table A-3: food 1,345, drugs 9,146, all industries 117,400), plus two 1992 federal flags (S vs D). Script: `scripts/sird_hist_check_pdf9604.py`.
   - Science and Engineering Indicators 2008, appendix tables 4-19, 4-20, 4-21 (UNT EOT 2008 copy of `nsf.gov/statistics/seind08/append/c4/at04-19.xls` etc.): 2005 total, company and federal agree for all 11 rows matched by NAICS code. Script: `scripts/sird_hist_check_sei08.py`.

   Tables used:
   - h-25 "Total (company, Federal, and other) funds for industrial R&D performance, by industry and by size of company: 1953-98" (`excel-files/historical_tables/h-25.xls`)
   - h-3 "Company and other (except Federal) funds ... 1953-98"
   - h-9 "Federal funds ... 1953-98"
   - Basic/applied/development by industry, one table per survey volume (IRIS menu item "B,A,D by Industry and Source"): NSF 56-16 A-12 (1953, basic only), 59-50 A-6 (1956), 60-049 A-6, 61-32 A-14, 62-3 A-14, 63-7 A-14, 64-9 A-16, 65-018 A-60 (1957-62, total by character only), 66-15 A-65/A-67, 66-28 63/65, 67-012 67/69, 68-020 68/70, 69-028 45/46, 70-029 44/45, 71-018 B-29/B-30, 72-309 B-47/B-48, 73-305 B-46/B-47, 74-312 B-43/B-44, 75-315 B-41/B-42, 76-322 B-45/B-46, 77-324 B-45/B-46, 78-314 B-44/B-45, 79-313 B-44/B-45, 81-324 B-29/B-30, 83-325 B-28/B-29, 85-325 B-28/B-29, 1984 B-25/B-26, 89-316 B-27/B-28 (1985), 95-324 A-23 to A-27 (1988-92), 96-304 A-26 to A-28 (1991-93), 97-331 A-23 to A-25 (1992-94), 99-312 A-22a to A-24a (1994-96), 99-358 A-31 (1997), 01-305 A-29 (1998); NAICS: 06-322 table 34 (2002), 10-319 table 28 (2005), 2006 table 24, 2007 table 58.
   - NAICS funds by industry: 10-319 table 1 (2004-05), 2006 table 1 (2005-06), 2007 table 30 (2006-07).

2. Science and Engineering Indicators. UNT EOT 2008 holds the SEI 2004, 2006 and 2008 chapter 4 appendix Excel files (downloaded to `raw/sird_hist/seind04|06|08/`); their industry tables are NAICS 1999-2005 only, so they were used only as a check. SEI 1987, 1989, 1991, 1993 and 1998 are on ERIC only as scanned PDFs (CVISION OCR; downloaded to `raw/sird_hist/eric/`) and were not needed once IRIS was available. SEI 2010 (ERIC ED514060) lists appendix tables 4-11 to 4-13 (industry R&D 2003-07) but they were online-only Excel and are not in the PDF; not needed either.

3. Research and Development in Industry volumes: of the 1990s volumes only NSF 96-304 (1993) has its PDFs in the UNT archive; the others (99-312, 99-358, 01-305, 02-312, 03-318, 05-305) have only their start pages archived. NSF 10-319 (2005) and 11-301 (2006-07) are not archived anywhere reachable; their tables come from IRIS (publications `nsf_10-319`, `nsf_2006`, `nsf_2007`). The scanned volumes on archive.org were left to the other agent as instructed.

Not reachable: web.archive.org (blocked), webarchive.loc.gov (Cloudflare challenge), archive.today (connection reset).

## Sum checks (primary rows; full output in `data/work/sird_hist_checks.txt`)

- Industries add to the all-industries total. Using the 15 top-level groups (food ... other manufacturing, plus nonmanufacturing, with transportation equipment or its three parts): total (h-25) adds exactly (difference at most $1 million) in every year where no group is suppressed, 1972-1980; company and other funds (h-3) add exactly in 1981-1988, 1990 and 1992-1998. Federal funds never have all groups published.
- total = company_nonfederal + federal for the same industry and year: 892 industry-years checked, 878 agree within 1%. The exceptions are 1953 other manufacturing, nine industries in 1956 (1956 company + federal = 6,231 vs total 6,605), 1959 industrial chemicals, 1964 primary metals, 1966 petroleum (small), and 1986 manufacturing (see quirks).
- Inside each BAD table, basic + applied + development = total (or the federal or company subtotal): 1,864 checks, 9 mismatches; federal + company = total by character: 1,679 checks, 2 mismatches. The mismatching cells are as published (for example 1992 nonferrous metals company development 1,623 against a company total of 318 in NSF 95-324 table A-27; 1971 stone, clay and glass total 755 against parts summing to 155 in NSF 74-312 table B-43, probably a misprint for 155).
- NAICS 2005-2007: all industries = federal + company and other exactly; manufacturing + nonmanufacturing = all industries exactly; basic + applied + development = all industries within $1 million (2005: 8,667 + 45,284 + 172,207 = 226,158 vs 226,159; 2006: 247,668 vs 247,669; 2007: 269,268 vs 269,267).

## Breaks and definitional changes

1. 1953: a separate pilot-style survey reporting "cost" of R&D; values carry decimals; industry groups differ (h-25 footnote 3: 1953 also had "Telecommunications and broadcasting" 113 and "Construction" 29, added as rows; footnote 4: "Other manufacturing" includes motor vehicles, tobacco, lumber, furniture, printing, leather and transportation equipment other than aircraft). No data for 1954-1955.
2. 1956-1957: totals in the 1956 and 1957 single-year BAD tables (6,231 and 7,155) are well below the h-25 totals (6,605 and 7,731); 1956 company + federal also falls short of total. The 1956-57 h-tables carry several NSF estimates (flag `e`) and footnoted reclassifications (1957-58 textiles and lumber inside nonmanufacturing in the federal table). Treat 1953-1957 as a different basis from 1958 on.
3. Totals in single-year BAD tables are the vintage of that volume. They match h-25 within 1% for 1958-1972 and 1988-1998, but run 1-7% low for 1973-1985 (1983 BAD total 62,816 vs h-25 65,268; 1985 78,268 vs 84,239) because h-25 carries the later revisions, including the 1988-91 sample redesign. To build basic/applied/development levels on the revised basis, apply each BAD table's within-industry shares to the h-25 totals rather than mixing levels.
4. Character of work by source (federal vs company) is published by industry only from 1963. 1957-1962 tables give total basic/applied/development only; 1953 gives basic only. No BAD by industry for 1978, 1980, 1982, 1986, 1987 in IRIS (the 1987 volume, NSF 89-323, has applied R&D by product field only).
5. SIC vintages are visible in the code strings printed in the tables rather than stated: industrial chemicals is "281-82" in tables up to 1975 and "281-82,286" in the longitudinal tables; optical/surgical instruments is "383-87" in 1970s-80s tables and "384-87" later (SIC 1987 moved optical instruments, 383, to 3827); nonferrous metals includes 3391-92 in some 1970s tables (h-table footnote: SIC 3391/3398 in nonferrous 1956-66). Tobacco (21) sits in "Other manufacturing" until 1984 (from 1984 with food, "20,21"). Communication equipment was "Telecommunications and broadcasting" in 1953-56. The BAD tables for 1958-1977 put communication services (SIC 48) with electrical equipment ("Electrical equipment and communication", 36,48); within it they combine "Communication equipment and electronic components" for 1958-1971 and "Communication equipment and communication" (366,48) for 1972-1977. These rows are not comparable with the h-table rows for 36, 366 and 367, which exclude SIC 48.
6. 1988-1991 revised for a new sample design that better covers nonmanufacturing firms and small firms; IRIS notes that "statistics for 1991 and later years are not directly comparable with statistics for 1990 and earlier years". Nonmanufacturing for 1990 and earlier covered only SICs 10-11, 14-17, 40-42, 44-51, 53-54, 56, 60, 62-63, 66, 72-73, 78, 806-07 and 87; nonmanufacturing R&D jumps from 7.8bn (1987) to 28.4bn (1991). Detailed nonmanufacturing industries appear only from 1995.
7. From 1996, manufacturing companies with fewer than 50 employees and nonmanufacturing companies with fewer than 15 employees were sampled without regard to industry and are lumped into "Other manufacturing industries" and "Other nonmanufacturing industries", so those two rows are not comparable before and after 1995.
8. Company classification: each company's whole R&D is assigned to one industry (its main industry, by payroll in SIRD), so conglomerates move between industries. The 2007 tables state that "the method used to assign industry classifications has changed; industry-specific estimates are not directly comparable with those for years prior to 2004" (see `data/berd_NOTES.md`, break 2, for the 2004 size of the effect: pharmaceuticals 15.9bn old method vs 31.5bn new).
9. SIC to NAICS: IRIS SIC series end in 1998; NAICS single-year tables begin in 1999. This file has NAICS rows only for 2002 (BAD table) and 2004-2007; 1999-2004 NAICS totals and funding splits are already in `data/berd_by_industry.csv`. Map with `data/berd_concordance.csv`.
10. FFRDCs: the 2002 and 2007 NAICS tables state they exclude industry-administered FFRDCs; IRIS keeps FFRDCs administered by industry in a separate series (h-10, not extracted).
11. Basic research estimation method: NSF changed the business basic/applied/development method from 1998 (National Patterns technical notes; `berd_NOTES.md` break 9), so 1998 shares are not strictly comparable with 1997 and earlier.

## Source quirks handled (editorial flags)

- h-25, 1953, petroleum: the cell reads 4146, a footnote marker 4 fused to 146. Stored as 146 with flag `footnote marker 4 removed (cell reads 4146; NSF 56-16 table A-12 gives 145.9)`. h-3 (138) + h-9 (8.2) = 146.2 confirms it.
- h-25, 1986, manufacturing total = 87,823, identical to all industries (company 55,192 + federal 25,185 = 80,377). Kept, flagged `suspect: equals all-industries total in source`.
- h-25, 1953 rows "Telecommunications and broadcasting" (113) and "Construction" (29) come from the table's footnote 3, flagged `from table footnote 3`.
- NSF 74-312 tables B-43/B-44 (1971-72) store footnote "(1)" cells as the number -1 in the Excel; read as flag `T` (the table's footnote 1 is "Not separately available but included in total").
- Footnote references in older tables ("(1)", "(a)") were translated using each table's own footnote text (T, D, S or lt0.5).

## Gaps

- No industry detail for 1954-55 (not collected) or for character of work in 1978, 1980, 1982, 1986, 1987.
- 2002 applied and development by industry: the IRIS Excel for NSF 06-322 table 34 lost the column headers of its second page, so only total/federal/company and basic were taken.
- 1999-2001 and 2003-2004 NAICS character-of-work tables exist in IRIS (NSF 02-312, 03-318, 05-305, 07-314 table 34, 09-301 table 28) but were not extracted here; 2003-2004 are already in `data/berd_by_industry.csv`.
- IRIS also has R&D by size of R&D program, net sales, employment, FTE scientists and engineers and type of cost by industry (h-2, h-17, h-19, h-23, h-26, h-27); not extracted.
- Nothing was interpolated. Suppressed cells are blank with their flag.

## Files and scripts

- Raw: `raw/sird_hist/gh_iris/` (mirror clone; Excel files in `raw/pages/`, crawl log `raw/logs/crawl2_log.tsv`), `raw/sird_hist/nsf96304/` (NSF 96-304 PDFs), `raw/sird_hist/seind04|06|08/` (SEI appendix Excel), `raw/sird_hist/eric/` (ERIC scans, unused), `raw/sird_hist/ait/` (Archive-It attempts).
- Scripts (run with `python3 -I`): `scripts/sird_hist_parse_h.py` (h-25, h-3, h-9), `scripts/sird_hist_parse_single.py` (single-year BAD and NAICS funds tables), `scripts/sird_hist_common.py`, `scripts/sird_hist_build.py` (assembly, flags, `is_primary`), `scripts/sird_hist_check.py`, `scripts/sird_hist_check_pdf9604.py`, `scripts/sird_hist_check_sei08.py`, `scripts/sird_hist_ait_poll.sh`.
- Rebuild: `cd rd-fields && P=raw/sird_hist/gh_iris/raw/pages && python3 -I scripts/sird_hist_parse_h.py $P data/work/sird_hist_h.csv && python3 -I scripts/sird_hist_parse_single.py $P data/work/sird_hist_single.csv && python3 -I scripts/sird_hist_build.py data/work/sird_hist_h.csv data/work/sird_hist_single.csv data/sird_hist_by_industry.csv && python3 -I scripts/sird_hist_check.py data/sird_hist_by_industry.csv > data/work/sird_hist_checks.txt`
