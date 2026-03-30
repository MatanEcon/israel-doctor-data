import asyncio
import csv
import json
import re
from playwright.async_api import async_playwright

async def scrape_maccabi():
    all_doctors = []
    seen_ids = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale='he-IL',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        city_codes = [
            ("תל אביב", "6700"),
            ("ירושלים", "2600"),
            ("חיפה", "4000"),
            ("באר שבע", "6000"),
            ("נתניה", "5200"),
        ]
        
        for city_name, city_code in city_codes:
            print(f"Scraping city: {city_name}")
            
            for page_num in range(1, 4):
                url = f"https://serguide.maccabi4u.co.il/heb/doctors/doctorssearchresults/?City={city_code}&PageNumber={page_num}"
                print(f"  Page {page_num}")
                
                try:
                    await page.goto(url, wait_until="networkidle", timeout=60000)
                    await asyncio.sleep(3)
                    
                    # Try to extract from __INITIAL_STATE__
                    init_state = await page.evaluate('''() => {
                        return window.__INITIAL_STATE__;
                    }''')
                    
                    if init_state and 'searchResults' in init_state:
                        sr = init_state['searchResults']
                        if isinstance(sr, dict):
                            # Try to find doctors in any key
                            for key, val in sr.items():
                                if isinstance(val, list) and len(val) > 0:
                                    print(f"    Found list in searchResults.{key}: {len(val)} items")
                                    for doc in val:
                                        if isinstance(doc, dict) and 'DoctorId' in doc:
                                            doc_id = str(doc.get('DoctorId', ''))
                                            if doc_id and doc_id not in seen_ids:
                                                seen_ids.add(doc_id)
                                                all_doctors.append({
                                                    "id": doc_id,
                                                    "name": doc.get('DisplayName', ''),
                                                    "specialty": doc.get('SpecialtyName', ''),
                                                    "kupa": "Maccabi",
                                                    "city": city_name
                                                })
                        elif isinstance(sr, list) and len(sr) > 0:
                            print(f"    Found list in searchResults: {len(sr)} items")
                            for doc in sr:
                                if isinstance(doc, dict):
                                    doc_id = str(doc.get('DoctorId', ''))
                                    if doc_id and doc_id not in seen_ids:
                                        seen_ids.add(doc_id)
                                        all_doctors.append({
                                            "id": doc_id,
                                            "name": doc.get('DisplayName', ''),
                                            "specialty": doc.get('SpecialtyName', ''),
                                            "kupa": "Maccabi",
                                            "city": city_name
                                        })
                    
                except Exception as e:
                    print(f"    Error: {e}")
                    continue
        
        await browser.close()
    
    print(f"\nTotal doctors: {len(all_doctors)}")
    
    with open("matanecon/data/raw/maccabi_doctors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "specialty", "kupa", "city"])
        writer.writeheader()
        writer.writerows(all_doctors)
    
    return all_doctors

if __name__ == "__main__":
    asyncio.run(scrape_maccabi())
