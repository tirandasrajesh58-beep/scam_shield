"""
Machine Learning Model Training, Comparison & Evaluation Pipeline for Fake Social Media Profiles.
Models evaluated:
1. Logistic Regression (Linear Baseline)
2. Random Forest Classifier (Ensemble Bagging)
3. Gradient Boosting Classifier (Ensemble Boosting)
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

FEATURE_COLUMNS = [
    'followers',
    'following',
    'posts',
    'account_age_days',
    'is_verified',
    'has_profile_pic',
    'has_bio',
    'has_external_link',
    'digits_ratio',
    'following_follower_ratio',
    'posts_per_day'
]

def train_and_evaluate_models():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dataset_path = os.path.join(base_dir, 'datasets', 'social_profiles_dataset.csv')
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)

    # 1. Load dataset
    if not os.path.exists(dataset_path):
        from generate_dataset import generate_profile_dataset
        generate_profile_dataset(1200, dataset_path)

    df = pd.read_csv(dataset_path)
    print("=" * 60)
    print(f"Loaded dataset: {dataset_path} with {len(df)} samples")
    print(f"Class distribution:\n{df['is_fake'].value_counts()}")
    print("=" * 60)

    X = df[FEATURE_COLUMNS]
    y = df['is_fake']

    # 2. Train / Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Training set: {X_train.shape[0]} samples | Testing set: {X_test.shape[0]} samples\n")

    # 3. Model Candidates
    candidates = {
        'Logistic Regression': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(max_iter=1000, random_state=42))
        ]),
        'Random Forest': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42))
        ]),
        'Gradient Boosting': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42))
        ])
    }

    results = {}
    best_model_name = None
    best_f1 = -1.0

    print("Evaluating Candidate Models...")
    print("-" * 60)
    print(f"{'Model Name':<22} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<8} | {'F1-Score':<8} | {'ROC-AUC':<8}")
    print("-" * 60)

    for name, pipeline in candidates.items():
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {
            'accuracy': round(float(acc), 4),
            'precision': round(float(prec), 4),
            'recall': round(float(rec), 4),
            'f1_score': round(float(f1), 4),
            'roc_auc': round(float(roc), 4),
            'confusion_matrix': cm
        }

        print(f"{name:<22} | {acc:.4f}   | {prec:.4f}    | {rec:.4f}   | {f1:.4f}   | {roc:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name

    print("-" * 60)
    print(f"Selected Best Model: {best_model_name} (F1-Score: {best_f1:.4f})\n")

    # 4. Serialize Selected Model
    best_pipeline = candidates[best_model_name]
    model_save_path = os.path.join(models_dir, 'fake_profile_model.joblib')
    joblib.dump(best_pipeline, model_save_path)
    print(f"Saved trained pipeline to: {model_save_path}")

    # Feature Importances (if tree-based)
    clf = best_pipeline.named_steps['clf']
    feature_importances = {}
    if hasattr(clf, 'feature_importances_'):
        importances = clf.feature_importances_
        for col, imp in zip(FEATURE_COLUMNS, importances):
            feature_importances[col] = round(float(imp), 4)
        # Sort by importance descending
        feature_importances = dict(sorted(feature_importances.items(), key=lambda x: x[1], reverse=True))

    # 5. Save Metadata
    metadata = {
        'model_name': best_model_name,
        'features': FEATURE_COLUMNS,
        'metrics': results[best_model_name],
        'all_models_comparison': results,
        'feature_importances': feature_importances,
        'training_timestamp': datetime.now().isoformat(),
        'dataset_sample_size': len(df)
    }

    metadata_path = os.path.join(models_dir, 'profile_model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata to: {metadata_path}")

    return metadata

if __name__ == '__main__':
    train_and_evaluate_models()
