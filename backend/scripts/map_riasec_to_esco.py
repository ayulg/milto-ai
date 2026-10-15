"""
map_riasec_to_esco.py - Map RIASEC from O*NET to ESCO careers
"""

import json
import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ONET_DIR = RAW_DIR / "onet"

def load_onet_riasec():
    """Load RIASEC from O*NET career_interest_types.csv"""
    file_path = ONET_DIR / "career_interest_types.csv"
    if not file_path.exists():
        print(f"❌ {file_path} not found!")
        return {}
    
    df = pd.read_csv(file_path, encoding='utf-8')
    print(f"   Loaded {len(df)} O*NET interest records")
    
    riasec_map = {}
    for _, row in df.iterrows():
        onet_code = row.get('O*NET-SOC Code', '')
        element_name = row.get('Element Name', '')
        data_value = row.get('Data Value', 0)
        
        if onet_code and element_name:
            name_to_dim = {
                'Realistic': 'R', 'Investigative': 'I', 'Artistic': 'A',
                'Social': 'S', 'Enterprising': 'E', 'Conventional': 'C'
            }
            
            if element_name in name_to_dim:
                if onet_code not in riasec_map:
                    riasec_map[onet_code] = {}
                dim = name_to_dim[element_name]
                # Scale from O*NET (1-7) to 1-5
                riasec_map[onet_code][dim] = float(data_value) * 5 / 7
    
    print(f"   Found RIASEC for {len(riasec_map)} O*NET occupations")
    return riasec_map

def load_onet_titles():
    """Load O*NET occupation titles"""
    file_path = ONET_DIR / "occupation_data.csv"
    if not file_path.exists():
        print(f"❌ {file_path} not found!")
        return {}
    
    df = pd.read_csv(file_path, encoding='utf-8')
    titles = {}
    for _, row in df.iterrows():
        code = row.get('O*NET-SOC Code', '')
        title = row.get('Title', '')
        if code and title:
            titles[code] = title.lower()
    
    print(f"   Loaded {len(titles)} O*NET titles")
    return titles

def load_unified_careers():
    """Load unified careers"""
    file_path = PROCESSED_DIR / "unified_careers.json"
    if not file_path.exists():
        print(f"❌ {file_path} not found!")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_matching_onet_code(title, onet_titles):
    """Find matching O*NET code by title"""
    if not title:
        return None, 0
    
    title_lower = title.lower()
    best_match = None
    best_score = 0
    
    for code, onet_title in onet_titles.items():
        # Check if titles match exactly
        if title_lower == onet_title:
            return code, 1.0
        
        # Check if one contains the other
        if title_lower in onet_title or onet_title in title_lower:
            score = len(set(title_lower.split()) & set(onet_title.split())) / max(len(title_lower.split()), len(onet_title.split()))
            if score > best_score:
                best_score = score
                best_match = code
    
    return best_match, best_score

def map_riasec_to_esco():
    """Map RIASEC from O*NET to ESCO careers"""
    print("\n" + "="*60)
    print("🗺️ MAPPING RIASEC FROM O*NET TO ESCO")
    print("="*60)
    
    print("\n📊 Loading O*NET RIASEC...")
    onet_riasec = load_onet_riasec()
    
    print("\n📊 Loading O*NET titles...")
    onet_titles = load_onet_titles()
    
    print("\n📊 Loading unified careers...")
    careers = load_unified_careers()
    if not careers:
        return
    
    print(f"   Loaded {len(careers)} careers")
    
    esco_count = 0
    mapped_count = 0
    already_have = 0
    no_match = 0
    
    for career in careers:
        sources = career.get('sources', [])
        
        # Check if already has RIASEC
        if career.get('riasec') and career.get('riasec', {}).get('R'):
            already_have += 1
            continue
        
        # Only process ESCO careers
        if 'esco' in sources and not 'onet' in sources:
            esco_count += 1
            
            # Try to find matching O*NET by title
            title = career.get('title', '')
            onet_code, score = find_matching_onet_code(title, onet_titles)
            
            if onet_code and onet_code in onet_riasec and score >= 0.5:
                career['riasec'] = onet_riasec[onet_code]
                career['riasec_source'] = 'onet_mapped'
                career['riasec_available'] = True
                career['riasec_match_score'] = score
                mapped_count += 1
            else:
                no_match += 1
    
    print(f"\n📊 RESULTS:")
    print(f"   Careers already with RIASEC: {already_have}")
    print(f"   ESCO careers without RIASEC: {esco_count}")
    print(f"   Mapped to O*NET RIASEC: {mapped_count}")
    print(f"   Still missing RIASEC: {no_match}")
    
    # Save updated careers
    output_file = PROCESSED_DIR / "unified_careers_v2.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(careers, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved to: {output_file}")
    
    # Also save as CSV
    df = pd.DataFrame(careers)
    csv_file = PROCESSED_DIR / "unified_careers_v2.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"✅ Saved to: {csv_file}")
    
    return careers

def main():
    map_riasec_to_esco()

if __name__ == "__main__":
    main()