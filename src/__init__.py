"""Source package for Kupot Cholim doctor scraper."""

from .config import (
    KUPA_CHOLIM,
    GENDER_MAP,
    SPECIALTIES_HEBREW_TO_ENGLISH,
    setup_logging,
    DoctorRecord,
    BASE_DIR,
    DATA_DIR,
    LOG_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR
)

__all__ = [
    "KUPA_CHOLIM",
    "GENDER_MAP",
    "SPECIALTIES_HEBREW_TO_ENGLISH",
    "setup_logging",
    "DoctorRecord",
    "BASE_DIR",
    "DATA_DIR",
    "LOG_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR"
]
