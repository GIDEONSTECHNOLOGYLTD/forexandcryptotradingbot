"""
Verification Script for Admin Auto-Trader
Checks all components and provides detailed report
"""
import sys
import importlib

def check_module(module_name):
    """Check if a module is available"""
    try:
        importlib.import_module(module_name)
        return True, "✅ Available"
    except ImportError as e:
        return False, f"❌ Missing: {e}"

def check_file(filepath):
    """Check if a file exists"""
    import os
    if os.path.exists(filepath):
        return True, "✅ Exists"
    else:
        return False, "❌ Not found"

def check_config(attr_name):
    """Check if config attribute exists"""
    try:
        import config
        if hasattr(config, attr_name):
            value = getattr(config, attr_name)
            if value and value != "":
                return True, "✅ Configured"
            else:
                return False, "⚠️ Empty"
        else:
            return False, "❌ Not set"
    except ImportError:
        return False, "❌ config.py not found"

print("=" * 60)
print("ADMIN AUTO-TRADER VERIFICATION")
print("=" * 60)
print()

# Check Python version
print("1. PYTHON VERSION")
print(f"   Version: {sys.version}")
print(f"   {'✅ OK' if sys.version_info >= (3, 8) else '❌ Need Python 3.8+'}")
print()

# Check required modules
print("2. REQUIRED MODULES")
modules = [
    'ccxt',
    'pymongo',
    'cryptography',
    'logging',
    'datetime',
]

all_modules_ok = True
for module in modules:
    ok, msg = check_module(module)
    print(f"   {module:20s} {msg}")
    if not ok:
        all_modules_ok = False
print()

# Check required files
print("3. REQUIRED FILES")
files = [
    'admin_auto_trader.py',
    'bot_engine.py',
    'new_listing_bot.py',
    'auto_profit_protector.py',
    'mongodb_database.py',
    'config.py',
]

all_files_ok = True
for file in files:
    ok, msg = check_file(file)
    print(f"   {file:30s} {msg}")
    if not ok:
        all_files_ok = False
print()

# Check configuration
print("4. OKX CONFIGURATION")
configs = [
    'OKX_API_KEY',
    'OKX_SECRET_KEY',
    'OKX_PASSPHRASE',
]

all_config_ok = True
for cfg in configs:
    ok, msg = check_config(cfg)
    print(f"   {cfg:20s} {msg}")
    if not ok:
        all_config_ok = False
print()

# Check MongoDB
print("5. MONGODB CONNECTION")
try:
    from mongodb_database import MongoTradingDatabase
    db = MongoTradingDatabase()
    db.client.server_info()
    print("   ✅ MongoDB connected")
    mongo_ok = True
except Exception as e:
    print(f"   ❌ MongoDB error: {e}")
    mongo_ok = False
print()

# Overall status
print("=" * 60)
print("OVERALL STATUS")
print("=" * 60)

if all_modules_ok and all_files_ok and all_config_ok and mongo_ok:
    print("✅ ALL CHECKS PASSED - READY TO RUN!")
    print()
    print("To start the admin auto-trader:")
    print("   python admin_auto_trader.py")
    print()
    print("Your $16.78 will start growing automatically!")
else:
    print("⚠️ SOME CHECKS FAILED - NEEDS SETUP")
    print()
    
    if not all_modules_ok:
        print("Install missing modules:")
        print("   pip install -r requirements.txt")
        print()
    
    if not all_config_ok:
        print("Configure OKX credentials in config.py or .env:")
        print("   OKX_API_KEY=your_api_key")
        print("   OKX_SECRET_KEY=your_secret_key")
        print("   OKX_PASSPHRASE=your_passphrase")
        print()
    
    if not mongo_ok:
        print("Start MongoDB or configure MONGODB_URI in .env")
        print()

print("=" * 60)
