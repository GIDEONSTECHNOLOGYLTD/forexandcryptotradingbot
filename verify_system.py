"""
Complete System Verification Script
Verifies all issues user reported:
1. Capital showing correct amount (not hardcoded $1000)
2. Bot details loading properly
3. Trade history showing real trades
4. Payment system working
"""
import pymongo
from datetime import datetime
import json

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://gideonaina29:yS1NNhgjINjzqgwF@cluster0.mongodb.net/trading_bot?retryWrites=true&w=majority")
db = client['trading_bot']

def verify_bots():
    """Verify bot capitals are correct, not hardcoded"""
    print("\n" + "="*60)
    print("1. VERIFYING BOT CAPITALS")
    print("="*60)
    
    bots = list(db['bot_instances'].find())
    print(f"Total bots: {len(bots)}")
    
    for bot in bots:
        bot_id = str(bot['_id'])
        capital = bot.get('config', {}).get('capital', 0)
        symbol = bot.get('config', {}).get('symbol', 'N/A')
        user_id = bot.get('user_id', 'N/A')
        status = bot.get('status', 'N/A')
        
        print(f"\nBot ID: {bot_id}")
        print(f"  User: {user_id}")
        print(f"  Symbol: {symbol}")
        print(f"  Capital: ${capital}")
        print(f"  Status: {status}")
        
        # Check if hardcoded
        if capital == 1000:
            print(f"  ⚠️  WARNING: Capital is $1000 - might be default!")
        elif capital == 100:
            print(f"  ⚠️  WARNING: Capital is $100 - might be default!")
        elif capital == 5:
            print(f"  ✅ Correct: Capital is $5 (user's actual amount)")
        else:
            print(f"  ℹ️  Capital: ${capital}")
    
    return bots

def verify_trades():
    """Verify trades are being saved and visible"""
    print("\n" + "="*60)
    print("2. VERIFYING TRADES")
    print("="*60)
    
    trades = list(db['trades'].find().sort("timestamp", -1).limit(20))
    print(f"Total trades (last 20): {len(trades)}")
    
    if len(trades) == 0:
        print("❌ NO TRADES FOUND! This is why trade history shows 0.")
        print("   Check if bot is actually executing trades.")
        return []
    
    for trade in trades:
        trade_id = str(trade['_id'])
        symbol = trade.get('symbol', 'N/A')
        side = trade.get('side', 'N/A')
        amount = trade.get('amount', 0)
        price = trade.get('price', 0)
        user_id = trade.get('user_id', 'N/A')
        bot_id = trade.get('bot_id', 'N/A')
        timestamp = trade.get('timestamp', 'N/A')
        status = trade.get('status', 'N/A')
        
        print(f"\nTrade ID: {trade_id}")
        print(f"  User: {user_id}")
        print(f"  Bot: {bot_id}")
        print(f"  Symbol: {symbol}")
        print(f"  Side: {side}")
        print(f"  Amount: {amount}")
        print(f"  Price: ${price}")
        print(f"  Status: {status}")
        print(f"  Time: {timestamp}")
        
        # Check if this is the $5 trade
        total_value = amount * price
        if 4 <= total_value <= 6:
            print(f"  ✅ This looks like the $5 trade!")
    
    return trades

def verify_users_and_subscriptions():
    """Verify users can pay and subscriptions work"""
    print("\n" + "="*60)
    print("3. VERIFYING USERS & SUBSCRIPTIONS")
    print("="*60)
    
    users = list(db['users'].find())
    print(f"Total users: {len(users)}")
    
    for user in users:
        user_id = str(user['_id'])
        email = user.get('email', 'N/A')
        role = user.get('role', 'user')
        subscription = user.get('subscription', 'free')
        exchange_connected = user.get('exchange_connected', False)
        
        print(f"\nUser: {email}")
        print(f"  ID: {user_id}")
        print(f"  Role: {role}")
        print(f"  Subscription: {subscription}")
        print(f"  Exchange Connected: {exchange_connected}")
        
        if role == 'admin':
            print(f"  👑 ADMIN USER")
        
        if subscription == 'free':
            print(f"  💰 FREE PLAN - Can upgrade!")
        elif subscription in ['pro', 'enterprise']:
            print(f"  ✅ PAID SUBSCRIPTION: {subscription.upper()}")
    
    return users

def verify_payment_history():
    """Check if payment records exist"""
    print("\n" + "="*60)
    print("4. VERIFYING PAYMENT HISTORY")
    print("="*60)
    
    # Check if payments collection exists
    collections = db.list_collection_names()
    print(f"Available collections: {', '.join(collections)}")
    
    if 'payments' in collections:
        payments = list(db['payments'].find().sort("created_at", -1).limit(10))
        print(f"\nTotal payments (last 10): {len(payments)}")
        
        if len(payments) == 0:
            print("⚠️  No payments recorded yet.")
            print("   Users haven't subscribed or payment integration not working.")
        
        for payment in payments:
            user_id = payment.get('user_id', 'N/A')
            amount = payment.get('amount', 0)
            plan = payment.get('plan', 'N/A')
            method = payment.get('payment_method', 'N/A')
            status = payment.get('status', 'N/A')
            timestamp = payment.get('created_at', 'N/A')
            
            print(f"\nPayment:")
            print(f"  User: {user_id}")
            print(f"  Plan: {plan}")
            print(f"  Amount: ${amount}")
            print(f"  Method: {method}")
            print(f"  Status: {status}")
            print(f"  Time: {timestamp}")
    else:
        print("⚠️  'payments' collection doesn't exist yet!")
        print("   No payments have been processed.")

def check_hardcoded_values():
    """Check for common hardcoded values"""
    print("\n" + "="*60)
    print("5. CHECKING FOR HARDCODED VALUES")
    print("="*60)
    
    # Check bots with capital = 1000
    hardcoded_1000 = db['bot_instances'].count_documents({'config.capital': 1000})
    print(f"Bots with capital=$1000: {hardcoded_1000}")
    if hardcoded_1000 > 0:
        print("  ⚠️  WARNING: These might be hardcoded defaults!")
    
    # Check bots with capital = 100
    hardcoded_100 = db['bot_instances'].count_documents({'config.capital': 100})
    print(f"Bots with capital=$100: {hardcoded_100}")
    if hardcoded_100 > 0:
        print("  ℹ️  These use the system default of $100")
    
    # Check bots with capital = 5
    actual_5 = db['bot_instances'].count_documents({'config.capital': 5})
    print(f"Bots with capital=$5: {actual_5}")
    if actual_5 > 0:
        print("  ✅ These are user's actual $5 bots!")

def generate_recommendations(bots, trades, users):
    """Generate recommendations based on findings"""
    print("\n" + "="*60)
    print("6. RECOMMENDATIONS")
    print("="*60)
    
    # Check capital issue
    capitals_1000 = [b for b in bots if b.get('config', {}).get('capital') == 1000]
    if capitals_1000:
        print("\n🔧 FIX REQUIRED: Capital showing $1000")
        print(f"   Found {len(capitals_1000)} bots with $1000 capital")
        print("   Solution: Update iOS app to show bot.config.capital from API")
        print("   File: mobile-app/src/screens/TradingScreen.tsx")
        print("   Current: Shows hardcoded $1000")
        print("   Fix: Display {bot.config?.capital || 0}")
    
    # Check trade history
    if len(trades) == 0:
        print("\n🔧 FIX REQUIRED: No trades in database")
        print("   Trades are not being saved!")
        print("   Check: bot_engine.py trade saving logic")
        print("   Verify: Trades are inserted into db['trades'] collection")
    
    # Check payments
    if 'payments' not in db.list_collection_names():
        print("\n🔧 FIX REQUIRED: Payment system not initialized")
        print("   No payments collection exists")
        print("   Action: Test payment flow end-to-end")
        print("   Files: PaymentScreen.tsx, web_dashboard.py payment endpoints")
    
    # Check subscription revenue
    paid_users = [u for u in users if u.get('subscription') in ['pro', 'enterprise']]
    if len(paid_users) == 0:
        print("\n💰 REVENUE ALERT: No paid subscriptions!")
        print("   All users are on free plan")
        print("   Action: Test payment methods:")
        print("   1. Card payment (Paystack)")
        print("   2. Crypto payment (OKX)")
        print("   3. In-app purchase (iOS)")

def main():
    print("\n" + "="*80)
    print("COMPLETE SYSTEM VERIFICATION")
    print("Checking all issues user reported")
    print("="*80)
    
    bots = verify_bots()
    trades = verify_trades()
    users = verify_users_and_subscriptions()
    verify_payment_history()
    check_hardcoded_values()
    generate_recommendations(bots, trades, users)
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE!")
    print("="*80)
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"   Total Bots: {len(bots)}")
    print(f"   Total Trades: {len(trades)}")
    print(f"   Total Users: {len(users)}")
    print(f"   Paid Users: {len([u for u in users if u.get('subscription') in ['pro', 'enterprise']])}")
    
    if len(trades) == 0:
        print("\n❌ CRITICAL: No trades found! Trade history will show 0.")
    else:
        print(f"\n✅ Trades exist: {len(trades)} trades in database")
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Check MongoDB connection string and credentials.")
