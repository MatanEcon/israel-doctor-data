import pandas as pd
import re
from collections import defaultdict

def normalize_name_moh_ima(name):
    """MOH and IMA use LAST FIRST format - need to reverse"""
    if pd.isna(name) or not name:
        return ''
    name = str(name).strip()
    name = re.sub(r'^ד"ר\s*', '', name)
    name = re.sub(r'^ד\s+', '', name)
    name = re.sub(r'^פרופ\'?\s*', '', name)
    name = re.sub(r'^מר\s*', '', name)
    parts = name.split()
    if len(parts) >= 2:
        name = ' '.join(parts[::-1])  # LAST FIRST -> FIRST LAST
    return name.lower().strip()

def normalize_name_med(name):
    """MedReviews uses FIRST LAST format - keep as is"""
    if pd.isna(name) or not name:
        return ''
    name = str(name).strip()
    name = re.sub(r'^ד"ר\s*', '', name)
    name = re.sub(r'^פרופ\'?\s*', '', name)
    name = re.sub(r'^מר\s*', '', name)
    return name.lower().strip()

def normalize_name(name):
    """Generic normalize - strips titles only"""
    if pd.isna(name) or not name:
        return ''
    name = str(name).strip()
    name = re.sub(r'^ד"ר\s*', '', name)
    name = re.sub(r'^ד\s+', '', name)
    name = re.sub(r'^פרופ\'?\s*', '', name)
    name = re.sub(r'^מר\s*', '', name)
    return name.lower().strip()

def normalize_specialty(spec):
    if pd.isna(spec) or not spec:
        return ''
    spec = str(spec).lower().strip()
    spec = re.sub(r'^מומח[הו]?\s*', '', spec)
    spec = re.sub(r'^מתמח[הו]?\s*', '', spec)
    spec = re.sub(r', ', ' ', spec)
    spec = re.sub(r'\s+', ' ', spec)
    return spec.strip()

SPECIALTY_SYNONYMS = {
    'פנימית': ['פנימית', 'רפואה פנימית'],
    'ילדים': ['רפואת ילדים', 'ילדים', 'פדיאטריה'],
    'כירורגיה': ['כירורגיה', 'כירורגיה כללית'],
    'אורתופדיה': ['אורתופדיה', 'אורתופדית'],
    'קרדיולוגיה': ['קרדיולוגיה', 'לב'],
    'נוירולוגיה': ['נוירולוגיה'],
    'פסיכיאטריה': ['פסיכיאטריה'],
    'רדיולוגיה': ['רדיולוגיה'],
    'א.א.ג': ['א.א.ג', 'אף אוזן גרון', 'אף-אוזן-גרון', 'מחלות א.א.ג'],
    'עיניים': ['עיניים', 'רפואת עיניים'],
    'עור': ['עור', 'מחלות עור', 'דרמטולוגיה'],
    'גינקולוגיה': ['גינקולוגיה', 'יילוד וגינקולוגיה'],
    'אורולוגיה': ['אורולוגיה', 'כירורגיה אורולוגית'],
}

def get_specialty_key(spec):
    spec = normalize_specialty(spec)
    for key, synonyms in SPECIALTY_SYNONYMS.items():
        for syn in synonyms:
            if syn in spec or spec in syn:
                return key
    return spec

def check_specialty_match(spec1, spec2):
    key1 = get_specialty_key(spec1)
    key2 = get_specialty_key(spec2)
    return key1 == key2 and key1 != ''

def match_doctors_with_specialty_verification(source_df, target_df, source_name_col='name', target_name_col='name', 
                                               source_spec_col='specialty', target_spec_col='specialty',
                                               source_label='source', target_label='target',
                                               source_norm_func=None, target_norm_func=None):
    if source_norm_func is None:
        source_norm_func = normalize_name
    if target_norm_func is None:
        target_norm_func = normalize_name
        
    source_df = source_df.copy()
    target_df = target_df.copy()
    
    source_df['norm_name'] = source_df[source_name_col].apply(source_norm_func)
    target_df['norm_name'] = target_df[target_name_col].apply(target_norm_func)
    
    source_df['norm_specialty'] = source_df[source_spec_col].apply(normalize_specialty) if source_spec_col in source_df.columns else ''
    target_df['norm_specialty'] = target_df[target_spec_col].apply(normalize_specialty) if target_spec_col in target_df.columns else ''
    
    matches = []
    used_source = set()
    used_target = set()
    
    norm_to_source = defaultdict(list)
    for idx, row in source_df.iterrows():
        if row['norm_name']:
            norm_to_source[row['norm_name']].append(idx)
    
    for idx, target_row in target_df.iterrows():
        target_name = target_row['norm_name']
        target_spec = target_row['norm_specialty']
        
        if target_name not in norm_to_source:
            continue
        
        best_match = None
        best_score = 0
        
        for source_idx in norm_to_source[target_name]:
            if source_idx in used_source:
                continue
            
            source_row = source_df.loc[source_idx]
            
            name_match = 1.0 if source_row['norm_name'] == target_name else 0.0
            
            spec_match = 0.0
            if target_spec and source_row['norm_specialty']:
                if check_specialty_match(target_spec, source_row['norm_specialty']):
                    spec_match = 1.0
                elif not target_spec or not source_row['norm_specialty']:
                    spec_match = 0.5
                else:
                    spec_match = 0.0
            
            confidence = name_match * 0.4 + spec_match * 0.6
            
            if confidence > best_score:
                best_score = confidence
                best_match = source_idx
        
        if best_match is not None and best_score >= 0.6:
            source_row = source_df.loc[best_match]
            matches.append({
                f'{target_label}_name': target_row.get(target_name_col, ''),
                f'{source_label}_name': source_row.get(source_name_col, ''),
                'norm_name': target_name,
                f'{target_label}_specialty': target_row.get(target_spec_col, ''),
                f'{source_label}_specialty': source_row.get(source_spec_col, ''),
                'confidence': best_score,
                'name_match': True,
                'specialty_match': spec_match >= 1.0 if 'spec_match' in dir() else False,
                f'{target_label}_idx': idx,
                f'{source_label}_idx': best_match
            })
            used_source.add(best_match)
            used_target.add(idx)
    
    return pd.DataFrame(matches)

def main():
    print("Loading datasets...")
    moh = pd.read_csv('data/raw/moh_doctors.csv')
    med = pd.read_csv('data/raw/medreviews_clean.csv')
    imd = pd.read_csv('data/raw/ima_doctors.csv', encoding='utf-8-sig')
    
    print(f"MOH: {len(moh)}")
    print(f"MedReviews: {len(med)}")
    print(f"IMA: {len(imd)}")
    
    print("\n=== Matching IMA with MOH (name + specialty verification) ===")
    imd_moh_matches = match_doctors_with_specialty_verification(
        imd, moh,
        source_name_col='raw_name', target_name_col='name',
        source_spec_col='specialty', target_spec_col='specialty',
        source_label='ima', target_label='moh',
        source_norm_func=normalize_name_moh_ima,  # Both use LAST FIRST
        target_norm_func=normalize_name_moh_ima
    )
    
    print(f"IMA-MOH matches with specialty verification: {len(imd_moh_matches)}")
    print(f"High confidence (>=0.8): {len(imd_moh_matches[imd_moh_matches['confidence'] >= 0.8])}")
    print(f"Medium confidence (0.6-0.8): {len(imd_moh_matches[(imd_moh_matches['confidence'] >= 0.6) & (imd_moh_matches['confidence'] < 0.8)])}")
    
    imd_moh_matches.to_csv('data/raw/ima_moh_matches.csv', index=False, encoding='utf-8-sig')
    print(f"\nSaved to data/raw/ima_moh_matches.csv")
    print(f"\nSaved to data/raw/ima_moh_matches.csv")
    
    print("\n=== Cross-reference with MedReviews ===")
    imd_med_matches = match_doctors_with_specialty_verification(
        imd, med,
        source_name_col='raw_name', target_name_col='name',
        source_spec_col='specialty', target_spec_col='specialty',
        source_label='ima', target_label='med',
        source_norm_func=normalize_name_moh_ima,  # IMA uses LAST FIRST
        target_norm_func=normalize_name_med  # MedReviews uses FIRST LAST
    )
    print(f"IMA-MedReviews matches: {len(imd_med_matches)}")
    
    imd_med_matches.to_csv('data/raw/ima_med_matches.csv', index=False, encoding='utf-8-sig')
    print(f"Saved to data/raw/ima_med_matches.csv")
    print(f"\nSaved to data/raw/ima_med_matches.csv")
    
    print("\n=== Summary ===")
    total_matched = len(set(imd_moh_matches['ima_idx'].tolist() if 'ima_idx' in imd_moh_matches.columns else []) | 
                        set(imd_med_matches['ima_idx'].tolist() if 'ima_idx' in imd_med_matches.columns else []))
    print(f"Total unique IMA doctors matched: {total_matched}")
    print(f"IMA doctors without matches: {len(imd) - total_matched}")

if __name__ == "__main__":
    main()
