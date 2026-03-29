"""
Base scraper class for Kupot Cholim doctor scraping
"""

import time
import random
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path
import json

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import (
    setup_logging, DoctorRecord, DATA_DIR, KUPA_CHOLIM,
    RAW_DATA_DIR, PROCESSED_DATA_DIR
)


class BaseScraper(ABC):
    """Base class for all Kupat Cholim scrapers."""
    
    def __init__(self, kupa_id: str, delay_range: tuple = (1, 3)):
        self.kupa_id = kupa_id
        self.kupa_info = KUPA_CHOLIM.get(kupa_id, {})
        self.name = self.kupa_info.get("name", kupa_id)
        self.logger = setup_logging(f"{kupa_id}_scraper")
        self.delay_range = delay_range
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })
        self.records: List[DoctorRecord] = []
    
    def _random_delay(self):
        """Add random delay between requests."""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, TimeoutError))
    )
    def _make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with retry logic."""
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.warning(f"Request failed: {url} - {e}")
            raise
    
    def _parse_html(self, content: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(content, "lxml")
    
    @abstractmethod
    def scrape(self) -> List[DoctorRecord]:
        """Main scraping method - must be implemented by subclasses."""
        pass
    
    def save_records(self, filename: Optional[str] = None):
        """Save scraped records to CSV."""
        if not self.records:
            self.logger.warning("No records to save")
            return
        
        if filename is None:
            filename = f"{self.kupa_id}_doctors_{pd.Timestamp.now().strftime('%Y%m%d')}.csv"
        
        filepath = RAW_DATA_DIR / filename
        df = pd.DataFrame([r.to_dict() for r in self.records])
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        self.logger.info(f"Saved {len(self.records)} records to {filepath}")
        return filepath
    
    def get_existing_records(self, filename: str) -> pd.DataFrame:
        """Load existing records from file."""
        filepath = RAW_DATA_DIR / filename
        if filepath.exists():
            return pd.read_csv(filepath)
        return pd.DataFrame()
    
    def add_kupa_indicator(self, record: DoctorRecord):
        """Add kupa indicator to record."""
        setattr(record, self.kupa_id, 1)


class ThirdPartyAggregator(BaseScraper):
    """Scraper for third-party doctor aggregator sites."""
    
    def __init__(self, site_name: str, base_url: str):
        super().__init__(site_name)
        self.site_name = site_name
        self.base_url = base_url
    
    @abstractmethod
    def parse_doctor_listing(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse doctor listings from page."""
        pass
    
    @abstractmethod
    def get_total_pages(self, soup: BeautifulSoup) -> int:
        """Get total number of pages."""
        pass


class MinistryHealthRegistry(BaseScraper):
    """Scraper for Ministry of Health doctor registry."""
    
    def __init__(self):
        super().__init__("ministry_health")
        self.base_url = "https://practitioners.health.gov.il"
        self.registry_url = f"{self.base_url}/Practitioners/8"
    
    def scrape(self) -> List[DoctorRecord]:
        """Scrape the Ministry of Health practitioner registry."""
        self.logger.info("Starting Ministry of Health registry scrape")
        return []  # Placeholder - needs implementation based on actual API structure
