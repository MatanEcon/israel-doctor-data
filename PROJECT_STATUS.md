# Israel Doctor Data - Project Status

## Goal
Create a comprehensive dataset of all doctors working in the 4 Israeli Kupot Cholim (health funds) for research on dual-practice doctors whose income appears as "atzmai" (self-employed) in tax data.

## Current Status

### Data Sources Scraped

| Source | Records | Kupa Data | Status |
|--------|---------|-----------|--------|
| MOH License DB | 62,818 | No | Complete |
| MedReviews | 2,822 | Yes | Complete (network blocked now) |
| Doctorim | 38 | Yes | Broken (pagination issue) |
| **Combined** | **65,678** | **Limited** | **Name matching failed** |

### Key Finding
The name-based matching between MOH and kupa data sources has very low overlap (~14 doctors). This is because:
- MOH data: All licensed doctors in Israel
- MedReviews: Doctors who specifically list on their private practice platform
- These are largely different populations

### Kupot Distribution (from MedReviews only)
- Clalit: 494 doctors
- Maccabi: 469 doctors
- Meuhedet: 331 doctors
- Leumit: 314 doctors

Note: These numbers represent only the 2,822 doctors in MedReviews, not all doctors in each kupa.

## Technical Issues Encountered

1. **Doctorim Pagination**: The site returns same doctors across all pages for some specialties
2. **MedReviews Network Block**: Cannot access from current network location
3. **Name Matching**: Datasets have different doctor populations, not just different representations

## Next Steps

1. **Fix Doctorim Scraper**: Debug pagination for specialties that return same content
2. **Find Additional Sources**: Need more sources with kupa affiliations
3. **Direct Kupa APIs**: Check if kupot have public doctor directories
4. **Alternative Matching**: Use fuzzy name matching or other identifiers

## Files

- `data/raw/moh_doctors.csv` - MOH license database (62k doctors)
- `data/raw/medreviews_full.csv` - MedReviews with kupa data (2.8k)
- `data/raw/doctorim_full.csv` - Doctorim with kupa data (38 unique)
- `data/raw/kupa_affiliations.csv` - Combined kupa affiliations
- `data/combined/kupa_doctors_combined.csv` - MOH merged with kupa data
- `references/knesset_doctor_salaries_2023.pdf` - Knesset research paper on dual-practice doctors
