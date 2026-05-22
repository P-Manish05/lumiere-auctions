from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# User / Auth Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


# Bid Schemas
class BidBase(BaseModel):
    amount: float = Field(..., gt=0)

class BidCreate(BidBase):
    pass

class BidResponse(BidBase):
    id: int
    auction_id: int
    bidder_id: int
    placed_at: datetime

    class Config:
        from_attributes = True


# Auction Schemas
class AuctionBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    starting_price: float = Field(..., ge=0)
    reserve_price: Optional[float] = Field(None, ge=0)
    ends_at: datetime
    status: str = "upcoming"
    lot_number: str
    category: Optional[str] = None

class AuctionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    starting_price: float = Field(..., ge=0)
    reserve_price: Optional[float] = Field(None, ge=0)
    ends_at: datetime
    lot_number: str
    category: Optional[str] = None

class AuctionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    starting_price: Optional[float] = None
    reserve_price: Optional[float] = None
    ends_at: Optional[datetime] = None
    status: Optional[str] = None
    lot_number: Optional[str] = None
    category: Optional[str] = None

# Nested / Minimized schemas to avoid recursion
class AuctionMin(BaseModel):
    id: int
    title: str
    status: str
    current_bid: Optional[float] = None
    lot_number: str

    class Config:
        from_attributes = True

# Bid with nested Auction info for dashboard
class BidWithAuction(BidResponse):
    auction: AuctionMin

class AuctionResponse(AuctionBase):
    id: int
    current_bid: Optional[float] = None
    seller_id: int
    bids: List[BidResponse] = []
    bid_count: int = 0

    class Config:
        from_attributes = True
