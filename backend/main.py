from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base, SessionLocal
from backend.routers import auth, auctions, bids
from backend.websocket import manager

# Create database tables
Base.metadata.create_all(bind=engine)

# Database seeding logic
def seed_database():
    from backend.models import User, Auction
    from backend.routers.auth import get_password_hash
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        # Check if auctions table is empty
        if db.query(Auction).count() == 0:
            print("Seeding database with default luxury auctions...")
            
            # 1. Create a system seller
            seller = db.query(User).filter(User.email == "system_seller@lumiere.com").first()
            if not seller:
                seller = User(
                    email="system_seller@lumiere.com",
                    password_hash=get_password_hash("lumiere_system_2026"),
                    full_name="Lumière System Seller"
                )
                db.add(seller)
                db.commit()
                db.refresh(seller)

            # 2. Seed 3 luxury auctions with ends_at set to 48 hours from now
            ends_at_time = datetime.utcnow() + timedelta(hours=48)
            
            watch = Auction(
                title="Rolex Cosmograph Daytona 'Paul Newman' Ref. 6239",
                description="An exceptionally rare and highly sought-after vintage Rolex Cosmograph Daytona with 'Paul Newman' exotic white-and-black dial. Pristine condition with original box and papers.",
                image_url="https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=800&q=80",
                starting_price=25000.0,
                current_bid=None,
                reserve_price=28000.0,
                seller_id=seller.id,
                ends_at=ends_at_time,
                status="live",
                lot_number="LOT-DAYTONA-001",
                category="Watches"
            )
            
            car = Auction(
                title="Porsche 911 Carrera RS 2.7 (1973)",
                description="One of the most iconic vintage sports cars of all time. Fully restored matching-numbers chassis, finished in classic Grand Prix White with blue lettering and Carrera decals.",
                image_url="https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&q=80",
                starting_price=85000.0,
                current_bid=None,
                reserve_price=95000.0,
                seller_id=seller.id,
                ends_at=ends_at_time,
                status="live",
                lot_number="LOT-PORSCHE-002",
                category="Classic Cars"
            )
            
            art = Auction(
                title="Symphony of the Azure Valley",
                description="A magnificent, large-scale abstract oil canvas by contemporary French artist, featuring vibrant brushstrokes, rich textures, and deep layered cobalt and azure tones.",
                image_url="https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=800&q=80",
                starting_price=12000.0,
                current_bid=None,
                reserve_price=15000.0,
                seller_id=seller.id,
                ends_at=ends_at_time,
                status="live",
                lot_number="LOT-AZUREART-003",
                category="Fine Art"
            )
            
            db.add_all([watch, car, art])
            db.commit()
            print("Database seeding completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

# Run seed
seed_database()

app = FastAPI(
    title="Lumière Auctions API",
    description="Backend API for the Lumière Auctions real-time bidding platform",
    version="1.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(auctions.router)
app.include_router(bids.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Lumière Auctions API. Access docs at /docs"}

# WebSocket endpoint for real-time bid updates
@app.websocket("/ws/{auction_id}")
async def websocket_endpoint(websocket: WebSocket, auction_id: int):
    await manager.connect(websocket, auction_id)
    try:
        while True:
            # Keep connection alive; clients listen for broadcasts
            # If clients send message (e.g. heartbeat), we receive it to keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, auction_id)
    except Exception:
        manager.disconnect(websocket, auction_id)
