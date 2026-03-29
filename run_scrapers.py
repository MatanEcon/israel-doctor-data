"""
Main orchestrator for running all scrapers
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List

sys.path.insert(0, str(Path(__file__).parent))

from src.config import setup_logging, KUPA_CHOLIM, PROCESSED_DATA_DIR, DATA_DIR
from src.scrapers import DoctorIndexScraper, MedReviewsScraper, MaccabiScraper
from src.scrapers.third_party import MedReviewsGraphQLScraper
from src.scrapers.clalit import ClalitScraper
from src.scrapers.leumit_meuhedet import LeumitScraper, MeuhedetScraper
from src.config import DoctorRecord

import pandas as pd


class DoctorScraperOrchestrator:
    """Orchestrates all doctor scrapers and data processing."""
    
    def __init__(self):
        self.logger = setup_logging("orchestrator")
        self.scrapers = {}
        self.all_records: List[DoctorRecord] = []
        self.validation_counts = {}
    
    def initialize_scrapers(self):
        """Initialize all scrapers."""
        self.logger.info("Initializing scrapers...")
        
        self.scrapers = {
            "doctorindex": DoctorIndexScraper(),
            "medreviews": MedReviewsScraper(),
            "medreviews_graphql": MedReviewsGraphQLScraper(),
            "clalit": ClalitScraper(),
            "maccabi": MaccabiScraper(),
            "meuhedet": MeuhedetScraper(),
            "leumit": LeumitScraper()
        }
        
        self.logger.info(f"Initialized {len(self.scrapers)} scrapers")
    
    def run_scraper(self, name: str, scraper) -> int:
        """Run a single scraper and track results."""
        self.logger.info(f"="*50)
        self.logger.info(f"Running scraper: {name}")
        self.logger.info(f"="*50)
        
        try:
            records = scraper.scrape()
            count = len(records)
            self.all_records.extend(records)
            self.validation_counts[name] = count
            self.logger.info(f"Scraper {name} completed: {count} records")
            
            filepath = scraper.save_records(f"{name}_doctors_{datetime.now().strftime('%Y%m%d')}.csv")
            
            return count
            
        except Exception as e:
            self.logger.error(f"Scraper {name} failed: {e}")
            self.validation_counts[name] = 0
            return 0
    
    def run_all_scrapers(self, test_mode: bool = True):
        """Run all scrapers."""
        self.initialize_scrapers()
        
        if test_mode:
            self.logger.info("Running in TEST MODE - limited scraping")
            self._run_test_mode()
        else:
            self.logger.info("Running in FULL MODE")
            self._run_full_mode()
        
        self.process_and_deduplicate()
        self.validate_against_benchmarks()
        self.save_combined_data()
    
    def _run_test_mode(self):
        """Run limited test of scrapers."""
        test_scrapers = ["maccabi"]
        
        for name in test_scrapers:
            if name in self.scrapers:
                self.run_scraper(name, self.scrapers[name])
    
    def _run_full_mode(self):
        """Run all scrapers fully."""
        for name, scraper in self.scrapers.items():
            self.run_scraper(name, scraper)
    
    def process_and_deduplicate(self):
        """Process and deduplicate all collected records."""
        self.logger.info("Processing and deduplicating records...")
        
        if not self.all_records:
            self.logger.warning("No records to process")
            return
        
        df = pd.DataFrame([r.to_dict() for r in self.all_records])
        
        before_count = len(df)
        
        df_dedup = df.drop_duplicates(subset=["name", "specialty", "license_number"])
        
        after_count = len(df_dedup)
        
        self.logger.info(f"Deduplication: {before_count} -> {after_count} records ({before_count - after_count} removed)")
        
        self.combined_df = df_dedup
        
        return df_dedup
    
    def validate_against_benchmarks(self):
        """Validate data against known benchmarks."""
        self.logger.info("Validating against benchmarks...")
        
        if not hasattr(self, 'combined_df') or self.combined_df.empty:
            self.logger.warning("No combined data to validate")
            return
        
        df = self.combined_df
        
        benchmarks = {
            "clalit": {"estimate": 13000, "description": "Clalit doctors estimate"},
            "maccabi": {"estimate": 9000, "description": "Maccabi doctors estimate"},
            "meuhedet": {"estimate": 4000, "description": "Meuhedet doctors estimate"},
            "leumit": {"estimate": 3000, "description": "Leumit doctors estimate"}
        }
        
        for kupa_id, benchmark in benchmarks.items():
            if kupa_id in df.columns:
                count = df[kupa_id].sum()
                expected = benchmark["estimate"]
                self.logger.info(
                    f"{KUPA_CHOLIM[kupa_id]['name']}: {count} scraped "
                    f"(expected ~{expected}, diff: {count - expected:+d})"
                )
                
                if count < expected * 0.5:
                    self.logger.warning(
                        f"{kupa_id}: Low count detected - may be missing data!"
                    )
    
    def save_combined_data(self, year: int = None):
        """Save combined and processed data."""
        if not hasattr(self, 'combined_df') or self.combined_df.empty:
            self.logger.warning("No data to save")
            return
        
        if year is None:
            year = datetime.now().year
        
        filename = f"all_doctors_{year}.csv"
        filepath = PROCESSED_DATA_DIR / filename
        
        df = self.combined_df.copy()
        df["year"] = year
        
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        self.logger.info(f"Saved combined data to {filepath}")
        
        for kupa in KUPA_CHOLIM.keys():
            if kupa in df.columns:
                kupa_count = df[df[kupa] == 1].shape[0]
                self.logger.info(f"Total {kupa}: {kupa_count} unique doctors")
        
        return filepath
    
    def generate_summary_report(self):
        """Generate summary report of scraping results."""
        report = []
        report.append("="*60)
        report.append("DOCTOR SCRAPING SUMMARY REPORT")
        report.append("="*60)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        report.append("Scraper Results:")
        for name, count in self.validation_counts.items():
            report.append(f"  {name}: {count} records")
        
        report.append("")
        report.append("Combined Data:")
        if hasattr(self, 'combined_df') and not self.combined_df.empty:
            df = self.combined_df
            report.append(f"  Total unique doctors: {len(df)}")
            
            for kupa in KUPA_CHOLIM.keys():
                if kupa in df.columns:
                    count = df[df[kupa] == 1].shape[0]
                    report.append(f"  {KUPA_CHOLIM[kupa]['name']}: {count}")
        
        report.append("")
        report.append("="*60)
        
        report_text = "\n".join(report)
        self.logger.info(report_text)
        
        report_file = DATA_DIR / f"scraping_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_text)
        
        return report_text


def main():
    """Main entry point."""
    orchestrator = DoctorScraperOrchestrator()
    
    test_mode = "--test" in sys.argv or "-t" in sys.argv
    
    orchestrator.run_all_scrapers(test_mode=test_mode)
    orchestrator.generate_summary_report()
    
    print("\nScraping complete! Check the logs and data directories for results.")


if __name__ == "__main__":
    main()
