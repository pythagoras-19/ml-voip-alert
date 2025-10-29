import os
import joblib
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global model variable
model: Optional[object] = None


def load_model():
    """Load the trained model from disk"""
    global model
    model_path = os.getenv('MODEL_PATH', './models/heart_pipeline.joblib')
    
    try:
        model = joblib.load(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {e}")
        raise


def get_model():
    """Get the loaded model"""
    global model
    if model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    return model
