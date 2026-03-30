import asyncio
import csv
import json
import re
from camoufox import AsyncCamoufox

async def scrape_maccabi():
    all_doctors = []
    seen_ids = set()
    
    async with AsyncCamoufox(headless=True) as browser:
        page = await browser.new_page()
        
        city_codes = [
            ("תל אביב", "6700"),
            ("ירושלים", "2600"),
            ("חיפה", "4000"),
            ("באר שבע", "6000"),
            ("נתניה", "5200"),
            ("אשדוד", "6200"),
            ("פתח תקווה", "5400"),
            ("ראשון לציון", "5600"),
            ("חולון", "6900"),
            ("בני ברק", "3100"),
        ]
        
        for city_name, city_code in city_codes:
            print(f"Scraping city: {city_name}")
            
            for page_num in range(1, 6):
                url = f"https://serguide.maccabi4u.co.il/heb/doctors/doctorssearchresults/?City={city_code}&PageNumber={page_num}"
                print(f"  Page {page_num}: {url}")
                
                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(2)
                    
                    content = await page.content()
                    
                    doctor_cards = await page.query_selector_all("[data-doctor-id]")
                    
                    if not doctor_cards:
                        break
                    
                    for card in doctor_cards:
                        try:
                            doctor_id = await card.get_attribute("data-doctor-id")
                            if doctor_id in seen_ids:
                                continue
                            seen_ids.add(doctor_id)
                            
                            name = await card.query_selector(".doctor-name, h3, [class*='name']")
                            name_text = await name.inner_text() if name else ""
                            
                            specialty = await card.query_selector(".specialty, [class*='specialty']")
                            specialty_text = await specialty.inner_text() if specialty else ""
                            
                            all_doctors.append({
                                "id": doctor_id,
                                "name": name_text.strip(),
                                "specialty": specialty_text.strip(),
                                "kupa": "Maccabi",
                                "city": city_name
                            })
                        except Exception as e:
                            print(f"    Error parsing card: {e}")
                            continue
                            
                except Exception as e:
                    print(f"    Error loading page: {e}")
                    break
        
        await page.close()
    
    with open("matanecon/data/raw/maccabi_doctors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "specialty", "kupa", "city"])
        writer.writeheader()
        writer.writerows(all_doctors)
    
    print(f"\nTotal doctors scraped: {len(all_doctors)}")
    return all_doctors

if __name__ == "__main__":
    asyncio.run(scrape_maccabi())
