"""
Feature engineering for purchase data analysis.
"""
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def extract_time_features(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Extract time-based features from a date column.
    
    Args:
        df: Input DataFrame
        date_column: Name of the date column
        
    Returns:
        DataFrame with added time features
    """
    # Make a copy to avoid modifying the original
    result = df.copy()
    
    # Check that date column exists
    if date_column not in result.columns:
        raise ValueError(f"Column '{date_column}' not found in DataFrame")
    
    # Extract features
    result['year'] = result[date_column].dt.year
    result['month'] = result[date_column].dt.month
    result['day'] = result[date_column].dt.day
    result['day_of_week'] = result[date_column].dt.dayofweek  # 0=Monday, 6=Sunday
    result['weekend'] = result['day_of_week'] >= 5  # Weekend flag (5=Sat, 6=Sun)
    result['hour'] = result[date_column].dt.hour
    result['quarter'] = result[date_column].dt.quarter
    result['week_of_year'] = result[date_column].dt.isocalendar().week
    
    return result


def calculate_purchase_frequency(
    df: pd.DataFrame, 
    user_id_column: Optional[str] = 'user_id',
    date_column: str = 'date'
) -> pd.DataFrame:
    """
    Calculate purchase frequency metrics.
    
    Args:
        df: DataFrame with purchase data
        user_id_column: Name of user ID column (if None, global metrics are calculated)
        date_column: Name of date column
        
    Returns:
        DataFrame with purchase frequency metrics
    """
    # Make a copy
    result = df.copy()
    
    # Sort by date
    result = result.sort_values(by=date_column)
    
    if user_id_column is not None and user_id_column in result.columns:
        # Calculate days since last purchase for each user
        result['prev_purchase_date'] = result.groupby(user_id_column)[date_column].shift(1)
    else:
        # Calculate global metrics
        result['prev_purchase_date'] = result[date_column].shift(1)
    
    # Calculate days between purchases
    result['days_since_last_purchase'] = (
        result[date_column] - result['prev_purchase_date']
    ).dt.total_seconds() / (24 * 3600)
    
    # Fill NaN for first purchase
    result['days_since_last_purchase'] = result['days_since_last_purchase'].fillna(-1)
    
    return result


def identify_recurring_purchases(
    df: pd.DataFrame,
    description_column: str = 'description',
    amount_column: str = 'amount',
    date_column: str = 'date',
    user_id_column: Optional[str] = 'user_id',
    min_occurrences: int = 3,
    max_amount_variance: float = 0.1,
    max_days_variance: int = 5
) -> pd.DataFrame:
    """
    Identify potentially recurring purchases based on description, amount, and timing.
    
    Args:
        df: Purchase DataFrame
        description_column: Name of description column
        amount_column: Name of amount column
        date_column: Name of date column
        user_id_column: Name of user ID column (if None, global analysis)
        min_occurrences: Minimum number of occurrences to be considered recurring
        max_amount_variance: Maximum allowed variance in amount (0.1 = 10%)
        max_days_variance: Maximum allowed variance in days between occurrences
        
    Returns:
        DataFrame with recurring purchase flag
    """
    result = df.copy()
    
    # Create a simplified description (lowercase, remove special chars, numbers)
    result['simple_desc'] = (
        result[description_column]
        .str.lower()
        .str.replace(r'[^a-z\s]', '', regex=True)
        .str.strip()
    )
    
    # Group by user if user_id_column is provided
    if user_id_column is not None and user_id_column in result.columns:
        group_cols = [user_id_column, 'simple_desc']
    else:
        group_cols = ['simple_desc']
    
    # Count occurrences
    desc_counts = result.groupby(group_cols).size().reset_index(name='occurrences')
    
    # Filter for descriptions with min_occurrences
    recurring_desc = desc_counts[desc_counts['occurrences'] >= min_occurrences]
    
    # Merge back to original data
    result = result.merge(
        recurring_desc[group_cols + ['occurrences']], 
        on=group_cols, 
        how='left'
    )
    
    # Initialize recurring flag
    result['is_recurring'] = False
    
    # For each potential recurring purchase
    for _, desc_row in recurring_desc.iterrows():
        # Filter for this description
        filter_cols = {}
        for col in group_cols:
            filter_cols[col] = desc_row[col]
        
        desc_purchases = result.loc[
            (result[list(filter_cols.keys())] == pd.Series(filter_cols)).all(axis=1)
        ].sort_values(by=date_column)
        
        # Check amount variance
        amount_values = desc_purchases[amount_column].values
        amount_variance = np.std(amount_values) / np.mean(amount_values) if len(amount_values) > 1 else 0
        
        # Check timing variance
        dates = pd.to_datetime(desc_purchases[date_column]).sort_values()
        if len(dates) > 1:
            days_between = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            days_variance = np.std(days_between) if len(days_between) > 1 else 0
        else:
            days_variance = 0
        
        # Update recurring flag if criteria are met
        if amount_variance <= max_amount_variance and days_variance <= max_days_variance:
            idx = desc_purchases.index
            result.loc[idx, 'is_recurring'] = True
    
    # Clean up
    result = result.drop(columns=['simple_desc', 'occurrences'])
    
    return result


def categorize_text(
    df: pd.DataFrame, 
    text_column: str,
    keywords_dict: Dict[str, List[str]]
) -> pd.DataFrame:
    """
    Categorize text based on keywords.
    
    Args:
        df: Input DataFrame
        text_column: Column containing text to categorize
        keywords_dict: Dictionary mapping categories to lists of keywords
        
    Returns:
        DataFrame with added category column
    """
    result = df.copy()
    
    # Initialize category column
    result['derived_category'] = 'Uncategorized'
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = result[text_column].str.lower()
    
    # Check each category's keywords
    for category, keywords in keywords_dict.items():
        # Create a regex pattern matching any of the keywords
        pattern = '|'.join(keywords)
        # Set category where pattern matches
        mask = text_lower.str.contains(pattern, na=False)
        result.loc[mask, 'derived_category'] = category
    
    return result
