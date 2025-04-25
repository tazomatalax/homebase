"""
Dataset management utilities.
"""
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from sqlmodel import Session, select

from src.models import Purchase, Category, User


def load_purchases_to_dataframe(
    session: Session,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    include_category_names: bool = True
) -> pd.DataFrame:
    """
    Load purchases from the database into a pandas DataFrame.
    
    Args:
        session: Database session
        user_id: Filter by user ID (optional)
        start_date: Filter by start date (optional)
        end_date: Filter by end date (optional)
        include_category_names: Whether to include category names (vs. just IDs)
        
    Returns:
        DataFrame with purchase data
    """
    # Start with base query
    query = select(Purchase)
    
    # Apply filters
    if user_id is not None:
        query = query.where(Purchase.user_id == user_id)
    if start_date is not None:
        query = query.where(Purchase.date >= start_date)
    if end_date is not None:
        query = query.where(Purchase.date <= end_date)
    
    # Execute query
    purchases = session.exec(query).all()
    
    # Convert to DataFrame
    if not purchases:
        # Return empty DataFrame with expected columns
        columns = [
            'id', 'amount', 'description', 'date', 'payment_method', 
            'currency', 'notes', 'location', 'is_recurring', 
            'user_id', 'category_id'
        ]
        if include_category_names:
            columns.append('category_name')
        return pd.DataFrame(columns=columns)
    
    # Convert to dict for DataFrame construction
    purchase_dicts = []
    for purchase in purchases:
        p_dict = {
            'id': purchase.id,
            'amount': purchase.amount,
            'description': purchase.description,
            'date': purchase.date,
            'payment_method': purchase.payment_method,
            'currency': purchase.currency,
            'notes': purchase.notes,
            'location': purchase.location,
            'is_recurring': purchase.is_recurring,
            'user_id': purchase.user_id,
            'category_id': purchase.category_id
        }
        
        # Add category name if requested
        if include_category_names and purchase.category:
            p_dict['category_name'] = purchase.category.name
        elif include_category_names:
            p_dict['category_name'] = 'Uncategorized'
            
        purchase_dicts.append(p_dict)
    
    # Create DataFrame
    df = pd.DataFrame(purchase_dicts)
    
    return df


def save_dataframe_to_purchases(
    df: pd.DataFrame,
    session: Session,
    user_id: int,
    update_existing: bool = False
) -> Tuple[int, int, List[str]]:
    """
    Save a DataFrame of purchases to the database.
    
    Args:
        df: DataFrame with purchase data
        session: Database session
        user_id: User ID to associate purchases with
        update_existing: Whether to update existing purchases (by ID)
        
    Returns:
        Tuple of (num_added, num_updated, errors)
    """
    required_columns = ['amount', 'description']
    
    # Validate required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    num_added = 0
    num_updated = 0
    errors = []
    
    # Process each row
    for _, row in df.iterrows():
        try:
            # Check if this is an update or new purchase
            purchase_id = row.get('id')
            if purchase_id and update_existing:
                # Try to get existing purchase
                purchase = session.get(Purchase, purchase_id)
                if purchase and purchase.user_id == user_id:
                    # Update fields
                    for field, value in row.items():
                        if field != 'id' and hasattr(purchase, field):
                            setattr(purchase, field, value)
                    num_updated += 1
                else:
                    # Not found or wrong user, create new
                    purchase_data = row.to_dict()
                    if 'id' in purchase_data:
                        del purchase_data['id']
                    purchase_data['user_id'] = user_id
                    purchase = Purchase(**purchase_data)
                    session.add(purchase)
                    num_added += 1
            else:
                # Create new purchase
                purchase_data = row.to_dict()
                if 'id' in purchase_data:
                    del purchase_data['id']
                purchase_data['user_id'] = user_id
                purchase = Purchase(**purchase_data)
                session.add(purchase)
                num_added += 1
                
        except Exception as e:
            errors.append(f"Error processing row {_}: {str(e)}")
    
    # Commit changes
    if num_added + num_updated > 0:
        session.commit()
    
    return num_added, num_updated, errors


def export_dataframe_to_csv(
    df: pd.DataFrame,
    output_path: str,
    include_headers: bool = True
) -> None:
    """
    Export a DataFrame to CSV.
    
    Args:
        df: DataFrame to export
        output_path: Path to save CSV file
        include_headers: Whether to include column headers
        
    Returns:
        None
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Export to CSV
    df.to_csv(
        output_path, 
        index=False, 
        header=include_headers
    )


def import_csv_to_dataframe(
    file_path: str,
    column_mapping: Dict[str, str],
    date_format: str = '%Y-%m-%d'
) -> pd.DataFrame:
    """
    Import a CSV file to a DataFrame with column mapping.
    
    Args:
        file_path: Path to CSV file
        column_mapping: Dictionary mapping CSV column names to DataFrame column names
        date_format: Format string for parsing dates
        
    Returns:
        DataFrame with imported and mapped data
    """
    # Read CSV
    df = pd.read_csv(file_path)
    
    # Rename columns based on mapping
    inv_mapping = {v: k for k, v in column_mapping.items()}
    df = df.rename(columns=inv_mapping)
    
    # Convert date columns
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], format=date_format, errors='coerce')
    
    # Convert numeric columns
    if 'amount' in df.columns:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    return df
