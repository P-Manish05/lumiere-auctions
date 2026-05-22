from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    auctions = relationship("Auction", back_populates="seller")
    bids = relationship("Bid", back_populates="bidder")


class Auction(Base):
    __tablename__ = "auctions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    starting_price = Column(Float, nullable=False)
    current_bid = Column(Float, nullable=True, default=None)
    reserve_price = Column(Float, nullable=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ends_at = Column(DateTime, nullable=False)
    status = Column(String, default="upcoming")  # live, ended, upcoming
    lot_number = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=True)

    # Relationships
    seller = relationship("User", back_populates="auctions")
    bids = relationship("Bid", back_populates="auction")


class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey("auctions.id"), nullable=False)
    bidder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    placed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    auction = relationship("Auction", back_populates="bids")
    bidder = relationship("User", back_populates="bids")
