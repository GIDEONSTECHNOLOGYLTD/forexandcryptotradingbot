# 🧪 COMPLETE TESTING GUIDE

## 🚀 SETUP INSTRUCTIONS

### 1. Install Backend Dependencies
```bash
cd /Users/gideonaina/Documents/GitHub/forexandcryptotradingbot
pip3 install -r requirements.txt
```

### 2. Start Backend Server
```bash
python3 web_dashboard.py
```

**Expected Output:**
```
✅ Trading Bot API Started
📊 Admin Dashboard: http://localhost:8000/docs
🔌 WebSocket: ws://localhost:8000/ws/trades
⚠️  Default admin created: admin@tradingbot.com / admin123
```

### 3. Start Mobile App
```bash
cd mobile-app
npx expo start
```

---

## ✅ TEST 1: BOT CREATION

### Test Regular User Bot Creation:

1. **Login as Regular User**
   - Email: test@example.com (or create new account)
   - Password: your password

2. **Navigate to Trading Tab**
   - Should see "No bots yet" or existing bots

3. **Click "+" Button**
   - Should navigate to Bot Config screen

4. **Fill Bot Details:**
   - Bot Type: Crypto or Forex
   - Symbol: BTC/USDT (for crypto) or EUR/USD (for forex)
   - Capital: 1000
   - Paper Trading: ON (for free users)

5. **Click "Create Bot"**
   - Should see success message
   - Should navigate back to Trading screen
   - Bot should appear in list

### Test Admin Bot Creation:

1. **Login as Admin**
   - Email: admin@tradingbot.com
   - Password: admin123

2. **Create Bot (Same Steps as Above)**
   - Admin can create with Paper Trading OFF
   - Admin can create unlimited bots
   - Admin uses admin OKX credentials

### Expected API Calls:
```
POST /api/bots/create
{
  "bot_type": "crypto",
  "symbol": "BTC/USDT",
  "capital": 1000,
  "paper_trading": true
}
```

### Common Issues:
- ❌ "Please connect exchange" → User needs to connect OKX first (for real trading)
- ❌ "Bot limit reached" → User needs to upgrade subscription
- ❌ "Real trading requires Pro" → User on free plan can only paper trade

---

## ✅ TEST 2: EXCHANGE CONNECTION

### Test Exchange Connection Flow:

1. **Navigate to Profile**
   - Tap Profile tab or Settings

2. **Tap "Exchange Connection"**
   - Should navigate to Exchange Connection screen

3. **Enter OKX Credentials:**
   - API Key: (your OKX API key)
   - Secret Key: (your OKX secret)
   - Passphrase: (your OKX passphrase)
   - Paper Trading: Toggle ON/OFF

4. **Click "Connect Exchange"**
   - Should see success message
   - Should show "Connected" status
   - Should navigate back

5. **Verify Connection:**
   - Go back to Exchange Connection screen
   - Should show "Connected" with green checkmark
   - Should show trading mode (Paper/Live)

### Expected API Calls:
```
POST /api/user/connect-exchange
{
  "okx_api_key": "...",
  "okx_secret_key": "...",
  "okx_passphrase": "...",
  "paper_trading": true
}

GET /api/user/exchange-status
Response: {
  "connected": true,
  "paper_trading": true
}
```

### Common Issues:
- ❌ "Failed to connect" → Check API credentials are correct
- ❌ "Encryption error" → Check ENCRYPTION_KEY in .env
- ❌ Network error → Check backend is running

---

## ✅ TEST 3: ADMIN TRADING

### Test Admin Can Create Bots:

1. **Login as Admin**
   - Email: admin@tradingbot.com
   - Password: admin123

2. **Check Admin Status:**
   - Should see "Enterprise" plan
   - Should have exchange_connected: true

3. **Create Real Trading Bot:**
   - Bot Type: Crypto
   - Symbol: BTC/USDT
   - Capital: 10000
   - Paper Trading: OFF ✅ (Admin can do this)

4. **Start Bot:**
   - Tap on created bot
   - Tap "Start Bot"
   - Should start successfully

5. **View All Bots:**
   - Admin should see ALL users' bots
   - Not just their own

### Expected Behavior:
- ✅ Admin bypasses exchange connection check
- ✅ Admin bypasses subscription limits
- ✅ Admin can create unlimited bots
- ✅ Admin uses admin OKX credentials
- ✅ Admin can start/stop any bot

### Verify in Backend:
```bash
# Check admin user in MongoDB
mongo
use trading_bot_db
db.users.findOne({email: "admin@tradingbot.com"})

# Should show:
{
  "role": "admin",
  "subscription": "enterprise",
  "exchange_connected": true,
  "paper_trading": false
}
```

---

## ✅ TEST 4: PAYMENT/SUBSCRIPTION

### Test Payment Screen:

1. **Navigate to Payment Screen**
   - Profile → Manage Subscription

2. **Select Payment Method:**
   - Card (default)
   - Crypto
   - App Store

3. **Select Plan:**
   - Pro ($29/month)
   - Enterprise ($99/month)

4. **Click "Select Plan"**
   - Should call backend API
   - Should see success message
   - Should update user subscription

### Expected API Calls:
```
POST /api/subscriptions/create
{
  "plan": "pro",
  "payment_method": "card"
}

Response: {
  "message": "Subscription created successfully",
  "plan": "pro"
}
```

### Verify Subscription Updated:
```
GET /api/users/me
Response: {
  "subscription": "pro",
  "subscription_start": "2025-11-12...",
  "subscription_end": "2025-12-12..."
}
```

---

## 🐛 DEBUGGING CHECKLIST

### If Bot Creation Fails:

1. **Check Backend Logs:**
   ```bash
   # Look for errors in terminal running web_dashboard.py
   ```

2. **Check User Subscription:**
   ```bash
   # In MongoDB or via API
   GET /api/users/me
   ```

3. **Check Exchange Connection:**
   ```bash
   GET /api/user/exchange-status
   ```

4. **Check Request Payload:**
   - Open React Native Debugger
   - Check Network tab
   - Verify POST /api/bots/create payload

### If Exchange Connection Fails:

1. **Check ENCRYPTION_KEY:**
   ```bash
   cat .env | grep ENCRYPTION_KEY
   # Should have a 32-character key
   ```

2. **Check OKX Credentials:**
   - Verify API key is valid
   - Verify secret is correct
   - Verify passphrase matches

3. **Check Backend Endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/user/connect-exchange \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"okx_api_key":"test","okx_secret_key":"test","okx_passphrase":"test","paper_trading":true}'
   ```

### If Admin Can't Trade:

1. **Check Admin User:**
   ```bash
   # In MongoDB
   db.users.findOne({email: "admin@tradingbot.com"})
   ```

2. **Verify Flags:**
   - `role`: "admin"
   - `exchange_connected`: true
   - `paper_trading`: false
   - `subscription`: "enterprise"

3. **Restart Backend:**
   ```bash
   # Stop current server (Ctrl+C)
   python3 web_dashboard.py
   # This will update existing admin user
   ```

---

## 📊 SUCCESS CRITERIA

### Bot Creation:
- [ ] Regular user can create paper trading bot
- [ ] Regular user with Pro can create real trading bot
- [ ] Admin can create any bot without restrictions
- [ ] Bot appears in bot list
- [ ] Bot can be started/stopped
- [ ] Error messages are clear

### Exchange Connection:
- [ ] User can navigate to screen
- [ ] User can input credentials
- [ ] Connection succeeds
- [ ] Status shows "Connected"
- [ ] Can disconnect
- [ ] Error messages are helpful

### Admin Trading:
- [ ] Admin can login
- [ ] Admin has exchange_connected: true
- [ ] Admin can create unlimited bots
- [ ] Admin can toggle paper trading off
- [ ] Admin can start/stop bots
- [ ] Admin sees all users' bots

### Payment:
- [ ] Can select payment method
- [ ] Can select plan
- [ ] Subscription updates
- [ ] User sees updated plan
- [ ] Features unlock based on plan

---

## 🚀 QUICK TEST SCRIPT

Run this to test all endpoints:

```bash
# 1. Start backend
cd /Users/gideonaina/Documents/GitHub/forexandcryptotradingbot
python3 web_dashboard.py &

# 2. Test endpoints
curl http://localhost:8000/api/health

# 3. Login as admin
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@tradingbot.com","password":"admin123"}'

# 4. Save token and test bot creation
# (Use token from step 3)

# 5. Test mobile app
cd mobile-app
npx expo start
```

---

**Follow this guide step by step to verify all functionality works!** 🎯
