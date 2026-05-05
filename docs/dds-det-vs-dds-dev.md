# DDS-Det vs DDS-Dev — Agency Disambiguation

Two unrelated Massachusetts agencies share the abbreviation "DDS." This is one of the most common research errors in this domain. **This repo concerns only the first one.**

## The two agencies

| Term | Full Name | Mission | 2023 Workforce | In 509 scope? |
|---|---|---|---|---|
| **DDS-Det** | Disability Determination Services (a division of MassAbility, formerly MRC) | Adjudicates SSDI/SSI claims for SSA; 100% federally funded | ~200 (division) within ~805 agency total | ✅ **Yes — SEIU Local 509 organizes here** |
| **DDS-Dev** | Department of Developmental Services (an EOHHS agency) | Serves people with intellectual/developmental disabilities (~40,000 MA residents) | 5,515 | ❌ No — separate agency, separate workforce |

## CTHRU department codes (cthru.data.socrata.com)

| `chris` code | `department_division` (CTHRU label) | What it is |
|---|---|---|
| `MRC` | MASS REHABILITATION COMMISSION (MRC) | MassAbility — **contains DDS-Det** |
| `DMR` | DEPARTMENT OF DEVELOPMENTAL SERVICES (DMR) | DDS-Dev — **separate agency** |
| `ADD` | DEVELOPMENTAL DISABILITIES COUNCIL (ADD) | I/DD federal advocacy body |
| `OHA` | MASSACHUSETTS OFFICE ON DISABILITY (OHA) | The MOD — runs RA process |

⚠ **The `DMR` chris code is a legacy artifact**: it's a holdover from the agency's pre-2009 name "Department of Mental Retardation." MA renamed the agency but kept the chris code. Don't be fooled — DMR in payroll data still refers to DDS-Dev.

## Workforce sanity check

A 7× headcount difference is the unmistakable signal that something is mis-scoped:

- DDS-Det division: ~200 staff
- MassAbility full agency (DDS-Det's parent): ~805 staff
- DDS-Dev: ~5,515 staff

If a "DDS staff" pull comes back near 5,500, you're looking at the wrong agency.

## Recommended SoQL pattern for DDS-Det data

```
https://cthru.data.socrata.com/resource/rxhc-k6iz.json?
  $select=year,count(*)
  &$where=chris='MRC' AND upper(position_title) like '%DISAB EXAMINER%'
  &$group=year&$order=year
```

- `chris='MRC'` filters to MassAbility
- Position-title patterns capture VDE roles, medical consultants, DDS-named management

Verified clean: across all years, 3,028 examiner-titled records exist; 100% are within MRC, zero in DMR or elsewhere.

## Where conflation sneaks in

- **Search engines** return DDS-Dev results (mass.gov "DDS Central Office", "DDS Eligibility Services") when querying generic "Massachusetts DDS"
- **The 2023 SRC Annual Report** uses "Department of Disability Services (DDS)" once — author typo for *Developmental*
- **CTHRU's `DMR` code** (see warning above)
- **MA legislature budget docs** sometimes group both under "DDS" line-items
- **The Arc of Massachusetts** site references DDS-Dev (advocacy partner), not DDS-Det

## Database/naming recommendation

For 509dds.com schema: prefer `disability_determination_*` over `dds_*`. If `dds_*` is unavoidable, add a column comment explaining scope. Same for routes, env vars, file names.

## Suggested 509dds resource-page disclaimer

> *Throughout this site, "DDS" refers to **Disability Determination Services**, the division within MassAbility (formerly MRC) that adjudicates federal SSI/SSDI claims and is represented by SEIU Local 509. It is distinct from the **Department of Developmental Services**, an unrelated MA agency that serves people with intellectual and developmental disabilities (~5,500 employees, separate workforce).*
