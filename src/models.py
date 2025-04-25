"""
Core application models using SQLModel.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"


class UserBase(SQLModel):
    """Base user model with common attributes."""
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)
    is_active: bool = True
    role: UserRole = UserRole.USER
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class User(UserBase, table=True):
    """User database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    
    # Relationships
    purchases: List["Purchase"] = Relationship(back_populates="user")
    categories: List["Category"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserRead(UserBase):
    """User response model."""
    id: int


class CategoryType(str, Enum):
    """Category type enumeration."""
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"


class CategoryBase(SQLModel):
    """Base category model with common attributes."""
    name: str = Field(index=True)
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    type: CategoryType = CategoryType.EXPENSE
    is_system: bool = False


class Category(CategoryBase, table=True):
    """Category database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="categories")
    purchases: List["Purchase"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    """Category creation model."""
    pass


class CategoryRead(CategoryBase):
    """Category response model."""
    id: int
    user_id: Optional[int] = None


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_PAYMENT = "mobile_payment"
    OTHER = "other"


class Currency(str, Enum):
    """Common currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    # Add more as needed


class PurchaseBase(SQLModel):
    """Base purchase model with common attributes."""
    amount: float
    description: str
    date: datetime = Field(default_factory=datetime.now)
    payment_method: PaymentMethod = PaymentMethod.OTHER
    currency: Currency = Currency.USD
    notes: Optional[str] = None
    location: Optional[str] = None
    is_recurring: bool = False


class Purchase(PurchaseBase, table=True):
    """Purchase database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    
    # Relationships
    user: User = Relationship(back_populates="purchases")
    category: Optional[Category] = Relationship(back_populates="purchases")


class PurchaseCreate(PurchaseBase):
    """Purchase creation model."""
    category_id: Optional[int] = None


class PurchaseRead(PurchaseBase):
    """Purchase response model."""
    id: int
    user_id: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None
