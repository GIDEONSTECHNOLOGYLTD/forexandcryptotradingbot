# 🚀 COMPLETE PRODUCTION-READY SETUP GUIDE

## 🎯 Your Mission: Get Everything Working & Production-Ready

This guide will take you from "not working" to "fully deployed and making money" in 1 hour.

---

## ⚡ STEP 1: Fix Mobile App RIGHT NOW (2 Minutes!)

### Quick Fix - Use Tunnel Mode
```bash
cd /Users/gideonaina/Documents/GitHub/forexandcryptotradingbot/mobile-app

# This works WITHOUT any system changes!
npx expo start --tunnel

# ✅ No more "too many open files" error!
# ✅ Scan QR code with iPhone
# ✅ Works over internet (not just WiFi)
```

**Why tunnel mode?**
- Avoids file watching (no EMFILE error)
- Works from anywhere
- Production-like testing
- No Mac configuration needed

---

## 🔑 STEP 2: Configure OKX API (5 Minutes)

### Get Your OKX API Keys

1. **Log into OKX:** https://www.okx.com
2. **Go to:** Profile → API → Create API Key
3. **Set Permissions:**
   - ✅ **Read** (view account, orders, positions)
   - ✅ **Trade** (place/cancel orders)
   - ⚠️ **Withdraw** (ONLY if you want automated withdrawals - NOT RECOMMENDED)
4. **IP Whitelist:** 
   - For testing: Leave empty or add `0.0.0.0/0`
   - For production: Add your server IP
5. **Save These:**
   - API Key: `xxxxxxxxx`
   - Secret Key: `xxxxxxxxx`
   - Passphrase: `xxxxxxxxx`

### Configure .env File

```bash
# Edit main .env file
cd /Users/gideonaina/Documents/GitHub/forexandcryptotradingbot
nano .env
```

**Add these lines:**
```bash
# ==========================================
# OKX API CONFIGURATION (REQUIRED!)
# ==========================================
OKX_API_KEY=your_api_key_here
OKX_SECRET_KEY=your_secret_key_here
OKX_PASSPHRASE=your_passphrase_here

# Trading Mode (IMPORTANT!)
PAPER_TRADING=True  # Change to False for LIVE trading

# ==========================================
# DATABASE CONFIGURATION
# ==========================================
# Local MongoDB (for testing)
MONGODB_URI=mongodb://localhost:27017/trading_bot

# OR MongoDB Atlas (for production)
# MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/trading_bot

# ==========================================
# SECURITY
# ==========================================
JWT_SECRET_KEY=your_very_long_random_secret_key_here_min_32_characters

# ==========================================
# TELEGRAM NOTIFICATIONS (Optional)
# ==========================================
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# ==========================================
# PAYMENT INTEGRATION (Optional - for revenue)
# ==========================================
# Stripe
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# PayStack (African markets)
PAYSTACK_SECRET_KEY=sk_test_xxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx

# Crypto Payments
COINGATE_API_KEY=xxxxx
```

**Save:** Press `Ctrl+O`, `Enter`, then `Ctrl+X`

---

## 🗄️ STEP 3: Setup MongoDB (Choose One)

### Option A: Local MongoDB (Testing - 2 Minutes)

```bash
# Install MongoDB with Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community

# Verify it's running
mongosh --eval "db.adminCommand('ping')"

# ✅ Use this in .env:
MONGODB_URI=mongodb://localhost:27017/trading_bot
```

### Option B: MongoDB Atlas (Production - 5 Minutes)

```bash
# 1. Go to: https://www.mongodb.com/cloud/atlas/register
# 2. Create FREE account
# 3. Create FREE cluster (M0 tier)
# 4. Create database user:
#    Username: tradingbot
#    Password: <generate strong password>
# 5. Network Access: Add 0.0.0.0/0 (allow from anywhere)
# 6. Get connection string from "Connect" button
# 7. Replace <password> with your actual password

# ✅ Use this in .env:
MONGODB_URI=mongodb+srv://tradingbot:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/trading_bot
```

**Recommendation:** Use MongoDB Atlas for production!

---

## 🧪 STEP 4: Test Backend Locally (5 Minutes)

### Start Backend

```bash
cd /Users/gideonaina/Documents/GitHub/forexandcryptotradingbot

# Make sure .env is configured (above)
# Make sure MongoDB is running (above)

# Start web dashboard
python web_dashboard.py

# Open in browser:
# http://localhost:8000/docs
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status":"healthy"}
```

### Test Trading Bot (Paper Trading!)

```bash
# In a new terminal
cd /Users/gideonaina/Documents/GitHub/forexandcryptotradingbot

# Make sure PAPER_TRADING=True in .env!
python advanced_trading_bot.py

# Should connect to OKX and start monitoring
# ✅ No real money will be used (paper trading mode)
```

---

## 📱 STEP 5: Configure Mobile App (5 Minutes)

### Create Mobile App .env

```bash
cd mobile-app
nano .env
```

**Add:**
```bash
# For local testing (same WiFi)
API_URL=http://192.168.1.XXX:8000/api

# For production (after deploying)
# API_URL=https://trading-bot-api.onrender.com/api

# App configuration
ENVIRONMENT=development
```

**Get your IP:**
```bash
ipconfig getifaddr en0
# Example: 192.168.1.105
# Use: API_URL=http://192.168.1.105:8000/api
```

### Update API Service

```bash
# Edit: mobile-app/src/services/api.ts
nano mobile-app/src/services/api.ts
```

**Update this line:**
```typescript
const API_BASE_URL = __DEV__ 
  ? 'http://192.168.1.XXX:8000/api'  // Your Mac's IP
  : 'https://your-production-domain.com/api';
```

---

## 🎯 STEP 6: Test Complete System (5 Minutes)

### Test Flow

```bash
# 1. Backend is running (Step 4)
# Terminal 1:
python web_dashboard.py

# 2. Trading bot is running (Step 4)  
# Terminal 2:
python advanced_trading_bot.py

# 3. Mobile app starts (Step 1)
# Terminal 3:
cd mobile-app
npx expo start --tunnel

# 4. Scan QR code with iPhone
# 5. Test app features!
```

---

## ☁️ STEP 7: Deploy to Production (15 Minutes)

### 7a. Create MongoDB Atlas (if not done)
See Step 3, Option B above

### 7b. Deploy to Render

```bash
# 1. Go to: https://render.com
# 2. Sign up with GitHub (free)
# 3. Click "New +" → "Blueprint"
# 4. Connect your GitHub repo
# 5. Render auto-detects render.yaml
# 6. Add environment variables:
```

**Required Environment Variables in Render:**
```
OKX_API_KEY=your_key
OKX_SECRET_KEY=your_secret
OKX_PASSPHRASE=your_passphrase
MONGODB_URI=mongodb+srv://...
JWT_SECRET_KEY=your_secret
PAPER_TRADING=True
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

**Optional (for payments):**
```
STRIPE_SECRET_KEY=sk_live_xxx
PAYSTACK_SECRET_KEY=sk_live_xxx
COINGATE_API_KEY=xxx
```

```bash
# 7. Click "Apply"
# 8. Wait 5-10 minutes for deployment
# 9. Get your URL: https://trading-bot-api.onrender.com
```

### 7c. Update Mobile App for Production

```bash
# Edit: mobile-app/src/services/api.ts
nano mobile-app/src/services/api.ts
```

**Update:**
```typescript
const API_BASE_URL = __DEV__ 
  ? 'http://192.168.1.105:8000/api'
  : 'https://trading-bot-api.onrender.com/api';  // Your Render URL
```

### 7d. Test Production

```bash
cd mobile-app
npx expo start --tunnel

# App should connect to cloud backend!
# Test all features
```

---

## 💰 STEP 8: Setup Payments (Optional - 10 Minutes)

### Choose Payment Method(s)

#### Option 1: Stripe (Global Cards)
```bash
# 1. Sign up: https://stripe.com
# 2. Get API keys from Dashboard
# 3. Add to .env:
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# 4. Test:
python payment_integration.py
```

#### Option 2: PayStack (African Markets)
```bash
# 1. Sign up: https://paystack.com
# 2. Get API keys
# 3. Add to .env:
PAYSTACK_SECRET_KEY=sk_test_xxx
PAYSTACK_PUBLIC_KEY=pk_test_xxx

# 4. Test:
python paystack_integration.py
```

#### Option 3: Crypto (Global)
```bash
# 1. Sign up: https://coingate.com
# 2. Get API key
# 3. Add to .env:
COINGATE_API_KEY=xxx

# 4. Test:
python crypto_payment.py
```

---

## 📊 STEP 9: Build iOS App for TestFlight (20 Minutes)

### Install EAS CLI
```bash
npm install -g eas-cli
eas login
```

### Initialize EAS
```bash
cd mobile-app
eas init
# Follow prompts
```

### Configure Apple Developer
```bash
# Get from: https://developer.apple.com/account
# - Team ID (10 characters)
# - Bundle ID: com.yourcompany.tradingbot

# Edit: mobile-app/app.json
nano app.json
```

**Update:**
```json
{
  "expo": {
    "ios": {
      "bundleIdentifier": "com.yourcompany.tradingbot"
    }
  }
}
```

### Build for iOS
```bash
eas build --platform ios

# Follow prompts:
# - Apple ID: your@email.com
# - Password: <app-specific password>
# - Team ID: XXXXXXXXXX

# Wait 20-30 minutes
# Download .ipa file
```

### Submit to TestFlight
```bash
eas submit --platform ios

# Or manually via Transporter app
```

---

## ✅ PRODUCTION CHECKLIST

### Backend Configuration
- [ ] OKX API keys configured
- [ ] MongoDB Atlas created and connected
- [ ] JWT secret key set (32+ characters)
- [ ] PAPER_TRADING=True for testing
- [ ] Backend deployed to Render
- [ ] Health endpoint working
- [ ] Telegram notifications working (optional)

### Mobile App
- [ ] App starts with `npx expo start --tunnel`
- [ ] Connects to backend successfully
- [ ] Can login/register
- [ ] Dashboard shows data
- [ ] Can configure bots
- [ ] Payment screens work (optional)

### Payment Systems (Optional)
- [ ] At least one payment method configured
- [ ] Test transactions successful
- [ ] Webhooks configured
- [ ] Subscription plans created

### iOS App
- [ ] Builds successfully with EAS
- [ ] Submitted to TestFlight
- [ ] Beta testers can install
- [ ] All features work in production

### Security
- [ ] All secrets in .env (never committed to git)
- [ ] PAPER_TRADING=True until ready for live
- [ ] IP whitelist configured on OKX
- [ ] Rate limiting enabled
- [ ] HTTPS on production API

---

## 🚨 IMPORTANT SECURITY NOTES

### Trading Bot Safety

```bash
# ALWAYS start with paper trading!
PAPER_TRADING=True

# Only switch to live after:
# - Tested for at least 1 week
# - Verified all strategies work
# - Set proper risk limits
# - Have stop-loss configured
```

### API Key Security

```bash
# ✅ DO:
- Store in .env files (not committed)
- Use IP whitelist on OKX
- Limit API permissions (no withdraw!)
- Use read-only keys for testing

# ❌ DON'T:
- Commit .env to git
- Share API keys
- Give withdraw permission
- Use in production without testing
```

---

## 🐛 Troubleshooting

### Mobile App Won't Start
```bash
# Use tunnel mode (avoids file issues)
cd mobile-app
npx expo start --tunnel
```

### Can't Connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check your IP
ipconfig getifaddr en0

# Update mobile-app .env with correct IP
```

### OKX Connection Failed
```bash
# Verify API keys in .env
# Check OKX API permissions
# Verify IP whitelist (if set)
# Check PAPER_TRADING is set
```

### MongoDB Connection Failed
```bash
# Local: Make sure MongoDB is running
brew services list | grep mongodb

# Atlas: Check connection string
# - Correct password
# - IP whitelist includes 0.0.0.0/0
# - Network access configured
```

---

## 📞 Quick Commands Reference

### Start Everything Locally
```bash
# Terminal 1: Backend
python web_dashboard.py

# Terminal 2: Trading Bot
python advanced_trading_bot.py

# Terminal 3: Mobile App
cd mobile-app && npx expo start --tunnel
```

### Deploy to Production
```bash
# 1. Push code
git add . && git commit -m "Production ready" && git push

# 2. Deploy on Render
# (automatic from render.yaml)

# 3. Update mobile app API URL
# 4. Test!
```

### Build iOS App
```bash
cd mobile-app
eas build --platform ios
eas submit --platform ios
```

---

## 🎉 YOU'RE PRODUCTION READY WHEN:

✅ Mobile app starts and connects to backend  
✅ Backend communicates with OKX API  
✅ MongoDB stores data correctly  
✅ Paper trading works without errors  
✅ Deployed to Render successfully  
✅ Mobile app connects to cloud backend  
✅ At least one payment method configured  
✅ iOS app builds and runs on TestFlight  

**Now you can:**
- 🎯 Start onboarding beta users
- 💰 Accept payments
- 📱 Submit to App Store
- 🚀 Launch publicly!

---

**START WITH:** `cd mobile-app && npx expo start --tunnel`
**THEN:** Configure OKX API keys in .env
**FINALLY:** Deploy to Render!

**You've got this! 💪**
