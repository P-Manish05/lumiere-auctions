from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Auction
from backend.schemas import AuctionCreate, AuctionUpdate, AuctionResponse
from backend.routers.auth import get_current_user

router = APIRouter(
    prefix="/auctions",
    tags=["Auctions"]
)

@router.get("/", response_model=List[AuctionResponse])
def get_auctions(
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all auctions with optional status and category filters.
    """
    query = db.query(Auction)
    if status:
        query = query.filter(Auction.status == status)
    if category:
        query = query.filter(Auction.category == category)
    
    auctions = query.all()
    # Calculate bid count for each auction
    for auction in auctions:
        auction.bid_count = len(auction.bids)
    
    return auctions


@router.get("/{auction_id}", response_model=AuctionResponse)
def get_auction(auction_id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of a single auction lot, including the bid count.
    """
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )
    auction.bid_count = len(auction.bids)
    return auction


@router.post("/", response_model=AuctionResponse, status_code=status.HTTP_201_CREATED)
def create_auction(
    auction_in: AuctionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new auction lot. Requires authentication.
    """
    # Ensure lot number is unique
    existing = db.query(Auction).filter(Auction.lot_number == auction_in.lot_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lot number must be unique"
        )
    
    db_auction = Auction(
        title=auction_in.title,
        description=auction_in.description,
        image_url=auction_in.image_url,
        starting_price=auction_in.starting_price,
        reserve_price=auction_in.reserve_price,
        ends_at=auction_in.ends_at,
        status="upcoming",  # default status
        lot_number=auction_in.lot_number,
        category=auction_in.category,
        seller_id=current_user.id,
        current_bid=None
    )
    
    db.add(db_auction)
    db.commit()
    db.refresh(db_auction)
    db_auction.bid_count = 0
    return db_auction


@router.put("/{auction_id}", response_model=AuctionResponse)
def update_auction(
    auction_id: int,
    auction_update: AuctionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update an auction. Only the seller of the auction can modify it.
    """
    db_auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not db_auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )
    
    # Check ownership
    if db_auction.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this auction lot"
        )
    
    update_data = auction_update.model_dump(exclude_unset=True)
    
    # Check lot number uniqueness if it is being changed
    if "lot_number" in update_data and update_data["lot_number"] != db_auction.lot_number:
        existing = db.query(Auction).filter(Auction.lot_number == update_data["lot_number"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lot number must be unique"
            )
            
    for key, value in update_data.items():
        setattr(db_auction, key, value)
        
    db.commit()
    db.refresh(db_auction)
    db_auction.bid_count = len(db_auction.bids)
    return db_auction


@router.delete("/{auction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auction(
    auction_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete an auction. Only the seller of the auction can delete it.
    """
    db_auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not db_auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )
    
    # Check ownership
    if db_auction.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this auction lot"
        )
        
    db.delete(db_auction)
    db.commit()
    return None
