"""
Web Dashboard - Admin & User Interface
Built with FastAPI + React-ready backend
Allows you to onboard users and monitor everything
"""
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
from colorama import Fore, Style
import config

# Import MongoDB database
try:
    from mongodb_database import MongoTradingDatabase
    MONGODB_AVAILABLE = True
except ImportError:
    print(f"{Fore.RED}❌ MongoDB not available. Install: pip install pymongo{Style.RESET_ALL}")
    MONGODB_AVAILABLE = False
    exit(1)

# Configuration
SECRET_KEY = config.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Initialize FastAPI
app = FastAPI(
    title="Trading Bot API",
    description="Admin Dashboard & User Management API",
    version="2.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    print(f"{Fore.YELLOW}⚠️  Static directory not found. Creating...{Style.RESET_ALL}")
    os.makedirs("static", exist_ok=True)

# Security
security = HTTPBearer()

# Database
db = MongoTradingDatabase()

# Add users collection
users_collection = db.db['users']
subscriptions_collection = db.db['subscriptions']
bot_instances_collection = db.db['bot_instances']


# ============================================================================
# DATA MODELS
# ============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "user"  # user, admin

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class BotConfig(BaseModel):
    user_id: str
    initial_capital: float = 10000
    max_position_size: float = 2.0
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0
    max_open_positions: int = 3
    timeframe: str = "1h"
    paper_trading: bool = True

class SubscriptionCreate(BaseModel):
    user_id: str
    plan: str  # free, pro, enterprise
    payment_method: Optional[str] = None


# ============================================================================
# AUTHENTICATION
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    user = users_collection.find_one({"email": payload.get("sub")})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_admin_user(user: dict = Depends(get_current_user)):
    """Require admin role"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/auth/register")
async def register(user_data: UserCreate):
    """Register new user"""
    # Check if user exists
    if users_collection.find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = {
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "role": user_data.role,
        "created_at": datetime.utcnow(),
        "is_active": True,
        "subscription": "free"
    }
    
    result = users_collection.insert_one(user)
    
    # Create access token
    token = create_access_token({"sub": user_data.email})
    
    return {
        "message": "User created successfully",
        "user_id": str(result.inserted_id),
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    """Login user"""
    user = users_collection.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.get("is_active"):
        raise HTTPException(status_code=401, detail="Account disabled")
    
    token = create_access_token({"sub": credentials.email})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "subscription": user.get("subscription", "free")
        }
    }

@app.get("/api/users/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user info"""
    user.pop("password", None)
    user["_id"] = str(user["_id"])
    return user

@app.get("/api/users")
async def get_all_users(admin: dict = Depends(get_admin_user)):
    """Get all users (admin only)"""
    users = list(users_collection.find())
    for user in users:
        user.pop("password", None)
        user["_id"] = str(user["_id"])
    return users

@app.put("/api/users/{user_id}/activate")
async def activate_user(user_id: str, admin: dict = Depends(get_admin_user)):
    """Activate/deactivate user (admin only)"""
    result = users_collection.update_one(
        {"_id": user_id},
        {"$set": {"is_active": True}}
    )
    return {"message": "User activated"}

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(get_admin_user)):
    """Delete user (admin only)"""
    users_collection.delete_one({"_id": user_id})
    return {"message": "User deleted"}


# ============================================================================
# BOT MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/bots/create")
async def create_bot(config: BotConfig, user: dict = Depends(get_current_user)):
    """Create bot instance for user"""
    bot_instance = {
        "user_id": config.user_id,
        "config": config.dict(),
        "status": "stopped",
        "created_at": datetime.utcnow(),
        "last_active": None
    }
    
    result = bot_instances_collection.insert_one(bot_instance)
    
    return {
        "message": "Bot created successfully",
        "bot_id": str(result.inserted_id)
    }

@app.get("/api/bots/my-bots")
async def get_my_bots(user: dict = Depends(get_current_user)):
    """Get user's bot instances"""
    bots = list(bot_instances_collection.find({"user_id": str(user["_id"])}))
    for bot in bots:
        bot["_id"] = str(bot["_id"])
    return bots

@app.get("/api/bots/{bot_id}/performance")
async def get_bot_performance(bot_id: str, user: dict = Depends(get_current_user)):
    """Get bot performance metrics"""
    # Get trades for this bot
    trades = list(db.trades.find({"bot_id": bot_id, "status": "closed"}))
    
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "profit_factor": 0
        }
    
    stats = db.get_statistics()
    return stats

@app.post("/api/bots/{bot_id}/start")
async def start_bot(bot_id: str, user: dict = Depends(get_current_user)):
    """Start bot instance"""
    bot_instances_collection.update_one(
        {"_id": bot_id},
        {"$set": {"status": "running", "last_active": datetime.utcnow()}}
    )
    return {"message": "Bot started"}

@app.post("/api/bots/{bot_id}/stop")
async def stop_bot(bot_id: str, user: dict = Depends(get_current_user)):
    """Stop bot instance"""
    bot_instances_collection.update_one(
        {"_id": bot_id},
        {"$set": {"status": "stopped"}}
    )
    return {"message": "Bot stopped"}


# ============================================================================
# ADMIN DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/api/admin/overview")
async def admin_overview(admin: dict = Depends(get_admin_user)):
    """Get admin dashboard overview"""
    total_users = users_collection.count_documents({})
    active_users = users_collection.count_documents({"is_active": True})
    total_bots = bot_instances_collection.count_documents({})
    running_bots = bot_instances_collection.count_documents({"status": "running"})
    
    # Get all trades
    total_trades = db.trades.count_documents({})
    total_volume = db.trades.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    
    # Revenue (from subscriptions)
    revenue = subscriptions_collection.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "bots": {
            "total": total_bots,
            "running": running_bots,
            "stopped": total_bots - running_bots
        },
        "trading": {
            "total_trades": total_trades,
            "total_volume": list(total_volume)[0]["total"] if list(total_volume) else 0
        },
        "revenue": {
            "total": list(revenue)[0]["total"] if list(revenue) else 0
        }
    }

@app.get("/api/admin/users/stats")
async def user_stats(admin: dict = Depends(get_admin_user)):
    """Get user statistics"""
    # Users by subscription
    by_subscription = list(users_collection.aggregate([
        {"$group": {"_id": "$subscription", "count": {"$sum": 1}}}
    ]))
    
    # Users by registration date
    by_date = list(users_collection.aggregate([
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": -1}},
        {"$limit": 30}
    ]))
    
    return {
        "by_subscription": by_subscription,
        "by_date": by_date
    }

@app.get("/api/admin/trading/stats")
async def trading_stats(admin: dict = Depends(get_admin_user)):
    """Get trading statistics"""
    # Trades by day
    by_day = list(db.trades.aggregate([
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$entry_time"}},
            "count": {"$sum": 1},
            "total_pnl": {"$sum": "$pnl"}
        }},
        {"$sort": {"_id": -1}},
        {"$limit": 30}
    ]))
    
    # Trades by symbol
    by_symbol = list(db.trades.aggregate([
        {"$group": {
            "_id": "$symbol",
            "count": {"$sum": 1},
            "total_pnl": {"$sum": "$pnl"}
        }},
        {"$sort": {"total_pnl": -1}},
        {"$limit": 10}
    ]))
    
    return {
        "by_day": by_day,
        "by_symbol": by_symbol
    }


# ============================================================================
# SUBSCRIPTION ENDPOINTS
# ============================================================================

@app.post("/api/subscriptions/create")
async def create_subscription(sub_data: SubscriptionCreate, user: dict = Depends(get_current_user)):
    """Create subscription"""
    subscription = {
        "user_id": sub_data.user_id,
        "plan": sub_data.plan,
        "amount": {"free": 0, "pro": 29, "enterprise": 99}[sub_data.plan],
        "status": "active",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=30)
    }
    
    result = subscriptions_collection.insert_one(subscription)
    
    # Update user subscription
    users_collection.update_one(
        {"_id": sub_data.user_id},
        {"$set": {"subscription": sub_data.plan}}
    )
    
    return {
        "message": "Subscription created",
        "subscription_id": str(result.inserted_id)
    }

@app.get("/api/subscriptions/my-subscription")
async def get_my_subscription(user: dict = Depends(get_current_user)):
    """Get user's subscription"""
    subscription = subscriptions_collection.find_one({"user_id": str(user["_id"])})
    if subscription:
        subscription["_id"] = str(subscription["_id"])
    return subscription or {"plan": "free"}


# ============================================================================
# REAL-TIME WEBSOCKET
# ============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/trades")
async def websocket_trades(websocket: WebSocket):
    """Real-time trade updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """Serve user dashboard"""
    return FileResponse("static/user_dashboard.html")

@app.get("/admin")
async def admin_dashboard():
    """Serve admin dashboard"""
    return FileResponse("static/admin_dashboard.html")

@app.get("/api")
async def api_root():
    """API health check"""
    return {
        "status": "online",
        "version": "2.0.0",
        "message": "Trading Bot API is running"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check database
        db.client.server_info()
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow()
    }


# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print(f"{Fore.GREEN}✅ Trading Bot API Started{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 Admin Dashboard: http://localhost:8000/docs{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔌 WebSocket: ws://localhost:8000/ws/trades{Style.RESET_ALL}")
    
    # Create default admin if doesn't exist
    if not users_collection.find_one({"email": "admin@tradingbot.com"}):
        admin = {
            "email": "admin@tradingbot.com",
            "password": hash_password("admin123"),  # Change this!
            "full_name": "Admin User",
            "role": "admin",
            "created_at": datetime.utcnow(),
            "is_active": True,
            "subscription": "enterprise"
        }
        users_collection.insert_one(admin)
        print(f"{Fore.YELLOW}⚠️  Default admin created: admin@tradingbot.com / admin123{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  CHANGE THIS PASSWORD IMMEDIATELY!{Style.RESET_ALL}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
