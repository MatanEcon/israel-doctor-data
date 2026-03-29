"""
Wayback Machine archival scraper for historical doctor data
"""

import json
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlencode

from ..base_scraper import BaseScraper
from ..config import DoctorRecord, KUPA_CHOLIM


class WaybackMachineScraper(BaseScraper):
    """Scraper for archived versions via Wayback Machine."""
    
    BASE_URL = "https://web.archive.org"
    
    def __init__(self):
        super().__init__("wayback")
        self.availability_url = f"{self.BASE_URL}/wayback/available"
        self.web_url = f"{self.BASE_URL}/web"
        self.logger.info("Initialized Wayback Machine scraper")
    
    def check_availability(self, url: str) -> Optional[Dict]:
        """Check if a URL is archived."""
        params = {"url": url}
        try:
            response = self._make_request(
                self.availability_url,
                params=params
            )
            if response:
                return response.json()
        except Exception as e:
            self.logger.warning(f"Wayback availability check failed: {e}")
        return None
    
    def get_closest_snapshot(self, url: str, year: int = None) -> Optional[str]:
        """Get the closest snapshot to a given year."""
        timestamp = f"{year}0101" if year else "*"
        archive_url = f"{self.web_url}/{timestamp}/{url}"
        
        try:
            response = self._make_request(archive_url, timeout=60)
            if response and response.status_code == 200:
                return archive_url
        except Exception as e:
            self.logger.warning(f"No snapshot found for {year}: {e}")
        return None
    
    def get_cdx_api_snapshots(self, url: str, from_year: int = None, 
                              to_year: int = None) -> List[Dict]:
        """Use CDX API to get all snapshots of a URL."""
        cdx_url = f"{self.BASE_URL}/cdx/search/cdx"
        params = {
            "url": url,
            "output": "json",
            "fl": "timestamp,statuscode,original"
        }
        
        if from_year:
            params["from"] = f"{from_year}0101"
        if to_year:
            params["to"] = f"{to_year}1231"
        
        try:
            response = self._make_request(cdx_url, params=params)
            if response and response.text:
                lines = response.text.strip().split('\n')
                snapshots = []
                for line in lines[1:]:
                    parts = line.split(' ')
                    if len(parts) >= 3:
                        snapshots.append({
                            "timestamp": parts[0],
                            "status": parts[1],
                            "url": parts[2]
                        })
                return snapshots
        except Exception as e:
            self.logger.error(f"CDX API error: {e}")
        return []
    
    def scrape_archived_page(self, url: str, timestamp: str = None) -> Optional[str]:
        """Scrape an archived version of a page."""
        if timestamp:
            archive_url = f"{self.web_url}/{timestamp}/{url}"
        else:
            archive_url = f"{self.web_url}/*/{url}"
        
        try:
            response = self._make_request(archive_url)
            if response and response.status_code == 200:
                return response.text
        except Exception as e:
            self.logger.warning(f"Archive scraping failed: {e}")
        return None
    
    def scrape(self) -> List[DoctorRecord]:
        """Main scrape - not applicable for Wayback."""
        self.logger.info("Use specific methods to scrape archived pages")
        return []


class DoctorIndexWaybackScraper(WaybackMachineScraper):
    """Scraper for DoctorIndex archived pages."""
    
    BASE_DOMAIN = "doctorindex.co.il"
    
    def __init__(self):
        super().__init__()
        self.base_url = f"https://{self.BASE_DOMAIN}"
        self.logger.info("Initialized DoctorIndex Wayback scraper")
    
    def get_specialty_pages(self) -> List[str]:
        """Get all specialty pages from archived version."""
        return [
            "רופאים-מומחים-רפואת-המשפחה",
            "רופאים-מומחים-פנימית",
            "רופאים-מומחים-ילדים",
            "רופאים-מומחים-נשים",
            "רופאים-מומחים-אורתופדיה",
            "רופאים-מומחים-כירורגיה",
            "רופאים-מומחים-עיניים",
            "רופאים-מומחים-לב",
            "רופאים-מומחים-עור",
            "רופאים-מומחים-סרטן",
        ]
    
    def scrape_archived_doctorindex(self, year: int = 2023) -> List[DoctorRecord]:
        """Scrape DoctorIndex from a specific year."""
        self.logger.info(f"Scraping DoctorIndex archives from {year}")
        
        snapshots = self.get_cdx_api_snapshots(
            self.BASE_DOMAIN,
            from_year=year,
            to_year=year
        )
        
        self.logger.info(f"Found {len(snapshots)} snapshots for {year}")
        return []
    
    def scrape(self) -> List[DoctorRecord]:
        """Main scrape."""
        return self.scrape_archived_doctorindex()


class MaccabiWaybackScraper(WaybackMachineScraper):
    """Scraper for Maccabi archived pages."""
    
    BASE_DOMAIN = "maccabi4u.co.il"
    
    def __init__(self):
        super().__init__()
        self.base_url = f"https://{self.BASE_DOMAIN}"
        self.logger.info("Initialized Maccabi Wayback scraper")
    
    def scrape_archived_maccabi(self, year: int = 2023) -> List[DoctorRecord]:
        """Scrape Maccabi doctor pages from a specific year."""
        self.logger.info(f"Scraping Maccabi archives from {year}")
        
        snapshots = self.get_cdx_api_snapshots(
            f"{self.BASE_DOMAIN}/heb/doctors/*",
            from_year=year,
            to_year=year
        )
        
        self.logger.info(f"Found {len(snapshots)} snapshots for {year}")
        
        records = []
        for snap in snapshots[:50]:
            content = self.scrape_archived_page(
                snap["url"].replace("https://", ""),
                snap["timestamp"]
            )
            if content:
                self._parse_maccabi_content(content, records)
        
        return records
    
    def _parse_maccabi_content(self, content: str, records: List):
        """Parse Maccabi archived page content."""
        pass
    
    def scrape(self) -> List[DoctorRecord]:
        """Main scrape."""
        return self.scrape_archived_maccabi()
