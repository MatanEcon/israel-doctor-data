"""
Scraper for Ministry of Health doctor licenses database via data.gov.il API
"""

import time
from typing import List, Dict, Optional
from datetime import datetime

from src.base_scraper import BaseScraper
from src.config import DoctorRecord, KUPA_CHOLIM


class MOHLicenseScraper(BaseScraper):
    """Scraper for Ministry of Health doctor licenses via data.gov.il API."""
    
    API_URL = "https://data.gov.il/api/3/action/datastore_search"
    BATCH_SIZE = 1000
    MAX_RECORDS = 100000
    
    def __init__(self):
        super().__init__("moh_licenses")
        self.base_url = "https://practitioners.health.gov.il"
        self.logger.info("Initialized MOH License scraper")
    
    def fetch_batch(self, offset: int = 0, limit: int = 1000) -> Dict:
        """Fetch a batch of records from the API."""
        params = {
            "resource_id": "9c64c522-bbc2-48fe-96fb-3b2a8626f59e",
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = self._make_request(self.API_URL, params=params)
            if response and response.status_code == 200:
                return response.json()
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
        
        return {"success": False, "result": {}}
    
    def parse_record(self, record: Dict) -> Optional[DoctorRecord]:
        """Parse an API record into a DoctorRecord."""
        first_name = record.get("שם פרטי", "")
        last_name = record.get("שם משפחה", "")
        name = f"{last_name} {first_name}".strip()
        
        if not name:
            return None
        
        return DoctorRecord(
            name=name,
            license_number=str(record.get("מספר רישיון רופא", "")),
            specialty=record.get("שם התמחות"),
            license_date=str(record.get("תאריך רישום רישיון", "")),
            specialty_registration_date=str(record.get("תאריך רישום התמחות", "")),
            source_url="https://data.gov.il/dataset/2721d62d-d0da-45fd-93ac-5e7809849222",
            source_name="MOH_Licenses"
        )
    
    def scrape(self, max_records: int = None) -> List[DoctorRecord]:
        """Scrape all doctor licenses from the MOH database."""
        if max_records is None:
            max_records = self.MAX_RECORDS
        
        all_records = []
        offset = 0
        total_estimate = 0
        
        while offset < max_records:
            self.logger.info(f"Fetching records {offset} to {offset + self.BATCH_SIZE}")
            
            result = self.fetch_batch(offset=offset, limit=self.BATCH_SIZE)
            
            if not result.get("success"):
                self.logger.error("API request failed")
                break
            
            data = result.get("result", {})
            
            if total_estimate == 0:
                total_estimate = data.get("total", 0)
                self.logger.info(f"Total records in database: {total_estimate}")
            
            records = data.get("records", [])
            
            if not records:
                break
            
            for rec in records:
                doctor = self.parse_record(rec)
                if doctor:
                    all_records.append(doctor)
            
            offset += self.BATCH_SIZE
            
            if len(records) < self.BATCH_SIZE:
                break
            
            self._random_delay()
        
        self.records = all_records
        self.logger.info(f"Scraped {len(all_records)} doctor records")
        return all_records


def scrape_moh_licenses(output_file: str = None) -> List[DoctorRecord]:
    """Main function to scrape MOH license data."""
    scraper = MOHLicenseScraper()
    records = scraper.scrape()
    
    if records and output_file:
        scraper.save_records(output_file)
    
    return records


if __name__ == "__main__":
    records = scrape_moh_licenses("moh_doctors.csv")
    print(f"Scraped {len(records)} doctor records from MOH database")
