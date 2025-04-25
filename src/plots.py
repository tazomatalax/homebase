"""
Data visualization utilities.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure


def create_spending_sunburst(
    purchases_df: pd.DataFrame, 
    hierarchy: List[str] = ['category_name', 'payment_method']
) -> Figure:
    """
    Create a sunburst chart showing spending hierarchy.
    
    Args:
        purchases_df: DataFrame of purchases
        hierarchy: List of columns to use as hierarchy levels
        
    Returns:
        Plotly figure object
    """
    # Ensure all hierarchy columns exist
    for col in hierarchy:
        if col not in purchases_df.columns:
            raise ValueError(f"Column {col} not found in DataFrame")
    
    # Group by hierarchy and sum amounts
    grouped = purchases_df.groupby(hierarchy)['amount'].sum().reset_index()
    
    fig = px.sunburst(
        grouped,
        path=hierarchy,
        values='amount',
        title='Spending Distribution',
    )
    return fig


def create_monthly_comparison(
    purchases_df: pd.DataFrame,
    current_month: Optional[datetime] = None,
    num_previous_months: int = 2,
) -> Figure:
    """
    Compare current month spending with previous months.
    
    Args:
        purchases_df: DataFrame of purchases
        current_month: Date in the month to compare (defaults to current month)
        num_previous_months: Number of previous months to include
        
    Returns:
        Plotly figure object
    """
    # Default to current month if not specified
    if current_month is None:
        current_month = datetime.now()
    
    # Add month column
    purchases_df = purchases_df.copy()
    purchases_df['month'] = purchases_df['date'].dt.strftime('%Y-%m')
    
    # Get current and previous months
    months = []
    for i in range(num_previous_months, -1, -1):
        month_date = current_month - pd.DateOffset(months=i)
        months.append(month_date.strftime('%Y-%m'))
    
    # Filter for these months
    filtered_df = purchases_df[purchases_df['month'].isin(months)]
    
    # Group by month and category
    monthly_category = filtered_df.pivot_table(
        index='category_name',
        columns='month',
        values='amount',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Select top categories by total spend across all months
    total_spend = monthly_category.sum(axis=1, numeric_only=True)
    top_categories = monthly_category.loc[
        total_spend.sort_values(ascending=False).index
    ].head(10)
    
    # Create figure
    fig = go.Figure()
    
    # Add a trace for each month
    for month in months:
        if month in top_categories.columns:
            fig.add_trace(go.Bar(
                x=top_categories['category_name'],
                y=top_categories[month],
                name=month,
            ))
    
    fig.update_layout(
        title='Monthly Category Comparison',
        xaxis_title='Category',
        yaxis_title='Amount',
        barmode='group',
    )
    
    return fig


def create_spending_heatmap(purchases_df: pd.DataFrame) -> Figure:
    """
    Create a heatmap of spending by day of week and hour.
    
    Args:
        purchases_df: DataFrame of purchases
        
    Returns:
        Plotly figure object
    """
    # Extract day of week and hour from date
    df = purchases_df.copy()
    df['day_of_week'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    
    # Order days of week correctly
    days_order = [
        'Monday', 'Tuesday', 'Wednesday', 
        'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]
    
    # Group by day and hour
    heatmap_data = df.pivot_table(
        index='day_of_week',
        columns='hour',
        values='amount',
        aggfunc='sum',
        fill_value=0
    )
    
    # Reorder days
    heatmap_data = heatmap_data.reindex(days_order)
    
    # Create heatmap
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Hour of Day", y="Day of Week", color="Spending"),
        x=[str(i) for i in range(24)],
        y=days_order,
        title="Spending Patterns by Day and Time",
        color_continuous_scale="Viridis",
    )
    
    return fig


def export_plots_to_pdf(figures: List[Figure], filename: str) -> None:
    """
    Export a list of plotly figures to a PDF report.
    
    Args:
        figures: List of plotly figures
        filename: Output PDF filename
        
    Returns:
        None
    """
    from plotly.io import write_image
    import matplotlib.backends.backend_pdf
    
    pdf = matplotlib.backends.backend_pdf.PdfPages(filename)
    
    for fig in figures:
        # Convert plotly figure to matplotlib
        fig_bytes = fig.to_image(format="png")
        
        # Create matplotlib figure from image
        plt_fig = plt.figure(figsize=(8.5, 11))
        plt.imshow(fig_bytes)
        plt.axis('off')
        
        # Add to PDF
        pdf.savefig(plt_fig)
        plt.close()
    
    pdf.close()
