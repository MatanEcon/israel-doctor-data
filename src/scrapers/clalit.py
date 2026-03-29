"""
Scraper for Clalit Health Services
https://www.clalit.co.il/
"""

import re
from typing import List, Optional, Dict

from ..base_scraper import BaseScraper
from ..config import DoctorRecord, KUPA_CHOLIM


class ClalitScraper(BaseScraper):
    """Scraper for Clalit Health Services doctor search."""
    
    def __init__(self):
        super().__init__("clalit")
        self.base_url = "https://www.clalit.co.il"
        self.search_url = f"{self.base_url}/he/findingadoctor"
        self.logger.info("Initialized Clalit scraper")
    
    def parse_search_results(self, soup) -> List[Dict]:
        """Parse doctor search results from Clalit."""
        doctors = []
        
        cards = soup.select(
            ".doctor-card, .doctor-item, .result-item, "
            "[class*='doctor'], [class*='physician']"
        )
        
        for card in cards:
            doctor = {}
            
            name_elem = card.select_one(
                "h2, h3, h4, .doctor-name, .name, [class*='name']"
            )
            if name_elem:
                doctor["name"] = name_elem.get_text(strip=True)
            
            specialty_elem = card.select_one(
                ".specialty, [class*='special'], .profession"
            )
            if specialty_elem:
                doctor["specialty"] = specialty_elem.get_text(strip=True)
            
            address_elem = card.select_one(
                ".address, .location, [class*='address'], [class*='location']"
            )
            if address_elem:
                doctor["address"] = address_elem.get_text(strip=True)
            
            phone_elem = card.select_one(
                "a[href^='tel:'], .phone, [class*='phone']"
            )
            if phone_elem:
                href = phone_elem.get("href", "")
                doctor["phone"] = href.replace("tel:", "") if href else phone_elem.get_text(strip=True)
            
            gender_elem = card.select_one("[class*='gender'], .gender-icon")
            if gender_elem:
                text = gender_elem.get_text(strip=True).lower()
                if "נקבה" in text or "female" in text:
                    doctor["gender"] = "F"
                elif "זכר" in text or "male" in text:
                    doctor["gender"] = "M"
            
            doctors.append(doctor)
        
        return doctors
    
    def get_pagination_info(self, soup) -> Dict:
        """Extract pagination information."""
        pagination = soup.select(".pagination a, .pager a, [class*='page']")
        
        pages = []
        for link in pagination:
            text = link.get_text(strip=True)
            if text.isdigit():
                pages.append(int(text))
        
        return {
            "total_pages": max(pages) if pages else 1,
            "current_page": 1
        }
    
    def search_by_specialty(self, specialty: str, max_pages: int = 20) -> List[DoctorRecord]:
        """Search for doctors by specialty."""
        records = []
        
        for page in range(1, max_pages + 1):
            params = {"specialty": specialty, "page": page}
            
            try:
                response = self._make_request(self.search_url, params=params)
                if not response:
                    break
                
                soup = self._parse_html(response.text)
                doctors = self.parse_search_results(soup)
                
                if not doctors:
                    break
                
                for doc_data in doctors:
                    if not doc_data.get("name"):
                        continue
                    
                    record = DoctorRecord(
                        name=doc_data["name"],
                        specialty=doc_data.get("specialty"),
                        gender=doc_data.get("gender"),
                        phone=doc_data.get("phone"),
                        clinic_address=doc_data.get("address"),
                        clalit=1,
                        source_url=self.search_url,
                        source_name="Clalit"
                    )
                    records.append(record)
                
                pagination = self.get_pagination_info(soup)
                if page >= pagination["total_pages"]:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error on page {page}: {e}")
                break
            finally:
                self._random_delay()
        
        return records
    
    def search_by_city(self, city: str, max_pages: int = 20) -> List[DoctorRecord]:
        """Search for doctors by city."""
        records = []
        
        for page in range(1, max_pages + 1):
            params = {"city": city, "page": page}
            
            try:
                response = self._make_request(self.search_url, params=params)
                if not response:
                    break
                
                soup = self._parse_html(response.text)
                doctors = self.parse_search_results(soup)
                
                if not doctors:
                    break
                
                for doc_data in doctors:
                    if not doc_data.get("name"):
                        continue
                    
                    record = DoctorRecord(
                        name=doc_data["name"],
                        specialty=doc_data.get("specialty"),
                        gender=doc_data.get("gender"),
                        phone=doc_data.get("phone"),
                        clinic_address=doc_data.get("address"),
                        clalit=1,
                        source_url=self.search_url,
                        source_name="Clalit"
                    )
                    records.append(record)
                
            except Exception as e:
                self.logger.error(f"Error on page {page}: {e}")
                break
            finally:
                self._random_delay()
        
        return records
    
    def scrape(self) -> List[DoctorRecord]:
        """Main scrape method - scrape all specialties."""
        specialties = [
            "רפואת משפחה", "פנימית", "ילדים", "נשים", "אורתופדיה",
            "כללי", "עיניים", "אף אוזן גרון", "עור", "לב",
            "מוח", "סרטן", "פסיכיאטריה", "ניתוחים", "רדיולוגיה",
            "הרדמה", "שיקום", "גסטרואנטרולוגיה", "אורולוגיה", "ריאות"
        ]
        
        all_records = []
        
        for specialty in specialties:
            self.logger.info(f"Scraping specialty: {specialty}")
            records = self.search_by_specialty(specialty)
            all_records.extend(records)
            self.logger.info(f"Found {len(records)} doctors for {specialty}")
        
        self.records = all_records
        return all_records
