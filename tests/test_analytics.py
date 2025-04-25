"""
Tests for analytics functions.
"""
from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.analytics import (
    get_spending_by_category,
    get_spending_over_time,
    plot_category_spending_trend,
    plot_spending_by_category,
    plot_spending_trend,
)


@pytest.fixture
def sample_purchases_df():
    """Create a sample DataFrame of purchases for testing."""
    # Create sample data
    data = {
        'amount': [10.50, 25.99, 5.25, 18.75, 50.00, 12.49, 8.99, 30.00],
        'description': [
            'Coffee', 'Dinner', 'Snack', 'Lunch', 'Groceries', 
            'Movie ticket', 'Book', 'Gas'
        ],
        'category_name': [
            'Food', 'Food', 'Food', 'Food', 'Groceries',
            'Entertainment', 'Entertainment', 'Transportation'
        ],
        'date': [
            datetime.now() - timedelta(days=i) for i in range(8)
        ]
    }
    return pd.DataFrame(data)


def test_get_spending_by_category(sample_purchases_df):
    """Test grouping spending by category."""
    result = get_spending_by_category(sample_purchases_df)
    
    assert len(result) == 3  # Should have 3 categories
    assert 'category_name' in result.columns
    assert 'amount' in result.columns
    
    # Check totals by category
    food_total = result[result['category_name'] == 'Food']['amount'].values[0]
    entertainment_total = result[result['category_name'] == 'Entertainment']['amount'].values[0]
    transportation_total = result[result['category_name'] == 'Transportation']['amount'].values[0]
    
    assert food_total == pytest.approx(60.49)  # 10.50 + 25.99 + 5.25 + 18.75
    assert entertainment_total == pytest.approx(21.48)  # 12.49 + 8.99
    assert transportation_total == pytest.approx(30.0)  # 30.00


def test_get_spending_over_time(sample_purchases_df):
    """Test calculating spending over time."""
    # Test daily aggregation
    daily_result = get_spending_over_time(sample_purchases_df, frequency='D')
    assert len(daily_result) == 8  # 8 days of data
    
    # Test monthly aggregation
    monthly_result = get_spending_over_time(sample_purchases_df, frequency='M')
    assert len(monthly_result) == 1  # All data in the same month
    
    # Test with category breakdown
    category_result = get_spending_over_time(
        sample_purchases_df, frequency='D', by_category=True
    )
    assert 'category_name' in category_result.columns
    assert len(category_result) > 8  # Multiple categories per day


def test_plotting_functions(sample_purchases_df):
    """Test that plotting functions return proper figure objects."""
    # Test category spending plot
    category_spending = get_spending_by_category(sample_purchases_df)
    fig1 = plot_spending_by_category(category_spending)
    assert hasattr(fig1, 'data')
    assert len(fig1.data) > 0
    
    # Test spending trend plot
    time_spending = get_spending_over_time(sample_purchases_df, frequency='D')
    fig2 = plot_spending_trend(time_spending)
    assert hasattr(fig2, 'data')
    assert len(fig2.data) > 0
    
    # Test category spending trend plot
    time_category_spending = get_spending_over_time(
        sample_purchases_df, frequency='D', by_category=True
    )
    fig3 = plot_category_spending_trend(time_category_spending, top_n_categories=2)
    assert hasattr(fig3, 'data')
    assert len(fig3.data) == 2  # Should have 2 categories
