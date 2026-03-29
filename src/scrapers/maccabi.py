"""
Scraper for Maccabi Healthcare Services
https://www.maccabi4u.co.il/
"""

import re
from typing import List, Optional, Dict
from urllib.parse import urlencode

from ..base_scraper import BaseScraper
from ..config import DoctorRecord, KUPA_CHOLIM


class MaccabiScraper(BaseScraper):
    """Scraper for Maccabi Health Services doctor search."""
    
    def __init__(self):
        super().__init__("maccabi")
        self.api_base = "https://sereotype.maccabi4u.co.il"
        self.search_endpoint = f"{self.api_base}/heb/doctors/doctorssearchresults/"
        self.cities_endpoint = f"{self.api_base}/api/locations/cities"
        self.specialties = self._get_specialties()
        self.logger.info(f"Initialized Maccabi scraper with {len(self.specialties)} specialties")
    
    def _get_specialties(self) -> Dict[str, str]:
        """Get specialty codes from Maccabi."""
        return {
            "006": "אורתופדיה",
            "001": "כללי",
            "002": "ילדים",
            "003": "נשים",
            "004": "עיניים",
            "005": "אף אוזן גרון",
            "007": "עור",
            "008": "לב",
            "009": "מוח",
            "010": "פנימית",
            "011": "ניתוחים",
            "012": "סרטן",
            "013": "פסיכיאטריה",
            "014": "רדיולוגיה",
            "015": "הרדמה",
            "016": "שיקום",
            "017": "גסטרואנטרולוגיה",
            "018": "אורולוגיה",
            "019": "ריאות",
            "020": "אנדוקרינולוגיה",
            "021": "נפרולוגיה",
            "022": "זיהומים",
            "023": "ראומטולוגיה",
            "024": "המטולוגיה",
            "025": "אלרגיה",
            "026": "גריאטריה",
            "027": "רפואת משפחה",
            "028": "רפואת חירום",
            "029": "פתולוגיה",
            "030": "נוירו-כירורגיה",
            "031": "פלסטיקה",
        }
    
    def get_cities(self) -> Dict[str, str]:
        """Get list of cities with their IDs."""
        try:
            response = self._make_request(self.cities_endpoint)
            if response and response.status_code == 200:
                return response.json()
        except Exception as e:
            self.logger.warning(f"Could not fetch cities: {e}")
        return {}
    
    def search_doctors(
        self,
        city: Optional[str] = None,
        specialty: Optional[str] = None,
        gender: Optional[str] = None,
        page: int = 1
    ) -> List[Dict]:
        """Search for doctors with given parameters."""
        params = {
            "PageNumber": page,
            "HideHeader": "true",
            "ismobileapplication": "1",
            "os": "2"
        }
        
        if city:
            params["City"] = city
        if specialty:
            params["Field"] = specialty
        if gender:
            params["Gender"] = "1" if gender == "F" else "2"
        
        try:
            response = self._make_request(self.search_endpoint, params=params)
            if not response:
                return []
            
            data = response.json()
            return data.get("Doctors", [])
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return []
    
    def parse_doctor(self, doctor_data: Dict) -> Optional[DoctorRecord]:
        """Parse doctor data into DoctorRecord."""
        name = doctor_data.get("DoctorName", "")
        if not name:
            return None
        
        full_name = name
        first_name = doctor_data.get("FirstName", "")
        last_name = doctor_data.get("LastName", "")
        if first_name and last_name:
            full_name = f"{last_name} {first_name}"
        
        return DoctorRecord(
            name=full_name,
            specialty=doctor_data.get("FieldName"),
            gender="F" if doctor_data.get("Gender") == 1 else "M",
            phone=doctor_data.get("Phone"),
            clinic_address=doctor_data.get("Address"),
            license_number=doctor_data.get("LicenseNumber"),
            maccabi=1,
            source_url=self.search_endpoint,
            source_name="Maccabi"
        )
    
    def scrape_by_specialty(self, specialty_code: str, max_pages: int = 20) -> List[DoctorRecord]:
        """Scrape all doctors for a specific specialty."""
        records = []
        
        for page in range(1, max_pages + 1):
            doctors = self.search_doctors(specialty=specialty_code, page=page)
            
            if not doctors:
                break
            
            for doc in doctors:
                record = self.parse_doctor(doc)
                if record:
                    records.append(record)
            
            self.logger.debug(f"Page {page}: found {len(doctors)} doctors")
            self._random_delay()
        
        return records
    
    def scrape_by_city(self, city_code: str, max_pages: int = 20) -> List[DoctorRecord]:
        """Scrape all doctors for a specific city."""
        records = []
        
        for page in range(1, max_pages + 1):
            doctors = self.search_doctors(city=city_code, page=page)
            
            if not doctors:
                break
            
            for doc in doctors:
                record = self.parse_doctor(doc)
                if record:
                    records.append(record)
            
            self._random_delay()
        
        return records
    
    def scrape(self) -> List[DoctorRecord]:
        """Main scrape - iterate through all specialties."""
        all_records = []
        
        for code, name in self.specialties.items():
            self.logger.info(f"Scraping specialty: {name} ({code})")
            records = self.scrape_by_specialty(code)
            all_records.extend(records)
            self.logger.info(f"Found {len(records)} doctors for {name}")
        
        self.records = all_records
        return all_records


class MaccabiSilfenScraper(MaccabiScraper):
    """Scraper for Maccabi's self-employed (atzmai) doctors listing."""
    
    def __init__(self):
        super().__init__()
        self.kupa_id = "maccabi_silfen"
        self.logger = setup_logging(f"{self.kupa_id}_scraper")
        self.logger.info("Initialized Maccabi Atzmai scraper")
    
    def scrape(self) -> List[DoctorRecord]:
        """Scrape doctors listed as self-employed."""
        return []  # Placeholder - would need specific endpoint for silfen doctors


def setup_logging(name: str):
    """Setup logging for this module."""
    import logging
    from pathlib import Path
    from datetime import datetime
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    if logger.handlers:
        return logger
    
    LOG_DIR = Path(__file__).parent.parent.parent / "logs"
    LOG_DIR.mkdir(exist_ok=True)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    log_file = LOG_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
