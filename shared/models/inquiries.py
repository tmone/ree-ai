"""
Inquiries models for REE AI platform

Handles communication between buyers and sellers.
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class InquiryStatus(str, Enum):
    """Inquiry status"""
    PENDING = "pending"  # Sent, awaiting response
    RESPONDED = "responded"  # Seller responded
    CLOSED = "closed"  # Inquiry closed


class InquiryCreate(BaseModel):
    """Create inquiry (buyer → seller)"""
    property_id: str
    message: str = Field(..., min_length=10, max_length=1000)
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class InquiryResponse(BaseModel):
    """Seller's response to inquiry"""
    message: str = Field(..., min_length=10, max_length=1000)


class InquiryStatusUpdate(BaseModel):
    """Update inquiry status"""
    status: InquiryStatus


class Inquiry(BaseModel):
    """Complete inquiry"""
    id: str
    property_id: str
    sender_id: str  # Buyer
    receiver_id: str  # Seller (property owner)

    # Message
    message: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

    # Response
    response: Optional[str] = None

    # Status
    status: InquiryStatus

    # Timestamps
    created_at: datetime
    responded_at: Optional[datetime] = None


class InquiryWithDetails(BaseModel):
    """Inquiry with property and user details"""
    id: str
    property_id: str
    sender_id: str
    receiver_id: str
    message: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    response: Optional[str] = None
    status: InquiryStatus
    created_at: datetime
    responded_at: Optional[datetime] = None

    # Embedded details
    property: Optional[dict] = None  # PropertyDocument
    sender: Optional[dict] = None  # UserResponse
    receiver: Optional[dict] = None  # UserResponse


class InquiryListResponse(BaseModel):
    """List of inquiries"""
    inquiries: List[InquiryWithDetails]
    total: int
    page: int = 1
    page_size: int = 20


class InquiryStats(BaseModel):
    """Inquiry statistics for seller"""
    total_inquiries: int
    pending_inquiries: int
    responded_inquiries: int
    response_rate: float  # 0.0 to 1.0
    avg_response_time: str  # "2h 30m"
