# ✨ LUMIÈRE AUCTIONS

> A full-stack real-time auction platform for luxury collectibles — fine art, haute horology, rare automobiles, and high jewelry.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square)
![WebSockets](https://img.shields.io/badge/WebSockets-Realtime-gold?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

---

## 🏛️ About

**Lumière Auctions** is a cinematic, dark-themed real-time bidding platform designed for high-end luxury items. It features live countdown timers, real-time WebSocket bid streaming, JWT-based authentication, and a premium UI with gold shimmer animations, glassmorphism, and smooth page transitions.

---

## 🧰 Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core language |
| **FastAPI** | REST API framework |
| **SQLAlchemy** | ORM for database models |
| **SQLite** | Lightweight relational database |
| **Uvicorn** | ASGI server |
| **python-jose** | JWT token generation & validation |
| **bcrypt** | Password hashing |
| **WebSockets** | Real-time bid broadcasting |

### Frontend
| Technology | Purpose |
|---|---|
| **HTML5 / CSS3 / JavaScript** | Core frontend |
| **Tailwind CSS (CDN)** | Utility-first styling |
| **Playfair Display + Inter** | Premium typography via Google Fonts |
| **Material Symbols** | Iconography |
| **WebSocket API** | Real-time bid updates |

---

## 📁 Project Structure

```
lumiere-auctions/
├── backend/
│   ├── main.py              # FastAPI app, CORS, seeding, WebSocket
│   ├── database.py          # SQLAlchemy engine & session
│   ├── models.py            # User, Auction, Bid models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── websocket.py         # WebSocket connection manager
│   └── routers/
│       ├── auth.py           # Register, Login, JWT, /me
│       ├── auctions.py       # CRUD for auctions
│       └── bids.py           # Place bids, bid history
├── frontend/
│   ├── index.html            # Landing page with hero & live lots
│   ├── login.html            # Login & Register with JWT auth
│   ├── auctions.html         # Browse all live auction lots
│   ├── auction-detail.html   # Lot detail with real-time bidding
│   └── dashboard.html        # User dashboard with bid tracking
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/lumiere-auctions.git
cd lumiere-auctions
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Backend Server
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be live at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### 5. Open the Frontend
Open `frontend/index.html` in your browser, or serve the `frontend/` directory with any static file server.

---

## 🔐 Authentication

- **Register**: `POST /auth/register` — JSON body with `email`, `password`, `full_name`
- **Login**: `POST /auth/login` — `application/x-www-form-urlencoded` with `username` (email) and `password`
- **Profile**: `GET /auth/me` — Bearer token required
- Tokens are stored in `localStorage` as `lumiere_token`

---

## ⚡ Key Features

- 🏷️ **Live Auctions** — Real-time countdown timers ticking every second
- 🔄 **WebSocket Bid Streaming** — Instant bid updates across all connected clients
- 🔒 **JWT Authentication** — Secure login/register with bcrypt password hashing
- 📊 **User Dashboard** — Track winning bids, outbid alerts, and full bid history
- ✨ **Premium Animations** — Gold shimmer effects, fade-up transitions, smooth page navigation
- 🍞 **Gold Toast Notifications** — Elegant styled notifications for all user actions
- 🌙 **Dark Luxury Theme** — Cinematic design with glassmorphism and gold accents

---

## 📜 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login with email & password |
| `GET` | `/auth/me` | Get current user profile |
| `GET` | `/auctions` | List all auctions (filter by status) |
| `GET` | `/auctions/{id}` | Get auction details |
| `POST` | `/auctions` | Create an auction (auth required) |
| `GET` | `/bids/{auction_id}` | Get bid history for an auction |
| `POST` | `/bids/{auction_id}` | Place a bid (auth required) |
| `GET` | `/bids/my-bids` | Get current user's bid history |
| `WS` | `/ws/{auction_id}` | WebSocket for real-time bid updates |

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">
  <strong>LUMIÈRE AUCTIONS</strong> — Where extraordinary things find extraordinary people.
</p>
