"""
Services for handling file imports (CSV, bank statements, etc.)
"""
import csv
from datetime import datetime
from io import StringIO
from typing import Dict, List, Optional, Tuple

import pandas as pd
from fastapi import UploadFile
from pydantic import BaseModel

from src.models import Currency, PaymentMethod, PurchaseCreate


class ImportResult(BaseModel):
    """Result of an import operation."""
    successful_imports: int
    failed_imports: int
    errors: List[str]


class ColumnMapping(BaseModel):
    """Mapping of CSV columns to purchase fields."""
    amount: str
    description: str
    date: str
    category: Optional[str] = None
    payment_method: Optional[str] = None
    currency: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    date_format: str = "%Y-%m-%d"  # Default date format


async def import_from_csv(
    file: UploadFile,
    column_mapping: ColumnMapping,
    category_lookup: Optional[Dict[str, int]] = None,
) -> Tuple[List[PurchaseCreate], ImportResult]:
    """
    Import purchases from a CSV file.
    
    Args:
        file: Uploaded CSV file
        column_mapping: Mapping of CSV columns to purchase fields
        category_lookup: Optional dict mapping category names to IDs
    
    Returns:
        Tuple[List[PurchaseCreate], ImportResult]: List of purchases and import results
    """
    content = await file.read()
    content_str = content.decode("utf-8")
    csv_data = StringIO(content_str)
    
    # Read CSV into DataFrame
    df = pd.read_csv(csv_data)
    
    purchases = []
    errors = []
    failed_imports = 0
    
    # Process each row
    for _, row in df.iterrows():
        try:
            # Extract purchase data using column mapping
            purchase_data = {
                "amount": float(row[column_mapping.amount]),
                "description": str(row[column_mapping.description]),
                "date": datetime.strptime(row[column_mapping.date], column_mapping.date_format),
            }
            
            # Add optional fields if they exist in the mapping
            if column_mapping.payment_method and column_mapping.payment_method in row:
                payment_method_str = row[column_mapping.payment_method].upper()
                try:
                    purchase_data["payment_method"] = PaymentMethod(payment_method_str)
                except ValueError:
                    purchase_data["payment_method"] = PaymentMethod.OTHER
            
            if column_mapping.currency and column_mapping.currency in row:
                currency_str = row[column_mapping.currency].upper()
                try:
                    purchase_data["currency"] = Currency(currency_str)
                except ValueError:
                    purchase_data["currency"] = Currency.USD
            
            if column_mapping.notes and column_mapping.notes in row:
                purchase_data["notes"] = str(row[column_mapping.notes])
            
            if column_mapping.location and column_mapping.location in row:
                purchase_data["location"] = str(row[column_mapping.location])
            
            # Handle category mapping if provided
            if column_mapping.category and column_mapping.category in row and category_lookup:
                category_name = str(row[column_mapping.category])
                if category_name in category_lookup:
                    purchase_data["category_id"] = category_lookup[category_name]
            
            # Create purchase
            purchase = PurchaseCreate(**purchase_data)
            purchases.append(purchase)
            
        except Exception as e:
            failed_imports += 1
            errors.append(f"Error in row {_}: {str(e)}")
    
    result = ImportResult(
        successful_imports=len(purchases),
        failed_imports=failed_imports,
        errors=errors,
    )
    
    return purchases, result
