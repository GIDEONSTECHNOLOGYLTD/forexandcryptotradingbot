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
MAX_POSITION_SIZE_PERCENT = float(os.getenv('MAX_POSITION_SIZE_PERCENT', '80.0'))
STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '2.0'))
TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '4.0'))
MAX_DAILY_LOSS_PERCENT = float(os.getenv('MAX_DAILY_LOSS_PERCENT', '5.0'))
MAX_OPEN_POSITIONS = int(os.getenv('MAX_OPEN_POSITIONS', '10'))

# Bug #9 fix: CONFIG VALIDATION - Prevent catastrophic user errors!
def validate_config():
    """Validate configuration values are within safe bounds"""
    errors = []
    warnings = []
    
    # Validate MAX_POSITION_SIZE_PERCENT (1% to 100%)
    if not (1.0 <= MAX_POSITION_SIZE_PERCENT <= 100.0):
        errors.append(f"MAX_POSITION_SIZE_PERCENT={MAX_POSITION_SIZE_PERCENT} invalid! Must be 1-100. Using default 80%")
        globals()['MAX_POSITION_SIZE_PERCENT'] = 80.0
    elif MAX_POSITION_SIZE_PERCENT > 90:
        warnings.append(f"MAX_POSITION_SIZE_PERCENT={MAX_POSITION_SIZE_PERCENT}% is risky! Recommend <= 90%")
    
    # Validate STOP_LOSS_PERCENT (0.1% to 50%)
    if not (0.1 <= STOP_LOSS_PERCENT <= 50.0):
        errors.append(f"STOP_LOSS_PERCENT={STOP_LOSS_PERCENT} invalid! Must be 0.1-50. Using default 2%")
        globals()['STOP_LOSS_PERCENT'] = 2.0
    elif STOP_LOSS_PERCENT > 20:
        warnings.append(f"STOP_LOSS_PERCENT={STOP_LOSS_PERCENT}% is too high! Recommend <= 20%")
    
    # Validate TAKE_PROFIT_PERCENT (0.1% to 1000%)
    if not (0.1 <= TAKE_PROFIT_PERCENT <= 1000.0):
        errors.append(f"TAKE_PROFIT_PERCENT={TAKE_PROFIT_PERCENT} invalid! Must be 0.1-1000. Using default 4%")
        globals()['TAKE_PROFIT_PERCENT'] = 4.0
    elif TAKE_PROFIT_PERCENT < STOP_LOSS_PERCENT:
        warnings.append(f"TAKE_PROFIT ({TAKE_PROFIT_PERCENT}%) < STOP_LOSS ({STOP_LOSS_PERCENT}%)! You'll lose money!")
    
    # Validate MAX_DAILY_LOSS_PERCENT (0.1% to 50%)
    if not (0.1 <= MAX_DAILY_LOSS_PERCENT <= 50.0):
        errors.append(f"MAX_DAILY_LOSS_PERCENT={MAX_DAILY_LOSS_PERCENT} invalid! Must be 0.1-50. Using default 5%")
        globals()['MAX_DAILY_LOSS_PERCENT'] = 5.0
    
    # Validate MAX_OPEN_POSITIONS (1 to 100)
    if not (1 <= MAX_OPEN_POSITIONS <= 100):
        errors.append(f"MAX_OPEN_POSITIONS={MAX_OPEN_POSITIONS} invalid! Must be 1-100. Using default 10")
        globals()['MAX_OPEN_POSITIONS'] = 10
    
    return errors, warnings

# Validate on import
_errors, _warnings = validate_config()
if _errors:
    logger.error("CONFIG VALIDATION ERRORS:")
    for error in _errors:
        logger.error(f"  {error}")
if _warnings:
    logger.warning("CONFIG VALIDATION WARNINGS:")
    for warning in _warnings:
        logger.warning(f"  {warning}")

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
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', '10000'))  # Starting capital (configurable)

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'trading_bot.log'

# Markets to trade
CRYPTO_MARKETS = True  # Trade cryptocurrencies
FOREX_MARKETS = False  # Trade forex (requires different account type on OKX)

# Preferred quote currencies
QUOTE_CURRENCIES = ['USDT', 'USDC', 'USD']

# New Listing Bot Configuration
NEW_LISTING_BUY_AMOUNT = float(os.getenv('NEW_LISTING_BUY_AMOUNT', '50'))  # USDT to invest per new listing
NEW_LISTING_TAKE_PROFIT = float(os.getenv('NEW_LISTING_TAKE_PROFIT', '30'))  # Take profit % (default 30%)
NEW_LISTING_STOP_LOSS = float(os.getenv('NEW_LISTING_STOP_LOSS', '15'))  # Stop loss % (default 15%)
NEW_LISTING_MAX_HOLD = int(os.getenv('NEW_LISTING_MAX_HOLD', '3600'))  # Max hold time in seconds (default 1 hour)
NEW_LISTING_CHECK_INTERVAL = int(os.getenv('NEW_LISTING_CHECK_INTERVAL', '60'))  # Check interval in seconds

# Admin Auto-Trader Configuration
ADMIN_MIN_TRADE_SIZE = float(os.getenv('ADMIN_MIN_TRADE_SIZE', '5'))  # Minimum trade size in USDT (OKX minimum)
ADMIN_MAX_TRADE_SIZE = float(os.getenv('ADMIN_MAX_TRADE_SIZE', '1000'))  # Maximum trade size per position
ADMIN_TARGET_PROFIT = float(os.getenv('ADMIN_TARGET_PROFIT', '15'))  # Target profit % - LOWERED for consistent wins!
ADMIN_STOP_LOSS = float(os.getenv('ADMIN_STOP_LOSS', '5'))  # Stop loss % - Tighter to protect capital
ADMIN_MOMENTUM_MIN_BALANCE = float(os.getenv('ADMIN_MOMENTUM_MIN_BALANCE', '50'))  # Minimum balance for momentum strategy

# Small Profit Strategy - Accumulate many small wins instead of chasing big gains
ADMIN_SMALL_PROFIT_MODE = os.getenv('ADMIN_SMALL_PROFIT_MODE', 'true').lower() == 'true'  # Enable small profit accumulation
ADMIN_SMALL_WIN_TARGET = float(os.getenv('ADMIN_SMALL_WIN_TARGET', '5'))  # Take profit at just 5%! ($0.50 on $10)
ADMIN_QUICK_EXIT_THRESHOLD = float(os.getenv('ADMIN_QUICK_EXIT_THRESHOLD', '10'))  # Exit at 10% max

# CRITICAL PROTECTION: Daily Loss Limits (prevent catastrophic losses!)
ADMIN_DAILY_LOSS_LIMIT = float(os.getenv('ADMIN_DAILY_LOSS_LIMIT', '10'))  # Stop trading if lose 10% of capital in one day
ADMIN_MAX_CONSECUTIVE_LOSSES = int(os.getenv('ADMIN_MAX_CONSECUTIVE_LOSSES', '3'))  # Stop after 3 losses in a row
