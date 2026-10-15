"""
train_ranker_v3.py - Train improved model with better features
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib

DATA_DIR = Path("data")
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def load_features():
    """Load V3 features"""
    file_path = PROCESSED_DIR / "career_features_v3.csv"
    if not file_path.exists():
        print("❌ career_features_v3.csv not found!")
        print("   Run: python scripts/create_features_v3.py")
        return None
    
    df = pd.read_csv(file_path)
    print(f"✅ Loaded {len(df)} career profiles")
    return df

def create_training_data_v3(df):
    """Create improved training data"""
    print("\n🔄 Creating improved training data...")
    
    np.random.seed(42)
    X_list = []
    y_list = []
    career_ids = []
    
    # Get feature columns
    feature_cols = [col for col in df.columns if col.startswith(('riasec_', 'has_')) or 
                   col in ['skill_count', 'quality_score']]
    
    if not feature_cols:
        print("❌ No feature columns found!")
        return None, None
    
    print(f"   Using {len(feature_cols)} features")
    
    for idx, row in df.iterrows():
        career_features = [row[col] for col in feature_cols]
        career_id = row.get('id', f'c_{idx}')
        
        # Generate different match levels
        for match_level in ['strong', 'moderate', 'weak', 'poor']:
            noise_scale = {
                'strong': 0.1,
                'moderate': 0.25,
                'weak': 0.4,
                'poor': 0.6
            }[match_level]
            
            num_samples = {
                'strong': 10,
                'moderate': 6,
                'weak': 4,
                'poor': 2
            }[match_level]
            
            for _ in range(num_samples):
                # Create user profile with noise
                user_features = []
                for i, v in enumerate(career_features):
                    col = feature_cols[i]
                    noise = np.random.normal(0, noise_scale)
                    # Ensure values stay in reasonable range
                    if col.startswith('riasec_'):
                        # RIASEC: 0-5 scale
                        user_val = max(0, min(5, v + noise * 5))
                    elif col.startswith('has_'):
                        # Binary: keep as 0 or 1
                        user_val = 1 if v > 0.5 else 0
                    else:
                        user_val = max(0, v + noise * v)
                    user_features.append(user_val)
                
                X_list.append(user_features)
                career_ids.append(career_id)
                
                # Calculate similarity
                similarity = 1 - np.mean([abs(a-b)/5 for a, b in zip(user_features, career_features)])
                
                # Label based on match level
                if match_level == 'strong':
                    label = max(0.7, min(1, similarity + np.random.normal(0, 0.05)))
                elif match_level == 'moderate':
                    label = max(0.4, min(0.7, similarity + np.random.normal(0, 0.05)))
                elif match_level == 'weak':
                    label = max(0.2, min(0.5, similarity + np.random.normal(0, 0.05)))
                else:
                    label = max(0, min(0.3, similarity + np.random.normal(0, 0.05)))
                
                y_list.append(label)
    
    X = np.array(X_list)
    y = np.array(y_list)
    
    print(f"✅ Created {len(X)} training examples")
    print(f"   Features: {X.shape[1]}")
    print(f"   Labels: min={y.min():.3f}, max={y.max():.3f}, mean={y.mean():.3f}")
    
    return X, y

def train_model_v3(X, y):
    """Train and evaluate model"""
    print("\n🧠 Training model with cross-validation...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Models to try
    models = {
        'Ridge Regression': Ridge(alpha=1.0),
        'Random Forest': RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            random_state=42,
            n_jobs=-1
        ),
        'Gradient Boosting': GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
    }
    
    results = {}
    best_model = None
    best_score = -float('inf')
    best_name = ""
    
    for name, model in models.items():
        print(f"\n   Training {name}...")
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
        print(f"      CV R²: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Train and test
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        test_r2 = r2_score(y_test, y_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"      Test R²: {test_r2:.4f}, RMSE: {test_rmse:.4f}")
        
        results[name] = {
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'test_r2': test_r2,
            'test_rmse': test_rmse,
            'model': model
        }
        
        if test_r2 > best_score:
            best_score = test_r2
            best_model = model
            best_name = name
    
    print(f"\n✅ Best model: {best_name}")
    print(f"   CV R²: {results[best_name]['cv_mean']:.4f}")
    print(f"   Test R²: {best_score:.4f}")
    
    # Save model
    joblib.dump(best_model, MODELS_DIR / 'career_ranker_v3.pkl')
    joblib.dump(scaler, MODELS_DIR / 'scaler_v3.pkl')
    
    # Save metadata
    metadata = {
        'model_type': best_name,
        'cv_r2': results[best_name]['cv_mean'],
        'test_r2': best_score,
        'features_count': X.shape[1],
        'training_samples': len(X),
        'feature_names': [f'f_{i}' for i in range(X.shape[1])],
        'results': {name: {
            'cv_mean': r['cv_mean'],
            'cv_std': r['cv_std'],
            'test_r2': r['test_r2'],
            'test_rmse': r['test_rmse']
        } for name, r in results.items()},
        'version': '3.0'
    }
    
    with open(MODELS_DIR / 'model_metadata_v3.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Model saved to: {MODELS_DIR}")
    
    return results, best_model

def main():
    print("="*60)
    print("🧠 TRAINING IMPROVED MODEL V3")
    print("="*60)
    
    # Load features
    df = load_features()
    if df is None:
        return
    
    # Create training data
    X, y = create_training_data_v3(df)
    if X is None:
        return
    
    # Train model
    train_model_v3(X, y)
    
    print("\n" + "="*60)
    print("✅ Training complete!")
    print("\n📋 NEXT STEPS:")
    print("1. Run: python app.py")
    print("2. Test the improved recommendations")

if __name__ == "__main__":
    main()