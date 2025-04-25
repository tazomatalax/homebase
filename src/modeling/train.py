"""
Training module for ML models.
"""
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os
import datetime

def prepare_training_data(
    purchases_df: pd.DataFrame,
    text_column: str = 'description',
    category_column: str = 'category_name'
) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Prepare purchase data for training a categorization model.
    
    Args:
        purchases_df: DataFrame with purchase data
        text_column: Column containing text to use for prediction
        category_column: Column containing category labels
        
    Returns:
        Tuple of (X_data, y_labels)
    """
    # Validate columns
    if text_column not in purchases_df.columns:
        raise ValueError(f"Text column '{text_column}' not found in DataFrame")
    if category_column not in purchases_df.columns:
        raise ValueError(f"Category column '{category_column}' not found in DataFrame")
    
    # Remove rows with missing values
    clean_df = purchases_df.dropna(subset=[text_column, category_column])
    
    # Extract features and labels
    X = clean_df[text_column].values
    y = clean_df[category_column].values
    
    return X, y


def train_categorization_model(
    X: np.ndarray,
    y: np.ndarray,
    model_path: str = 'models/category_model.joblib',
    test_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, float]:
    """
    Train a text categorization model and save it to disk.
    
    Args:
        X: Text data
        y: Category labels
        model_path: Path to save model
        test_size: Proportion of data to use for testing
        random_state: Random seed for reproducibility
        
    Returns:
        Dict with model metrics
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Create text classification pipeline
    model = Pipeline([
        ('vectorizer', CountVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )),
        ('classifier', MultinomialNB(alpha=1.0))
    ])
    
    # Train model
    model.fit(X_train, y_train)
    
    # Evaluate
    train_accuracy = model.score(X_train, y_train)
    test_accuracy = model.score(X_test, y_test)
    
    # Save model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    
    # Create metadata about the model
    metadata = {
        'train_accuracy': train_accuracy,
        'test_accuracy': test_accuracy,
        'model_type': 'MultinomialNB',
        'num_categories': len(np.unique(y)),
        'num_samples': len(X),
        'training_date': datetime.datetime.now().isoformat(),
    }
    
    # Save metadata
    metadata_path = os.path.splitext(model_path)[0] + '_metadata.joblib'
    joblib.dump(metadata, metadata_path)
    
    return metadata


def evaluate_model(
    model_path: str,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> Dict[str, float]:
    """
    Evaluate a trained model on test data.
    
    Args:
        model_path: Path to saved model
        X_test: Test text data
        y_test: Test category labels
        
    Returns:
        Dict with evaluation metrics
    """
    # Load model
    model = joblib.load(model_path)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate accuracy
    accuracy = (y_pred == y_test).mean()
    
    # Calculate metrics per category
    categories = np.unique(y_test)
    per_category_accuracy = {}
    
    for category in categories:
        mask = (y_test == category)
        if mask.sum() > 0:  # Avoid division by zero
            cat_accuracy = (y_pred[mask] == y_test[mask]).mean()
            per_category_accuracy[category] = cat_accuracy
    
    return {
        'overall_accuracy': accuracy,
        'per_category_accuracy': per_category_accuracy,
    }
