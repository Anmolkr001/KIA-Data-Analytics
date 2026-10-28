"""
Lead Scoring Predictor with Local SHAP Explanations for Ask Your Data.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import joblib
import numpy as np
import pandas as pd
import shap

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

MODEL_PATH = ROOT_DIR / "models" / "lead_scoring_xgb.joblib"

_MODEL_BUNDLE: Optional[Dict[str, Any]] = None
_EXPLAINER: Optional[shap.TreeExplainer] = None


def get_model_bundle() -> Dict[str, Any]:
    global _MODEL_BUNDLE, _EXPLAINER
    if _MODEL_BUNDLE is None:
        if not MODEL_PATH.exists():
            from ask_your_data.lead_scoring.train import train_and_evaluate_model
            _MODEL_BUNDLE = train_and_evaluate_model()
        else:
            _MODEL_BUNDLE = joblib.load(MODEL_PATH)
        _EXPLAINER = shap.TreeExplainer(_MODEL_BUNDLE["model"])
    return _MODEL_BUNDLE


def predict_lead_conversion(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts lead feature dictionary, returns:
    - conversion_probability: float (0.0 to 1.0)
    - priority_tier: str ('HIGH', 'MEDIUM', 'LOW')
    - action_recommendation: str
    - top_shap_factors: List[Dict[str, Any]] with local attribution
    """
    bundle = get_model_bundle()
    model = bundle["model"]
    preprocessor = bundle["preprocessor"]
    feature_names = bundle["feature_names"]
    global _EXPLAINER
    if _EXPLAINER is None:
        _EXPLAINER = shap.TreeExplainer(model)

    # Format into DataFrame row
    row = pd.DataFrame([{
        "car_model": str(features.get("car_model", "SONET")).strip().upper(),
        "lead_source": str(features.get("lead_source", "Walkin")).strip(),
        "lead_warmth": str(features.get("lead_warmth", "Warm")).strip(),
        "customer_type": str(features.get("customer_type", "Individual")).strip(),
        "test_drive_done": "Yes" if str(features.get("test_drive_done", "No")).strip().lower() in ["yes", "y", "done", "1"] else "No",
        "city_clean": str(features.get("city", "BHUBANESWAR")).strip().upper(),
        "exchange_interest": "Yes" if str(features.get("exchange_interest", "No")).strip().lower() in ["yes", "y", "1"] else "No",
        "fuel_type": str(features.get("fuel_type", "Gasoline")).strip().title(),
        "followup_count": int(features.get("followup_count", 2)),
        "aging_days": int(features.get("aging_days", 10)),
        "quotation_count": float(features.get("quotation_count", 0)),
    }])

    # Preprocess
    X_enc = preprocessor.transform(row)

    # Inference probability
    prob = float(model.predict_proba(X_enc)[0, 1])

    # Local SHAP explanation
    shap_vals = _EXPLAINER.shap_values(X_enc)[0]

    # Rank local features by impact
    indexed_shap = sorted(enumerate(shap_vals), key=lambda x: abs(x[1]), reverse=True)
    top_factors = []
    for idx, impact in indexed_shap[:5]:
        clean_name = feature_names[idx].replace("cat__", "").replace("num__", "").replace("_", " ").title()
        direction = "Positive" if impact > 0 else "Negative"
        top_factors.append({
            "feature": clean_name,
            "raw_feature": feature_names[idx],
            "impact_direction": direction,
            "shap_value": round(float(impact), 4),
            "description": f"{direction} contribution ({impact:+.2f}) to conversion likelihood",
        })

    # Priority Tier
    if prob >= 0.40:
        tier = "HIGH"
        badge = "🔥 High Priority"
        recommendation = "Customer demonstrates prime buying signals. Assign immediately to a senior consultant to close booking receipt within 24 hours."
    elif prob >= 0.15:
        tier = "MEDIUM"
        badge = "🟡 Moderate Priority"
        if row["test_drive_done"].iloc[0] == "No":
            recommendation = "Prospect has solid interest. Primary bottleneck: Test drive pending. Schedule a doorstep test drive immediately."
        else:
            recommendation = "Prospect is evaluating. Provide customized finance/insurance quote and follow up within 48 hours."
    else:
        tier = "LOW"
        badge = "❄️ Low Priority"
        recommendation = "Low current conversion velocity. Enroll in automated marketing WhatsApp/SMS campaigns; avoid exhausting sales capacity."

    return {
        "conversion_probability": round(prob, 4),
        "conversion_percentage": round(prob * 100, 2),
        "priority_tier": tier,
        "badge": badge,
        "recommendation": recommendation,
        "top_shap_factors": top_factors,
        "inputs": features,
    }
