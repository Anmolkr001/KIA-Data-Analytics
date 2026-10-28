"""
FastAPI service exposing Lead Conversion Scoring and SHAP Explanations (/predict).
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ask_your_data.lead_scoring.predictor import predict_lead_conversion, get_model_bundle

api_app = FastAPI(
    title="Ask Your Data — Lead Scoring API",
    description="Machine Learning service predicting car dealership enquiry conversion probability with SHAP explanations.",
    version="1.0.0",
)

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LeadFeatures(BaseModel):
    car_model: str = Field(default="SONET", description="Kia vehicle model (e.g. SONET, NEW SELTOS, CARENS)")
    lead_source: str = Field(default="Walkin", description="Source channel (Walkin, Referral, Hyperlocal, Field, Online/CRM)")
    lead_warmth: str = Field(default="Warm", description="CRM stage warmth: Hot, Warm, Cold")
    customer_type: str = Field(default="Individual", description="Individual or Corporate")
    test_drive_done: str = Field(default="No", description="Yes or No")
    city: str = Field(default="BHUBANESWAR", description="Customer location / city")
    exchange_interest: str = Field(default="No", description="Interested in vehicle exchange (Yes/No)")
    fuel_type: str = Field(default="Gasoline", description="Fuel type: Gasoline, Diesel, Electric")
    followup_count: int = Field(default=2, ge=0, le=50, description="Touchpoints completed")
    aging_days: int = Field(default=10, ge=0, description="Days since initial inquiry")
    quotation_count: float = Field(default=0.0, ge=0.0, description="Number of quotation emails sent")


class PredictResponse(BaseModel):
    conversion_probability: float
    conversion_percentage: float
    priority_tier: str
    badge: str
    recommendation: str
    top_shap_factors: List[Dict[str, Any]]
    inputs: Dict[str, Any]


@api_app.get("/health")
async def health_check():
    bundle = get_model_bundle()
    return {
        "status": "healthy",
        "service": "Lead Scoring Predictor",
        "model_loaded": bundle is not None,
        "test_roc_auc": bundle["metrics"]["test_roc_auc"],
        "class_imbalance_ratio": bundle["pos_weight"],
    }


@api_app.get("/model-metrics")
async def get_metrics():
    bundle = get_model_bundle()
    return {
        "metrics": bundle["metrics"],
        "top_global_shap_factors": bundle["top_shap_factors"],
    }


@api_app.post("/predict", response_model=PredictResponse)
async def predict_endpoint(payload: LeadFeatures):
    try:
        features = payload.model_dump()
        result = predict_lead_conversion(features)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    from ask_your_data.config import FASTAPI_HOST, FASTAPI_PORT
    uvicorn.run(api_app, host=FASTAPI_HOST, port=FASTAPI_PORT)
