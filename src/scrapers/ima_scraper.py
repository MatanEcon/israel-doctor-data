import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://www.ima.org.il/DoctorsIndexNew/Results.aspx"

def normalize_name_hebrew(name):
    if pd.isna(name) or not name:
        return ''
    name = str(name).strip()
    name = re.sub(r'^ד"ר\s*', '', name)
    name = re.sub(r'^ד\s*', '', name)
    name = re.sub(r'^פרופ\'?\s*', '', name)
    name = re.sub(r'^מר\s*', '', name)
    parts = name.split()
    if len(parts) >= 2:
        name = ' '.join(parts[::-1])
    return name.lower().strip()

def normalize_specialty(spec):
    if pd.isna(spec) or not spec:
        return ''
    spec = str(spec)
    spec = re.sub(r'^מומח[הו]?\s*', '', spec)
    spec = re.sub(r'^מתמח[הו]?\s*', '', spec)
    spec = re.sub(r', ', ' ', spec)
    return spec.lower().strip()

def parse_doctors_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    doctors = []
    
    results = soup.find('div', class_='results_results')
    if not results:
        return doctors
    
    for elem in results.find_all(['div', 'span', 'a', 'p']):
        text = elem.get_text(strip=True)
        if text and len(text) > 10:
            if text.startswith('ד"ר') or text.startswith('ד '):
                name_match = re.match(r'^ד"ר\s+(.+?)(?=מומחה|מתמחה|$)', text)
                if name_match:
                    name = name_match.group(1).strip()
                    spec = text[len(name_match.group(0)):].strip()
                    
                    if name and len(name) > 2:
                        doctors.append({
                            'name': f'ד"ר {name}',
                            'raw_name': name,
                            'specialty': spec,
                            'norm_name': normalize_name_hebrew(name),
                            'norm_specialty': normalize_specialty(spec),
                            'source': 'IMA'
                        })
            elif text.startswith('פרופ'):
                name_match = re.match(r'^פרופ\'?\s+(.+?)(?=מומחה|$)', text)
                if name_match:
                    name = name_match.group(1).strip()
                    spec = text[len(name_match.group(0)):].strip()
                    
                    if name and len(name) > 2:
                        doctors.append({
                            'name': f'פרופ {name}',
                            'raw_name': name,
                            'specialty': spec,
                            'norm_name': normalize_name_hebrew(name),
                            'norm_specialty': normalize_specialty(spec),
                            'source': 'IMA'
                        })
    
    return doctors

def scrape_page(session, page_num):
    try:
        response = session.get(f"{BASE_URL}?page={page_num}", timeout=30)
        doctors = parse_doctors_from_html(response.text)
        return doctors, page_num
    except Exception as e:
        return [], page_num

def scrape_all_ima(max_pages=100, max_workers=3):
    all_doctors = []
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print(f"Scraping IMA doctor index...")
    
    for page in range(1, max_pages + 1):
        doctors, _ = scrape_page(session, page)
        all_doctors.extend(doctors)
        
        if page % 10 == 0:
            print(f"Progress: {page}/{max_pages} pages, {len(all_doctors)} doctors")
        
        time.sleep(0.5)
    
    df = pd.DataFrame(all_doctors)
    df.drop_duplicates(subset=['raw_name', 'norm_specialty'], inplace=True)
    
    print(f"Total IMA doctors scraped: {len(df)}")
    return df

if __name__ == "__main__":
    df = scrape_all_ima(max_pages=100, max_workers=3)
    df.to_csv('data/raw/ima_doctors.csv', index=False, encoding='utf-8-sig')
    print(f"Saved to data/raw/ima_doctors.csv")
