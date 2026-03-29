"""
Scraper for Doctorim.co.il - Doctor appointment scheduling site
~27,000 doctors across all Kupot Cholim
"""

import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from src.base_scraper import BaseScraper
from src.config import DoctorRecord, KUPA_CHOLIM


class DoctorimScraper(BaseScraper):
    """Scraper for Doctorim.co.il doctor directory."""

    BASE_URL = "https://www.doctorim.co.il"
    SPECIALTIES_URL = f"{BASE_URL}/catalog.php?type=specialities"
    SEARCH_URL = f"{BASE_URL}/SearchBySpecialty"

    KUPA_PATTERNS = {
        "clalit": ["כללית", "כלל"],
        "maccabi": ["מכבי"],
        "meuhedet": ["מאוחדת", "מאוחד"],
        "leumit": ["לאומית", "לומית"]
    }

    def __init__(self):
        super().__init__("doctorim", delay_range=(1, 2))
        self.logger.info("Initialized Doctorim scraper")

    def get_specialties(self) -> List[Dict]:
        """Get list of all specialties with their IDs."""
        html = self._curl_request(self.SPECIALTIES_URL)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        specialties = []

        links = soup.select("a[href*='spec_id=']")
        seen_ids = set()

        for link in links:
            href = link.get("href", "")
            match = re.search(r"spec_id=(\d+)", href)
            if match:
                spec_id = match.group(1)
                if spec_id not in seen_ids:
                    seen_ids.add(spec_id)
                    specialties.append({
                        "id": spec_id,
                        "name": link.get_text(strip=True),
                        "url": href
                    })

        self.logger.info(f"Found {len(specialties)} specialties")
        return specialties

    def scrape_specialty_page(self, spec_id: str, page: int = 1) -> List[DoctorRecord]:
        """Scrape a single page of doctors for a specialty."""
        url = f"{self.SEARCH_URL}/*/*/all/?spec_id={spec_id}&page={page}"

        html = self._curl_request(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        return self._parse_doctors(soup)

    def _parse_doctors(self, soup: BeautifulSoup) -> List[DoctorRecord]:
        """Parse doctor listings from page."""
        doctors = []
        doctor_links = soup.select("a.doctors-item__link")

        for link in doctor_links:
            try:
                href = link.get("href", "")
                match = re.search(r"doctor-(\d+)", href)
                if not match:
                    continue

                doctor_id = match.group(1)
                name = link.get_text(strip=True).replace("ד\"ר", "").replace("ד'", "").strip()

                parent = link.find_parent("div", class_="doctors-item")
                if not parent:
                    continue

                specialty_elem = parent.select_one(".doctors-item__informationSpecialization")
                specialty = specialty_elem.get_text(strip=True) if specialty_elem else None

                kupot = {"clalit": 0, "maccabi": 0, "meuhedet": 0, "leumit": 0}
                insurance_elem = parent.select_one(".doctors-item__info-item_insurance")
                if insurance_elem:
                    insurance_text = insurance_elem.get_text(strip=True)
                    for kupa_id, patterns in self.KUPA_PATTERNS.items():
                        for pattern in patterns:
                            if pattern in insurance_text:
                                kupot[kupa_id] = 1

                address_elem = parent.select_one(".doctors-item__clinic-parameter_location")
                address = address_elem.get_text(strip=True) if address_elem else None

                record = DoctorRecord(
                    name=name,
                    specialty=specialty,
                    clinic_address=address,
                    source_url=f"{self.BASE_URL}/s/doctor-{doctor_id}",
                    source_name="Doctorim"
                )

                for kupa_id, val in kupot.items():
                    setattr(record, kupa_id, val)

                doctors.append(record)

            except Exception as e:
                self.logger.debug(f"Error parsing doctor: {e}")
                continue

        return doctors

    def get_total_pages(self, spec_id: str) -> int:
        """Get total pages for a specialty."""
        url = f"{self.SEARCH_URL}/*/*/all/?spec_id={spec_id}&page=1"
        html = self._curl_request(url)
        if not html:
            return 1

        soup = BeautifulSoup(html, "lxml")
        
        # Find pagination container and get page links within it
        pagination = soup.select_one(".site__paginationSite")
        if not pagination:
            # Fallback: count doctors and estimate pages
            doctors = soup.select("a.doctors-item__link")
            if len(doctors) == 10:
                return 50  # Assume at least 50 pages if full page
            return 1
        
        page_links = pagination.select("a[href*='page=']")
        max_page = 1
        for link in page_links:
            href = link.get("href", "")
            match = re.search(r"page=(\d+)", href)
            if match:
                page_num = int(match.group(1))
                max_page = max(max_page, page_num)
        return max_page

    def scrape_specialty(self, spec_id: str, spec_name: str = "", max_pages: int = None) -> List[DoctorRecord]:
        """Scrape all pages for a specialty."""
        records = []
        total_pages = self.get_total_pages(spec_id)

        if max_pages:
            total_pages = min(total_pages, max_pages)

        self.logger.info(f"Scraping {spec_name} (spec_id={spec_id}): {total_pages} pages")

        for page in range(1, total_pages + 1):
            try:
                page_records = self.scrape_specialty_page(spec_id, page)
                records.extend(page_records)

                if page % 10 == 0:
                    self.logger.info(f"  Page {page}/{total_pages}: {len(records)} doctors so far")

            except Exception as e:
                self.logger.error(f"Error on page {page}: {e}")

            self._random_delay()

        return records

    def scrape(self, max_pages_per_specialty: int = 10, specialty_ids: List[str] = None) -> List[DoctorRecord]:
        """Scrape doctors from all or specified specialties."""
        all_records = []

        if specialty_ids:
            specialties = [{"id": sid, "name": ""} for sid in specialty_ids]
        else:
            specialties = self.get_specialties()

        for i, spec in enumerate(specialties):
            self.logger.info(f"[{i+1}/{len(specialties)}] Scraping {spec['name']}")
            records = self.scrape_specialty(spec["id"], spec["name"], max_pages_per_specialty)
            all_records.extend(records)
            self.logger.info(f"  Found {len(records)} doctors")

        self.records = all_records
        return all_records


if __name__ == "__main__":
    scraper = DoctorimScraper()

    print("Getting specialties...")
    specs = scraper.get_specialties()
    print(f"Found {len(specs)} specialties")

    print("\nScraping first 3 specialties (10 pages each)...")
    records = scraper.scrape(max_pages_per_specialty=10, specialty_ids=[s["id"] for s in specs[:3]])

    print(f"\nTotal: {len(records)} doctors")

    if records:
        scraper.save_records("doctorim_test.csv")
    else:
        print("No records scraped - testing curl directly...")
        test_url = "https://www.doctorim.co.il/SearchBySpecialty/*/*/all/?spec_id=1183&page=1"
        result = scraper._curl_request(test_url)
        if result:
            print(f"curl returned {len(result)} bytes")
            soup = BeautifulSoup(result, "lxml")
            doctors = soup.select("a.doctors-item__link")
            print(f"Found {len(doctors)} doctor links on test page")
