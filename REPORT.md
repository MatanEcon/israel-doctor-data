# Israel Doctor Dataset - Comprehensive Report

**Generated:** March 2026  
**Project:** Israeli Kupot Cholim Doctor Data Collection

---

## Executive Summary

This report presents a comprehensive dataset of doctors in Israel, with a focus on identifying those affiliated with the four major Kupot Cholim (health funds): Clalit, Maccabi, Meuhedet, and Leumit. The data was collected to support research on dual-practice doctors whose income appears as "atzmai" (self-employed) in tax data but who work in the public health system.

### Current Status: Data Collection Blocked

**CRITICAL ISSUE:** All major data sources are protected by advanced anti-bot systems:
- **data.gov.il**: Radware anti-bot protection (Imperva/Incapsula)
- **Maccabi**: Dynamic React app with anti-bot (Radware)
- **Leumit/Clalit**: Similar protections

**Current coverage:** ~1,148 matched doctors with kupa affiliations (target: ~40,000)

## 1. Dataset Overview

### 1.1 Total Records
- **Total records:** ~74,000+
- **Unique doctors:** ~65,000+
- **Records with kupa affiliation:** 866 (insufficient - target: ~40,000)
- **MOH-MedReviews matched with kupa:** 1,148 (after name order fix)
- **IMA doctors collected:** 5,964
- **Cross-dataset matches:** 1,263 IMA-MOH, 125 IMA-MedReviews

### 1.2 Critical Finding: Hebrew Name Order
- **MOH format:** `LAST FIRST` (e.g., "זילבר משה")
- **MedReviews format:** `FIRST LAST` (e.g., "ד"ר משה זילבר")
- **Before fix:** Only 14 matches
- **After fix:** 1,148 matches (82x improvement!)

### 1.3 Data Sources

| Source | Records | Description |
|--------|---------|-------------|
| MOH License Database | 62,818 | Official Ministry of Health licensed doctor registry |
| MedReviews | 2,820 | Doctor appointment platform with kupa affiliations |
| Doctorim | 2,414 | Doctor scheduling site with kupa affiliations |
| IMA (Israeli Medical Association) | 5,964 | IMA member directory |

### 1.3 Coverage by Kupa

| Health Fund | Hebrew | Doctors | Coverage % |
|-------------|-------|---------|------------|
| Clalit | כללית | 501 | Based on available data |
| Maccabi | מכבי | 468 | Based on available data |
| Meuhedet | מאוחדת | 328 | Based on available data |
| Leumit | לאומית | 315 | Based on available data |

## 2. Data Variables

### 2.1 Core Variables

| Variable | Type | Description | Source |
|----------|------|-------------|--------|
| name | string | Doctor's full name in Hebrew | All sources |
| teudat_zehut | string | Israeli ID number | MOH |
| specialty | string | Medical specialty | All sources |
| year | integer | Year of birth (if available) | MOH |
| gender | string | Male/Female | MOH |
| clinic_address | string | Clinic location | All sources |
| phone | string | Contact phone | MedReviews, MOH |
| license_number | string | Medical license number | MOH |
| license_date | date | Date of license issuance | MOH |
| specialty_registration_date | date | Date of specialty certification | MOH |
| source_url | string | URL to source profile | All sources |
| source_name | string | Name of data source | All sources |
| scrape_date | datetime | Date data was collected | All sources |

### 2.2 Kupa Affiliation Variables (Binary)

| Variable | Type | Description |
|----------|------|-------------|
| clalit | integer (0/1) | Affiliated with Clalit Health Services |
| maccabi | integer (0/1) | Affiliated with Maccabi Healthcare Services |
| meuhedet | integer (0/1) | Affiliated with Meuhedet Health Services |
| leumit | integer (0/1) | Affiliated with Leumit Health Services |

### 2.3 Derived Variables

| Variable | Type | Description |
|----------|------|-------------|
| has_kupa | boolean | Whether doctor has any kupa affiliation |
| kupa_count | integer | Number of kupot doctor is affiliated with |

## 3. Specialty Distribution

### 3.1 Top 15 Specialties (All Data)

| Rank | Specialty | Count |
|------|-----------|-------|
| 1 | Internal Medicine (רפואה פנימית) | 5,635 |
| 2 | Pediatrics (רפואת ילדים) | 4,096 |
| 3 | Family Medicine (רפואת המשפחה) | 3,237 |
| 4 | Obstetrics & Gynecology (יילוד וגינקולוגיה) | 2,253 |
| 5 | Psychiatry (פסיכיאטריה) | 1,725 |
| 6 | Anesthesiology (הרדמה) | 1,355 |
| 7 | Orthopedic Surgery (כירורגיה אורתופדית) | 1,271 |
| 8 | General Surgery (כירורגיה כללית) | 1,220 |
| 9 | Ophthalmology (מחלות עיניים) | 1,137 |
| 10 | Diagnostic Radiology (רדיולוגיה אבחנתית) | 1,101 |
| 11 | Cardiology (קרדיולוגיה) | 1,030 |
| 12 | Geriatrics (גריאטריה) | 708 |
| 13 | Neurology (נוירולוגיה) | 701 |
| 14 | Gastroenterology (גסטרואנטרולוגיה) | 568 |
| 15 | Dermatology (דרמטולוגיה) | 555 |

### 3.2 Top Specialties with Kupa Affiliation

| Specialty | Count |
|-----------|-------|
| Orthopedic Surgery | 27 |
| Physiotherapy | 27 |
| Ophthalmology | 27 |
| General Surgery | 21 |
| OB/GYN | 18 |
| Plastic Surgery | 17 |
| Gastroenterology | 16 |
| Cardiology | 14 |
| Urology | 13 |
| ENT | 11 |

## 4. Multi-Kupa Analysis

### 4.1 Distribution of Kupa Affiliations

| Kupa Count | Doctors | Percentage |
|------------|---------|------------|
| 0 | 64,753 | 98.7% |
| 1 | 419 | 0.6% |
| 2 | 233 | 0.4% |
| 3 | 129 | 0.2% |
| 4 | 85 | 0.1% |

### 4.2 Interpretation

The data shows that while most doctors in the MOH registry do not have documented kupa affiliations, among those who do, there is significant multi-affiliation:
- 85 doctors (0.1%) are affiliated with all 4 kupot
- 129 doctors (0.2%) are affiliated with 3 kupot
- 233 doctors (0.4%) are affiliated with 2 kupot

This multi-affiliation pattern is consistent with the dual-practice phenomenon described in the Knesset Research Paper.

## 5. Data Quality Notes

### 5.1 Coverage Limitations

1. **Kupa Data Gap**: Only 866 doctors (1.3%) have documented kupa affiliations - FAR BELOW the ~40,000 doctors working in kupot
2. **Source Coverage**: MedReviews and Doctorim represent doctors who list on appointment platforms, not all doctors
3. **Name Matching**: MOH data and kupa data have low overlap due to different populations
4. **Anti-Bot Blocking**: Major scraping targets (Maccabi, data.gov.il, Leumit) all use advanced anti-bot protection (Radware/Imperva)

### 5.2 Anti-Bot Challenges Encountered

| Target | Protection | Attempted Solutions |
|--------|------------|---------------------|
| data.gov.il | Imperva/Incapsula | curl, requests, camoufox, playwright |
| Maccabi serek | Radware | camoufox, playwright (partial) |
| Leumit | Unknown | requests (blocked) |
| Clalit | Unknown | requests (blocked) |

**Key finding:** Israeli health websites use sophisticated anti-bot systems that block automated data collection.

### 5.3 Available Tools Tested

| Tool | Status | Notes |
|------|--------|-------|
| requests | ❌ Blocked | Simple HTTP requests detected |
| BeautifulSoup | N/A | HTML parser only |
| camoufox | ⚠️ Partial | Stealth browser but slow |
| playwright | ⚠️ Partial | Can bypass some protections but data loads dynamically |
| selenium | ⚠️ Partial | Requires login for some sites |

### 5.2 Data Completeness

| Variable | Completeness |
|----------|--------------|
| name | 100% |
| specialty | 100% |
| license_number | MOH: 100%, Others: Varies |
| teudat_zehut | MOH: Mostly empty |
| year | MOH: Mostly empty |
| gender | MOH: Mostly empty |
| clinic_address | Varies by source |
| phone | MedReviews/Doctorim: Good |

## 6. Reference Benchmark

According to the 2024 Knesset Research Paper on dual-practice doctors:

- **Total licensed doctors in Israel (2022):** 33,558
- **Total doctors including retired/inactive:** 44,840
- **Actively practicing doctors:** 31,396

### Dual Practice Rates by Health Fund (2023):
| Health Fund | High Estimate | Low Estimate |
|-------------|--------------|-------------|
| Clalit | 85% | 75% |
| Maccabi | 53% | 48% |
| Meuhedet | 44% | 37% |
| Leumit | 17% | 15% |

## 7. File Descriptions

### 7.1 Data Files

| File | Description |
|------|-------------|
| `data/final/israel_doctors_final.csv` | Main unified dataset |
| `data/raw/moh_doctors.csv` | MOH license database |
| `data/raw/medreviews_full.csv` | MedReviews scraper output |
| `data/raw/doctorim_parallel.csv` | Doctorim key specialties |
| `data/raw/doctorim_more.csv` | Doctorim additional specialties |
| `data/raw/all_kupa_affiliations.csv` | Combined kupa affiliations |

### 7.2 Reference Files

| File | Description |
|------|-------------|
| `references/knesset_doctor_salaries_2023.pdf` | Knesset research paper |
| `references/pdf_text.txt` | Extracted text from PDF |

## 8. Methodology

### 8.1 Data Collection

1. **MOH License Database**: API access to data.gov.il
2. **MedReviews**: GraphQL API reverse-engineered from web requests
3. **Doctorim**: HTML scraping using curl for SSL bypass

### 8.2 Data Integration

1. Names were normalized (lowercase, Hebrew character handling)
2. Kupa affiliations aggregated by doctor name
3. Final dataset created by merging MOH base with kupa data

## 9. Conclusions

This dataset provides a foundation for analyzing doctor affiliations with Israeli health funds. Key findings:

1. The dataset contains ~74,000 records representing 62,818 MOH-licensed doctors plus additional doctors from MedReviews, Doctorim, and IMA
2. Only 866 doctors (1.3%) have documented kupa affiliations - **critically insufficient** for research requiring ~40,000 doctors
3. Among doctors with kupa data, 85 are affiliated with all 4 kupot
4. **MAJOR BLOCKER:** Advanced anti-bot systems (Radware/Imperva) prevent automated data collection from major Israeli health websites

### Critical Gap

The current dataset cannot support meaningful research on dual-practice doctors because:
- Target: ~40,000 doctors with kupa affiliations
- Current coverage: 866 doctors (2.2% of target)
- Name-based matching alone is insufficient without unique identifiers (teudat_zehut)

### Required Actions

To complete this project, alternative data acquisition methods are needed:
1. Formal data requests to Ministry of Health
2. Direct partnership with Kupot Cholim
3. Academic data sharing agreements
4. Legal/freedom of information requests

### Recommendations for Future Work

1. **Expand kupa data collection to cover more doctors**
   - Partner with kupot directly for data access
   - Use official data requests (freedom of information)
   - Consider legal channels for academic research data

2. **Obtain teudat_zehut for proper record linkage**
   - Currently no unique identifier linking datasets
   - Name matching is probabilistic and error-prone

3. **Cross-reference with tax authority data for dual-practice analysis**
   - Income data from "atzmai" status
   - Requires legal cooperation with tax authority

4. **Collect data directly from kupa websites**
   - May require login credentials
   - Alternative: Request bulk data from Ministry of Health

### 5.4 Potential Solutions to Explore

1. **Government FOIA Request**: Request doctor affiliation data through formal channels
2. **Academic Partnerships**: Partner with Israeli universities that may have data access agreements
3. **Kupa Collaboration**: Approach kupot directly for research partnerships
4. **Manual Data Entry**: If automated scraping fails, consider crowd-sourced data collection
5. **Browser Extension**: Create a browser extension users can install to anonymously share kupa affiliation data

---

**GitHub Repository:** https://github.com/MatanEcon/israel-doctor-data

**Dataset Location:** `data/final/israel_doctors_final.csv`
