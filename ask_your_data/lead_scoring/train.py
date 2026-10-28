"""
Gradient Boosted Lead Conversion Model Training with Class Imbalance & SHAP Explanations.
Saves model artifacts to models/lead_scoring_xgb.joblib.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from typing import Dict, Any, Tuple

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from ask_your_data.config import ROOT_DIR
from ask_your_data.data_loader import load_dataset

MODELS_DIR = ROOT_DIR / "models"
MODEL_PATH = MODELS_DIR / "lead_scoring_xgb.joblib"
METRICS_PATH = MODELS_DIR / "model_metrics.json"

CATEGORICAL_FEATURES = [
    "car_model",
    "lead_source",
    "lead_warmth",
    "customer_type",
    "test_drive_done",
    "city_clean",
    "exchange_interest",
    "fuel_type",
]

NUMERICAL_FEATURES = [
    "followup_count",
    "aging_days",
    "quotation_count",
]


def prepare_training_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Extracts and cleans features and target from raw dataset."""
    data = pd.DataFrame()

    # Target
    target = df["is_converted"].astype(int)

    # Categorical mappings
    data["car_model"] = df["car_model"].fillna("UNKNOWN").astype(str).str.strip().str.upper()
    data["lead_source"] = df["lead_source"].fillna("UNKNOWN").astype(str).str.strip()
    data["lead_warmth"] = df["lead_warmth"].fillna("UNKNOWN").astype(str).str.strip()
    data["customer_type"] = df.get("Customer Type", pd.Series("Individual", index=df.index)).fillna("Individual").astype(str).str.strip()
    data["test_drive_done"] = df["test_drive_done"].fillna("No").astype(str).str.strip()

    # Group rare cities into 'OTHER'
    top_cities = df["city_clean"].value_counts().head(8).index.tolist()
    data["city_clean"] = df["city_clean"].apply(lambda x: x if x in top_cities else "OTHER")

    # Exchange interest
    exchange_col = df.get("Interested in Exchange(Y/N)", pd.Series("N", index=df.index)).fillna("N").astype(str).str.strip().str.upper()
    data["exchange_interest"] = np.where(exchange_col == "Y", "Yes", "No")

    # Fuel type
    fuel_col = df.get("Fuel type", pd.Series("Gasoline", index=df.index)).fillna("Gasoline").astype(str).str.strip().str.title()
    data["fuel_type"] = fuel_col

    # Numerical features
    data["followup_count"] = pd.to_numeric(df.get("Followup Count", 0), errors="coerce").fillna(0).astype(int)
    data["aging_days"] = pd.to_numeric(df.get("enquiry aging days", 0), errors="coerce").fillna(0).astype(int)
    data["quotation_count"] = pd.to_numeric(df.get("Total Quotation Email Count", 0), errors="coerce").fillna(0).astype(float)

    return data, target


def train_and_evaluate_model() -> Dict[str, Any]:
    """
    Trains XGBoost model with class imbalance compensation,
    evaluates using Stratified 5-Fold Cross Validation,
    computes SHAP feature importance, and saves artifacts.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    print("--- [1/4] Loading and preparing CRM dataset for Lead Scoring ---")
    df = load_dataset()
    X, y = prepare_training_features(df)

    n_pos = int(y.sum())
    n_neg = int(len(y) - n_pos)
    pos_weight = round(n_neg / n_pos, 2)
    print(f"Total dataset: {len(X)} leads | Retail Deliveries: {n_pos} ({n_pos/len(X):.2%}) | Ratio: 1:{pos_weight}")

    # Build Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
            (
                "num",
                StandardScaler(),
                NUMERICAL_FEATURES,
            ),
        ]
    )

    # -----------------------------------------------------------------
    # Cross Validation (5-Fold Stratified)
    # -----------------------------------------------------------------
    print("--- [2/4] Running 5-Fold Stratified Cross Validation ---")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_roc_aucs = []
    cv_pr_aucs = []
    cv_precisions = []
    cv_recalls = []
    cv_f1s = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]

        X_tr_enc = preprocessor.fit_transform(X_tr)
        X_val_enc = preprocessor.transform(X_val)

        fold_model = XGBClassifier(
            n_estimators=120,
            max_depth=4,
            learning_rate=0.05,
            scale_pos_weight=pos_weight,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="logloss",
        )
        fold_model.fit(X_tr_enc, y_tr)

        val_probs = fold_model.predict_proba(X_val_enc)[:, 1]
        val_preds = (val_probs >= 0.5).astype(int)

        cv_roc_aucs.append(roc_auc_score(y_val, val_probs))
        cv_pr_aucs.append(average_precision_score(y_val, val_probs))
        cv_precisions.append(precision_score(y_val, val_preds, zero_division=0))
        cv_recalls.append(recall_score(y_val, val_preds, zero_division=0))
        cv_f1s.append(f1_score(y_val, val_preds, zero_division=0))

    cv_results = {
        "mean_roc_auc": round(float(np.mean(cv_roc_aucs)), 4),
        "std_roc_auc": round(float(np.std(cv_roc_aucs)), 4),
        "mean_pr_auc": round(float(np.mean(cv_pr_aucs)), 4),
        "mean_precision": round(float(np.mean(cv_precisions)), 4),
        "mean_recall": round(float(np.mean(cv_recalls)), 4),
        "mean_f1": round(float(np.mean(cv_f1s)), 4),
    }
    print(f"  CV ROC-AUC: {cv_results['mean_roc_auc']} ± {cv_results['std_roc_auc']}")
    print(f"  CV PR-AUC (Avg Precision): {cv_results['mean_pr_auc']}")
    print(f"  CV Recall (Lead Capture): {cv_results['mean_recall']}")

    # -----------------------------------------------------------------
    # Train Final Model (80/20 Stratified Split)
    # -----------------------------------------------------------------
    print("--- [3/4] Fitting Production Model & Computing SHAP Values ---")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    X_train_enc = preprocessor.fit_transform(X_train)
    X_test_enc = preprocessor.transform(X_test)

    # Feature names from preprocessor
    cat_feature_names = preprocessor.named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    feature_names = cat_feature_names + NUMERICAL_FEATURES

    final_model = XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.05,
        scale_pos_weight=pos_weight,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss",
    )
    final_model.fit(X_train_enc, y_train)

    test_probs = final_model.predict_proba(X_test_enc)[:, 1]
    test_roc_auc = round(float(roc_auc_score(y_test, test_probs)), 4)
    test_pr_auc = round(float(average_precision_score(y_test, test_probs)), 4)

    # Compute SHAP Explanations
    explainer = shap.TreeExplainer(final_model)
    shap_values = explainer.shap_values(X_test_enc)

    # Calculate global mean |SHAP| feature importance
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_indices = np.argsort(mean_abs_shap)[::-1][:15]

    top_shap_factors = []
    for idx in top_indices:
        top_shap_factors.append({
            "feature": feature_names[idx],
            "importance": round(float(mean_abs_shap[idx]), 4),
        })

    print(f"  Final Holdout ROC-AUC: {test_roc_auc} | PR-AUC: {test_pr_auc}")
    print("  Top 5 Global SHAP Drivers of Conversion:")
    for f in top_shap_factors[:5]:
        print(f"    • {f['feature']}: {f['importance']}")

    # -----------------------------------------------------------------
    # Save Artifacts
    # -----------------------------------------------------------------
    print("--- [4/4] Saving Model & Preprocessor Artifacts ---")
    model_bundle = {
        "model": final_model,
        "preprocessor": preprocessor,
        "feature_names": feature_names,
        "categorical_features": CATEGORICAL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "pos_weight": pos_weight,
        "metrics": {
            "cv": cv_results,
            "test_roc_auc": test_roc_auc,
            "test_pr_auc": test_pr_auc,
        },
        "top_shap_factors": top_shap_factors,
    }

    joblib.dump(model_bundle, MODEL_PATH)
    print(f"Saved model bundle: {MODEL_PATH}")

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "cv_metrics": cv_results,
            "test_roc_auc": test_roc_auc,
            "test_pr_auc": test_pr_auc,
            "top_shap_factors": top_shap_factors,
        }, f, indent=2)

    return model_bundle


if __name__ == "__main__":
    train_and_evaluate_model()
