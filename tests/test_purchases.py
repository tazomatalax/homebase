"""
Tests for purchase-related API endpoints.
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.models import Category, Purchase, User


def test_create_purchase(client: TestClient, test_user: User, test_categories: list[Category], session: Session):
    """Test creating a new purchase."""
    # Get authentication token
    login_data = {
        "username": "testuser",
        "password": "password123",
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    # Create a purchase
    purchase_data = {
        "amount": 25.99,
        "description": "Lunch at Restaurant",
        "date": datetime.now().isoformat(),
        "payment_method": "credit_card",
        "category_id": test_categories[0].id,
    }
    
    response = client.post("/purchases/", json=purchase_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["amount"] == 25.99
    assert data["description"] == "Lunch at Restaurant"
    assert data["payment_method"] == "credit_card"
    assert data["category_id"] == test_categories[0].id
    assert data["category_name"] == test_categories[0].name
    
    # Verify in database
    db_purchase = session.get(Purchase, data["id"])
    assert db_purchase is not None
    assert db_purchase.amount == 25.99
    assert db_purchase.user_id == test_user.id


def test_get_purchases(client: TestClient, test_user: User, test_categories: list[Category], session: Session):
    """Test retrieving purchases."""
    # Create test purchases
    purchases = [
        Purchase(
            amount=25.99,
            description="Lunch",
            user_id=test_user.id,
            category_id=test_categories[0].id,
        ),
        Purchase(
            amount=15.50,
            description="Bus ticket",
            user_id=test_user.id,
            category_id=test_categories[1].id,
        ),
        Purchase(
            amount=30.00,
            description="Movie tickets",
            user_id=test_user.id,
            category_id=test_categories[2].id,
        ),
    ]
    for purchase in purchases:
        session.add(purchase)
    session.commit()
    
    # Get authentication token
    login_data = {
        "username": "testuser",
        "password": "password123",
    }
    response = client.post("/token", data=login_data)
    token_data = response.json()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    # Test get all purchases
    response = client.get("/purchases/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Test filter by category
    response = client.get(f"/purchases/?category_id={test_categories[0].id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Lunch"
    assert data[0]["category_name"] == "Food"


def test_create_purchase_with_invalid_category(client: TestClient, test_user: User, session: Session):
    """Test creating a purchase with an invalid category ID."""
    # Get authentication token
    login_data = {
        "username": "testuser",
        "password": "password123",
    }
    response = client.post("/token", data=login_data)
    token_data = response.json()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    # Try to create purchase with non-existent category ID
    purchase_data = {
        "amount": 25.99,
        "description": "Lunch at Restaurant",
        "date": datetime.now().isoformat(),
        "payment_method": "credit_card",
        "category_id": 9999,  # Non-existent ID
    }
    
    response = client.post("/purchases/", json=purchase_data, headers=headers)
    assert response.status_code == 400
    assert "Invalid category" in response.json()["detail"]
