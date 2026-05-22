from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Auction, Bid, User
from backend.schemas import BidCreate, BidResponse, BidWithAuction
from backend.routers.auth import get_current_user
from backend.websocket import manager

router = APIRouter(
    prefix="/bids",
    tags=["Bids"]
)

@router.get("/my-bids", response_model=List[BidWithAuction])
def get_my_bids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the history of all bids placed by the currently authenticated user.
    """
    bids = db.query(Bid).filter(Bid.bidder_id == current_user.id).order_by(Bid.placed_at.desc()).all()
    return bids


@router.post("/{auction_id}", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def place_bid(
    auction_id: int,
    bid_in: BidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Place a new bid on an auction lot.
    Validates that:
    1. The auction lot exists.
    2. The auction is live and has not expired.
    3. The bidder is not the seller.
    4. The bid amount is greater than the current bid (or starting price).
    On success, updates the auction's current bid and broadcasts the new bid via WebSockets.
    """
    # Fetch the auction
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction lot not found"
        )
    
    # 1. Auction must be live
    if auction.status != "live":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot place bid. Auction is currently '{auction.status}'"
        )
    
    if auction.ends_at < datetime.utcnow():
        # Auto-update status if ends_at has passed
        auction.status = "ended"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot place bid. This auction has ended"
        )

    # 2. Seller cannot bid on their own auction
    if auction.seller_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sellers are not permitted to bid on their own auction lots"
        )

    # 3. Bid must exceed current bid or starting price
    min_required_bid = auction.starting_price
    if auction.current_bid is not None:
        min_required_bid = auction.current_bid
        if bid_in.amount <= min_required_bid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bid amount must strictly exceed current bid of ${min_required_bid:.2f}"
            )
    else:
        if bid_in.amount < min_required_bid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bid amount must be at least the starting price of ${min_required_bid:.2f}"
            )

    # Save the new bid
    db_bid = Bid(
        auction_id=auction_id,
        bidder_id=current_user.id,
        amount=bid_in.amount,
        placed_at=datetime.utcnow()
    )
    db.add(db_bid)
    
    # Update current bid on the auction
    auction.current_bid = bid_in.amount
    db.commit()
    db.refresh(db_bid)
    
    # Calculate metadata for broadcast
    total_bids = db.query(Bid).filter(Bid.auction_id == auction_id).count()

    # Broadcast update to all connected WebSocket clients on this auction room
    broadcast_payload = {
        "event": "new_bid",
        "bidder": current_user.full_name,
        "amount": db_bid.amount,
        "total_bids": total_bids,
        "timestamp": db_bid.placed_at.isoformat()
    }
    await manager.broadcast_to_auction(auction_id, broadcast_payload)

    return db_bid


@router.get("/{auction_id}", response_model=List[BidResponse])
def get_bid_history(
    auction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the history of bids placed on a specific auction lot, newest first.
    """
    # Verify auction exists
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction lot not found"
        )
        
    bids = db.query(Bid).filter(Bid.auction_id == auction_id).order_by(Bid.placed_at.desc()).all()
    return bids
