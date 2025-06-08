"""
Transaction and deal models
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class DealStatus(Enum):
    """Deal status enumeration"""
    CREATED = "created"
    FUNDED = "funded" 
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class Deal:
    """Deal model"""
    deal_id: str
    creator_id: int
    description: str
    amount: float
    terms: str
    status: DealStatus = DealStatus.CREATED
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'deal_id': self.deal_id,
            'creator_id': self.creator_id,
            'description': self.description,
            'amount': self.amount,
            'terms': self.terms,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Deal':
        """Create from dictionary"""
        return cls(
            deal_id=data['deal_id'],
            creator_id=data['creator_id'],
            description=data['description'],
            amount=data['amount'],
            terms=data['terms'],
            status=DealStatus(data.get('status', 'created')),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

@dataclass
class Payment:
    """Payment model"""
    payment_id: str
    deal_id: str
    payer_id: int
    amount: float
    payment_method: str
    reference_id: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'payment_id': self.payment_id,
            'deal_id': self.deal_id,
            'payer_id': self.payer_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'reference_id': self.reference_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        """Create from dictionary"""
        return cls(
            payment_id=data['payment_id'],
            deal_id=data['deal_id'],
            payer_id=data['payer_id'],
            amount=data['amount'],
            payment_method=data['payment_method'],
            reference_id=data.get('reference_id'),
            status=PaymentStatus(data.get('status', 'pending')),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )

@dataclass
class User:
    """User model"""
    user_id: int
    username: Optional[str]
    first_name: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create from dictionary"""
        return cls(
            user_id=data['user_id'],
            username=data.get('username'),
            first_name=data['first_name'],
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )

@dataclass
class DealStats:
    """Deal statistics model"""
    total_deals: int = 0
    active_deals: int = 0
    completed_deals: int = 0
    disputed_deals: int = 0
    cancelled_deals: int = 0
    total_value: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_deals': self.total_deals,
            'active_deals': self.active_deals,
            'completed_deals': self.completed_deals,
            'disputed_deals': self.disputed_deals,
            'cancelled_deals': self.cancelled_deals,
            'total_value': self.total_value
        }

def format_amount(amount: float) -> str:
    """Format amount for display"""
    return f"₹{amount:,.2f}"

def format_deal_id(deal_id: str) -> str:
    """Format deal ID for display"""
    return f"#{deal_id}"

def get_status_emoji(status: str) -> str:
    """Get emoji for status"""
    status_emojis = {
        'created': '⏳',
        'funded': '💰',
        'completed': '✅',
        'disputed': '⚠️',
        'cancelled': '❌'
    }
    return status_emojis.get(status, '🔒')

def validate_deal_data(description: str, amount: float, terms: str) -> tuple[bool, str]:
    """Validate deal creation data"""
    
    if not description or len(description.strip()) < 10:
        return False, "Description must be at least 10 characters"
    
    if len(description.strip()) > 500:
        return False, "Description must be less than 500 characters"
    
    if amount <= 0:
        return False, "Amount must be greater than 0"
    
    if amount < 100:
        return False, "Minimum amount is ₹100"
    
    if amount > 500000:
        return False, "Maximum amount is ₹5,00,000"
    
    if not terms or len(terms.strip()) < 20:
        return False, "Terms must be at least 20 characters"
    
    if len(terms.strip()) > 1000:
        return False, "Terms must be less than 1000 characters"
    
    return True, "Valid"
