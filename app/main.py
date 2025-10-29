import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from .schemas import ScoreRequest, ScoreResponse, Factor, AlertData
from .deps import load_model, get_model
from .rules import should_alert
from .storage import storage
from .notifier import notifier
from .shap_explain import safe_explain_top_k

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup"""
    try:
        load_model()
        logger.info("Application startup complete")
        yield
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


# Initialize FastAPI app
app = FastAPI(
    title="ML VoIP Alert System",
    description="Cardiac risk prediction with VoIP alerts",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


@app.post("/score", response_model=ScoreResponse)
async def score_patient(request: ScoreRequest):
    """
    Score a patient for cardiac risk and potentially trigger alerts.
    """
    try:
        # Get the loaded model
        model = get_model()
        
        # Convert features to DataFrame for prediction
        features_df = pd.DataFrame([request.features])
        
        # Get prediction probability
        risk_prob = model.predict_proba(features_df)[0][1]  # Probability of positive class
        
        # Get SHAP explanations (safe fallback)
        top_factors = safe_explain_top_k(model, request.features, k=3)
        
        # Convert to Factor objects
        factors = [Factor(feature=f['feature'], impact=f['impact']) for f in top_factors]
        
        # Check if alert should be triggered
        alerted = should_alert(risk_prob, request.patient_ref_token)
        alert_id = None
        
        if alerted:
            # Generate alert ID
            alert_id = f"alrt_{uuid.uuid4().hex[:8]}"
            
            # Create alert data
            alert_data = AlertData(
                alert_id=alert_id,
                patient_token=request.patient_ref_token,
                risk=risk_prob,
                top_factors=factors,
                timestamp=datetime.now().isoformat()
            )
            
            # Save alert
            storage.save_alert(alert_data)
            
            # Set cooldown
            storage.set_cooldown(request.patient_ref_token)
            
            # Send voice notification
            notifier.notify_voice(alert_data)
            
            logger.info(f"Alert triggered for patient {request.patient_ref_token}, risk: {risk_prob:.3f}")
        else:
            logger.info(f"No alert for patient {request.patient_ref_token}, risk: {risk_prob:.3f}")
        
        return ScoreResponse(
            risk=risk_prob,
            top_factors=factors,
            alerted=alerted,
            alert_id=alert_id
        )
        
    except Exception as e:
        logger.error(f"Scoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@app.get("/case/{token}", response_class=HTMLResponse)
async def view_case(request: Request, token: str):
    """
    View case details in HTML format.
    """
    try:
        # Get alert data
        alert = storage.get_alert(token)
        
        if not alert:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Convert to template format
        context = {
            "request": request,
            "token": token,
            "risk": alert.risk,
            "top_factors": alert.top_factors,
            "timestamp": alert.timestamp,
            "alerted": True,
            "alert_id": alert.alert_id
        }
        
        return templates.TemplateResponse("case.html", context)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Case view failed: {e}")
        raise HTTPException(status_code=500, detail=f"Case view failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": get_model() is not None}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ML VoIP Alert System",
        "version": "1.0.0",
        "endpoints": {
            "POST /score": "Score patient for cardiac risk",
            "GET /case/{token}": "View case details",
            "GET /health": "Health check",
            "GET /": "This information"
        }
    }
