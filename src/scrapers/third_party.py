"""
Scrapers for third-party doctor aggregators.
MedReviews.co.il - uses GraphQL API (working)
DoctorIndex.co.il - comprehensive Israeli doctor database
"""

import re
import json
from typing import List, Optional, Dict

from src.base_scraper import BaseScraper, ThirdPartyAggregator
from src.config import DoctorRecord, KUPA_CHOLIM

GRAPHQL_URL = "https://www.medreviews.co.il/graphql"

KUPA_NAME_MAP = {
    "כללית": "clalit",
    "כללית מושלם": "clalit",
    "כללית מושלם פלטינום": "clalit",
    "מכבי": "maccabi",
    "מכבי זהב": "maccabi",
    "מכבי שלי": "maccabi",
    "מאוחדת": "meuhedet",
    "מאוחדת עדיף": "meuhedet",
    "מאוחדת שיא": "meuhedet",
    "לאומית": "leumit",
    "לאומית כסף": "leumit",
    "לאומית זהב": "leumit",
    "באופן פרטי": "private",
}


class MedReviewsGraphQLScraper(BaseScraper):
    """
    Scraper for MedReviews.co.il using their GraphQL API.
    
    API discovered through reverse engineering:
    - Endpoint: https://www.medreviews.co.il/graphql
    - Query: profilesPageBySearchParams(lang: "he", limit: N, skip: N)
    - Returns: name, _id, specialization, insurances (with name)
    """

    KUPA_NAME_MAP = KUPA_NAME_MAP

    def __init__(self):
        super().__init__("medreviews")
        self.graphql_url = GRAPHQL_URL
        self.logger.info("Initialized MedReviews GraphQL scraper")

    def get_total_pages(self, soup=None) -> int:
        return self.get_total_count()

    def parse_doctor_listing(self, soup) -> List[Dict]:
        return []

    def _graphql_query(self, limit: int = 100, skip: int = 0) -> Dict:
        """Execute GraphQL query for doctors."""
        query = """
        query GetDoctors($lang: String!, $limit: Int!, $skip: Int!) {
            profilesPageBySearchParams(lang: $lang, limit: $limit, skip: $skip) {
                total
                items {
                    _id
                    name
                    specialization
                    subSpecialization
                    slug
                    insurances {
                        name
                    }
                }
            }
        }
        """
        payload = {
            "query": query,
            "variables": {
                "lang": "he",
                "limit": limit,
                "skip": skip
            }
        }
        response = self._make_request(
            self.graphql_url,
            method="POST",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        if response:
            return response.json()
        return {}

    def _extract_kupot(self, insurances: List[Dict]) -> Dict[str, int]:
        """Extract kupa affiliations from insurance list."""
        result = {"clalit": 0, "maccabi": 0, "meuhedet": 0, "leumit": 0}
        if not insurances:
            return result
        for ins in insurances:
            ins_name = ins.get("name", "")
            for kupa_pattern, kupa_id in self.KUPA_NAME_MAP.items():
                if kupa_pattern in ins_name and kupa_id in result:
                    result[kupa_id] = 1
        return result

    def _parse_doctor(self, item: Dict) -> DoctorRecord:
        """Parse a single doctor item into DoctorRecord."""
        insurances = item.get("insurances", [])
        kupot = self._extract_kupot(insurances)

        record = DoctorRecord(
            name=item.get("name", ""),
            specialty=item.get("specialization"),
            source_url=f"https://www.medreviews.co.il/provider/{item.get('slug', '')}",
            source_name="MedReviews"
        )
        for kupa_id, val in kupot.items():
            setattr(record, kupa_id, val)
        return record

    def get_total_count(self) -> int:
        """Get total number of profiles."""
        result = self._graphql_query(limit=1, skip=0)
        if result and result.get("data"):
            return result["data"]["profilesPageBySearchParams"]["total"]
        return 0

    def scrape(self, batch_size: int = 100, max_doctors: Optional[int] = None) -> List[DoctorRecord]:
        """Scrape all doctors using GraphQL pagination."""
        records = []
        skip = 0
        total = self.get_total_count()
        self.logger.info(f"Total profiles to scrape: {total}")

        if max_doctors:
            total = min(total, max_doctors)

        while skip < total:
            result = self._graphql_query(limit=batch_size, skip=skip)
            if not result or "data" not in result:
                self.logger.error(f"Failed to fetch batch at skip={skip}")
                break

            items = result["data"]["profilesPageBySearchParams"]["items"]
            if not items:
                break

            for item in items:
                record = self._parse_doctor(item)
                records.append(record)

            self.logger.info(f"Scraped {len(records)}/{total} doctors")
            skip += batch_size
            self._random_delay()

        self.records = records
        return records


class DoctorIndexScraper(ThirdPartyAggregator):
    """Scraper for DoctorIndex.co.il - comprehensive Israeli doctor database."""

    def __init__(self):
        super().__init__("doctorindex", "https://doctorindex.co.il")
        self.search_url = "https://doctorindex.co.il/search/"
        self.logger.info("Initialized DoctorIndex scraper")
    
    def parse_doctor_listing(self, soup) -> List[Dict]:
        """Parse doctor listings from DoctorIndex."""
        doctors = []
        cards = soup.select(".doctor-card, .result-item, article")
        
        for card in cards:
            doctor = {}
            
            name_elem = card.select_one("h2, h3, .doctor-name, [class*='name']")
            if name_elem:
                doctor["name"] = name_elem.get_text(strip=True)
            
            specialty_elem = card.select_one(".specialty, [class*='special']")
            if specialty_elem:
                doctor["specialty"] = specialty_elem.get_text(strip=True)
            
            address_elem = card.select_one(".address, [class*='address']")
            if address_elem:
                doctor["address"] = address_elem.get_text(strip=True)
            
            phone_elem = card.select_one("a[href^='tel:'], .phone")
            if phone_elem:
                doctor["phone"] = phone_elem.get("href", "").replace("tel:", "")
            
            kupa_elements = card.select("[class*='kupa'], [class*='health'], [class*='fund']")
            for kupa_elem in kupa_elements:
                text = kupa_elem.get_text(strip=True).lower()
                for kupa_id, info in KUPA_CHOLIM.items():
                    if info["name_hebrew"] in text or info["name"].lower() in text:
                        doctor[kupa_id] = 1
            
            doctors.append(doctor)
        
        return doctors
    
    def get_total_pages(self, soup) -> int:
        """Get total number of pages."""
        pagination = soup.select(".pagination a, .pager a")
        if pagination:
            pages = []
            for link in pagination:
                text = link.get_text(strip=True)
                if text.isdigit():
                    pages.append(int(text))
            return max(pages) if pages else 1
        return 1
    
    def scrape_specialty(self, specialty: str, max_pages: int = 10) -> List[DoctorRecord]:
        """Scrape doctors by specialty."""
        records = []
        
        for page in range(1, max_pages + 1):
            params = {"specialty": specialty, "page": page}
            try:
                response = self._make_request(self.search_url, params=params)
                if not response:
                    continue
                
                soup = self._parse_html(response.text)
                doctors = self.parse_doctor_listing(soup)
                
                for doc_data in doctors:
                    record = DoctorRecord(
                        name=doc_data.get("name", ""),
                        specialty=doc_data.get("specialty"),
                        phone=doc_data.get("phone"),
                        clinic_address=doc_data.get("address"),
                        source_url=self.search_url,
                        source_name="DoctorIndex"
                    )
                    for kupa_id in KUPA_CHOLIM.keys():
                        if doc_data.get(kupa_id):
                            setattr(record, kupa_id, 1)
                    records.append(record)
                
                total_pages = self.get_total_pages(soup)
                if page >= total_pages:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {e}")
                continue
            finally:
                self._random_delay()
        
        return records
    
    def scrape(self) -> List[DoctorRecord]:
        """Main scrape method - scrape all specialties."""
        specialties = [
            "רפואת משפחה", "פנימית", "ילדים", "נשים", "אורתופדיה",
            "כללי", "עיניים", "אף אוזן גרון", "עור", "לב",
            "מוח", "סרטן", "פסיכיאטריה", "ניתוחים"
        ]
        
        all_records = []
        for specialty in specialties:
            self.logger.info(f"Scraping specialty: {specialty}")
            records = self.scrape_specialty(specialty)
            all_records.extend(records)
            self.logger.info(f"Found {len(records)} doctors for {specialty}")
        
        self.records = all_records
        return all_records


class MedReviewsScraper(ThirdPartyAggregator):
    """Scraper for MedReviews.co.il - Doctor reviews by insurance."""
    
    KAPA_IDS = {
        1: "clalit",
        2: "meuhedet", 
        3: "leumit",
        4: "maccabi"
    }
    
    def __init__(self):
        super().__init__("medreviews", "https://www.medreviews.co.il")
        self.base_search_url = f"{self.base_url}/en/search/all"
        self.logger.info("Initialized MedReviews scraper")
    
    def parse_doctor_listing(self, soup) -> List[Dict]:
        """Parse doctor listings from MedReviews."""
        doctors = []
        cards = soup.select(".doctor-card, .result-card, .doctor-item")
        
        for card in cards:
            doctor = {}
            
            name_elem = card.select_one("h3, h4, .doctor-name, [class*='name']")
            if name_elem:
                doctor["name"] = name_elem.get_text(strip=True)
            
            specialty_elem = card.select_one(".specialty, [class*='special']")
            if specialty_elem:
                doctor["specialty"] = specialty_elem.get_text(strip=True)
            
            area_elem = card.select_one(".area, [class*='location']")
            if area_elem:
                doctor["area"] = area_elem.get_text(strip=True)
            
            insurance_elem = card.select("[class*='insurance'], [class*='kupa']")
            for ins in insurance_elem:
                text = ins.get_text(strip=True)
                for kupa_id, info in KUPA_CHOLIM.items():
                    if info["name"].lower() in text.lower():
                        doctor[kupa_id] = 1
            
            doctors.append(doctor)
        
        return doctors
    
    def get_total_count(self, soup) -> int:
        """Get total number of doctors found."""
        count_elem = soup.select_one(".result-count, .found, [class*='count']")
        if count_elem:
            text = count_elem.get_text(strip=True)
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
        return 0
    
    def get_total_pages(self, soup) -> int:
        """Get total number of pages."""
        total = self.get_total_count(soup)
        if total > 0:
            return (total + 9) // 10  # Assuming ~10 results per page
        return 1
    
    def scrape_kupa(self, kupa_id: str, insurance_num: int) -> List[DoctorRecord]:
        """Scrape doctors for a specific kupa."""
        records = []
        page = 1
        max_pages = 50
        
        while page <= max_pages:
            url = f"{self.base_search_url}?insurance={insurance_num}&page={page}"
            try:
                response = self._make_request(url)
                if not response:
                    break
                
                soup = self._parse_html(response.text)
                doctors = self.parse_doctor_listing(soup)
                
                if not doctors:
                    break
                
                for doc_data in doctors:
                    record = DoctorRecord(
                        name=doc_data.get("name", ""),
                        specialty=doc_data.get("specialty"),
                        clinic_address=doc_data.get("area"),
                        source_url=url,
                        source_name="MedReviews"
                    )
                    setattr(record, kupa_id, 1)
                    records.append(record)
                
                total = self.get_total_count(soup)
                if page * 10 >= total:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error on page {page}: {e}")
                break
            finally:
                self._random_delay()
            
            page += 1
        
        return records
    
    def scrape(self) -> List[DoctorRecord]:
        """Main scrape - iterate through all kupot."""
        all_records = []
        
        for insurance_num, kupa_id in self.KAPA_IDS.items():
            self.logger.info(f"Scraping {KUPA_CHOLIM[kupa_id]['name']} (insurance={insurance_num})")
            records = self.scrape_kupa(kupa_id, insurance_num)
            all_records.extend(records)
            self.logger.info(f"Found {len(records)} doctors in {kupa_id}")
        
        self.records = all_records
        return all_records
