"""
Data validation and benchmarking script
Compares scraped data against official reports and statistics
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.config import KUPA_CHOLIM, setup_logging


@dataclass
class Benchmark:
    """Benchmark data for validation."""
    name: str
    year: int
    source: str
    total_physicians: int
    by_kupa: Dict[str, int]
    by_specialty: Dict[str, int]
    notes: str = ""


VALIDATION_BENCHMARKS = {
    2021: Benchmark(
        name="Ministry of Health 2021",
        year=2021,
        source="Ministry of Health Health Workforce Report 2021",
        total_physicians=38247,
        by_kupa={
            "clalit": 13000,
            "maccabi": 9000,
            "meuhedet": 4000,
            "leumit": 3000
        },
        by_specialty={
            "family_medicine": 6000,
            "internal_medicine": 4500,
            "pediatrics": 3500,
            "surgery": 2500
        },
        notes="Approximate figures from annual report"
    ),
    2022: Benchmark(
        name="Ministry of Health 2022",
        year=2022,
        source="Ministry of Health Health Workforce Report 2022",
        total_physicians=39000,
        by_kupa={
            "clalit": 13500,
            "maccabi": 9200,
            "meuhedet": 4200,
            "leumit": 3100
        },
        by_specialty={
            "family_medicine": 6200,
            "internal_medicine": 4600,
            "pediatrics": 3600,
            "surgery": 2600
        }
    ),
    2023: Benchmark(
        name="Ministry of Health 2023",
        year=2023,
        source="Ministry of Health Health Workforce Report 2023",
        total_physicians=40000,
        by_kupa={
            "clalit": 14000,
            "maccabi": 9500,
            "meuhedet": 4400,
            "leumit": 3200
        },
        by_specialty={
            "family_medicine": 6400,
            "internal_medicine": 4700,
            "pediatrics": 3700,
            "surgery": 2700
        }
    )
}


class DataValidator:
    """Validates scraped data against benchmarks."""
    
    def __init__(self, data_dir: Path = None):
        self.logger = setup_logging("validator")
        self.data_dir = data_dir or (Path(__file__).parent.parent / "data" / "processed")
        self.validation_results = []
    
    def load_scraped_data(self, year: int) -> Optional[pd.DataFrame]:
        """Load scraped data for a given year."""
        filepath = self.data_dir / f"all_doctors_{year}.csv"
        
        if not filepath.exists():
            self.logger.warning(f"No data file found for {year}: {filepath}")
            return None
        
        df = pd.read_csv(filepath, encoding="utf-8-sig")
        self.logger.info(f"Loaded {len(df)} records from {filepath}")
        return df
    
    def validate_counts(self, df: pd.DataFrame, year: int) -> Dict:
        """Validate doctor counts against benchmarks."""
        if year not in VALIDATION_BENCHMARKS:
            self.logger.warning(f"No benchmark for year {year}")
            return {}
        
        benchmark = VALIDATION_BENCHMARKS[year]
        
        results = {
            "year": year,
            "benchmark_source": benchmark.source,
            "total_physicians": {
                "scraped": len(df),
                "expected": benchmark.total_physicians,
                "coverage": len(df) / benchmark.total_physicians * 100 if benchmark.total_physicians else 0
            },
            "by_kupa": {},
            "completeness": "unknown"
        }
        
        for kupa_id, expected in benchmark.by_kupa.items():
            if kupa_id in df.columns:
                scraped = df[kupa_id].sum()
                coverage = scraped / expected * 100 if expected else 0
                results["by_kupa"][kupa_id] = {
                    "scraped": int(scraped),
                    "expected": expected,
                    "coverage_pct": round(coverage, 1),
                    "status": self._get_status(coverage)
                }
        
        coverage_pct = results["total_physicians"]["coverage"]
        if coverage_pct >= 80:
            results["completeness"] = "good"
        elif coverage_pct >= 50:
            results["completeness"] = "moderate"
        else:
            results["completeness"] = "poor"
        
        return results
    
    def _get_status(self, coverage_pct: float) -> str:
        """Get validation status based on coverage."""
        if coverage_pct >= 90:
            return "excellent"
        elif coverage_pct >= 70:
            return "good"
        elif coverage_pct >= 50:
            return "moderate"
        elif coverage_pct >= 25:
            return "poor"
        else:
            return "critical"
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict:
        """Validate data quality metrics."""
        results = {
            "total_records": len(df),
            "fields": {}
        }
        
        for col in df.columns:
            non_null = df[col].notna().sum()
            null_count = df[col].isna().sum()
            results["fields"][col] = {
                "non_null": int(non_null),
                "null_count": int(null_count),
                "completeness_pct": round(non_null / len(df) * 100, 1) if len(df) > 0 else 0
            }
        
        if "name" in df.columns:
            unique_names = df["name"].nunique()
            results["unique_doctors"] = int(unique_names)
            results["name_duplicates"] = int(len(df) - unique_names)
        
        return results
    
    def generate_validation_report(self, df: pd.DataFrame, year: int) -> str:
        """Generate comprehensive validation report."""
        report = []
        report.append("="*70)
        report.append("DATA VALIDATION REPORT")
        report.append("="*70)
        report.append(f"Year: {year}")
        report.append(f"Generated: {pd.Timestamp.now().isoformat()}")
        report.append("")
        
        count_results = self.validate_counts(df, year)
        if count_results:
            report.append("COUNT VALIDATION:")
            report.append("-"*40)
            total = count_results["total_physicians"]
            report.append(f"  Total Physicians:")
            report.append(f"    Scraped: {total['scraped']}")
            report.append(f"    Expected: {total['expected']}")
            report.append(f"    Coverage: {total['coverage']:.1f}%")
            report.append(f"    Completeness: {count_results['completeness']}")
            report.append("")
            
            report.append("  By Kupat Cholim:")
            for kupa_id, data in count_results["by_kupa"].items():
                kupa_name = KUPA_CHOLIM.get(kupa_id, {}).get("name", kupa_id)
                report.append(f"    {kupa_name}:")
                report.append(f"      Scraped: {data['scraped']}")
                report.append(f"      Expected: {data['expected']}")
                report.append(f"      Coverage: {data['coverage_pct']}% [{data['status']}]")
            report.append("")
        
        quality = self.validate_data_quality(df)
        report.append("DATA QUALITY:")
        report.append("-"*40)
        report.append(f"  Total records: {quality['total_records']}")
        if "unique_doctors" in quality:
            report.append(f"  Unique doctors: {quality['unique_doctors']}")
            report.append(f"  Name duplicates: {quality['name_duplicates']}")
        report.append("")
        
        report.append("  Field Completeness:")
        for field, stats in quality["fields"].items():
            report.append(f"    {field}: {stats['completeness_pct']}% ({stats['non_null']}/{quality['total_records']})")
        report.append("")
        
        report.append("="*70)
        
        return "\n".join(report)
    
    def run_validation(self, year: int) -> Optional[str]:
        """Run full validation for a year."""
        self.logger.info(f"Running validation for year {year}")
        
        df = self.load_scraped_data(year)
        if df is None:
            return None
        
        report = self.generate_validation_report(df, year)
        
        report_file = self.data_dir / f"validation_report_{year}.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        self.logger.info(f"Validation report saved to {report_file}")
        
        return report


def main():
    """Main entry point for validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate scraped doctor data")
    parser.add_argument("--year", "-y", type=int, help="Year to validate")
    parser.add_argument("--all", "-a", action="store_true", help="Validate all years")
    
    args = parser.parse_args()
    
    validator = DataValidator()
    
    if args.all:
        years = list(VALIDATION_BENCHMARKS.keys())
    elif args.year:
        years = [args.year]
    else:
        years = [pd.Timestamp.now().year]
    
    for year in years:
        report = validator.run_validation(year)
        if report:
            print(report)
        else:
            print(f"No data found for year {year}")


if __name__ == "__main__":
    main()
