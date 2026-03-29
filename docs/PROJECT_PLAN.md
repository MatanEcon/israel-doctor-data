# Project Plan - Israel Kupot Cholim Doctor Scraper

## Current Status
- [x] Repository created at github.com/MatanEcon/matanecon
- [x] Initial code structure implemented
- [x] Base scraper framework created
- [ ] Needs testing with actual websites
- [ ] Needs API endpoint discovery

## Implementation Phases

### Phase 1: Infrastructure (COMPLETED)
- [x] Project structure created
- [x] Base scraper classes
- [x] Configuration management
- [x] Logging setup
- [x] Data models (DoctorRecord)

### Phase 2: Source Discovery & Testing (TODO)
- [ ] Discover actual API endpoints for each site
- [ ] Test scraping on Maccabi (has clearest API structure)
- [ ] Test scraping on Clalit
- [ ] Test scraping on Meuhedet
- [ ] Test scraping on Leumit
- [ ] Test third-party aggregators

### Phase 3: Full Scraping (TODO)
- [ ] Run Maccabi scraper across all specialties
- [ ] Run Clalit scraper
- [ ] Run Meuhedet scraper
- [ ] Run Leumit scraper
- [ ] Run DoctorIndex scraper
- [ ] Run MedReviews scraper

### Phase 4: Data Processing (TODO)
- [ ] Deduplicate records
- [ ] Standardize specialty names
- [ ] Standardize doctor names
- [ ] Generate Kupat Cholim indicators
- [ ] Add year field

### Phase 5: Validation (TODO)
- [ ] Compare counts against Ministry of Health benchmarks
- [ ] Spot-check sample records
- [ ] Verify data quality

### Phase 6: Historical Data (TODO)
- [ ] Develop strategy for 2010-2023 data
- [ ] Check for archived data sources
- [ ] Implement year-based scraping

## Data Sources & API Exploration

### Known API Endpoints

#### Maccabi (Most Promising)
- Base URL: `https://sereotype.maccabi4u.co.il`
- Search: `/heb/doctors/doctorssearchresults/`
- Parameters: `City`, `Field` (specialty code), `Gender`, `PageNumber`
- Cities: `City=5000` for Tel Aviv
- Specialties: `Field=006` for Orthopedics, etc.

#### Leumit
- API endpoint: `/API/Doctors` (reported)
- Web interface: `/heb/doctorssearch`

#### Third-Party Sources
- DoctorIndex: `https://doctorindex.co.il/search/`
- MedReviews: `https://www.medreviews.co.il/en/search/all?insurance={1-4}`

### Challenges to Address

1. **Rate Limiting**: Sites may block scraping
2. **JavaScript Rendering**: Some sites may require Selenium
3. **API Authentication**: Some endpoints may require login
4. **Data Completeness**: Websites only show doctors accepting new patients
5. **Historical Data**: No historical snapshots available

## Validation Benchmarks

Based on Ministry of Health reports:

| Year | Total Physicians | Clalit | Maccabi | Meuhedet | Leumit |
|------|------------------|--------|---------|----------|--------|
| 2021 | 38,247 | ~13,000 | ~9,000 | ~4,000 | ~3,000 |
| 2022 | 39,000 | ~13,500 | ~9,200 | ~4,200 | ~3,100 |
| 2023 | 40,000 | ~14,000 | ~9,500 | ~4,400 | ~3,200 |

Note: Numbers overlap - same doctor may work in multiple kupot.

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Test Maccabi scraper**: `python test_scraper.py`
3. **Inspect actual website responses** to refine scraping logic
4. **Run full scrape** when ready: `python run_scrapers.py`

## Key Files

- `run_scrapers.py` - Main orchestrator
- `test_scraper.py` - Simple test script
- `src/scrapers/` - Individual scraper implementations
- `src/validate.py` - Data validation
- `notebooks/analysis.ipynb` - Data analysis

## Research Notes

### The Atzmai Problem
Doctors in Kupot Cholim often work as "atzmaim" (self-employed), meaning:
- In tax data, they appear as private income recipients
- Their income comes from public health funds
- Need to identify these to properly classify income as public sector

### Dual Practice
Many specialists work in both public hospitals AND Kupot Cholim:
- Need to identify which doctors work where
- Cross-reference with hospital employment data
- Track multi-employment patterns

### Data Enrichment Ideas
1. Cross-reference with Ministry of Health license registry
2. Match with tax authority data
3. Use name standardization algorithms
4. Add geographic clustering
