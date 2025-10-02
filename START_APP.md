# 🚀 START YOUR APP - Quick Guide

## ✅ Setup Complete!

I've done all the needful:
- ✅ Created virtual environment
- ✅ Installed all dependencies
- ✅ Created .env file
- ✅ Created static directory
- ✅ Everything is ready!

---

## 🚀 Start the App (2 Steps)

### Step 1: Configure MongoDB (Optional for now)

Edit `.env` file and add your MongoDB connection:
```bash
nano .env
```

Add this line (or use local MongoDB):
```
MONGODB_URI=mongodb://localhost:27017/
```

**Note:** The app will work without MongoDB for testing, but you need it for production.

### Step 2: Start the Web Dashboard

```bash
source venv/bin/activate
python web_dashboard.py
```

---

## 🌐 Access Your App

Once started, you'll see:
```
✅ Trading Bot API Started
📊 Admin Dashboard: http://localhost:8000/docs
🔌 WebSocket: ws://localhost:8000/ws/trades
⚠️  Default admin created: admin@tradingbot.com / admin123
⚠️  CHANGE THIS PASSWORD IMMEDIATELY!
```

### Access Points:

**User Dashboard:**
- URL: http://localhost:8000/
- For your customers to trade

**Admin Dashboard:**
- URL: http://localhost:8000/admin
- Login: admin@tradingbot.com / admin123
- For you to manage everything

**API Documentation:**
- URL: http://localhost:8000/docs
- Interactive API testing

---

## 🎯 What to Do Next

### 1. Test User Dashboard
```
1. Open: http://localhost:8000/
2. Click "Register"
3. Create test account
4. Create a bot
5. Start trading (paper mode)
```

### 2. Test Admin Dashboard
```
1. Open: http://localhost:8000/admin
2. Login: admin@tradingbot.com / admin123
3. See overview
4. View users
5. Monitor system
```

### 3. Setup MongoDB (For Production)
```
1. Go to: https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create cluster
4. Get connection string
5. Add to .env file
6. Restart app
```

---

## 🐛 Troubleshooting

### If MongoDB error:
The app needs MongoDB to run. Either:
1. Install local MongoDB
2. Use MongoDB Atlas (free)
3. Or comment out MongoDB code for testing

### If port 8000 is busy:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in web_dashboard.py
# At bottom: uvicorn.run(app, host="0.0.0.0", port=8001)
```

### If dependencies error:
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📝 Quick Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Start web dashboard
python web_dashboard.py

# Start trading bot (separate terminal)
python advanced_trading_bot.py

# Run backtest
python backtester.py

# Test MongoDB
python mongodb_database.py

# Test Telegram
python telegram_notifier.py
```

---

## 🎉 You're Ready!

Everything is set up and ready to go!

**Next:** Start the app and test it!

```bash
source venv/bin/activate
python web_dashboard.py
```

Then open: http://localhost:8000/

**Happy Trading! 🚀💰**
