"""Build scheduled-rates.json for peer states from cached salary-schedule PDFs.

Run from any cwd. Inputs cached at C:/temp/pdfs/{md,va,wa,wi}.pdf
(see fetch step in research-notes.md per state).

Outputs:
- ./MD/scheduled-rates.json  (Standard Salary Schedule grades 14 + 19)
- ./VA/scheduled-rates.json  (Pay Bands SW + NoVA, bands 4 + 5)
- ./WA/scheduled-rates.json  (General Service Schedule ranges 46/52/56 + range for class 953)
- ./WI/scheduled-rates.json  (Compensation Plan pay ranges keyed by class 49201 + 49220)

If extraction is partial, the JSON includes "extraction_status": "partial"
plus the specific gap.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pdfplumber

REPO_ROOT = Path(__file__).resolve().parent
PDF_DIR = Path("C:/temp/pdfs")


def _money(s: str) -> int | None:
    """Parse "$58,191" or "58,191" or "58191" -> 58191."""
    if s is None:
        return None
    s = re.sub(r"[\$,\s]", "", s)
    if not s or not re.fullmatch(r"\d+", s):
        return None
    return int(s)


# ----------------------------------------------------------------- Maryland
def parse_md() -> dict:
    """MD Standard Salary Schedule effective Jul 1 2025.

    Layout: each pay grade row holds 24 STEP columns numbered 5..28.
    Two profile lines per grade: STD/ASTD and a few related profiles.
    Grade 14 = Disability Claims Examiner I (class 5260).
    Grade 19 = Disability Claims Examiner Supervisor (class 5263).
    """
    pdf_path = PDF_DIR / "md.pdf"
    out: dict = {
        "state": "MD",
        "salary_schedule_url": "https://dbm.maryland.gov/employees/Pages/SalaryInformation.aspx",
        "salary_schedule_pdf_url": "https://dbm.maryland.gov/employees/Documents/SalaryStandardScale.pdf",
        "effective_date": "2025-07-01",
        "fiscal_year": "FY2026",
        "bargaining_status": "AFSCME representation; Disability Claims Examiner Supervisor in AFSCME Maryland Supervisors Union (Unit S)",
        "step_basis": "annual",
        "steps_offered": list(range(5, 29)),  # steps 5..28
        "grades": {},
        "source_pdf": "md.pdf",
        "extraction_status": "complete",
    }
    with pdfplumber.open(str(pdf_path)) as p:
        text = "\n".join(pg.extract_text() or "" for pg in p.pages)

    # Sample target rows (extracted from text; the table rows look like:
    #   "0014  STD/ASTD  $58,428 $... $90,709"  with the grade number followed
    #   by 24 step values. We search for a row starting with the four-digit
    #   grade code zero-padded.

    def _row_for_grade(grade: int) -> list[int] | None:
        # Some rows print the grade as "0014" or just "14"; allow either.
        # The numeric values are dollar-formatted with $ + comma.
        pattern = re.compile(
            rf"\b0?0?{grade:02d}\b[^\n\r]*?(?:STD/ASTD|STD\b)?(?P<steps>(?:\s*\$\d{{1,3}}(?:,\d{{3}})*)+)",
            re.MULTILINE,
        )
        # Easier: scan line-by-line for STD/ASTD rows that contain 24 dollar amounts.
        lines = text.splitlines()
        results = []
        for i, line in enumerate(lines):
            amounts = re.findall(r"\$\d{1,3}(?:,\d{3})+", line)
            if len(amounts) == 24:
                # the grade number appears 1-4 lines above in the surrounding
                # context. Look back up to 6 lines for a "0014" or "14" alone.
                window = "\n".join(lines[max(0, i - 6) : i + 1])
                if (
                    re.search(rf"\b0{grade:03d}\b", window)
                    or re.search(rf"\b{grade}\s*$", window, flags=re.MULTILINE)
                    or re.search(rf"\b00{grade:02d}\b", window)
                ):
                    results.append([_money(a) for a in amounts])
        # de-dupe identical rows (the schedule lists STD/ASTD then ASTD-only etc.)
        unique = []
        for r in results:
            if r not in unique:
                unique.append(r)
        return unique[0] if unique else None

    for grade in (14, 19):
        steps = _row_for_grade(grade)
        if steps is None:
            out["grades"][str(grade)] = {"extraction_status": "missing"}
            out["extraction_status"] = "partial"
            continue
        out["grades"][str(grade)] = {
            "step_basis": "annual",
            "min": steps[0],
            "max": steps[-1],
            "steps": dict(zip(map(str, range(5, 29)), steps)),
        }

    out["grades"]["14"]["maps_to_class"] = {
        "5260": "Disability Claims Examiner I",
    }
    out["grades"]["19"]["maps_to_class"] = {
        "5263": "Disability Claims Examiner Supervisor",
    }
    return out


# ----------------------------------------------------------------- Virginia
def parse_va() -> dict:
    pdf_path = PDF_DIR / "va.pdf"
    out: dict = {
        "state": "VA",
        "salary_schedule_url": "https://www.dhrm.virginia.gov/docs/default-source/compensationdocuments/fy26salarystructure.pdf",
        "effective_date": "2025-06-10",
        "fiscal_year": "FY2026",
        "bargaining_status": "no collective bargaining for state employees",
        "step_basis": "min/max only — VA uses pay-band ranges, not stepped grids",
        "pay_bands": {"SW": {}, "NoVA": {}},
        "source_pdf": "va.pdf",
        "extraction_status": "complete",
    }
    with pdfplumber.open(str(pdf_path)) as p:
        text = "\n".join(pg.extract_text() or "" for pg in p.pages)

    # Statewide table appears first under "Virginia Statewide Pay Area (SW)".
    # Then "Northern Virginia Pay Area (FP)".
    sw_match = re.search(
        r"Virginia Statewide Pay Area.*?Band\s+Minimum\s+Maximum\s+(.*?)Northern Virginia",
        text,
        re.DOTALL,
    )
    nv_match = re.search(
        r"Northern Virginia Pay Area.*?Band\s+Minimum\s+Maximum\s+(.*?)(?:\Z|\n[A-Z][a-z]+\s)",
        text,
        re.DOTALL,
    )

    def _bands_from_block(block: str) -> dict[str, dict[str, int | str]]:
        result: dict[str, dict[str, int | str]] = {}
        for line in block.strip().splitlines():
            m = re.match(r"\s*(\d)\s+(\$[\d,]+)\s+(\$[\d,]+|Market)\s*$", line)
            if m:
                band, mn, mx = m.groups()
                result[band] = {
                    "min": _money(mn),
                    "max": _money(mx) if mx != "Market" else "Market",
                }
        return result

    if sw_match:
        out["pay_bands"]["SW"] = _bands_from_block(sw_match.group(1))
    if nv_match:
        out["pay_bands"]["NoVA"] = _bands_from_block(nv_match.group(1))

    out["role_band_assignments"] = {
        "DDS Analyst — Trainee 1 (#ARSD0134)": "Band 4 (NV 4 in NoVA)",
        "DDS Analyst — Journey (#ARSD0315)": "Band 4 (NV 4 in NoVA)",
        "DDS Analyst — Junior (#ARSD0436)": "Band 4 (NV 4 in NoVA)",
        "DDS Supervisor — Line Unit (#ARSD0252)": "Band 5 (NV 5 in NoVA)",
    }
    out["dds_internal_starting_salaries_fy26"] = {
        "DDS Analyst — Trainee 1": 54106,
        "DDS Analyst — Journey": 64190,
        "DDS Analyst — Junior": 69479,
        "DDS Supervisor — Line Unit": 105212,
    }
    if not (out["pay_bands"]["SW"] and out["pay_bands"]["NoVA"]):
        out["extraction_status"] = "partial"
    return out


# --------------------------------------------------------------- Washington
def parse_wa() -> dict:
    pdf_path = PDF_DIR / "wa.pdf"
    out: dict = {
        "state": "WA",
        "salary_schedule_url": (
            "https://ofm.wa.gov/wp-content/uploads/sites/default/files/public/shr/"
            "CompensationAndJobClasses/Salary%20Schedules/2025SalarSchedules/"
            "2025SalarySchedules/GS_2025Jul1_Represented.pdf"
        ),
        "effective_date": "2025-07-01",
        "fiscal_year": "Biennium 2025-27",
        "bargaining_status": "WFSE General Government CBA 2025-27 (3% 2025, 2% 2026)",
        "step_basis": "monthly (annual = monthly * 12)",
        "steps_offered": list("ABCDEFGHIJKLM"),  # M is 'M*' premium step
        "ranges": {},
        "source_pdf": "wa.pdf",
        "extraction_status": "complete",
    }
    with pdfplumber.open(str(pdf_path)) as p:
        text = "\n".join(pg.extract_text() or "" for pg in p.pages)

    # Each range block looks like:
    #   46 Annual 50556 51480 ...
    #     Monthly 4213 4290 ...
    #     Hourly 24.21 24.66 ...
    # Capture the Annual line per range (range numbers we care about: 46/52/56/62/etc.)
    targets = {46, 52, 56, 62, 66, 70}  # cover supervisor candidates too

    range_blocks = re.split(r"\n(?=\d{1,3}\s+Annual\s)", text)
    for block in range_blocks:
        first_line = block.strip().splitlines()[0] if block.strip() else ""
        m = re.match(r"^(\d{1,3})\s+Annual\s+(.+)$", first_line)
        if not m:
            continue
        range_num = int(m.group(1))
        if range_num not in targets:
            continue
        annual_vals = [_money(x) for x in re.findall(r"\d{4,6}", m.group(2))]
        # Monthly line is the next line
        lines = block.strip().splitlines()
        monthly_vals: list[int | None] = []
        hourly_vals: list[float] = []
        for ln in lines[1:5]:
            if ln.strip().startswith("Monthly"):
                monthly_vals = [_money(x) for x in re.findall(r"\d{3,5}", ln)]
            elif ln.strip().startswith("Hourly"):
                hourly_vals = [float(x) for x in re.findall(r"\d{1,3}\.\d{2}", ln)]
        steps = list("ABCDEFGHIJKLM")[: len(annual_vals)]
        out["ranges"][str(range_num)] = {
            "annual": dict(zip(steps, annual_vals)),
            "monthly": dict(zip(steps, monthly_vals)) if monthly_vals else None,
            "hourly": dict(zip(steps, hourly_vals)) if hourly_vals else None,
            "min_annual": annual_vals[0] if annual_vals else None,
            "max_annual": annual_vals[-1] if annual_vals else None,
        }

    out["class_code_to_range"] = {
        "956 (DDS Adjudicator 1 — in-training)": "46",
        "955 (DDS Adjudicator 2 — journey)": "52",
        "954 (DDS Adjudicator 3 — senior)": "56",
        "953 (DDS Adjudicator 5 — supervisor/expert)": "tbd — see notes",
    }
    out["notes"] = (
        "Class code 953 (DDS Adjudicator 5) is the supervisory/expert level. "
        "Specific salary range was not directly mapped in this extraction; "
        "OFM publishes the mapping at "
        "https://ofm.wa.gov/state-human-resources/compensation-job-classes/"
        "ClassifiedJobListing — manual lookup needed to confirm."
    )
    if not out["ranges"]:
        out["extraction_status"] = "partial"
    return out


# ---------------------------------------------------------------- Wisconsin
def parse_wi() -> dict:
    pdf_path = PDF_DIR / "wi.pdf"
    out: dict = {
        "state": "WI",
        "salary_schedule_url": (
            "https://dpm.wi.gov/Documents/BCER/Compensation/2025-27%20Comp%20Plan.pdf"
        ),
        "effective_date": "2025-08-10",
        "fiscal_year": "Biennium 2025-27",
        "bargaining_status": "non-represented post-Wisconsin Act 10 (2011); compensation set by Legislature, not bargained",
        "step_basis": "discretionary; pay range min/max with $1.00 service-anniversary differentials at 5/7/10 yrs",
        "class_codes": {
            "49201": {"title": "Disability Determination Specialist"},
            "49220": {"title": "Disability Determination Supervisor"},
        },
        "source_pdf": "wi.pdf",
        "extraction_status": "partial",
    }
    # 229-page comp plan -- targeted text search for "49201" and "49220" tokens.
    found_assignment = {}
    with pdfplumber.open(str(pdf_path)) as p:
        for pg_num, pg in enumerate(p.pages, start=1):
            txt = pg.extract_text() or ""
            for code in ("49201", "49220"):
                if code in txt and code not in found_assignment:
                    # capture the context line(s) that mention the code
                    for line in txt.splitlines():
                        if code in line:
                            found_assignment[code] = {
                                "page": pg_num,
                                "context_line": line.strip(),
                            }
                            break

    # Try to map the found context to a pay range token (e.g. "07-02").
    range_pattern = re.compile(r"\b\d{2}-\d{2}\b")
    for code, info in found_assignment.items():
        ranges_in_line = range_pattern.findall(info["context_line"])
        out["class_codes"][code].update(info)
        if ranges_in_line:
            out["class_codes"][code]["pay_range_code"] = ranges_in_line[0]
            out["extraction_status"] = "partial-with-pay-range"

    out["notes"] = (
        "229-page Compensation Plan PDF parsed; class codes 49201 and 49220 "
        "located by string search. Mapping the codes to a specific pay range "
        "and dollar amounts requires cross-referencing the 'Compensation Plan "
        "Schedule' tables which are spread across multiple grids (NOREP, "
        "Schedule 07, etc.). Manual cross-walk recommended for bargaining-grade "
        "evidence; market-rate estimate from ZipRecruiter (Apr 2026): mean "
        "~$60,202; range $48,400-$65,600."
    )
    return out


# ------------------------------------------------------------------ runner
PARSERS = {"MD": parse_md, "VA": parse_va, "WA": parse_wa, "WI": parse_wi}


def main(states: list[str] | None = None) -> int:
    states = states or list(PARSERS)
    summary: list[str] = []
    for st in states:
        if st not in PARSERS:
            summary.append(f"{st}: skipped (no parser)")
            continue
        try:
            data = PARSERS[st]()
        except Exception as exc:  # pragma: no cover - extraction is best-effort
            summary.append(f"{st}: ERROR {type(exc).__name__}: {exc}")
            continue
        out_path = REPO_ROOT / st / "scheduled-rates.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        status = data.get("extraction_status", "unknown")
        summary.append(f"{st}: {out_path.relative_to(REPO_ROOT)} ({status})")
    print("\n".join(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or None))
