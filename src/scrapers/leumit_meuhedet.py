"""
Scrapers for Leumit and Meuhedet Health Services
"""

import re
from typing import List, Optional, Dict

from ..base_scraper import BaseScraper
from ..config import DoctorRecord, KUPA_CHOLIM


class LeumitScraper(BaseScraper):
    """Scraper for Leumit Health Services doctor search."""
    
    def __init__(self):
        super().__init__("leumit")
        self.base_url = "https://www.leumit.co.il"
        self.search_url = f"{self.base_url}/heb/doctorssearch"
        self.api_url = f"{self.base_url}/API/Doctors"
        self.logger.info("Initialized Leumit scraper")
    
    def parse_doctor_card(self, card) -> Optional[Dict]:
        """Parse a single doctor card from Leumit."""
        doctor = {}
        
        name_elem = card.select_one("h3, h4, .doctor-name, [class*='name']")
        if name_elem:
            doctor["name"] = name_elem.get_text(strip=True)
        
        specialty_elem = card.select_one(".specialty, [class*='special']")
        if specialty_elem:
            doctor["specialty"] = specialty_elem.get_text(strip=True)
        
        address_elem = card.select_one(".address, .clinic-address")
        if address_elem:
            doctor["address"] = address_elem.get_text(strip=True)
        
        phone_elem = card.select_one("a[href^='tel:'], .phone")
        if phone_elem:
            href = phone_elem.get("href", "")
            doctor["phone"] = href.replace("tel:", "") if href else phone_elem.get_text(strip=True)
        
        return doctor if doctor.get("name") else None
    
    def parse_search_results(self, soup) -> List[Dict]:
        """Parse search results page."""
        doctors = []
        cards = soup.select(".doctor-card, .doctor-item, .result-item, article")
        
        for card in cards:
            doctor = self.parse_doctor_card(card)
            if doctor:
                doctors.append(doctor)
        
        return doctors
    
    def get_pagination(self, soup) -> int:
        """Get total pages from pagination."""
        pagination = soup.select(".pagination a, .pager a")
        pages = []
        for link in pagination:
            text = link.get_text(strip=True)
            if text.isdigit():
                pages.append(int(text))
        return max(pages) if pages else 1
    
    def search(self, params: Dict, max_pages: int = 20) -> List[DoctorRecord]:
        """Generic search with parameters."""
        records = []
        
        for page in range(1, max_pages + 1):
            params["page"] = page
            
            try:
                response = self._make_request(self.search_url, params=params)
                if not response:
                    break
                
                soup = self._parse_html(response.text)
                doctors = self.parse_search_results(soup)
                
                if not doctors:
                    break
                
                for doc_data in doctors:
                    record = DoctorRecord(
                        name=doc_data.get("name", ""),
                        specialty=doc_data.get("specialty"),
                        phone=doc_data.get("phone"),
                        clinic_address=doc_data.get("address"),
                        leumit=1,
                        source_url=self.search_url,
                        source_name="Leumit"
                    )
                    records.append(record)
                
                total_pages = self.get_pagination(soup)
                if page >= total_pages:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error on page {page}: {e}")
                break
            finally:
                self._random_delay()
        
        return records
    
    def scrape_by_specialty(self, specialty: str) -> List[DoctorRecord]:
        """Scrape doctors by specialty."""
        return self.search({"specialty": specialty})
    
    def scrape_by_city(self, city: str) -> List[DoctorRecord]:
        """Scrape doctors by city."""
        return self.search({"city": city})
    
    def scrape(self) -> List[DoctorRecord]:
        """Main scrape - iterate through specialties."""
        specialties = [
            "רפואת משפחה", "פנימית", "ילדים", "נשים", "אורתופדיה",
            "כללי", "עיניים", "אף אוזן גרון", "עור", "לב",
            "מוח", "סרטן", "פסיכיאטריה", "ניתוחים"
        ]
        
        all_records = []
        
        for specialty in specialties:
            self.logger.info(f"Scraping specialty: {specialty}")
            records = self.scrape_by_specialty(specialty)
            all_records.extend(records)
            self.logger.info(f"Found {len(records)} doctors for {specialty}")
        
        self.records = all_records
        return all_records


class MeuhedetScraper(BaseScraper):
    """Scraper for Meuhedet Health Services doctor search."""
    
    def __init__(self):
        super().__init__("meuhedet")
        self.base_url = "https://www.meuhedet.co.il"
        self.search_url = f"{self.base_url}/heb/Doctors"
        self.logger.info("Initialized Meuhedet scraper")
    
    def parse_doctor_card(self, card) -> Optional[Dict]:
        """Parse a single doctor card."""
        doctor = {}
        
        name_elem = card.select_one("h3, h4, .doctor-name, [class*='name']")
        if name_elem:
            doctor["name"] = name_elem.get_text(strip=True)
        
        specialty_elem = card.select_one(".specialty, [class*='special']")
        if specialty_elem:
            doctor["specialty"] = specialty_elem.get_text(strip=True)
        
        address_elem = card.select_one(".address, .clinic-address")
        if address_elem:
            doctor["address"] = address_elem.get_text(strip=True)
        
        phone_elem = card.select_one("a[href^='tel:'], .phone")
        if phone_elem:
            href = phone_elem.get("href", "")
            doctor["phone"] = href.replace("tel:", "") if href else phone_elem.get_text(strip=True)
        
        return doctor if doctor.get("name") else None
    
    def parse_search_results(self, soup) -> List[Dict]:
        """Parse search results page."""
        doctors = []
        cards = soup.select(".doctor-card, .doctor-item, .result-item, article")
        
        for card in cards:
            doctor = self.parse_doctor_card(card)
            if doctor:
                doctors.append(doctor)
        
        return doctors
    
    def get_pagination(self, soup) -> int:
        """Get total pages."""
        pagination = soup.select(".pagination a, .pager a")
        pages = []
        for link in pagination:
            text = link.get_text(strip=True)
            if text.isdigit():
                pages.append(int(text))
        return max(pages) if pages else 1
    
    def search(self, params: Dict, max_pages: int = 20) -> List[DoctorRecord]:
        """Generic search."""
        records = []
        
        for page in range(1, max_pages + 1):
            params["page"] = page
            
            try:
                response = self._make_request(self.search_url, params=params)
                if not response:
                    break
                
                soup = self._parse_html(response.text)
                doctors = self.parse_search_results(soup)
                
                if not doctors:
                    break
                
                for doc_data in doctors:
                    record = DoctorRecord(
                        name=doc_data.get("name", ""),
                        specialty=doc_data.get("specialty"),
                        phone=doc_data.get("phone"),
                        clinic_address=doc_data.get("address"),
                        meuhedet=1,
                        source_url=self.search_url,
                        source_name="Meuhedet"
                    )
                    records.append(record)
                
                total_pages = self.get_pagination(soup)
                if page >= total_pages:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error on page {page}: {e}")
                break
            finally:
                self._random_delay()
        
        return records
    
    def scrape_by_specialty(self, specialty: str) -> List[DoctorRecord]:
        """Scrape by specialty."""
        return self.search({"specialty": specialty})
    
    def scrape_by_city(self, city: str) -> List[DoctorRecord]:
        """Scrape by city."""
        return self.search({"city": city})
    
    def scrape(self) -> List[DoctorRecord]:
        """Main scrape."""
        specialties = [
            "רפואת משפחה", "פנימית", "ילדים", "נשים", "אורתופדיה",
            "כללי", "עיניים", "אף אוזן גרון", "עור", "לב",
            "מוח", "סרטן", "פסיכיאטריה", "ניתוחים"
        ]
        
        all_records = []
        
        for specialty in specialties:
            self.logger.info(f"Scraping specialty: {specialty}")
            records = self.scrape_by_specialty(specialty)
            all_records.extend(records)
            self.logger.info(f"Found {len(records)} doctors for {specialty}")
        
        self.records = all_records
        return all_records
