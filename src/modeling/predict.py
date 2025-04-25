"""
Prediction module for ML models.
"""
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import os
import pandas as pd

from pydantic import BaseModel


class PredictionResult(BaseModel):
    """
    Result of a category prediction.
    
    Attributes:
        category: Predicted category name
        confidence: Confidence score (0-1)
        alternative_categories: Dictionary of alternative categories with scores
    """
    category: str
    confidence: float
    alternative_categories: Dict[str, float] = {}


def load_model(model_path: str = 'models/category_model.joblib'):
    """
    Load a trained model from disk.
    
    Args:
        model_path: Path to the saved model
        
    Returns:
        Loaded model
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    return joblib.load(model_path)


def predict_category(
    text: str,
    model_path: str = 'models/category_model.joblib',
    top_n: int = 3
) -> PredictionResult:
    """
    Predict the category for a purchase description.
    
    Args:
        text: Purchase description text
        model_path: Path to the trained model
        top_n: Number of alternative categories to include
        
    Returns:
        PredictionResult with prediction details
    """
    # Load model
    model = load_model(model_path)
    
    # Get prediction probabilities
    probabilities = model.predict_proba([text])[0]
    
    # Get class names
    classes = model.classes_
    
    # Get the index of the highest probability
    top_idx = np.argmax(probabilities)
    
    # Create result
    result = PredictionResult(
        category=classes[top_idx],
        confidence=float(probabilities[top_idx])
    )
    
    # Add alternative categories
    sorted_indices = np.argsort(probabilities)[::-1]  # Sort in descending order
    alt_categories = {}
    
    for idx in sorted_indices[1:top_n+1]:  # Skip the top one, already used
        if idx < len(classes):
            alt_categories[classes[idx]] = float(probabilities[idx])
    
    result.alternative_categories = alt_categories
    
    return result


def batch_predict_categories(
    texts: List[str],
    model_path: str = 'models/category_model.joblib'
) -> List[PredictionResult]:
    """
    Predict categories for multiple purchase descriptions.
    
    Args:
        texts: List of purchase description texts
        model_path: Path to the trained model
        
    Returns:
        List of PredictionResult objects
    """
    # Load model
    model = load_model(model_path)
    
    # Get class names
    classes = model.classes_
    
    # Get prediction probabilities for all texts
    all_probabilities = model.predict_proba(texts)
    
    results = []
    for probabilities in all_probabilities:
        # Get the index of the highest probability
        top_idx = np.argmax(probabilities)
        
        # Create result
        result = PredictionResult(
            category=classes[top_idx],
            confidence=float(probabilities[top_idx])
        )
        
        # Add alternative categories (top 3)
        sorted_indices = np.argsort(probabilities)[::-1]  # Sort in descending order
        alt_categories = {}
        
        for idx in sorted_indices[1:4]:  # Skip the top one, already used
            if idx < len(classes):
                alt_categories[classes[idx]] = float(probabilities[idx])
        
        result.alternative_categories = alt_categories
        results.append(result)
    
    return results


def update_purchases_with_predictions(
    purchases_df: pd.DataFrame,
    text_column: str = 'description',
    model_path: str = 'models/category_model.joblib',
    confidence_threshold: float = 0.5
) -> pd.DataFrame:
    """
    Update a DataFrame of purchases with predicted categories.
    
    Args:
        purchases_df: DataFrame with purchase data
        text_column: Column containing text to use for prediction
        model_path: Path to the trained model
        confidence_threshold: Minimum confidence to accept prediction
        
    Returns:
        DataFrame with added prediction columns
    """
    # Make a copy to avoid modifying original
    result_df = purchases_df.copy()
    
    # Get descriptions
    descriptions = result_df[text_column].tolist()
    
    # Make predictions
    predictions = batch_predict_categories(descriptions, model_path)
    
    # Add prediction columns
    result_df['predicted_category'] = [p.category for p in predictions]
    result_df['prediction_confidence'] = [p.confidence for p in predictions]
    
    # Add column indicating if prediction should be applied
    result_df['apply_prediction'] = result_df['prediction_confidence'] >= confidence_threshold
    
    return result_df
