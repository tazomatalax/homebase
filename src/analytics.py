"""
Data analysis and visualization utilities for purchase data.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure


def get_spending_by_category(
    purchases_df: pd.DataFrame, 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> pd.DataFrame:
    """
    Group spending by category within a date range.
    
    Args:
        purchases_df: DataFrame of purchases
        start_date: Start of date range (optional)
        end_date: End of date range (optional)
        
    Returns:
        DataFrame with category spending totals
    """
    # Filter by date range if provided
    if start_date:
        purchases_df = purchases_df[purchases_df['date'] >= start_date]
    if end_date:
        purchases_df = purchases_df[purchases_df['date'] <= end_date]
        
    # Group by category and sum amounts
    category_spending = purchases_df.groupby('category_name')['amount'].sum().reset_index()
    return category_spending.sort_values('amount', ascending=False)


def get_spending_over_time(
    purchases_df: pd.DataFrame,
    frequency: str = 'M',  # 'D' for daily, 'W' for weekly, 'M' for monthly
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    by_category: bool = False
) -> pd.DataFrame:
    """
    Calculate spending over time, with optional category breakdown.
    
    Args:
        purchases_df: DataFrame of purchases
        frequency: Time grouping frequency ('D', 'W', 'M', etc.)
        start_date: Start of date range (optional)
        end_date: End of date range (optional)
        by_category: Whether to group by category
        
    Returns:
        DataFrame with spending over time
    """
    # Filter by date range if provided
    if start_date:
        purchases_df = purchases_df[purchases_df['date'] >= start_date]
    if end_date:
        purchases_df = purchases_df[purchases_df['date'] <= end_date]
    
    # Add period column based on frequency
    purchases_df['period'] = purchases_df['date'].dt.to_period(frequency)
    
    # Group by period (and category if specified)
    if by_category:
        result = purchases_df.groupby(['period', 'category_name'])['amount'].sum().reset_index()
        # Convert period to datetime for plotting
        result['period'] = result['period'].dt.to_timestamp()
        return result
    else:
        result = purchases_df.groupby(['period'])['amount'].sum().reset_index()
        # Convert period to datetime for plotting
        result['period'] = result['period'].dt.to_timestamp()
        return result


def plot_spending_by_category(category_spending: pd.DataFrame) -> Figure:
    """
    Create a pie chart or bar chart of spending by category.
    
    Args:
        category_spending: DataFrame with category spending totals
        
    Returns:
        Plotly figure object
    """
    fig = px.pie(
        category_spending,
        values='amount',
        names='category_name',
        title='Spending by Category',
        hole=0.4,
    )
    return fig


def plot_spending_trend(time_spending: pd.DataFrame) -> Figure:
    """
    Create a line chart of spending over time.
    
    Args:
        time_spending: DataFrame with spending over time
        
    Returns:
        Plotly figure object
    """
    fig = px.line(
        time_spending,
        x='period',
        y='amount',
        title='Spending Trend',
    )
    return fig


def plot_category_spending_trend(
    time_category_spending: pd.DataFrame,
    top_n_categories: int = 5
) -> Figure:
    """
    Create a stacked area chart of top categories over time.
    
    Args:
        time_category_spending: DataFrame with spending by category over time
        top_n_categories: Number of top categories to include
        
    Returns:
        Plotly figure object
    """
    # Get top categories by total spending
    top_categories = time_category_spending.groupby('category_name')['amount'].sum()\
        .sort_values(ascending=False).head(top_n_categories).index.tolist()
    
    # Filter for top categories
    df_plot = time_category_spending[time_category_spending['category_name'].isin(top_categories)]
    
    fig = px.area(
        df_plot,
        x='period',
        y='amount',
        color='category_name',
        title=f'Spending Trend by Top {top_n_categories} Categories',
        groupnorm='',  # Use '' for raw values, 'percent' for percentage
    )
    return fig
