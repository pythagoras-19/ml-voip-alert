import os
from .storage import storage


def should_alert(risk: float, patient_token: str) -> bool:
    """
    Determine if an alert should be sent based on risk threshold and cooldown.
    
    Args:
        risk: Predicted risk probability (0.0 to 1.0)
        patient_token: Patient reference token
        
    Returns:
        True if alert should be sent, False otherwise
    """
    # Get risk threshold from environment
    risk_threshold = float(os.getenv('RISK_THRESHOLD', '0.80'))
    
    # Check if risk is above threshold
    if risk < risk_threshold:
        return False
    
    # Check if patient is in cooldown period
    if storage.in_cooldown(patient_token):
        return False
    
    return True
