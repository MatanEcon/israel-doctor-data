"""
Simple test script to verify scraping works
Run with: python test_scraper.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import setup_logging
from src.scrapers.maccabi import MaccabiScraper


def test_maccabi_scraper():
    """Test the Maccabi scraper with minimal parameters."""
    logger = setup_logging("test_maccabi")
    logger.info("Starting Maccabi scraper test")
    
    scraper = MaccabiScraper()
    
    logger.info(f"Maccabi specialties: {list(scraper.specialties.items())[:5]}...")
    
    try:
        records = scraper.scrape_by_specialty("001", max_pages=2)
        logger.info(f"Test completed: found {len(records)} doctors")
        
        for record in records[:5]:
            print(f"  - {record.name}: {record.specialty}")
        
        return len(records) > 0
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_maccabi_scraper()
    sys.exit(0 if success else 1)
