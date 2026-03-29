"""
Scraper for DoctorIndex - Comprehensive Israeli Doctor Database
https://doctorindex.co.il/
"""

import re
from typing import List, Optional, Dict

from .base_scraper import BaseScraper, ThirdPartyAggregator
from .config import DoctorRecord, KUPA_CHOLIM


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
