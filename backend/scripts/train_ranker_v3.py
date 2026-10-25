"""
train_ranker_v3.py - Train improved model with better features
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_val_score, RandomizedSearchCV
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
        print("âŒ career_features_v3.csv not found!")
        print("   Run: python scripts/create_features_v3.py")
        return None
    
    df = pd.read_csv(file_path)
    print(f"âœ… Loaded {len(df)} career profiles")
    return df

def create_training_data_v3(df):
    """Create improved training data"""
    print("\nðŸ”„ Creating improved training data...")
    
    np.random.seed(42)
    X_list = []
    y_list = []
    career_ids = []
    
    # Get feature columns
    feature_cols = [col for col in df.columns if col.startswith(('riasec_', 'has_')) or 
                   col in ['skill_count', 'quality_score']]
    
    if not feature_cols:
        print("âŒ No feature columns found!")
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
    
    print(f"âœ… Created {len(X)} training examples")
    print(f"   Features: {X.shape[1]}")
    print(f"   Labels: min={y.min():.3f}, max={y.max():.3f}, mean={y.mean():.3f}")
    
    return X, y, np.array(career_ids)


def train_model_v3(X, y, groups):
    """Train and evaluate models without career-level data leakage."""
    print("\nTraining with career-grouped validation...")

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y, groups=groups))

    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    train_groups = groups[train_idx]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        "Ridge Regression": Ridge(),
        "Random Forest": RandomForestRegressor(random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42)
    }

    results = {}
    best_model, best_name, best_score = None, "", -float("inf")

    n_splits = min(5, len(set(train_groups)))
    if n_splits < 2:
        raise ValueError("Not enough distinct career groups for cross-validation.")

    cv = GroupKFold(n_splits=n_splits)

    for name, model in models.items():
        print(f"\nTraining {name}...")
        if name == "Random Forest":
            search = RandomizedSearchCV(
                model,
                {
                    "n_estimators": [100, 200, 300],
                    "max_depth": [None, 8, 12, 16],
                    "min_samples_leaf": [1, 2, 4],
                    "min_samples_split": [2, 5, 10]
                },
                n_iter=8, scoring="r2", cv=cv, random_state=42,
                n_jobs=-1, refit=True
            )
        elif name == "Gradient Boosting":
            search = RandomizedSearchCV(
                model,
                {
                    "n_estimators": [100, 200, 300],
                    "max_depth": [2, 3, 4],
                    "learning_rate": [0.03, 0.05, 0.1],
                    "min_samples_leaf": [2, 5, 10],
                    "subsample": [0.7, 0.85, 1.0]
                },
                n_iter=8, scoring="r2", cv=cv, random_state=42,
                n_jobs=-1, refit=True
            )
        else:
            search = RandomizedSearchCV(
                model, {"alpha": [0.01, 0.1, 1.0, 10.0, 100.0]},
                n_iter=5, scoring="r2", cv=cv, random_state=42,
                n_jobs=-1, refit=True
            )

        search.fit(X_train_scaled, y_train, groups=train_groups)
        fitted = search.best_estimator_
        pred = fitted.predict(X_test_scaled)
        test_r2 = r2_score(y_test, pred)
        test_rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
        print(f"  Grouped CV R2: {search.best_score_:.4f}")
        print(f"  Held-out career R2: {test_r2:.4f}; RMSE: {test_rmse:.4f}")
        print(f"  Best parameters: {search.best_params_}")

        results[name] = {
            "cv_mean": float(search.best_score_),
            "cv_std": 0.0,
            "test_r2": float(test_r2),
            "test_rmse": test_rmse,
            "model": fitted
        }

        if test_r2 > best_score:
            best_score, best_model, best_name = test_r2, fitted, name

    joblib.dump(best_model, MODELS_DIR / "career_ranker_v3.pkl")
    joblib.dump(scaler, MODELS_DIR / "scaler_v3.pkl")

    metadata = {
        "model_type": best_name,
        "cv_r2": results[best_name]["cv_mean"],
        "test_r2": float(best_score),
        "features_count": int(X.shape[1]),
        "training_samples": int(len(train_idx)),
        "feature_names": [f"f_{i}" for i in range(X.shape[1])],
        "results": {
            name: {k: v for k, v in result.items() if k != "model"}
            for name, result in results.items()
        },
        "version": "3.1",
        "validation": "GroupShuffleSplit by career ID; GroupKFold tuning"
    }

    with open(MODELS_DIR / "model_metadata_v3.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nBest model: {best_name}")
    print(f"Grouped CV R2: {results[best_name]['cv_mean']:.4f}")
    print(f"Held-out career R2: {best_score:.4f}")
    print(f"Saved model and scaler in: {MODELS_DIR}")
    return results, best_model

def main():
    print("="*60)
    print("ðŸ§  TRAINING IMPROVED MODEL V3")
    print("="*60)
    
    # Load features
    df = load_features()
    if df is None:
        return
    
    # Create training data
    X, y, groups = create_training_data_v3(df)
    if X is None:
        return
    
    # Train model
    train_model_v3(X, y, groups)
    
    print("\n" + "="*60)
    print("âœ… Training complete!")
    print("\nðŸ“‹ NEXT STEPS:")
    print("1. Run: python app.py")
    print("2. Test the improved recommendations")

if __name__ == "__main__":
    main()

