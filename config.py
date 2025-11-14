"""
Configuration file for the trading bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Exchange Configuration
EXCHANGE = 'okx'
OKX_API_KEY = os.getenv('OKX_API_KEY', '')
OKX_SECRET_KEY = os.getenv('OKX_SECRET_KEY', '')
OKX_PASSPHRASE = os.getenv('OKX_PASSPHRASE', '')

# Database Configuration
USE_MONGODB = True  # Set to True for production (multi-user support)
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')

# JWT Configuration (for user authentication)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-this-secret-key')

# Encryption Key (for API keys)
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'generate-a-fernet-key-here')

# Payment Configuration
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY', '')
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY', '')

# Crypto Payment (CoinGate, NOWPayments, etc.)
COINGATE_API_KEY = os.getenv('COINGATE_API_KEY', '')

# Telegram Notifications
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# In-App Purchase Configuration
APPLE_SHARED_SECRET = os.getenv('APPLE_SHARED_SECRET', '')
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', '')
ANDROID_PACKAGE_NAME = os.getenv('ANDROID_PACKAGE_NAME', 'com.tradingbot.app')

# API URL
API_URL = os.getenv('API_URL', 'http://localhost:8000')

# Trading Configuration
TIMEFRAME = '1h'  # 1 hour candles
PAPER_TRADING = False  # REAL TRADING ENABLED! Bot will use real money and make real profits! 💰

# Risk Management - ULTRA SAFE FOR SMALL BALANCE!
MAX_POSITION_SIZE_PERCENT = 80.0  # Use 80% per trade (with $16, trade $12-13)
STOP_LOSS_PERCENT = 2.0  # 2% stop loss (max $0.32 loss per trade)
TAKE_PROFIT_PERCENT = 4.0  # 4% take profit ($0.64 profit per trade)
MAX_DAILY_LOSS_PERCENT = 5.0  # Stop trading if daily loss exceeds 5% ($0.80 max loss per day)
MAX_OPEN_POSITIONS = 10  # ADMIN MODE: Multiple positions for profit! 🚀 (Regular users limited by subscription)

# Token Scanner Configuration
MIN_VOLUME_USD = 1000000  # Minimum 24h volume in USD
MIN_PRICE_CHANGE_PERCENT = 2.0  # Minimum price change to consider
SCAN_INTERVAL_MINUTES = 15  # How often to scan for new opportunities

# Strategy Parameters
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_PERIOD = 14

# Bollinger Bands
BB_PERIOD = 20
BB_STD = 2

# Moving Averages
SMA_FAST = 20
SMA_SLOW = 50
EMA_FAST = 12
EMA_SLOW = 26

# MACD
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Backtesting
BACKTEST_DAYS = 90  # Number of days to backtest
INITIAL_CAPITAL = 10000  # Starting capital for backtesting

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'trading_bot.log'

# Markets to trade
CRYPTO_MARKETS = True  # Trade cryptocurrencies
FOREX_MARKETS = False  # Trade forex (requires different account type on OKX)

# Preferred quote currencies
QUOTE_CURRENCIES = ['USDT', 'USDC', 'USD']
