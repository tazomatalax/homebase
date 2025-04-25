"""
Main FastAPI application.
"""
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from src.database import create_db_and_tables, get_session
from src.models import (
    Category,
    CategoryCreate,
    CategoryRead,
    Purchase,
    PurchaseCreate,
    PurchaseRead,
    User,
    UserCreate,
    UserRead,
)
from src.services.auth import (
    create_access_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
)

app = FastAPI(
    title="PurchaseTracker API",
    description="API for tracking and analyzing purchases",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    create_db_and_tables()

# User endpoints
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """
    Create a new user.
    
    Args:
        user: User data
        session: Database session
        
    Returns:
        Created user
    """
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        is_active=user.is_active,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# Category endpoints
@app.post("/categories/", response_model=CategoryRead)
def create_category(
    category: CategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new category.
    
    Args:
        category: Category data
        session: Database session
        current_user: Authenticated user
        
    Returns:
        Created category
    """
    db_category = Category.from_orm(category, update={"user_id": current_user.id})
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=list[CategoryRead])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get user's categories.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        session: Database session
        current_user: Authenticated user
        
    Returns:
        List of categories
    """
    categories = session.exec(
        select(Category)
        .where(Category.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return categories

# Purchase endpoints
@app.post("/purchases/", response_model=PurchaseRead)
def create_purchase(
    purchase: PurchaseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Record a new purchase.
    
    Args:
        purchase: Purchase data
        session: Database session
        current_user: Authenticated user
        
    Returns:
        Recorded purchase
    """
    # Check if category exists if provided
    if purchase.category_id:
        category = session.get(Category, purchase.category_id)
        if not category or category.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category",
            )
    
    # Create purchase
    db_purchase = Purchase.from_orm(purchase, update={"user_id": current_user.id})
    session.add(db_purchase)
    session.commit()
    session.refresh(db_purchase)
    
    # Add category name to response
    result = PurchaseRead.from_orm(db_purchase)
    if db_purchase.category:
        result.category_name = db_purchase.category.name
    
    return result

@app.get("/purchases/", response_model=list[PurchaseRead])
def get_purchases(
    skip: int = 0,
    limit: int = 100,
    category_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get user's purchases, with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        category_id: Filter by category ID
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        session: Database session
        current_user: Authenticated user
        
    Returns:
        List of purchases
    """
    query = select(Purchase).where(Purchase.user_id == current_user.id)
    
    # Apply filters
    if category_id:
        query = query.where(Purchase.category_id == category_id)
    if start_date:
        query = query.where(Purchase.date >= start_date)
    if end_date:
        query = query.where(Purchase.date <= end_date)
    
    # Execute query with pagination
    purchases = session.exec(query.offset(skip).limit(limit)).all()
    
    # Add category names to responses
    results = []
    for purchase in purchases:
        result = PurchaseRead.from_orm(purchase)
        if purchase.category:
            result.category_name = purchase.category.name
        results.append(result)
    
    return results
