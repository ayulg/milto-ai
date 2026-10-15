"""
create_features_v3.py - Create enhanced features with mapped RIASEC
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("data")
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def load_careers():
    """Load V2 careers with mapped RIASEC"""
    file_path = PROCESSED_DIR / "unified_careers_v2.json"
    if not file_path.exists():
        print("❌ unified_careers_v2.json not found!")
        print("   Run: python scripts/map_riasec_to_esco.py")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_features_v3(career):
    """Extract enhanced features"""
    features = {}
    
    # Basic info
    features['id'] = career.get('id', '')
    features['title'] = career.get('title', '')
    
    # RIASEC (1-5 scale) - now with mapped data!
    riasec = career.get('riasec', {})
    for dim in ['R', 'I', 'A', 'S', 'E', 'C']:
        val = riasec.get(dim, 0)
        features[f'riasec_{dim}'] = val
    
    # RIASEC availability flag
    features['riasec_available'] = 1 if riasec else 0
    
    # Skills
    skills = career.get('skills', [])
    features['skill_count'] = len(skills) if skills else 0
    
    # Skill categories
    skill_categories = ['programming', 'writing', 'communication', 'leadership', 
                       'design', 'research', 'teaching', 'data', 'systems', 
                       'creativity', 'quant', 'empathy', 'persuasion', 'project']
    
    for cat in skill_categories:
        features[f'has_{cat}'] = 1 if any(cat in s.lower() for s in skills) else 0
    
    # Source
    features['source_esco'] = 1 if 'esco' in career.get('sources', []) else 0
    features['source_onet'] = 1 if 'onet' in career.get('sources', []) else 0
    features['source_mapped'] = 1 if career.get('riasec_source') == 'onet_mapped' else 0
    
    # Quality score
    quality = 0
    if features['riasec_available']:
        quality += 1
    if features['skill_count'] > 0:
        quality += 1
    if career.get('description'):
        quality += 1
    features['quality_score'] = quality / 3
    
    return features

def create_feature_matrix_v3():
    """Create enhanced feature matrix"""
    print("\n" + "="*60)
    print("📊 CREATING ENHANCED FEATURE MATRIX V3")
    print("="*60)
    
    careers = load_careers()
    if not careers:
        return None, None
    
    print(f"   Loaded {len(careers)} careers")
    
    # Extract features
    feature_list = []
    for career in careers:
        features = extract_features_v3(career)
        feature_list.append(features)
    
    df = pd.DataFrame(feature_list)
    
    # Select numeric features
    numeric_cols = [col for col in df.columns if col.startswith(('riasec_', 'has_')) or 
                   col in ['skill_count', 'quality_score', 'riasec_available']]
    
    if numeric_cols:
        X = df[numeric_cols].copy()
        
        # Handle missing values - fill with median
        for col in X.columns:
            if X[col].isna().any():
                median_val = X[col].median()
                X[col] = X[col].fillna(median_val)
        
        print(f"   Feature matrix: {X.shape}")
        print(f"   Features: {', '.join(X.columns.tolist()[:10])}...")
    else:
        print("⚠️ No numeric features found!")
        X = pd.DataFrame()
    
    # Save features
    if not df.empty:
        df.to_csv(PROCESSED_DIR / "career_features_v3_full.csv", index=False, encoding='utf-8')
        print(f"✅ Full features saved to: {PROCESSED_DIR / 'career_features_v3_full.csv'}")
    
    if not X.empty:
        X.to_csv(PROCESSED_DIR / "career_features_v3.csv", index=False, encoding='utf-8')
        print(f"✅ Features saved to: {PROCESSED_DIR / 'career_features_v3.csv'}")
        
        # Feature statistics
        stats = {
            'total_careers': len(df),
            'features_count': len(numeric_cols),
            'riasec_available': int(df['riasec_available'].sum()),
            'avg_quality': float(df['quality_score'].mean()),
            'feature_stats': {
                col: {
                    'mean': float(X[col].mean()),
                    'std': float(X[col].std()),
                    'min': float(X[col].min()),
                    'max': float(X[col].max())
                } for col in X.columns
            }
        }
        
        with open(PROCESSED_DIR / "feature_stats_v3.json", 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"✅ Stats saved to: {PROCESSED_DIR / 'feature_stats_v3.json'}")
    
    return X, df

def main():
    X, df = create_feature_matrix_v3()
    
    if X is not None and not X.empty:
        print(f"\n📊 FEATURE STATISTICS:")
        print(f"   Careers: {len(df)}")
        print(f"   Features: {X.shape[1]}")
        print(f"   RIASEC available: {df['riasec_available'].sum()}")
        print(f"   Avg quality score: {df['quality_score'].mean():.2f}")
    
    print("\n" + "="*60)
    print("✅ Feature creation complete!")
    print("\n📋 NEXT STEPS:")
    print("1. Run: python scripts/train_ranker_v3.py")

if __name__ == "__main__":
    main()