import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def explain_top_k(model, features: Dict[str, Any], k: int = 3) -> List[Dict[str, Any]]:
    """
    Generate SHAP explanations for top K features.
    Falls back gracefully if SHAP is not available or model is not supported.
    
    Args:
        model: Trained scikit-learn model
        features: Dictionary of feature values
        k: Number of top features to return
        
    Returns:
        List of dictionaries with 'feature' and 'impact' keys
    """
    try:
        import shap
        
        # Convert features to DataFrame
        feature_df = pd.DataFrame([features])
        
        # Try TreeExplainer for tree-based models
        if hasattr(model, 'tree_') or hasattr(model, 'estimators_'):
            try:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(feature_df)
                
                # Handle binary classification (get positive class)
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]  # Positive class
                
                # Get feature names
                feature_names = feature_df.columns.tolist()
                
                # Create feature importance pairs
                feature_impacts = []
                for i, (name, value) in enumerate(zip(feature_names, shap_values[0])):
                    feature_impacts.append({
                        'feature': name,
                        'impact': float(abs(value))  # Use absolute value for impact
                    })
                
                # Sort by impact and return top k
                feature_impacts.sort(key=lambda x: x['impact'], reverse=True)
                return feature_impacts[:k]
                
            except Exception as e:
                logger.warning(f"TreeExplainer failed: {e}")
        
        # Try LinearExplainer for linear models
        elif hasattr(model, 'coef_'):
            try:
                explainer = shap.LinearExplainer(model, feature_df)
                shap_values = explainer.shap_values(feature_df)
                
                # Get feature names
                feature_names = feature_df.columns.tolist()
                
                # Create feature importance pairs
                feature_impacts = []
                for i, (name, value) in enumerate(zip(feature_names, shap_values[0])):
                    feature_impacts.append({
                        'feature': name,
                        'impact': float(abs(value))
                    })
                
                # Sort by impact and return top k
                feature_impacts.sort(key=lambda x: x['impact'], reverse=True)
                return feature_impacts[:k]
                
            except Exception as e:
                logger.warning(f"LinearExplainer failed: {e}")
        
        # Fallback to permutation importance
        return _permutation_importance_fallback(model, features, k)
        
    except ImportError:
        logger.warning("SHAP not available, using permutation importance fallback")
        return _permutation_importance_fallback(model, features, k)
    except Exception as e:
        logger.warning(f"SHAP explanation failed: {e}")
        return _permutation_importance_fallback(model, features, k)


def _permutation_importance_fallback(model, features: Dict[str, Any], k: int = 3) -> List[Dict[str, Any]]:
    """
    Fallback method using simple feature importance or random sampling.
    """
    try:
        # Try to get feature importance from model
        if hasattr(model, 'feature_importances_'):
            feature_names = list(features.keys())
            importances = model.feature_importances_
            
            # Create feature importance pairs
            feature_impacts = []
            for name, importance in zip(feature_names, importances):
                feature_impacts.append({
                    'feature': name,
                    'impact': float(importance)
                })
            
            # Sort by impact and return top k
            feature_impacts.sort(key=lambda x: x['impact'], reverse=True)
            return feature_impacts[:k]
        
        # If no feature importance available, return empty list
        logger.warning("No feature importance available, returning empty explanation")
        return []
        
    except Exception as e:
        logger.warning(f"Permutation importance fallback failed: {e}")
        return []


def safe_explain_top_k(model, features: Dict[str, Any], k: int = 3) -> List[Dict[str, Any]]:
    """
    Safe wrapper that never raises exceptions.
    Always returns a list, even if empty.
    """
    try:
        return explain_top_k(model, features, k)
    except Exception as e:
        logger.error(f"All explanation methods failed: {e}")
        return []
