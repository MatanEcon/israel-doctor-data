# Israel Kupot Cholim Doctor Scraper

## Project Overview
Comprehensive scraping and analysis of doctors working in the 4 Israeli health funds (Kupot Cholim) for salary research, specifically to distinguish dual practice specialists whose income appears as "atzmai" (self-employed/private) in tax data but should be classified as public income.

## The Problem
- Doctors work as "atzmaim" (self-employed) in Kupot Cholim
- In tax data, this appears as private income rather than public sector income
- Need to accurately categorize which doctors work in which Kupot Cholim

## Target Data Fields
- `name`: Doctor's full name
- `teudat_zehut`: Israeli ID (when available from public records)
- `specialty`: Medical specialty
- `year`: Year of practice in Kupa
- `gender`: Male/Female
- `clalit`: Binary indicator (1 = works in Clalit)
- `maccabi`: Binary indicator (1 = works in Maccabi)
- `meuhedet`: Binary indicator (1 = works in Meuhedet)
- `leumit`: Binary indicator (1 = works in Leumit)

## Data Sources

### Primary Sources (Kupa Websites)
1. **Clalit** - https://www.clalit.co.il/
2. **Maccabi** - https://www.maccabi4u.co.il/ (has API potential)
3. **Meuhedet** - https://www.meuhedet.co.il/
4. **Leumit** - https://www.leumit.co.il/

### Third-Party Doctor Finders
1. **DoctorIndex** - https://doctorindex.co.il/ - Comprehensive doctor database
2. **MedReviews** - https://www.medreviews.co.il/ - Has doctor listings by insurance
3. **Drtor** - https://drtor.co.il/ - Doctor scheduling
4. **Booa** - https://booa.co.il/ - Ministry of Health registry search

### Official Registries
1. **Ministry of Health Practitioner Registry** - https://practitioners.health.gov.il/
2. **Doctor License Registry (פנקס הרופאים)** - Official registry of licensed physicians
3. **Medical Committees Registry** - Doctors eligible for medical committees (2012+)

### Open Data
1. **gov.il Open Data** - https://data.gov.il/
2. **odata.org.il** - Israeli open data portal
3. **CBS (Central Bureau of Statistics)** - Official statistics

### Reference Reports for Validation
1. Ministry of Health "Health Workforce" reports (annual, 2010-2023)
2. Taub Center health workforce reports
3. CBS labor force surveys

## Known APIs and Scraping Points

### Maccabi
- Has internal API structure (observed in search URLs)
- Search endpoint: `/heb/doctors/doctorssearchresults/`
- Parameters: City, Field (specialty), Gender, PageNumber

### Clalit
- Website search with Selenium options
- Alternative: medreviews.co.il aggregation

### Leumit
- Web-based search interface
- Mobile app API endpoint available

### Meuhedet
- MyDoctor platform integration
- Web-based search

## Validation Benchmarks
Based on Ministry of Health reports:
- Total physicians in Israel (2021): ~38,000
- Physicians by sector distribution needed
- Annual growth rate: ~2-3%

## Technical Approach

### Phase 1: Infrastructure Setup
- [ ] Set up Python environment with required packages
- [ ] Create database schema
- [ ] Implement logging and error handling

### Phase 2: Source Exploration
- [ ] Test each data source API/structure
- [ ] Document rate limits and access restrictions
- [ ] Identify data availability by year

### Phase 3: Scraping Implementation
- [ ] Implement scrapers for each Kupa
- [ ] Implement third-party aggregator scrapers
- [ ] Cross-reference with Ministry of Health registry

### Phase 4: Data Processing
- [ ] Deduplicate records
- [ ] Standardize names and specialties
- [ ] Generate Kupa indicator columns

### Phase 5: Validation
- [ ] Compare counts against official reports
- [ ] Verify data quality
- [ ] Audit completeness

## Output Format
- CSV files organized by year: `doctors_2010.csv`, `doctors_2011.csv`, etc.
- Master file: `all_doctors_combined.csv`
- Log files for each scrape operation

## Dependencies
- Python 3.8+
- requests / httpx for HTTP requests
- BeautifulSoup / lxml for HTML parsing
- selenium (if needed for JS-heavy sites)
- pandas for data manipulation
- logging for operations tracking
