# 🍃 MongoDB Setup Guide - Easy Database (No SQL Knowledge Needed!)

## Why MongoDB is Perfect for You

### ✅ Advantages Over SQL:
- **No complex queries** - Just use Python dictionaries
- **No schema design** - Store data as-is
- **Easy to learn** - If you know Python, you know MongoDB
- **Flexible** - Add fields anytime without migrations
- **Free cloud hosting** - MongoDB Atlas is free forever
- **Scalable** - Grows with your business

### 🆚 MongoDB vs SQLite:

| Feature | MongoDB | SQLite |
|---------|---------|--------|
| **Ease of Use** | ✅ Very Easy | ❌ Need SQL |
| **Cloud Hosting** | ✅ Free (Atlas) | ❌ File-based |
| **Scalability** | ✅ Excellent | ❌ Limited |
| **Learning Curve** | ✅ Minimal | ❌ Steep |
| **Flexibility** | ✅ Very Flexible | ❌ Rigid Schema |

---

## 🚀 Quick Setup (5 Minutes)

### Option 1: MongoDB Atlas (Recommended - Free Cloud)

**Step 1: Create Account**
1. Go to: https://www.mongodb.com/cloud/atlas
2. Click "Try Free"
3. Sign up with email or Google

**Step 2: Create Free Cluster**
1. Choose "Shared" (Free tier)
2. Select cloud provider (AWS recommended)
3. Choose region closest to you
4. Click "Create Cluster" (takes 3-5 minutes)

**Step 3: Create Database User**
1. Click "Database Access" (left sidebar)
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Username: `tradingbot`
5. Password: Create a strong password (save it!)
6. User Privileges: "Read and write to any database"
7. Click "Add User"

**Step 4: Allow Network Access**
1. Click "Network Access" (left sidebar)
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (for testing)
4. Click "Confirm"

**Step 5: Get Connection String**
1. Click "Database" (left sidebar)
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. It looks like: `mongodb+srv://tradingbot:<password>@cluster0.xxxxx.mongodb.net/`

**Step 6: Configure Bot**
1. Open `.env` file
2. Add this line:
   ```
   MONGODB_URI=mongodb+srv://tradingbot:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/trading_bot
   ```
3. Replace `YOUR_PASSWORD` with your actual password
4. Replace `cluster0.xxxxx` with your actual cluster address

**Done! ✅**

---

### Option 2: Local MongoDB (For Development)

**macOS:**
```bash
# Install with Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community

# Add to .env
MONGODB_URI=mongodb://localhost:27017/
```

**Linux (Ubuntu/Debian):**
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Add to .env
MONGODB_URI=mongodb://localhost:27017/
```

**Windows:**
1. Download from: https://www.mongodb.com/try/download/community
2. Run installer (choose "Complete" installation)
3. Install as Windows Service
4. Add to .env: `MONGODB_URI=mongodb://localhost:27017/`

---

## 🧪 Test Your Setup

```bash
# Install MongoDB driver
pip install pymongo

# Test connection
python mongodb_database.py
```

**Expected Output:**
```
✅ MongoDB connected successfully!
Testing save trade...
✅ Trade saved with ID: 507f1f77bcf86cd799439011
✅ MongoDB is working perfectly!
```

---

## 💻 How to Use MongoDB in Your Bot

### Simple Usage (No SQL Knowledge Needed!)

**Save a trade:**
```python
from mongodb_database import MongoTradingDatabase

db = MongoTradingDatabase()

# Just pass a Python dictionary!
trade = {
    'symbol': 'BTC/USDT',
    'side': 'buy',
    'entry_price': 43250.50,
    'amount': 0.0046,
    'confidence': 75.0
}

db.save_trade(trade)  # That's it!
```

**Get trades:**
```python
# Get all trades
trades = db.get_trades(limit=100)
print(trades)

# Get open trades
open_trades = db.get_open_trades()
print(open_trades)

# Get statistics
stats = db.get_statistics()
print(stats)
```

**Update a trade:**
```python
exit_data = {
    'exit_price': 44980.52,
    'exit_time': datetime.now(),
    'pnl': 8.00,
    'pnl_percent': 4.0
}

db.update_trade('BTC/USDT', exit_data)
```

**That's all you need to know!** No SQL queries, no complex syntax.

---

## 🔄 Switch from SQLite to MongoDB

### In your bot:

**Before (SQLite):**
```python
bot = AdvancedTradingBot()
```

**After (MongoDB):**
```python
bot = AdvancedTradingBot(use_mongodb=True)
```

**That's it!** Everything else works the same.

---

## 📊 MongoDB Collections (Like Tables)

Your bot automatically creates these:

1. **trades** - All your trades
   ```python
   {
       'symbol': 'BTC/USDT',
       'side': 'buy',
       'entry_price': 43250.50,
       'exit_price': 44980.52,
       'pnl': 8.00,
       'status': 'closed'
   }
   ```

2. **performance** - Daily snapshots
   ```python
   {
       'date': '2025-10-01',
       'capital': 10008.00,
       'daily_pnl': 8.00,
       'win_rate': 100.0
   }
   ```

3. **signals** - Trading signals
   ```python
   {
       'symbol': 'BTC/USDT',
       'signal': 'buy',
       'confidence': 75.0,
       'timestamp': '2025-10-01 23:00:00'
   }
   ```

4. **strategy_performance** - Strategy stats
   ```python
   {
       'strategy_name': 'RSI',
       'symbol': 'BTC/USDT',
       'win_rate': 65.0,
       'total_signals': 100
   }
   ```

---

## 🎯 MongoDB Atlas Free Tier Limits

**What you get for FREE:**
- ✅ 512 MB storage (enough for millions of trades)
- ✅ Shared RAM
- ✅ Shared vCPU
- ✅ No credit card required
- ✅ Never expires
- ✅ Perfect for your bot

**When to upgrade:**
- Storage > 512 MB (unlikely for years)
- Need dedicated resources
- Want backups
- Need more performance

---

## 🔐 Security Best Practices

### 1. Strong Password
```
❌ Bad: password123
✅ Good: Tr@d1ng!B0t#2025$Secure
```

### 2. IP Whitelist (Production)
Instead of "Allow from Anywhere":
1. Get your server IP
2. Add only that IP
3. More secure

### 3. Environment Variables
```bash
# ✅ Good - in .env file
MONGODB_URI=mongodb+srv://user:pass@cluster.net/

# ❌ Bad - in code
db = MongoTradingDatabase("mongodb+srv://user:pass@...")
```

### 4. Read-Only User (for analytics)
Create separate user with read-only access for viewing data.

---

## 📱 MongoDB Compass (GUI Tool)

**Visual database browser - No code needed!**

1. Download: https://www.mongodb.com/try/download/compass
2. Install and open
3. Paste your connection string
4. Click "Connect"
5. Browse your data visually!

**Features:**
- View all trades
- Filter and search
- Export to CSV
- Run queries (optional)
- Visual charts

---

## 🆚 Comparison: MongoDB vs SQLite

### For Your Trading Bot:

**MongoDB Wins:**
- ✅ Easier to use (no SQL)
- ✅ Cloud hosting (free)
- ✅ Better for scaling
- ✅ More flexible
- ✅ Better analytics
- ✅ Visual tools (Compass)

**SQLite Wins:**
- ✅ No internet needed
- ✅ Single file
- ✅ Slightly faster (local)
- ✅ No setup needed

**Recommendation:** Use MongoDB!

---

## 🚀 Advanced Features (Optional)

### Aggregation (Powerful Analytics)

```python
# Get total PnL by symbol
pipeline = [
    {'$match': {'status': 'closed'}},
    {'$group': {
        '_id': '$symbol',
        'total_pnl': {'$sum': '$pnl'},
        'count': {'$sum': 1}
    }},
    {'$sort': {'total_pnl': -1}}
]

results = db.trades.aggregate(pipeline)
```

### Indexes (Faster Queries)

```python
# Already created automatically!
db.trades.create_index('symbol')
db.trades.create_index('status')
```

### Backup & Restore

```bash
# Backup (MongoDB Atlas does this automatically)
mongodump --uri="your_connection_string"

# Restore
mongorestore --uri="your_connection_string" dump/
```

---

## 🐛 Troubleshooting

### "Connection failed"
**Solution:**
1. Check internet connection
2. Verify connection string in .env
3. Check IP whitelist in Atlas
4. Verify username/password

### "Authentication failed"
**Solution:**
1. Check password in connection string
2. Verify user exists in Atlas
3. Check user permissions

### "Network timeout"
**Solution:**
1. Check firewall settings
2. Verify IP whitelist
3. Try different network

### "Database not found"
**Solution:**
- MongoDB creates database automatically
- Just start using it!

---

## 📚 Learning Resources

### Official Docs:
- MongoDB Manual: https://docs.mongodb.com/manual/
- Python Driver: https://pymongo.readthedocs.io/

### Tutorials:
- MongoDB University (Free): https://university.mongodb.com/
- YouTube: "MongoDB Crash Course"

### Community:
- MongoDB Community Forum
- Stack Overflow (mongodb tag)

---

## ✅ Quick Reference

### Common Operations:

```python
from mongodb_database import MongoTradingDatabase

db = MongoTradingDatabase()

# Save
db.save_trade({'symbol': 'BTC/USDT', ...})

# Get
trades = db.get_trades(limit=100)

# Update
db.update_trade('BTC/USDT', {'exit_price': 45000})

# Statistics
stats = db.get_statistics()

# Export
db.export_to_csv('trades', 'my_trades.csv')

# Close
db.close()
```

---

## 🎉 You're Ready!

**MongoDB is now set up and ready to use!**

### To use it in your bot:

```bash
# 1. Make sure MongoDB URI is in .env
nano .env

# 2. Install pymongo
pip install pymongo

# 3. Test it
python mongodb_database.py

# 4. Run bot with MongoDB
python advanced_trading_bot.py
# The bot will automatically use MongoDB if configured!
```

---

## 💡 Pro Tips

1. **Start with Atlas** - Free and easy
2. **Use Compass** - Visual database browser
3. **Export regularly** - Backup your data
4. **Monitor usage** - Check Atlas dashboard
5. **Learn basics** - 30 minutes of MongoDB tutorial

---

**MongoDB is easier than SQL and perfect for your trading bot!** 🚀

**No SQL knowledge needed - just Python dictionaries!** 🐍

**Get started now:** `python mongodb_database.py` ✅
