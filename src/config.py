"""
Israel Kupot Cholim Doctor Scraper
Base configuration and utilities
"""

import os
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

for d in [DATA_DIR, LOG_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

KUPA_CHOLIM = {
    "clalit": {
        "name": "Clalit Health Services",
        "name_hebrew": "קופת חולים כללית",
        "website": "https://www.clalit.co.il/",
        "doctor_search": "https://www.clalit.co.il/heb/findingadoctor/"
    },
    "maccabi": {
        "name": "Maccabi Healthcare Services",
        "name_hebrew": "קופת חולים מכבי",
        "website": "https://www.maccabi4u.co.il/",
        "doctor_search": "https://sereotype.maccabi4u.co.il/heb/Doctors",
        "api_base": "https://sereotype.maccabi4u.co.il"
    },
    "meuhedet": {
        "name": "Meuhedet Health Services",
        "name_hebrew": "קופת חולים מאוחדת",
        "website": "https://www.meuhedet.co.il/",
        "doctor_search": "https://www.meuhedet.co.il/heb/Doctors"
    },
    "leumit": {
        "name": "Leumit Health Services",
        "name_hebrew": "קופת חולים לאומית",
        "website": "https://www.leumit.co.il/",
        "doctor_search": "https://www.leumit.co.il/heb/doctorssearch/"
    }
}

GENDER_MAP = {
    "זכר": "M",
    "נקבה": "F",
    "male": "M",
    "female": "F",
    "M": "M",
    "F": "F"
}

SPECIALTIES_HEBREW_TO_ENGLISH = {
    "כללי": "General",
    "פנימית": "Internal Medicine",
    "ילדים": "Pediatrics",
    "נשים": "Obstetrics/Gynecology",
    "אורתופדיה": "Orthopedics",
    "עיניים": "Ophthalmology",
    "אף אוזן גרון": "ENT",
    "עור": "Dermatology",
    "ניתוחים": "Surgery",
    "לב": "Cardiology",
    "מוח": "Neurology",
    "סרטן": "Oncology",
    "פסיכיאטריה": "Psychiatry",
    "רדיולוגיה": "Radiology",
    "אנדוקרינולוגיה": "Endocrinology",
    "גסטרואנטרולוגיה": "Gastroenterology",
    "נפרולוגיה": "Nephrology",
    "ראומטולוגיה": "Rheumatology",
    "אלרגיה": "Allergy",
    "המטולוגיה": "Hematology",
    "זיהומים": "Infectious Diseases",
    "ריאות": "Pulmonology",
    "שיקום": "Rehabilitation",
    "גריאטריה": "Geriatrics",
    "רפואת משפחה": "Family Medicine",
    "רפואת חירום": "Emergency Medicine",
    "הרדמה": "Anesthesiology",
    "פתולוגיה": "Pathology",
    "רפואה גרעינית": "Nuclear Medicine",
    "רפואת ילדים": "Pediatrics",
    "כירורגיה": "Surgery",
    "אורולוגיה": "Urology",
    "נוירו-כירורגיה": "Neurosurgery",
    "פלסטיקה": "Plastic Surgery",
    "ילדים חירום": "Pediatric Emergency",
    "נשים ויולדות": "Obstetrics"
}

def setup_logging(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        default_log = LOG_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(default_log)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

@dataclass
class DoctorRecord:
    """Data class for doctor records."""
    name: str
    teudat_zehut: Optional[str] = None
    specialty: Optional[str] = None
    year: Optional[int] = None
    gender: Optional[str] = None
    clinic_address: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    clalit: int = 0
    maccabi: int = 0
    meuhedet: int = 0
    leumit: int = 0
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    scrape_date: Optional[str] = None
    
    def __post_init__(self):
        if self.scrape_date is None:
            self.scrape_date = datetime.now().isoformat()
        if self.gender:
            self.gender = GENDER_MAP.get(self.gender, self.gender)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "teudat_zehut": self.teudat_zehut,
            "specialty": self.specialty,
            "year": self.year,
            "gender": self.gender,
            "clinic_address": self.clinic_address,
            "phone": self.phone,
            "license_number": self.license_number,
            "clalit": self.clalit,
            "maccabi": self.maccabi,
            "meuhedet": self.meuhedet,
            "leumit": self.leumit,
            "source_url": self.source_url,
            "source_name": self.source_name,
            "scrape_date": self.scrape_date
        }
