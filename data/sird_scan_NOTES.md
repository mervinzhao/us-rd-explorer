# SIRD by industry, SIC basis, transcribed from scanned NSF volumes (archive.org)

Built 2026-11-19. These are values transcribed by hand from page images of NSF *Research and Development in Industry* (Survey of Industrial Research and Development, SIRD) report volumes on archive.org. The OCR text layers were not used for numbers, with one exception: the 1999 volume is a clean typeset PDF, and its trend tables were read from the text layer and then checked visually.

Files:

- `data/sird_scan_by_industry.csv`: long format, 8,563 rows (6,456 preferred).
- `raw/sird_scan/tx/*.txt`: one pipe-delimited wide transcription per table, exactly as read, with page, title and footnotes in the header. These are the source of truth, and the CSV is rebuilt from them.
- Scripts: `scripts/sird_scan_build.py` (tx to CSV), `scripts/sird_scan_check.py` (sum checks within a table), `scripts/sird_scan_xcheck.py` (checks that total = federal + company), `scripts/sird_scan_render.py` and `scripts/sird_scan_contact.py` (render and tile pages), `scripts/sird_scan_parse_trend.py` (text-layer parser used only for the 1999 trend tables).
- Raw downloads: `raw/sird_scan/*.pdf` (archive.org PDFs), `*.txt` (archive.org djvu OCR, used only to find tables), `img/` (page tiles that were read).

## Columns

| column | meaning |
|---|---|
| year | year of R&D performance |
| sic_code_native, industry_label_native | as printed in that table. SIC vintages differ between volumes (see breaks) |
| measure | `total`, `company_nonfederal` (company and other non-Federal funds), `federal`, `basic`, `applied`, `development`, and funder × character splits such as `basic_federal` or `development_company_nonfederal` |
| value_usd_millions_nominal | millions of current dollars. Blank when the cell is not a number |
| flag | `D` withheld (disclosure); `S` imputation >50% (the value is kept when one is printed; in 1985-86 table B-29, S means withheld for imputation and no value is printed); `NA_included_in_total` (printed "not separately available but included in total" or NA); `E_estimated_by_NSF`; `lt_0.5` (less than $0.5 million); `none` (printed dash or nil); `included_in_other_electrical`, `included_in_other_manufacturing`, `included_in_nonmanufacturing` (the cell's value sits in another line, per footnote); `U_uncertain_reading` (blurred digits, see below); `X_from_other_table`; `illegible`; `printed_dots` |
| source_item | archive.org identifier |
| page | PDF page(s) (1-based), with the printed page number in brackets |
| table_title | as printed |
| industry_key | my harmonized short key for the line, used to match the same line across volumes. It is not a concordance across SIC vintages |
| preferred | 1 = the row to use. 0 = the same year, line and measure from an older volume (kept to show revisions), or a combined line that a later volume prints split into components. Exception: when the latest volume's cell is illegible, the older volume's reading is preferred |

Use `preferred == 1`. For all-industry rows (`industry_key == total`), the preferred values for every year 1953-99 come from the 1999 volume's trend tables. These revise some earlier totals: for 1969-77 they differ from the all-industry totals of the 1977 volume, so industry detail for 1969-77 sums to the 1977-volume total (kept as a non-preferred row), not to the preferred total. The gaps run from -4 to -59 for 1969-76 and +84 for 1977. Before and after that span, preferred industry rows add to the preferred total within 3.

## Volumes and tables used

| archive.org id | Volume | Tables used | Years taken (preferred) |
|---|---|---|---|
| `ERIC_ED064074` | R&D in Industry, 1969 (NSF 71-18) | B-2 total, B-6 federal, B-8 company, by industry 1956/57-69 (pp. 40, 44, 46) | 1959-62 |
| `ERIC_ED106097` | R&D in Industry, 1972 | B-3 total, B-7 federal, B-10 company: 1956-58 and 1963-72 (pp. 60-62, 67-68, 71-72) | 1957-58, 1964-65 (total also 1957) |
| `ERIC_ED186278` | R&D in Industry, 1977 (NSF 79-313) | B-3 total (1956, 1963, 1966-77), B-6 federal and B-9 company (1957, 1963, 1966-77) (pp. 31-33) | 1956 (total), 1957 (fed/company), 1963, 1966-77 |
| `ns-reports_ns-122in-2-988` | R&D in Industry, 1988 (NSF 90-319) | B-3 total, B-7 company, B-11 federal by industry: 1978-88 (pp. 24-25, 32-33, 38-39) | 1978-84 |
| `ns-reports_ns-122in-2-985-86` | R&D in Industry, 1985-86 (NSF 89-316) | B-29 basic research by industry: 1957-58, 1963, 1967, 1972, 1974-77, 1979, 1981, 1983-85 (p. 52) | basic, those years |
| `ns-reports_ns-122in-2-995-96` | R&D in Industry, 1995-96 | A-3 total, A-7 company, A-13 federal: 1985-95 (pp. 25-27, 37-39, 50-52); A-3a, A-7a, A-12a 1996 column (pp. 182-184, 194-196, 207-209); A-29 (1993), A-22a (1994), A-23a (1995), A-24a (1996) basic/applied/development by industry and source (pp. 90-92, 233-242) | 1985-96 total/company/federal; 1993-96 character of work |
| `ERIC_ED463163` | R&D in Industry, 1999 (NSF 02-312) | A-1 total/federal/company 1953-99 (pp. 19-20); A-25, A-26, A-27 basic/applied/development by source 1953-99 (pp. 84-89). All-industry only | all-industry 1953-99 |

The 1999 volume (`ERIC_ED463163`) and later ones classify industries by NAICS, with 1997-98 backcast to NAICS, so they give no SIC industry detail. Only their all-industry totals are used. NSF states these totals are identical to the SIC-based ones.

Inspected but not used: `researchdevelopm1987nati` (1987 volume, benchmark years only, superseded by the 1988 and 1995-96 volumes). Found on archive.org but not opened: the 1979-84 and 1989-94 volumes (`ERIC_ED223411`, `ns-reports_ns-122in-2-980` to `-984`, `-989`, `ns-reports_ns-122-in-2-990`, `-991`, `DTIC_ADA299913` (1992), `ns-reports_ns-118993`, `ERIC_ED416096` (1994)). They are the route to character of work by industry for 1986-92 (see gaps).

## Coverage (preferred rows, industry detail)

| measure | years |
|---|---|
| total | 1956-96 (1956 all-industry plus a few lines; full detail from 1957) |
| company_nonfederal | 1957-96 |
| federal | 1957-96 |
| basic | 1957, 1958, 1963, 1967, 1972, 1974-77, 1979, 1981, 1983-85, 1993-96 |
| applied, development | 1993-96 |
| basic/applied/development × federal/company | 1993-96 |
| all-industry total, federal, company, basic, applied, development (each also by source) | 1953-99 |

Many cells are suppressed. Preferred rows: 1,391 `D`, 350 "not separately available", 55 `S`. Suppression is heavy in 1978-96 for the federal measure, for the textile, lumber, paper and rubber lines, for chemical subindustries, and for the radio/TV and other-electrical lines.

## Definitional breaks shown in the volumes

- 1953-56: BLS surveys. From 1957: Census surveys, which also include industry-administered FFRDCs. 1956 was adjusted by Census for comparability (1969 volume, Scope of Study).
- Industry lines change between volumes, and each volume restates earlier years on its own basis:
  - 1969 and 1972 volumes: "Electrical equipment and communication" (SIC 36, 48) with a combined "Communication equipment and electronic components" line (366-67, 48), and a combined "Motor vehicles and other transportation equipment" line. Aircraft and missiles is 372, 19. SIC 3391 and 3399 were put in nonferrous metals for 1956-65.
  - 1977 volume: from 1972, electronic components (367) are split from communication equipment and communication (366, 48), motor vehicles (371) from other transportation (373-75, 379), and office/computing machines (357) are tabulated. Aircraft and missiles is 372, 376, and nonmanufacturing adds 737. The 1972 SIC revision shows in these codes, and 1966-72 values differ from the 1972 volume.
  - 1988 volume (1978-88) and 1995-96 volume (1985-96): electrical equipment is SIC 36 only, so communication services (48) are in nonmanufacturing. Transportation equipment (37) is a group, industrial chemicals are 281-82, 286, other machinery is 351-56, 358-59, optical etc. instruments are 383-87 (1988) or 384-87 (1995), and tobacco (21) is with food from 1984 (before 1984 it was in other manufacturing). The nonmanufacturing SIC list includes 87 (1987 SIC).
- 1988-91 were revised in the 1995-96 volume after a new sample design. 1991 and later are not directly comparable with 1990 and earlier: the redesign captured much more nonmanufacturing and small-firm R&D (nonmanufacturing rises from $6.7B in 1985 to $28.4B in 1991). NSF also stopped routinely revising prior years with the 1995 cycle.
- Nonmanufacturing detail (transportation and utilities, trade, FIRE, services and so on) was first published for 1995.
- 1996: manufacturing firms with fewer than 50 employees and nonmanufacturing firms with fewer than 15 were sampled separately and put into "Other manufacturing" and "Other nonmanufacturing", so those two lines are not comparable with earlier years.
- Character of work: estimation was revised for 1986 and later years, so it is not comparable with 1985 and earlier. Some years' all-industry splits (1953-55, 1978, 1980, 1982) are NSF estimates.
- Basic research by industry in B-29: before 1972 the communication-equipment line covers 366-67 and the motor-vehicle line covers all non-aircraft transportation. No 1986 data were available.

## Sum checks

Two checks were run on each table: child lines against their group lines and against the all-industry total, using every cell that could be checked, with a tolerance of 2 (larger for groups with many children); and total against federal + company within the same volume. Rows that failed were re-read on zoomed crops. Results after re-reading:

- 1995-96 volume A-3/A-7/A-13 (1985-95) and A-3a/A-7a/A-12a (1996): no failures. total = federal + company holds in all 233 checkable cells.
- 1988 volume B-3/B-7/B-11: no failures. total = federal + company holds in all 193 cells. Company lines sum to the total within 2 for 1981-88.
- 1977 volume: industry lines sum to the total within 3 except 1969, where the sum is 14 short. The 1969 other-manufacturing cell (104) is flagged U. In 1977 electrical equipment, children sum 10 over the parent, and the parent is flagged U. total − federal − company differs by 9-19 for chemicals in 1971, 1973 and 1974, by 8 for communication/components in 1971, and by 4-9 for aircraft in 1969 and 1973. These were re-read and kept as printed.
- 1972 volume: lines sum to totals within 3. Rubber 1964 is off by 11 between total and federal + company, kept as printed.
- 1969 volume: lines sum to totals within 2. Kept as printed after zoomed re-reads: federal chemicals 1959 (parent 147 vs subindustries 137), company primary metals 1964 (196 vs 186), and ±10 total-vs-sources differences in 1959 industrial chemicals, 1960 electrical, 1964 primary metals and 1967 machinery. The 1958 textiles, other manufacturing and nonmanufacturing differences are explained by footnote g: 1957-58 federal "other manufacturing" includes textiles, lumber and nonmanufacturing.
- Character of work 1993-96: subindustry checks pass except for small printed inconsistencies. 1993: electrical company applied 2,904 vs children 2,901, and company development 8,422 while total − federal = 8,416, so manufacturing company development children are over by 7. 1996: off by 3-4 in transportation and utilities, services and engineering and management services development cells (e.g., other engineering and management services prints total 101, federal 1, company 101). In each table, basic + applied + development of each line matches the A-7 company totals within 2, except electrical equipment in 1993 (+8, printed). The 1999 trend tables add within 4 in every year.
- B-29 basic 1957-85 (dot-matrix print, blurred scan): the industry sum cannot be checked in most years because cells are withheld. Where lines were resolvable they add up, and fixes from subtotal arithmetic are flagged U. Chemicals = industrial + drugs + other holds (e.g., 1974: 157+107+24 = 288). Machinery rows only appear to fail because office machinery was not tabulated before 1972-75.

20 preferred cells are flagged `U_uncertain_reading`: mostly B-29 (1957-85 basic), where 8, 0, 6 and 3 are hard to tell apart (e.g., aircraft 1979-85, machinery 1981 and 1983, transportation 1984-85), plus three 1977-volume cells and one 1995 cell (electrical equipment applied total, printed "$3,882 D)").

## Not read, or left as gaps

- SIC industry detail for 1997-98: archive.org has no 1997 or 1998 SIRD volume (searched by title and in the ns-reports and ERIC collections). The 1999 volume restates 1997-98 on NAICS only.
- 1953-55 industry detail (BLS surveys) and annual detail before 1956. The 1969 volume's industry table starts in 1956.
- Basic research by industry for 1959-62, 1964-66, 1968-71, 1973, 1978, 1980, 1982 and 1986-92; applied research and development by industry before 1993. The annual volumes listed above as not opened would fill 1979-92 for one year each.
- Not transcribed: size-of-company breakdowns, energy and pollution-abatement R&D, R&D scientists and engineers, net sales and product-field tables.
- Illegible cells, left blank and flagged `illegible`: in the 1972 volume B-10, company ferrous 1958, machinery 1965 and 1968, electrical 1969, aircraft 1958 and 1971, and instruments 1971; in the 1977 volume B-6, petroleum federal 1976; in the 1977 volume B-9, communication/components company 1966. Where an illegible cell sits in the most recent volume for that year, the next older volume's reading is marked preferred instead (1958 ferrous and aircraft, and 1965 machinery company, come from the 1969 volume; 1966 communication/components company comes from the 1972 volume). Petroleum federal 1976 has no other source.
- The federal transportation-and-utilities cell for 1996 is damaged in A-12a. Its value (186) is taken from A-24a in the same volume and flagged X.
- In A-7 (1995 set), the R&D testing (873) line prints stray "876/877/878" in its 1985-94 cells. They were treated as not available. A-23a prints its 1995 company total as 2,829, but this value was not used (A-7a gives 2,829 in the 1996 set, consistent).
