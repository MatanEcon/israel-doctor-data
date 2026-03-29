"""
Code Audit Script
Verifies that the scraper code is properly structured and functional
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def audit_imports():
    """Check if all imports work."""
    print("=" * 60)
    print("AUDIT: Import Check")
    print("=" * 60)
    
    tests = []
    
    try:
        from src.config import KUPA_CHOLIM, DoctorRecord
        tests.append(("config imports", True))
    except Exception as e:
        tests.append(("config imports", False, str(e)))
    
    try:
        from src.base_scraper import BaseScraper
        tests.append(("base_scraper imports", True))
    except Exception as e:
        tests.append(("base_scraper imports", False, str(e)))
    
    try:
        from src.scrapers import DoctorIndexScraper, MedReviewsScraper, MaccabiScraper
        tests.append(("scrapers imports", True))
    except Exception as e:
        tests.append(("scrapers imports", False, str(e)))
    
    try:
        from src.scrapers.clalit import ClalitScraper
        tests.append(("clalit scraper imports", True))
    except Exception as e:
        tests.append(("clalit scraper imports", False, str(e)))
    
    try:
        from src.scrapers.leumit_meuhedet import LeumitScraper, MeuhedetScraper
        tests.append(("leumit/meuhedet scraper imports", True))
    except Exception as e:
        tests.append(("leumit/meuhedet scraper imports", False, str(e)))
    
    try:
        from src.validate import DataValidator
        tests.append(("validator imports", True))
    except Exception as e:
        tests.append(("validator imports", False, str(e)))
    
    for test in tests:
        status = "PASS" if test[1] else "FAIL"
        print(f"  [{status}] {test[0]}")
        if len(test) > 2:
            print(f"         Error: {test[2]}")
    
    return all(t[1] for t in tests)


def audit_structure():
    """Check if all required files exist."""
    print("\n" + "=" * 60)
    print("AUDIT: File Structure")
    print("=" * 60)
    
    required_files = [
        "README.md",
        "requirements.txt",
        "run_scrapers.py",
        "test_scraper.py",
        "src/__init__.py",
        "src/config.py",
        "src/base_scraper.py",
        "src/validate.py",
        "src/scrapers/__init__.py",
        "src/scrapers/maccabi.py",
        "src/scrapers/clalit.py",
        "src/scrapers/leumit_meuhedet.py",
        "src/scrapers/third_party.py",
        "notebooks/analysis.ipynb"
    ]
    
    base_dir = Path(__file__).parent
    all_exist = True
    
    for file in required_files:
        filepath = base_dir / file
        exists = filepath.exists()
        status = "PASS" if exists else "FAIL"
        print(f"  [{status}] {file}")
        if not exists:
            all_exist = False
    
    return all_exist


def audit_data_model():
    """Check if DoctorRecord works correctly."""
    print("\n" + "=" * 60)
    print("AUDIT: Data Model")
    print("=" * 60)
    
    try:
        from src.config import DoctorRecord
        
        record = DoctorRecord(
            name="ד\"ר יוסי כהן",
            specialty="אורתופדיה",
            gender="M",
            clalit=1,
            maccabi=1
        )
        
        assert record.name == "ד\"ר יוסי כהן"
        assert record.specialty == "אורתופדיה"
        assert record.gender == "M"
        assert record.clalit == 1
        assert record.maccabi == 1
        
        record_dict = record.to_dict()
        assert "name" in record_dict
        assert "clalit" in record_dict
        assert "maccabi" in record_dict
        
        print("  [PASS] DoctorRecord creation")
        print("  [PASS] DoctorRecord.to_dict()")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Data model: {e}")
        return False


def audit_kupa_config():
    """Check if Kupa configuration is correct."""
    print("\n" + "=" * 60)
    print("AUDIT: Kupat Cholim Configuration")
    print("=" * 60)
    
    try:
        from src.config import KUPA_CHOLIM
        
        required_kupot = ["clalit", "maccabi", "meuhedet", "leumit"]
        
        for kupa in required_kupot:
            if kupa not in KUPA_CHOLIM:
                print(f"  [FAIL] Missing kupa: {kupa}")
                return False
            
            info = KUPA_CHOLIM[kupa]
            required_fields = ["name", "name_hebrew", "website", "doctor_search"]
            
            for field in required_fields:
                if field not in info:
                    print(f"  [FAIL] Missing field '{field}' for {kupa}")
                    return False
        
        print(f"  [PASS] All {len(required_kupot)} kupot configured")
        
        for kupa, info in KUPA_CHOLIM.items():
            print(f"       - {kupa}: {info['name']}")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Kupa config: {e}")
        return False


def audit_scraper_classes():
    """Check if scraper classes are properly structured."""
    print("\n" + "=" * 60)
    print("AUDIT: Scraper Classes")
    print("=" * 60)
    
    try:
        from src.base_scraper import BaseScraper
        from src.scrapers.maccabi import MaccabiScraper
        from src.scrapers.clalit import ClalitScraper
        from src.scrapers.leumit_meuhedet import LeumitScraper, MeuhedetScraper
        from src.scrapers.third_party import DoctorIndexScraper, MedReviewsScraper
        
        scrapers = [
            ("MaccabiScraper", MaccabiScraper),
            ("ClalitScraper", ClalitScraper),
            ("LeumitScraper", LeumitScraper),
            ("MeuhedetScraper", MeuhedetScraper),
            ("DoctorIndexScraper", DoctorIndexScraper),
            ("MedReviewsScraper", MedReviewsScraper)
        ]
        
        for name, cls in scrapers:
            if not hasattr(cls, 'scrape'):
                print(f"  [FAIL] {name} missing scrape() method")
                return False
            if not hasattr(cls, 'save_records'):
                print(f"  [FAIL] {name} missing save_records() method")
                return False
        
        print(f"  [PASS] All {len(scrapers)} scrapers have required methods")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Scraper class audit: {e}")
        return False


def audit_validation():
    """Check if validation module works."""
    print("\n" + "=" * 60)
    print("AUDIT: Validation Module")
    print("=" * 60)
    
    try:
        from src.validate import DataValidator, VALIDATION_BENCHMARKS
        
        if not VALIDATION_BENCHMARKS:
            print("  [FAIL] No benchmarks defined")
            return False
        
        print(f"  [PASS] {len(VALIDATION_BENCHMARKS)} validation benchmarks defined")
        
        validator = DataValidator()
        print("  [PASS] DataValidator instantiation")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Validation module: {e}")
        return False


def main():
    """Run all audits."""
    print("\n" + "#" * 60)
    print("# ISRAEL KUPOT CHOLIM SCRAPER - CODE AUDIT")
    print("#" * 60 + "\n")
    
    results = {
        "imports": audit_imports(),
        "structure": audit_structure(),
        "data_model": audit_data_model(),
        "kupa_config": audit_kupa_config(),
        "scraper_classes": audit_scraper_classes(),
        "validation": audit_validation()
    }
    
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("OVERALL: ALL CHECKS PASSED")
        print("The code is properly structured and ready for testing.")
    else:
        print("OVERALL: SOME CHECKS FAILED")
        print("Please fix the issues above before proceeding.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
