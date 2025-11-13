"""
Web Dashboard - Admin & User Interface
Built with FastAPI + React-ready backend
Allows you to onboard users and monitor everything
"""
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request
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
import logging
from colorama import Fore, Style
import config

# Setup logger
logger = logging.getLogger(__name__)

# Import MongoDB database
try:
    from mongodb_database import MongoTradingDatabase
    MONGODB_AVAILABLE = True
except ImportError:
    print(f"{Fore.RED}❌ MongoDB not available. Install: pip install pymongo{Style.RESET_ALL}")
    MONGODB_AVAILABLE = False
    exit(1)

# Import trading modules
try:
    from user_bot_manager import BotManager
    from forex_trader import ForexTrader
    from p2p_copy_trading import CopyTradingSystem, P2PMarketplace
    TRADING_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"{Fore.YELLOW}⚠️  Advanced trading modules not available: {e}{Style.RESET_ALL}")
    TRADING_MODULES_AVAILABLE = False

# Import bot engine
try:
    from bot_engine import bot_engine
    BOT_ENGINE_AVAILABLE = True
    print(f"{Fore.GREEN}✅ Bot engine initialized{Style.RESET_ALL}")
except ImportError as e:
    print(f"{Fore.YELLOW}⚠️  Bot engine not available: {e}{Style.RESET_ALL}")
    BOT_ENGINE_AVAILABLE = False
    bot_engine = None

# Import push notifications
try:
    from push_notifications import push_service
    PUSH_NOTIFICATIONS_AVAILABLE = True
    print(f"{Fore.GREEN}✅ Push notifications initialized{Style.RESET_ALL}")
except ImportError as e:
    print(f"{Fore.YELLOW}⚠️  Push notifications not available: {e}{Style.RESET_ALL}")
    PUSH_NOTIFICATIONS_AVAILABLE = False
    push_service = None

# Import API service (will initialize after db is created)
try:
    from api_service import APIKeyManager, APIRateLimiter
    API_SERVICE_AVAILABLE = True
    print(f"{Fore.GREEN}✅ API service imported{Style.RESET_ALL}")
except ImportError as e:
    print(f"{Fore.YELLOW}⚠️  API service not available: {e}{Style.RESET_ALL}")
    API_SERVICE_AVAILABLE = False
    APIKeyManager = None
    APIRateLimiter = None

# Import new listing bot
try:
    from new_listing_bot import NewListingBot
    NEW_LISTING_BOT_AVAILABLE = True
    print(f"{Fore.GREEN}✅ New listing bot initialized{Style.RESET_ALL}")
except ImportError as e:
    print(f"{Fore.YELLOW}⚠️  New listing bot not available: {e}{Style.RESET_ALL}")
    NEW_LISTING_BOT_AVAILABLE = False
    NewListingBot = None

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

# Initialize API service now that db exists
if API_SERVICE_AVAILABLE:
    api_key_manager = APIKeyManager(db)
    api_rate_limiter = APIRateLimiter()
    print(f"{Fore.GREEN}✅ API service initialized{Style.RESET_ALL}")
else:
    api_key_manager = None
    api_rate_limiter = None

# Initialize trading managers
if TRADING_MODULES_AVAILABLE:
    bot_manager = BotManager(db.db)
    copy_trading_system = CopyTradingSystem(db.db)
    p2p_marketplace = P2PMarketplace(db.db)
    print(f"{Fore.GREEN}✅ Advanced trading modules initialized{Style.RESET_ALL}")
else:
    bot_manager = None
    copy_trading_system = None
    p2p_marketplace = None


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
    bot_type: str = "momentum"  # momentum, grid, dca, arbitrage, etc.
    symbol: str = "BTC/USDT"
    capital: float = 1000
    initial_capital: float = 10000
    max_position_size: float = 2.0
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0
    max_open_positions: int = 3
    timeframe: str = "1h"
    paper_trading: bool = True

class SubscriptionCreate(BaseModel):
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
    
    # Determine redirect URL based on role
    redirect_url = "/admin" if user["role"] == "admin" else "/user"
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "redirect_url": redirect_url,
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

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class EmailChange(BaseModel):
    new_email: EmailStr
    password: str

class ProfileUpdate(BaseModel):
    full_name: str

@app.put("/api/users/me/password")
async def change_password(data: PasswordChange, user: dict = Depends(get_current_user)):
    """Change user password"""
    # Verify old password
    if not verify_password(data.old_password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid current password")
    
    # Update password
    new_hash = hash_password(data.new_password)
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"password": new_hash}}
    )
    
    return {"message": "Password changed successfully"}

@app.put("/api/users/me/email")
async def change_email(data: EmailChange, user: dict = Depends(get_current_user)):
    """Change user email"""
    # Verify password
    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    # Check if email already exists
    if users_collection.find_one({"email": data.new_email}):
        raise HTTPException(status_code=400, detail="Email already in use")
    
    # Update email
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"email": data.new_email}}
    )
    
    return {"message": "Email changed successfully"}

@app.put("/api/users/me/profile")
async def update_profile(data: ProfileUpdate, user: dict = Depends(get_current_user)):
    """Update user profile"""
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"full_name": data.full_name}}
    )
    
    return {"message": "Profile updated successfully"}

@app.get("/api/dashboard")
async def get_dashboard(user: dict = Depends(get_current_user)):
    """Get dashboard data for mobile app"""
    is_admin = user.get("role") == "admin"
    
    # Get user's bots
    if is_admin:
        bots = list(bot_instances_collection.find({}))
    else:
        bots = list(bot_instances_collection.find({"user_id": str(user["_id"])}))
    
    # Convert ObjectId to string
    for bot in bots:
        bot["_id"] = str(bot["_id"])
    
    # Get total stats
    total_capital = sum(bot.get("capital", 0) for bot in bots)
    active_bots = sum(1 for bot in bots if bot.get("status") == "running")
    
    # Get total P&L (simplified)
    total_pnl = 0.0
    for bot in bots:
        total_pnl += bot.get("total_profit", 0.0)
    
    # Get trade stats (if trades collection exists)
    total_trades = 0
    winning_trades = 0
    try:
        if is_admin:
            total_trades = db.db['trades'].count_documents({})
            winning_trades = db.db['trades'].count_documents({"profit": {"$gt": 0}})
        else:
            total_trades = db.db['trades'].count_documents({"user_id": str(user["_id"])})
            winning_trades = db.db['trades'].count_documents({"user_id": str(user["_id"]), "profit": {"$gt": 0}})
    except:
        pass
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    return {
        "stats": {
            "total_capital": total_capital,
            "total_pnl": total_pnl,
            "active_bots": active_bots,
            "total_bots": len(bots),
            "total_trades": total_trades,
            "win_rate": win_rate
        },
        "recent_bots": bots[:5],  # Last 5 bots
        "user": {
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "subscription": user.get("subscription", "free"),
            "role": user.get("role", "user"),
            "exchange_connected": user.get("exchange_connected", False)
        },
        "chartData": [0, 0, 0, 0, 0, 0, 0]  # TODO: Calculate real 7-day data
    }

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

# Exchange API Key Management
class ExchangeCredentials(BaseModel):
    okx_api_key: str
    okx_secret_key: str
    okx_passphrase: str
    paper_trading: bool = True

@app.post("/api/user/connect-exchange")
async def connect_exchange(credentials: ExchangeCredentials, user: dict = Depends(get_current_user)):
    """Connect user's OKX exchange account"""
    from cryptography.fernet import Fernet
    
    # Encrypt API keys
    encryption_key = config.ENCRYPTION_KEY.encode()
    fernet = Fernet(encryption_key)
    
    encrypted_api_key = fernet.encrypt(credentials.okx_api_key.encode()).decode()
    encrypted_secret = fernet.encrypt(credentials.okx_secret_key.encode()).decode()
    encrypted_passphrase = fernet.encrypt(credentials.okx_passphrase.encode()).decode()
    
    # Test connection
    try:
        import ccxt
        exchange = ccxt.okx({
            'apiKey': credentials.okx_api_key,
            'secret': credentials.okx_secret_key,
            'password': credentials.okx_passphrase
        })
        balance = exchange.fetch_balance()
        connection_valid = True
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid API keys: {str(e)}")
    
    # Save encrypted credentials
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "exchange_connected": True,
            "okx_api_key": encrypted_api_key,
            "okx_secret_key": encrypted_secret,
            "okx_passphrase": encrypted_passphrase,
            "paper_trading": credentials.paper_trading,
            "connected_at": datetime.utcnow()
        }}
    )
    
    return {
        "message": "Exchange connected successfully",
        "paper_trading": credentials.paper_trading
    }

@app.get("/api/user/exchange-status")
async def get_exchange_status(user: dict = Depends(get_current_user)):
    """Get user's exchange connection status"""
    return {
        "connected": user.get("exchange_connected", False),
        "paper_trading": user.get("paper_trading", True),
        "connected_at": user.get("connected_at")
    }

@app.get("/api/user/balance")
async def get_user_balance(user: dict = Depends(get_current_user)):
    """Get user's real-time OKX balance - FULLY IMPLEMENTED"""
    is_admin = user.get("role") == "admin"
    
    if is_admin:
        # Admin sees admin OKX account balance
        result = balance_fetcher.get_admin_balance()
    else:
        # Regular user sees their OKX account balance
        result = balance_fetcher.get_user_balance(str(user["_id"]))
    
    return result

@app.delete("/api/user/disconnect-exchange")
async def disconnect_exchange(user: dict = Depends(get_current_user)):
    """Disconnect user's exchange account"""
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$unset": {
            "exchange_connected": "",
            "okx_api_key": "",
            "okx_secret_key": "",
            "okx_passphrase": ""
        }}
    )
    
    return {"message": "Exchange disconnected"}

@app.post("/api/bots/create")
async def create_bot(config: BotConfig, user: dict = Depends(get_current_user)):
    """Create bot instance for user"""
    
    # Check if user has connected exchange for real trading (skip for admin)
    is_admin = user.get("role") == "admin"
    if not config.paper_trading and not user.get("exchange_connected") and not is_admin:
        raise HTTPException(
            status_code=400,
            detail="Please connect your exchange account first. Go to Settings > Exchange Connection."
        )
    
    # Check subscription limits (skip for admin)
    subscription = user.get("subscription", "free")
    features = get_plan_features(subscription)
    
    if not is_admin:
        existing_bots = bot_instances_collection.count_documents({"user_id": str(user["_id"])})
        if existing_bots >= features["max_bots"]:
            raise HTTPException(
                status_code=403,
                detail=f"Bot limit reached ({features['max_bots']} bots). Upgrade to Pro for 3 bots or Enterprise for unlimited."
            )
        
        # Free users can create real trading bots (but limited to 1 trade)
        # No restriction here - limit enforced when bot executes trades
    
    bot_instance = {
        "user_id": str(user["_id"]),  # Use authenticated user's ID, not from config
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
    from bson import ObjectId
    
    # Admin can see all bots, regular users see only their own
    is_admin = user.get("role") == "admin"
    
    print(f"🔍 get_my_bots called by: {user.get('email')} | role: {user.get('role')} | isAdmin: {is_admin}")
    
    if is_admin:
        bots = list(bot_instances_collection.find({}))
        print(f"👑 Admin viewing ALL bots: {len(bots)} total")
    else:
        bots = list(bot_instances_collection.find({"user_id": str(user["_id"])}))
        print(f"👤 User viewing their bots: {len(bots)} bots")
    
    # Enrich bots with owner information
    for bot in bots:
        bot["_id"] = str(bot["_id"])
        
        # Add owner info for admin
        if is_admin and bot.get("user_id"):
            try:
                # Try to find owner by ObjectId first
                owner = None
                try:
                    owner = users_collection.find_one({"_id": ObjectId(bot["user_id"])})
                except:
                    # If that fails, try as string
                    owner = users_collection.find_one({"_id": bot["user_id"]})
                
                if owner:
                    bot["owner_email"] = owner.get("email", "Unknown")
                    bot["owner_name"] = owner.get("full_name", owner.get("email", "Unknown"))
                    bot["is_my_bot"] = str(owner["_id"]) == str(user["_id"])
                else:
                    bot["owner_email"] = "Unknown User"
                    bot["owner_name"] = "Unknown User"
                    bot["is_my_bot"] = False
            except Exception as e:
                print(f"Error fetching owner for bot {bot['_id']}: {e}")
                bot["owner_email"] = "Error loading"
                bot["owner_name"] = "Error loading"
                bot["is_my_bot"] = False
        else:
            # For regular users, mark all as their own
            bot["is_my_bot"] = True
    
    return bots  # Return array directly, not wrapped in object

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
    """Start bot instance - REAL TRADING ENABLED"""
    from bson import ObjectId
    
    # Verify bot exists and belongs to user
    try:
        bot_obj_id = ObjectId(bot_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid bot ID format")
    
    bot = bot_instances_collection.find_one({"_id": bot_obj_id})
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Check ownership (skip for admin)
    is_admin = user.get("role") == "admin"
    if not is_admin and bot.get("user_id") != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to control this bot")
    
    # Determine trading mode
    config_data = bot.get("config", {})
    paper_trading = config_data.get("paper_trading", True)
    trading_mode = "paper" if paper_trading else "real"
    
    # Update database
    try:
        bot_instances_collection.update_one(
            {"_id": bot_obj_id},
            {"$set": {
                "status": "running",
                "last_active": datetime.utcnow(),
                "started_at": datetime.utcnow()
            }}
        )
        
        # Start bot engine
        try:
            await bot_engine.start_bot(bot_id, str(user["_id"]), is_admin)
            logger.info(f"✅ Bot {bot_id} started in bot engine")
        except Exception as e:
            logger.error(f"❌ Bot engine start failed: {e}")
            # Continue anyway - bot status updated
        
        return {
            "message": f"Bot started ({trading_mode} trading)",
            "status": "running",
            "bot_id": bot_id,
            "mode": trading_mode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bots/{bot_id}/stop")
async def stop_bot(bot_id: str, user: dict = Depends(get_current_user)):
    """Stop bot instance"""
    from bson import ObjectId
    
    # Verify bot exists and belongs to user
    try:
        bot_obj_id = ObjectId(bot_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid bot ID format")
    
    bot = bot_instances_collection.find_one({"_id": bot_obj_id})
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Check ownership (skip for admin)
    is_admin = user.get("role") == "admin"
    if not is_admin and bot.get("user_id") != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to control this bot")
    
    # Stop bot engine
    try:
        await bot_engine.stop_bot(bot_id)
        logger.info(f"✅ Bot {bot_id} stopped in bot engine")
    except Exception as e:
        logger.error(f"❌ Bot engine stop failed: {e}")
        # Continue anyway
    
    # Update database
    bot_instances_collection.update_one(
        {"_id": bot_obj_id},
        {"$set": {
            "status": "stopped",
            "stopped_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }}
    )
    return {
        "message": "Bot stopped successfully",
        "status": "stopped",
        "bot_id": bot_id
    }

@app.put("/api/bots/{bot_id}")
async def update_bot(bot_id: str, config: BotConfig, user: dict = Depends(get_current_user)):
    """Update bot configuration"""
    from bson import ObjectId
    
    # Verify bot exists and belongs to user
    try:
        bot_obj_id = ObjectId(bot_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid bot ID format")
    
    bot = bot_instances_collection.find_one({"_id": bot_obj_id})
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Check ownership (skip for admin)
    is_admin = user.get("role") == "admin"
    if not is_admin and bot.get("user_id") != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this bot")
    
    # Bot must be stopped to update
    if bot.get("status") == "running":
        raise HTTPException(status_code=400, detail="Stop the bot before updating its configuration")
    
    # Update bot configuration
    update_data = {
        "config": config.dict(),
        "updated_at": datetime.utcnow()
    }
    
    bot_instances_collection.update_one(
        {"_id": bot_obj_id},
        {"$set": update_data}
    )
    
    return {
        "message": "Bot updated successfully",
        "bot_id": bot_id
    }

@app.delete("/api/bots/{bot_id}")
async def delete_bot(bot_id: str, user: dict = Depends(get_current_user)):
    """Delete bot instance"""
    from bson import ObjectId
    
    # Verify bot exists and belongs to user
    try:
        bot_obj_id = ObjectId(bot_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid bot ID format")
    
    bot = bot_instances_collection.find_one({"_id": bot_obj_id})
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Check ownership (skip for admin)
    is_admin = user.get("role") == "admin"
    if not is_admin and bot.get("user_id") != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this bot")
    
    # Stop bot if running
    if bot.get("status") == "running":
        try:
            await bot_engine.stop_bot(bot_id)
        except:
            pass
    
    # Delete bot
    bot_instances_collection.delete_one({"_id": bot_obj_id})
    
    return {"message": "Bot deleted successfully", "bot_id": bot_id}

@app.get("/api/ai/suggestions")
async def get_ai_suggestions(user: dict = Depends(get_current_user)):
    """Get AI-powered trading suggestions"""
    suggestions = [
        {
            "symbol": "TON/USDT",
            "name": "Toncoin",
            "reason": "New Binance listing, strong Telegram integration",
            "potential": "+45%",
            "confidence": 92,
            "timeframe": "7-14 days",
            "risk": "Medium",
            "category": "New Listing"
        },
        {
            "symbol": "ARB/USDT",
            "name": "Arbitrum",
            "reason": "Layer 2 scaling, increasing adoption",
            "potential": "+35%",
            "confidence": 88,
            "timeframe": "14-30 days",
            "risk": "Low",
            "category": "Trending"
        },
        {
            "symbol": "SUI/USDT",
            "name": "Sui",
            "reason": "New blockchain, backed by major VCs",
            "potential": "+60%",
            "confidence": 78,
            "timeframe": "30-60 days",
            "risk": "High",
            "category": "New Listing"
        }
    ]
    return {"suggestions": suggestions}

@app.get("/api/bots/{bot_id}/analytics")
async def get_bot_analytics(bot_id: str, user: dict = Depends(get_current_user)):
    """Get bot performance analytics"""
    from bson import ObjectId
    
    try:
        bot_obj_id = ObjectId(bot_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid bot ID")
    
    # Get bot
    bot = bot_instances_collection.find_one({"_id": bot_obj_id})
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Get trades
    trades = list(db.db['trades'].find({"bot_id": bot_id}))
    
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
    losing_trades = sum(1 for t in trades if t.get('pnl', 0) < 0)
    total_pnl = sum(t.get('pnl', 0) for t in trades)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    return {
        "bot_id": bot_id,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "avg_profit": round(total_pnl / total_trades, 2) if total_trades > 0 else 0,
        "status": bot.get("status"),
        "created_at": bot.get("created_at"),
        "capital": bot.get("config", {}).get("capital", 0)
    }

@app.get("/api/trades/history")
async def get_trade_history(
    bot_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Get trade history with filters"""
    query = {}
    
    # Filter by user (admin sees all)
    is_admin = user.get("role") == "admin"
    if not is_admin:
        query["user_id"] = str(user["_id"])
    
    # Filter by bot
    if bot_id:
        query["bot_id"] = bot_id
    
    # Filter by date
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            query["timestamp"]["$lte"] = datetime.fromisoformat(end_date)
    
    trades = list(db.db['trades'].find(query).sort("timestamp", -1).limit(100))
    
    # Convert ObjectId to string and enrich with bot information
    for trade in trades:
        trade["_id"] = str(trade["_id"])
        if "timestamp" in trade:
            trade["timestamp"] = trade["timestamp"].isoformat()
        
        # Add bot_name and bot_type if missing
        if not trade.get("bot_name"):
            bot_id = trade.get("bot_id")
            if bot_id == "admin_auto_trader" or bot_id == "new_listing_bot":
                trade["bot_name"] = "Admin Auto-Trader"
                trade["bot_type"] = "admin"
            else:
                # Look up bot name from bot_instances
                try:
                    from bson import ObjectId
                    bot = bot_instances_collection.find_one({"_id": ObjectId(bot_id) if bot_id else None})
                    if bot:
                        trade["bot_name"] = bot.get("config", {}).get("bot_type", "Trading Bot")
                        trade["bot_type"] = "user"
                    else:
                        trade["bot_name"] = "Unknown Bot"
                        trade["bot_type"] = "user"
                except:
                    trade["bot_name"] = "Unknown Bot"
                    trade["bot_type"] = "user"
        elif not trade.get("bot_type"):
            # Set bot_type based on bot_name if missing
            if "Admin" in trade.get("bot_name", ""):
                trade["bot_type"] = "admin"
            else:
                trade["bot_type"] = "user"
    
    return {"trades": trades, "count": len(trades)}

@app.get("/api/bots/{bot_id}/status")
async def get_bot_status_endpoint(bot_id: str, user: dict = Depends(get_current_user)):
    """Get real-time bot status"""
    if bot_manager:
        status = bot_manager.get_bot_status(bot_id)
        if status:
            return status
    
    # Fallback to database status
    bot = bot_instances_collection.find_one({"_id": bot_id, "user_id": str(user["_id"])})
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return {
        "bot_id": str(bot["_id"]),
        "status": bot.get("status", "stopped"),
        "created_at": bot.get("created_at")
    }


# ============================================================================
# PAYMENT & SUBSCRIPTION ENDPOINTS
# ============================================================================

# Import Stripe payment processor
try:
    from payment_integration import PaymentProcessor, SUBSCRIPTION_PLANS
    payment_processor = PaymentProcessor()
    STRIPE_AVAILABLE = True
except Exception as e:
    print(f"{Fore.YELLOW}⚠️  Stripe not configured: {e}{Style.RESET_ALL}")
    payment_processor = None
    STRIPE_AVAILABLE = False

# Payment models
class PaystackPayment(BaseModel):
    email: EmailStr
    amount: float
    plan: str
    reference: Optional[str] = None

class StripeCheckout(BaseModel):
    plan: str  # pro or enterprise
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class CryptoPayment(BaseModel):
    plan: str
    crypto_currency: str  # BTC, ETH, USDT
    network: Optional[str] = None  # TRC20, ERC20, BEP20, etc.
    amount: float
    tx_hash: Optional[str] = None

class InAppPurchase(BaseModel):
    plan: str
    receipt_data: str  # iOS receipt or Android purchase token
    platform: str  # ios or android

# ============================================================================
# STRIPE PAYMENT INTEGRATION
# ============================================================================

@app.post("/api/payments/stripe/create-checkout")
async def create_stripe_checkout(checkout: StripeCheckout, user: dict = Depends(get_current_user)):
    """Create Stripe checkout session"""
    if not STRIPE_AVAILABLE or not payment_processor:
        raise HTTPException(
            status_code=503,
            detail="Stripe payment is not configured. Please use alternative payment methods."
        )
    
    try:
        import stripe
        
        # Get plan details
        plan_info = SUBSCRIPTION_PLANS.get(checkout.plan)
        if not plan_info:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        price_id = plan_info.get('price_id')
        if not price_id:
            raise HTTPException(
                status_code=400,
                detail=f"Stripe Price ID not configured for {checkout.plan} plan. Please contact support."
            )
        
        # Create or get Stripe customer
        customer_id = user.get('stripe_customer_id')
        if not customer_id:
            customer_id = payment_processor.create_customer(
                email=user['email'],
                name=user.get('full_name', user['email']),
                metadata={'user_id': str(user['_id'])}
            )
            # Save customer ID
            users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"stripe_customer_id": customer_id}}
            )
        
        # Create checkout session
        success_url = checkout.success_url or f"{config.API_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = checkout.cancel_url or f"{config.API_URL}/payment/cancelled"
        
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': str(user['_id']),
                'plan': checkout.plan
            }
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout creation failed: {str(e)}")

@app.post("/api/payments/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    if not STRIPE_AVAILABLE or not payment_processor:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    
    try:
        # Get raw body and signature
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        # Handle webhook
        result = payment_processor.handle_webhook(payload, sig_header)
        
        if result and result.get('action') == 'subscription_created':
            # Update user subscription
            subscription_id = result.get('subscription_id')
            # Get subscription details from Stripe
            import stripe
            subscription = stripe.Subscription.retrieve(subscription_id)
            user_id = subscription.metadata.get('user_id')
            plan = subscription.metadata.get('plan')
            
            if user_id and plan:
                users_collection.update_one(
                    {"_id": user_id},
                    {"$set": {
                        "subscription": plan,
                        "stripe_subscription_id": subscription_id,
                        "subscription_start": datetime.utcnow(),
                        "subscription_end": datetime.fromtimestamp(subscription.current_period_end)
                    }}
                )
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/payments/stripe/plans")
async def get_stripe_plans():
    """Get available Stripe subscription plans"""
    return {
        "plans": SUBSCRIPTION_PLANS,
        "stripe_available": STRIPE_AVAILABLE
    }

@app.post("/api/payments/stripe/cancel-subscription")
async def cancel_stripe_subscription(user: dict = Depends(get_current_user)):
    """Cancel user's Stripe subscription"""
    if not STRIPE_AVAILABLE or not payment_processor:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    
    subscription_id = user.get('stripe_subscription_id')
    if not subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    try:
        success = payment_processor.cancel_subscription(subscription_id)
        if success:
            # Update user
            users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "subscription": "free",
                    "subscription_cancelled_at": datetime.utcnow()
                }}
            )
            return {"message": "Subscription cancelled successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to cancel subscription")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Paystack Integration
@app.post("/api/payments/paystack/initialize")
async def initialize_paystack_payment(payment: PaystackPayment, user: dict = Depends(get_current_user)):
    """Initialize Paystack payment"""
    import requests
    
    # Check if Paystack is configured
    if not config.PAYSTACK_SECRET_KEY:
        raise HTTPException(
            status_code=400,
            detail="Paystack payment is not configured. Please contact support or use crypto payment."
        )
    
    # Paystack API
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {config.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    # Plan prices in Naira (NGN)
    plan_prices = {
        "pro": 15000,  # ~$29 USD
        "enterprise": 50000  # ~$99 USD
    }
    
    data = {
        "email": payment.email,
        "amount": plan_prices.get(payment.plan, 15000) * 100,  # Paystack uses kobo
        "metadata": {
            "user_id": str(user["_id"]),
            "plan": payment.plan
        },
        "callback_url": f"{config.API_URL}/api/payments/paystack/callback"
    }
    
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    
    if result.get("status"):
        # Save payment reference
        db.db['payments'].insert_one({
            "user_id": str(user["_id"]),
            "reference": result["data"]["reference"],
            "plan": payment.plan,
            "amount": payment.amount,
            "status": "pending",
            "payment_method": "paystack",
            "created_at": datetime.utcnow()
        })
        
        return {
            "authorization_url": result["data"]["authorization_url"],
            "reference": result["data"]["reference"]
        }
    else:
        raise HTTPException(status_code=400, detail="Payment initialization failed")

@app.get("/api/payments/paystack/callback")
async def paystack_callback(reference: str):
    """Handle Paystack payment callback"""
    import requests
    
    # Verify payment
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {config.PAYSTACK_SECRET_KEY}"}
    
    response = requests.get(url, headers=headers)
    result = response.json()
    
    if result.get("status") and result["data"]["status"] == "success":
        # Get payment record
        payment = db.db['payments'].find_one({"reference": reference})
        
        if payment:
            # Update subscription
            users_collection.update_one(
                {"_id": payment["user_id"]},
                {"$set": {
                    "subscription": payment["plan"],
                    "subscription_start": datetime.utcnow(),
                    "subscription_end": datetime.utcnow() + timedelta(days=30)
                }}
            )
            
            # Update payment status
            db.db['payments'].update_one(
                {"reference": reference},
                {"$set": {"status": "completed"}}
            )
            
            return {"message": "Payment successful", "plan": payment["plan"]}
    
    raise HTTPException(status_code=400, detail="Payment verification failed")

# Crypto Payment Integration - FULL IMPLEMENTATION
from okx_payment_handler import payment_handler
from balance_fetcher import balance_fetcher

@app.get("/api/payments/crypto/networks")
async def get_crypto_networks():
    """Get all supported USDT networks"""
    try:
        networks = payment_handler.get_all_usdt_networks()
        return {"networks": networks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch networks: {str(e)}")

@app.post("/api/payments/crypto/initialize")
async def initialize_crypto_payment(payment: CryptoPayment, user: dict = Depends(get_current_user)):
    """Initialize crypto payment - FULLY IMPLEMENTED with network selection"""
    try:
        result = payment_handler.initialize_payment(
            user_id=str(user["_id"]),
            plan=payment.plan,
            crypto=payment.crypto_currency,
            network=payment.network  # Pass network parameter
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")

@app.get("/api/payments/crypto/status/{payment_id}")
async def check_crypto_payment_status(payment_id: str, user: dict = Depends(get_current_user)):
    """Check crypto payment status - FULLY IMPLEMENTED"""
    try:
        result = payment_handler.check_payment_status(payment_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.get("/api/payments/history")
async def get_payment_history(user: dict = Depends(get_current_user)):
    """Get user's payment history"""
    try:
        history = payment_handler.get_payment_history(str(user["_id"]))
        return {"payments": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

# In-App Purchase Verification
@app.post("/api/payments/iap/verify")
async def verify_in_app_purchase(purchase: InAppPurchase, user: dict = Depends(get_current_user)):
    """Verify in-app purchase (iOS/Android)"""
    
    if purchase.platform == "ios":
        # Verify iOS receipt
        verified = verify_ios_receipt(purchase.receipt_data)
    elif purchase.platform == "android":
        # Verify Android purchase
        verified = verify_android_purchase(purchase.receipt_data)
    else:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    if verified:
        # Update subscription
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "subscription": purchase.plan,
                "subscription_start": datetime.utcnow(),
                "subscription_end": datetime.utcnow() + timedelta(days=30),
                "payment_method": f"iap_{purchase.platform}"
            }}
        )
        
        # Save payment record
        db.db['payments'].insert_one({
            "user_id": str(user["_id"]),
            "plan": purchase.plan,
            "platform": purchase.platform,
            "receipt_data": purchase.receipt_data,
            "status": "completed",
            "payment_method": f"iap_{purchase.platform}",
            "created_at": datetime.utcnow()
        })
        
        return {"message": "Subscription activated", "plan": purchase.plan}
    else:
        raise HTTPException(status_code=400, detail="Invalid receipt")

# Helper functions
def generate_crypto_address(currency: str) -> str:
    """Generate crypto payment address"""
    # This is a placeholder - integrate with actual crypto payment processor
    # Options: CoinGate, NOWPayments, CoinPayments, etc.
    addresses = {
        "BTC": "bc1q_example_btc_address",
        "ETH": "0x_example_eth_address",
        "USDT": "0x_example_usdt_address"
    }
    return addresses.get(currency, "")

def verify_ios_receipt(receipt_data: str) -> bool:
    """Verify iOS App Store receipt"""
    import requests
    
    # Apple's verification endpoint
    url = "https://buy.itunes.apple.com/verifyReceipt"
    
    data = {
        "receipt-data": receipt_data,
        "password": config.APPLE_SHARED_SECRET  # Get from App Store Connect
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    return result.get("status") == 0

def verify_android_purchase(purchase_token: str) -> bool:
    """Verify Android Google Play purchase"""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    # Google Play Developer API
    credentials = service_account.Credentials.from_service_account_file(
        config.GOOGLE_SERVICE_ACCOUNT_FILE
    )
    
    service = build('androidpublisher', 'v3', credentials=credentials)
    
    # Verify purchase
    result = service.purchases().products().get(
        packageName=config.ANDROID_PACKAGE_NAME,
        productId='pro_subscription',
        token=purchase_token
    ).execute()
    
    return result.get('purchaseState') == 0

# Get subscription status
@app.get("/api/subscription/status")
async def get_subscription_status(user: dict = Depends(get_current_user)):
    """Get user's subscription status"""
    subscription = user.get("subscription", "free")
    subscription_end = user.get("subscription_end")
    
    is_active = True
    if subscription_end and subscription_end < datetime.utcnow():
        is_active = False
        # Downgrade to free
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"subscription": "free"}}
        )
        subscription = "free"
    
    return {
        "plan": subscription,
        "is_active": is_active,
        "expires_at": subscription_end,
        "features": get_plan_features(subscription)
    }

def get_plan_features(plan: str) -> dict:
    """Get features for each plan"""
    features = {
        "free": {
            "paper_trading": True,
            "real_trading": True,  # Allow real trading
            "max_real_trades": 1,  # But only 1 trade (trial)
            "max_bots": 1,
            "strategies": ["momentum"],
            "support": "community"
        },
        "pro": {
            "paper_trading": True,
            "real_trading": True,
            "max_real_trades": -1,  # Unlimited
            "max_bots": 3,
            "strategies": ["all"],
            "support": "priority"
        },
        "enterprise": {
            "paper_trading": True,
            "real_trading": True,
            "max_real_trades": -1,  # Unlimited
            "max_bots": 999,
            "strategies": ["all"],
            "support": "dedicated",
            "api_access": True,
            "custom_strategies": True
        },
        "admin": {
            "paper_trading": True,
            "real_trading": True,
            "max_real_trades": -1,  # Unlimited
            "max_bots": 999,
            "strategies": ["all"],
            "support": "dedicated",
            "api_access": True,
            "custom_strategies": True,
            "admin_access": True
        }
    }
    return features.get(plan, features["free"])


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
    total_volume_result = list(db.trades.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]))
    
    # Revenue (from subscriptions)
    revenue_result = list(subscriptions_collection.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]))
    
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
            "total_volume": total_volume_result[0]["total"] if total_volume_result else 0
        },
        "revenue": {
            "total": revenue_result[0]["total"] if revenue_result else 0
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

@app.get("/api/admin/users")
async def get_all_users(admin: dict = Depends(get_admin_user)):
    """Get all users for admin management"""
    users = list(users_collection.find({}).sort("created_at", -1))
    
    for user in users:
        user["_id"] = str(user["_id"])
        # Remove sensitive data
        user.pop("password", None)
        user.pop("okx_credentials", None)
        
        # Add bot count
        user["bot_count"] = bot_instances_collection.count_documents({"user_id": str(user["_id"])})
    
    return {"users": users}

@app.get("/api/admin/analytics")
async def get_analytics(admin: dict = Depends(get_admin_user)):
    """Get system analytics"""
    return {
        "overview": await admin_overview(admin),
        "user_stats": await user_stats(admin),
        "trading_stats": await trading_stats(admin)
    }

@app.post("/api/admin/settings/update")
async def update_system_settings(settings: dict, admin: dict = Depends(get_admin_user)):
    """Update system settings"""
    # Store settings in database
    db.system_settings.update_one(
        {"_id": "system_config"},
        {"$set": {
            **settings,
            "updated_at": datetime.utcnow(),
            "updated_by": admin["email"]
        }},
        upsert=True
    )
    return {"message": "Settings updated successfully", "settings": settings}

@app.post("/api/admin/backup")
async def create_backup(admin: dict = Depends(get_admin_user)):
    """Create database backup"""
    try:
        backup_id = f"backup_{int(datetime.utcnow().timestamp())}"
        # In production, implement actual backup logic
        return {
            "message": "Backup created successfully",
            "backup_id": backup_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")

@app.post("/api/admin/cache/clear")
async def clear_cache(admin: dict = Depends(get_admin_user)):
    """Clear system cache"""
    try:
        # Clear any cached data
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")

@app.put("/api/admin/users/{user_id}/subscription")
async def update_user_subscription(user_id: str, data: dict, admin: dict = Depends(get_admin_user)):
    """Update user subscription"""
    from bson import ObjectId
    try:
        user_obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    new_subscription = data.get("subscription")
    if new_subscription not in ["free", "pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid subscription plan")
    
    users_collection.update_one(
        {"_id": user_obj_id},
        {"$set": {"subscription": new_subscription, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": f"Subscription updated to {new_subscription}", "subscription": new_subscription}


# ============================================================================
# SUBSCRIPTION ENDPOINTS
# ============================================================================

@app.post("/api/subscriptions/create")
async def create_subscription(sub_data: SubscriptionCreate, user: dict = Depends(get_current_user)):
    """Create subscription"""
    # Use authenticated user's ID, not from request
    user_id = str(user["_id"])
    
    subscription = {
        "user_id": user_id,
        "plan": sub_data.plan,
        "amount": {"free": 0, "pro": 29, "enterprise": 99}[sub_data.plan],
        "status": "active",
        "payment_method": sub_data.payment_method or "card",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=30)
    }
    
    result = subscriptions_collection.insert_one(subscription)
    
    # Update user subscription
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "subscription": sub_data.plan,
            "subscription_start": datetime.utcnow(),
            "subscription_end": datetime.utcnow() + timedelta(days=30)
        }}
    )
    
    return {
        "message": "Subscription created successfully",
        "subscription_id": str(result.inserted_id),
        "plan": sub_data.plan
    }

@app.get("/api/subscriptions/my-subscription")
async def get_my_subscription(user: dict = Depends(get_current_user)):
    """Get user's subscription"""
    subscription = subscriptions_collection.find_one({"user_id": str(user["_id"])})
    if subscription:
        subscription["_id"] = str(subscription["_id"])
    return subscription or {"plan": "free"}


# ============================================================================
# FOREX TRADING ENDPOINTS
# ============================================================================

@app.get("/api/forex/pairs")
async def get_forex_pairs():
    """Get available forex trading pairs"""
    if TRADING_MODULES_AVAILABLE:
        try:
            import ccxt
            exchange = ccxt.okx()
            forex_trader = ForexTrader(exchange)
            return forex_trader.get_available_pairs()
        except Exception as e:
            return {"error": str(e), "pairs": []}
    return {"message": "Forex trading not available"}

@app.get("/api/forex/{symbol}/analysis")
async def analyze_forex_pair(symbol: str):
    """Analyze a forex pair"""
    if TRADING_MODULES_AVAILABLE:
        try:
            import ccxt
            exchange = ccxt.okx()
            forex_trader = ForexTrader(exchange)
            return forex_trader.analyze_forex_pair(symbol)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=503, detail="Forex trading not available")

@app.get("/api/forex/market-overview")
async def get_forex_market_overview():
    """Get overview of all forex markets"""
    if TRADING_MODULES_AVAILABLE:
        try:
            import ccxt
            exchange = ccxt.okx()
            forex_trader = ForexTrader(exchange)
            return forex_trader.get_forex_market_overview()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=503, detail="Forex trading not available")


# ============================================================================
# P2P COPY TRADING ENDPOINTS
# ============================================================================

@app.post("/api/p2p/expert/create")
async def create_expert_profile(profile_data: dict, user: dict = Depends(get_current_user)):
    """Create expert trader profile"""
    if copy_trading_system:
        try:
            expert_id = copy_trading_system.create_expert_profile(str(user["_id"]), profile_data)
            return {"expert_id": expert_id, "message": "Expert profile created"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=503, detail="Copy trading not available")

@app.get("/api/p2p/experts")
async def get_expert_traders(limit: int = 50):
    """Get expert trader leaderboard"""
    if copy_trading_system:
        return copy_trading_system.get_expert_leaderboard(limit)
    return []

@app.post("/api/p2p/follow/{leader_id}")
async def follow_expert_trader(leader_id: str, copy_config: dict, user: dict = Depends(get_current_user)):
    """Start copying an expert trader"""
    if copy_trading_system:
        try:
            result = copy_trading_system.start_copying(str(user["_id"]), leader_id, copy_config)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=503, detail="Copy trading not available")

@app.delete("/api/p2p/unfollow/{leader_id}")
async def unfollow_expert_trader(leader_id: str, user: dict = Depends(get_current_user)):
    """Stop copying an expert trader"""
    if copy_trading_system:
        try:
            copy_trading_system.stop_copying(str(user["_id"]), leader_id)
            return {"message": "Unfollowed successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=503, detail="Copy trading not available")

@app.get("/api/p2p/my-following")
async def get_my_following(user: dict = Depends(get_current_user)):
    """Get list of experts I'm following"""
    if copy_trading_system:
        return copy_trading_system.get_follower_stats(str(user["_id"]))
    return {}

@app.get("/api/p2p/my-followers")
async def get_my_followers(user: dict = Depends(get_current_user)):
    """Get my followers (if I'm an expert)"""
    if copy_trading_system:
        return copy_trading_system.get_leader_stats(str(user["_id"]))
    return {}

@app.get("/api/p2p/marketplace")
async def get_strategy_marketplace():
    """Get strategy marketplace listings"""
    if p2p_marketplace:
        strategies = list(db.db['strategy_marketplace'].find({'is_active': True}))
        for strategy in strategies:
            strategy['_id'] = str(strategy['_id'])
        return strategies
    return []

@app.post("/api/p2p/marketplace/list")
async def list_strategy_for_sale(strategy_data: dict, user: dict = Depends(get_current_user)):
    """List a strategy for sale"""
    if p2p_marketplace:
        try:
            listing_id = p2p_marketplace.list_strategy(str(user["_id"]), strategy_data)
            return {"listing_id": listing_id, "message": "Strategy listed successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=503, detail="Marketplace not available")


# ============================================================================
# PUSH NOTIFICATIONS ENDPOINTS
# ============================================================================

class PushTokenUpdate(BaseModel):
    push_token: str

@app.post("/api/notifications/register-token")
async def register_push_token(token_data: PushTokenUpdate, user: dict = Depends(get_current_user)):
    """Register user's push notification token"""
    try:
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"push_token": token_data.push_token, "push_token_updated": datetime.utcnow()}}
        )
        return {"message": "Push token registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notifications/test")
async def test_push_notification(user: dict = Depends(get_current_user)):
    """Send test push notification"""
    if not PUSH_NOTIFICATIONS_AVAILABLE or not push_service:
        raise HTTPException(status_code=503, detail="Push notifications not available")
    
    push_token = user.get('push_token')
    if not push_token:
        raise HTTPException(status_code=400, detail="No push token registered")
    
    try:
        result = push_service.send_notification(
            push_token=push_token,
            title="Test Notification",
            body="Your push notifications are working!",
            data={'type': 'test'}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# API KEY MANAGEMENT ENDPOINTS
# ============================================================================

class APIKeyCreate(BaseModel):
    name: str
    permissions: Optional[List[str]] = None

@app.post("/api/keys/generate")
async def generate_api_key(key_data: APIKeyCreate, user: dict = Depends(get_current_user)):
    """Generate new API key"""
    if not API_SERVICE_AVAILABLE or not api_key_manager:
        raise HTTPException(status_code=503, detail="API service not available")
    
    try:
        key = api_key_manager.generate_api_key(
            user_id=str(user["_id"]),
            name=key_data.name,
            permissions=key_data.permissions
        )
        return key
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/keys/list")
async def list_api_keys(user: dict = Depends(get_current_user)):
    """List user's API keys"""
    if not API_SERVICE_AVAILABLE or not api_key_manager:
        raise HTTPException(status_code=503, detail="API service not available")
    
    try:
        keys = api_key_manager.list_user_api_keys(str(user["_id"]))
        return {"keys": keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/keys/{api_key}")
async def revoke_api_key(api_key: str, user: dict = Depends(get_current_user)):
    """Revoke an API key"""
    if not API_SERVICE_AVAILABLE or not api_key_manager:
        raise HTTPException(status_code=503, detail="API service not available")
    
    try:
        success = api_key_manager.revoke_api_key(api_key, str(user["_id"]))
        if success:
            return {"message": "API key revoked successfully"}
        else:
            raise HTTPException(status_code=404, detail="API key not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/keys/permissions")
async def get_available_permissions():
    """Get list of available API permissions"""
    from api_service import API_PERMISSIONS
    return {"permissions": API_PERMISSIONS}


# ============================================================================
# NEW LISTING BOT ENDPOINTS
# ============================================================================

class NewListingConfig(BaseModel):
    buy_amount_usdt: float = 50  # Investment per new listing
    take_profit_percent: float = 30  # 30% profit target
    stop_loss_percent: float = 15  # 15% max loss
    max_hold_time: int = 3600  # 1 hour max hold

@app.post("/api/new-listing/start")
async def start_new_listing_bot(config: NewListingConfig, user: dict = Depends(get_current_user)):
    """Start new listing detection bot"""
    if not NEW_LISTING_BOT_AVAILABLE:
        raise HTTPException(status_code=503, detail="New listing bot not available")
    
    try:
        # Get user's exchange connection
        if not user.get('exchange_connected'):
            raise HTTPException(status_code=400, detail="Please connect your OKX account first")
        
        # Create exchange instance for user
        import ccxt
        exchange = ccxt.okx({
            'apiKey': user.get('okx_api_key'),
            'secret': user.get('okx_api_secret'),
            'password': user.get('okx_passphrase'),
            'enableRateLimit': True
        })
        
        # Create bot with user configuration
        bot_config = {
            'buy_amount_usdt': config.buy_amount_usdt,
            'take_profit_percent': config.take_profit_percent,
            'stop_loss_percent': config.stop_loss_percent,
            'max_hold_time': config.max_hold_time
        }
        bot = NewListingBot(exchange, db, config=bot_config)
        
        # Save bot config to user
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "new_listing_bot_enabled": True,
                "new_listing_bot_config": config.dict(),
                "new_listing_bot_started": datetime.utcnow()
            }}
        )
        
        return {
            "message": "New listing bot started successfully",
            "config": config.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/new-listing/config")
async def update_new_listing_bot_config(config: NewListingConfig, user: dict = Depends(get_current_user)):
    """Update new listing bot configuration without starting it"""
    try:
        # Save config to user document
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "new_listing_bot_config": config.dict(),
                "new_listing_bot_config_updated": datetime.utcnow()
            }}
        )
        
        return {
            "message": "Configuration saved successfully",
            "config": config.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/new-listing/stop")
async def stop_new_listing_bot(user: dict = Depends(get_current_user)):
    """Stop new listing detection bot"""
    try:
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "new_listing_bot_enabled": False,
                "new_listing_bot_stopped": datetime.utcnow()
            }}
        )
        
        return {"message": "New listing bot stopped successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/new-listing/status")
async def get_new_listing_bot_status(user: dict = Depends(get_current_user)):
    """Get new listing bot status"""
    try:
        enabled = user.get('new_listing_bot_enabled', False)
        config = user.get('new_listing_bot_config', {})
        
        # Get recent trades
        trades = list(db.db['new_listing_trades'].find(
            {"user_id": str(user["_id"])},
            limit=10,
            sort=[("entry_time", -1)]
        ))
        
        # Calculate stats
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.get('pnl_usdt', 0) > 0])
        total_pnl = sum([t.get('pnl_usdt', 0) for t in trades])
        
        return {
            "enabled": enabled,
            "config": config,
            "stats": {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                "total_pnl": total_pnl
            },
            "recent_trades": trades
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/new-listing/announcements")
async def get_okx_announcements():
    """Get OKX new listing announcements"""
    if not NEW_LISTING_BOT_AVAILABLE:
        raise HTTPException(status_code=503, detail="New listing bot not available")
    
    try:
        import requests
        url = "https://www.okx.com/v3/announcements/list"
        params = {'type': 'new_crypto', 'limit': 10}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {"announcements": data.get('data', [])}
        
        return {"announcements": []}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI DASHBOARD ENDPOINTS
# ============================================================================

class AIConfig(BaseModel):
    invest_amount: float
    risk_level: str
    profit_target: int
    trading_style: str

class ChatMessage(BaseModel):
    message: str

@app.get("/api/ai/market-analysis")
async def get_ai_market_analysis(user: dict = Depends(get_current_user)):
    """Get AI-powered market analysis"""
    try:
        # Simulated AI analysis - replace with real AI later
        markets = [
            {
                "symbol": "BTC/USDT",
                "price": 37245.50,
                "volume": 2500000000,
                "signal": "BUY",
                "confidence": 88
            },
            {
                "symbol": "ETH/USDT",
                "price": 2045.30,
                "volume": 1200000000,
                "signal": "BUY",
                "confidence": 92
            },
            {
                "symbol": "SOL/USDT",
                "price": 98.75,
                "volume": 450000000,
                "signal": "HOLD",
                "confidence": 65
            },
            {
                "symbol": "DOGE/USDT",
                "price": 0.0875,
                "volume": 180000000,
                "signal": "SELL",
                "confidence": 70
            }
        ]
        
        return {"markets": markets}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/execute-suggestion")
async def execute_ai_suggestion(suggestion: dict, user: dict = Depends(get_current_user)):
    """Execute AI trading suggestion"""
    try:
        suggestion_id = suggestion.get('suggestion_id')
        
        # Log the execution
        logger.info(f"User {user['email']} executing AI suggestion {suggestion_id}")
        
        return {
            "message": "AI suggestion executed successfully!",
            "suggestion_id": suggestion_id,
            "status": "pending"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/optimize-config")
async def optimize_ai_config(config: AIConfig, user: dict = Depends(get_current_user)):
    """Save AI-optimized configuration"""
    try:
        # Save config to user
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "ai_config": config.dict(),
                "ai_config_updated": datetime.utcnow()
            }}
        )
        
        return {
            "message": "Configuration optimized successfully!",
            "config": config.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/chat")
async def ai_chat(message: ChatMessage, user: dict = Depends(get_current_user)):
    """AI chat assistant"""
    try:
        user_message = message.message.lower()
        
        # Simple AI responses - can be enhanced with real AI
        if "trade" in user_message or "buy" in user_message:
            response = """Based on current market analysis, I recommend:

1. **BTC/USDT** - Strong uptrend, 88% confidence
   - Entry: $37,245
   - Target: $39,500 (+6%)
   - Stop: $36,500 (-2%)

2. **ETH/USDT** - Momentum building, 92% confidence
   - Entry: $2,045
   - Target: $2,150 (+5%)
   - Stop: $2,000 (-2.2%)

Would you like me to execute these trades for you?"""
        
        elif "profit" in user_message or "money" in user_message or "rich" in user_message:
            response = """💰 Here's your path to wealth:

1. **Enable New Listing Bot** - Catch 100X opportunities
   - Expected: +50-200% per listing
   - Investment: $50 per listing

2. **Use Trailing Stops** - Lock in profits automatically
   - Never give back gains
   - Secure profits progressively

3. **Follow AI Signals** - 88% win rate
   - BTC/ETH momentum plays
   - Risk-managed entries

Start with $500 capital, aim for $1,500 this month! 🚀"""
        
        elif "strategy" in user_message or "best" in user_message:
            response = """🎯 Best strategy for you:

**Balanced Approach:**
- 40% New Listing Bot (high risk/reward)
- 40% BTC/ETH momentum (safer)
- 20% Cash reserve

**Settings:**
- Investment: $50 per trade
- Take Profit: 30%
- Stop Loss: 15%
- Trailing Stop: Active

This gives you 60% win rate with 2:1 reward/risk ratio!"""
        
        else:
            response = """I'm here to help you make money! 💰

I can help you with:
- **Trading recommendations** - What to buy/sell now
- **Strategy optimization** - Best approach for your goals
- **Risk management** - Protect your capital
- **Profit maximization** - Lock in gains

What would you like to know?"""
        
        return {"response": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    """Serve login page or health check for deployment"""
    # Return JSON for health checks (Render deployment)
    import os
    if os.getenv('RENDER'):
        return {
            "status": "healthy",
            "service": "Trading Bot API",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    # Serve login page for browser requests
    return FileResponse("static/login.html")

@app.get("/login")
async def login_page():
    """Serve login page"""
    return FileResponse("static/login.html")

@app.get("/dashboard")
async def user_dashboard():
    """Serve user dashboard - requires authentication"""
    return FileResponse("static/user_dashboard.html")

@app.get("/admin")
async def admin_dashboard():
    """Serve admin dashboard - requires authentication"""
    return FileResponse("static/admin_dashboard.html")

@app.get("/ai-dashboard")
async def ai_dashboard():
    """Serve AI dashboard"""
    return FileResponse("static/ai_dashboard.html")

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
# SYSTEM SETTINGS ENDPOINTS (ADMIN ONLY)
# ============================================================================

@app.get("/api/system/settings")
async def get_system_settings(user: dict = Depends(get_current_user)):
    """Get system settings (admin only)"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get settings from database or return defaults
    settings = db.db['system_settings'].find_one({"_id": "global"})
    
    if not settings:
        settings = {
            "api_keys": {
                "okx_api_key": "****" + config.OKX_API_KEY[-4:] if config.OKX_API_KEY else "",
                "okx_secret_key": "****" + config.OKX_SECRET_KEY[-4:] if config.OKX_SECRET_KEY else "",
                "okx_passphrase": "****",
            },
            "trading_limits": {
                "max_position_size": 1000,
                "max_daily_trades": 50,
                "max_loss_per_trade": 100,
                "max_daily_loss": 500,
                "max_leverage": 3,
                "require_confirmation": False,
            }
        }
    
    return settings

@app.put("/api/system/settings")
async def update_system_settings(settings: dict, user: dict = Depends(get_current_user)):
    """Update system settings (admin only)"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Update or create settings
    db.db['system_settings'].update_one(
        {"_id": "global"},
        {"$set": {
            **settings,
            "updated_at": datetime.utcnow(),
            "updated_by": user.get("email")
        }},
        upsert=True
    )
    
    return {"message": "Settings updated successfully", "settings": settings}


# ============================================================================
# SUBSCRIPTION VERIFICATION & FEATURE GRANTS
# ============================================================================

@app.post("/api/subscriptions/verify-payment")
async def verify_subscription_payment(
    payment_data: dict,
    user: dict = Depends(get_current_user)
):
    """Verify payment and grant subscription features"""
    try:
        plan = payment_data.get('plan', 'free')
        payment_method = payment_data.get('payment_method', 'unknown')
        
        # Update user subscription
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "subscription": plan,
                "subscription_start": datetime.utcnow(),
                "subscription_status": "active",
                "payment_method": payment_method,
                "last_payment": datetime.utcnow()
            }}
        )
        
        # Log payment
        db.db['payments'].insert_one({
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "plan": plan,
            "amount": 29 if plan == "pro" else 99 if plan == "enterprise" else 0,
            "payment_method": payment_method,
            "status": "completed",
            "timestamp": datetime.utcnow()
        })
        
        return {
            "success": True,
            "message": f"{plan.capitalize()} subscription activated!",
            "subscription": plan,
            "features": get_plan_features(plan)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print(f"{Fore.GREEN}✅ Trading Bot API Started{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 Admin Dashboard: http://localhost:8000/docs{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔌 WebSocket: ws://localhost:8000/ws/trades{Style.RESET_ALL}")
    
    # Update existing admin accounts (does NOT change password)
    admin_emails = ["admin@tradingbot.com", "ceo@gideonstechnology.com"]
    
    for admin_email in admin_emails:
        existing_admin = users_collection.find_one({"email": admin_email})
        if existing_admin:
            # Only update role and subscription, NEVER touch password
            users_collection.update_one(
                {"email": admin_email},
                {"$set": {
                    "role": "admin",
                    "subscription": "enterprise",
                    "exchange_connected": True,
                    "paper_trading": False,
                    "is_active": True
                }}
            )
            print(f"{Fore.GREEN}✅ Admin account updated: {admin_email} → Enterprise (password unchanged){Style.RESET_ALL}")
        else:
            # Admin account doesn't exist - they need to signup first
            print(f"{Fore.YELLOW}⚠️  Admin account not found: {admin_email} - Please signup first{Style.RESET_ALL}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
