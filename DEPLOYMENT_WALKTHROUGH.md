# 🎯 DEPLOYMENT WALKTHROUGH - Step-by-Step with Screenshots Guide

## 📖 What This Guide Covers

This is a **visual walkthrough** of deploying your trading bot to Render. Follow each step exactly as shown.

**Total Time:** 30-45 minutes
**Cost:** Free (or $14/month for production)

---

## 🗺️ Deployment Overview

```
Step 1: MongoDB Atlas (Database)
   ↓
Step 2: Render Account (Hosting)
   ↓
Step 3: Deploy Services (API + Worker)
   ↓
Step 4: Configure Environment Variables
   ↓
Step 5: Verify & Test
   ↓
Step 6: Update Mobile App
   ↓
✅ DONE!
```

---

## 📍 STEP 1: MongoDB Atlas Setup (10 minutes)

### 1.1 Create Account

**Go to:** https://www.mongodb.com/cloud/atlas/register

**What you'll see:**
- Sign up form
- Options: Google, GitHub, or Email

**Action:**
1. Click "Sign up with Google" (easiest)
2. Or fill in email, password
3. Click "Create your Atlas account"

**Result:** You're logged into MongoDB Atlas dashboard

---

### 1.2 Create Free Cluster

**What you'll see:**
- "Deploy a cloud database" page
- Three options: Serverless, Dedicated, Shared

**Action:**
1. Click "Create" under **"Shared"** (FREE tier)
2. Provider: **AWS** (recommended)
3. Region: Choose closest to you (e.g., **us-east-1**)
4. Cluster Tier: **M0 Sandbox** (FREE)
5. Cluster Name: `trading-bot-cluster`
6. Click **"Create Cluster"**

**Wait:** 3-5 minutes for cluster to deploy

**Result:** Green checkmark ✅ "Cluster is ready"

---

### 1.3 Create Database User

**What you'll see:**
- Security Quickstart modal
- "How would you like to authenticate your connection?"

**Action:**
1. Choose **"Username and Password"**
2. Username: `tradingbot`
3. Click **"Autogenerate Secure Password"**
4. **⚠️ COPY THIS PASSWORD!** Save it somewhere safe!
5. Click **"Create User"**

**Example password:** `MySecurePass123`

**Result:** User created ✅

---

### 1.4 Configure Network Access

**What you'll see:**
- "Where would you like to connect from?"
- Options: My Local Environment, Cloud Environment

**Action:**
1. Click **"Cloud Environment"**
2. Or click **"Add My Current IP Address"** then **"Add IP Address"**
3. In the modal:
   - Click **"Allow Access from Anywhere"**
   - IP Address: `0.0.0.0/0` (auto-filled)
   - Description: "Render deployment"
4. Click **"Add Entry"**

**Result:** Network access configured ✅

---

### 1.5 Get Connection String

**What you'll see:**
- "Choose a connection method" modal

**Action:**
1. Click **"Connect"** button on your cluster
2. Choose **"Connect your application"**
3. Driver: **Python**
4. Version: **3.12 or later**
5. Copy the connection string:

```
mongodb+srv://tradingbot:<password>@trading-bot-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

6. Replace `<password>` with the password you saved earlier
7. **Save this complete connection string!**

**Example:**
```
mongodb+srv://tradingbot:MySecurePass123@trading-bot-cluster.abc123.mongodb.net/?retryWrites=true&w=majority
```

**Result:** Connection string ready ✅

---

## 📍 STEP 2: Render Account Setup (5 minutes)

### 2.1 Create Render Account

**Go to:** https://render.com

**What you'll see:**
- Render homepage
- "Get Started for Free" button

**Action:**
1. Click **"Get Started for Free"**
2. Click **"Sign up with GitHub"** (recommended!)
3. Authorize Render to access your GitHub
4. Select repositories: Choose **"All repositories"** or select specific repo

**Result:** Logged into Render dashboard

---

### 2.2 Dashboard Overview

**What you'll see:**
- Render dashboard
- "New +" button in top right
- List of services (empty if first time)

**You're ready to deploy!**

---

## 📍 STEP 3: Deploy Using Blueprint (10 minutes)

### 3.1 Start Blueprint Deployment

**What you'll see:**
- Render dashboard

**Action:**
1. Click **"New +"** button (top right)
2. Select **"Blueprint"**

**What you'll see:**
- "Create a new Blueprint Instance" page
- Connect a repository section

---

### 3.2 Connect Repository

**Action:**
1. Find your repository: **forexandcryptotradingbot**
2. Click **"Connect"**

**What you'll see:**
- Repository connected
- Render scanning for `render.yaml`

**Result:** Render found your `render.yaml` file ✅

---

### 3.3 Configure Blueprint

**What you'll see:**
- Blueprint configuration page
- Service Group Name field
- List of services to be created:
  - `trading-bot-api` (Web Service)
  - `trading-bot-worker` (Background Worker)

**Action:**
1. Service Group Name: `trading-bot` (or keep default)
2. Branch: **main** (or **master** if that's your default)
3. Review the services listed
4. Click **"Apply"**

**What happens:**
- Render creates 2 services
- Starts building both services
- This takes 5-10 minutes

**Result:** Services deploying ✅

---

### 3.4 Monitor Build Progress

**What you'll see:**
- Build logs streaming
- Progress indicators for both services

**You'll see messages like:**
```
==> Cloning from https://github.com/...
==> Running build command: pip install -r requirements.txt
==> Installing dependencies...
==> Build successful!
==> Starting service...
```

**Wait for:**
- Both services show **"Live"** status (green)
- This takes 5-10 minutes

**If build fails:**
- Check logs for errors
- Usually missing dependencies or Python version issues
- See troubleshooting section

---

## 📍 STEP 4: Configure Environment Variables (15 minutes)

### 4.1 Configure API Service Variables

**Action:**
1. In Render dashboard, click **"trading-bot-api"**
2. Click **"Environment"** tab (left sidebar)

**What you'll see:**
- List of environment variables
- Some auto-generated (like `JWT_SECRET_KEY`)
- "Add Environment Variable" button

---

### 4.2 Add Required Variables to API

**Click "Add Environment Variable" for each:**

#### Variable 1: MONGODB_URI
```
Key: MONGODB_URI
Value: mongodb+srv://tradingbot:YourPassword@trading-bot-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```
**⚠️ Use YOUR actual connection string from Step 1.5!**

#### Variable 2: OKX_API_KEY
```
Key: OKX_API_KEY
Value: your-okx-api-key-here
```
**Get from:** https://www.okx.com → Profile → API

#### Variable 3: OKX_SECRET_KEY
```
Key: OKX_SECRET_KEY
Value: your-okx-secret-key-here
```
**Get from:** OKX API creation (same place as API key)

#### Variable 4: OKX_PASSPHRASE
```
Key: OKX_PASSPHRASE
Value: your-okx-passphrase-here
```
**Get from:** OKX API creation (passphrase you created)

#### Variable 5: PAPER_TRADING
```
Key: PAPER_TRADING
Value: True
```
**⚠️ IMPORTANT:** Start with `True` for testing!

---

### 4.3 Save API Variables

**Action:**
1. After adding all variables, click **"Save Changes"**
2. Service will restart automatically
3. Wait 1-2 minutes for restart

**What you'll see:**
- "Deploying..." status
- Then "Live" status (green)

**Result:** API service configured ✅

---

### 4.4 Configure Worker Service Variables

**Action:**
1. Go back to Render dashboard
2. Click **"trading-bot-worker"**
3. Click **"Environment"** tab

**Add the SAME variables as API:**

```
Key: MONGODB_URI
Value: (same as API)

Key: OKX_API_KEY
Value: (same as API)

Key: OKX_SECRET_KEY
Value: (same as API)

Key: OKX_PASSPHRASE
Value: (same as API)

Key: PAPER_TRADING
Value: True
```

**Action:**
1. Click **"Save Changes"**
2. Wait for restart (1-2 minutes)

**Result:** Worker service configured ✅

---

## 📍 STEP 5: Verify Deployment (10 minutes)

### 5.1 Check API Service

**Action:**
1. In Render dashboard, click **"trading-bot-api"**
2. Look for the URL at the top (e.g., `https://trading-bot-api.onrender.com`)
3. Click the URL

**What you should see:**
- Your API is running!
- Or a welcome page

**Test endpoints:**

#### Health Check
```
https://trading-bot-api.onrender.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "2.0.0"
}
```

#### API Documentation
```
https://trading-bot-api.onrender.com/docs
```

**Expected:** FastAPI Swagger UI with all endpoints

#### User Dashboard
```
https://trading-bot-api.onrender.com/static/user_dashboard.html
```

**Expected:** Trading dashboard HTML page

**Result:** API working ✅

---

### 5.2 Check Worker Service Logs

**Action:**
1. In Render dashboard, click **"trading-bot-worker"**
2. Click **"Logs"** tab

**What you should see:**
```
✅ Connected to MongoDB successfully
✅ Database: trading_bot
✅ Connected to OKX API
✅ Paper trading mode: True
✅ Starting trading bot...
✅ Monitoring markets: BTC-USDT, ETH-USDT...
```

**Good signs:**
- No error messages
- "Connected to MongoDB"
- "Connected to OKX"
- "Paper trading mode: True"
- Market monitoring messages

**Bad signs (need to fix):**
- "Failed to connect to MongoDB" → Check MONGODB_URI
- "Invalid API key" → Check OKX credentials
- "Import error" → Check requirements.txt

**Result:** Worker running ✅

---

### 5.3 Test API Endpoints

**Using browser or curl:**

#### Test 1: Health Check
```bash
curl https://trading-bot-api.onrender.com/health
```

**Expected:** `{"status": "healthy", ...}`

#### Test 2: Create Test User
```bash
# Go to: https://trading-bot-api.onrender.com/docs
# Find: POST /api/register
# Click "Try it out"
# Enter:
{
  "email": "test@example.com",
  "password": "TestPass123",
  "full_name": "Test User"
}
# Click "Execute"
```

**Expected:** User created successfully

#### Test 3: Login
```bash
# In API docs: POST /api/login
# Enter:
{
  "email": "test@example.com",
  "password": "TestPass123"
}
# Click "Execute"
```

**Expected:** JWT token returned

**Result:** All tests pass ✅

---

## 📍 STEP 6: Update Mobile App (5 minutes)

### 6.1 Find API Configuration

**Action:**
```bash
cd /Users/gideonaina/Documents/GitHub/forexandcryptotradingbot/mobile-app
```

**Look for one of these files:**
- `src/services/api.ts`
- `src/config.ts`
- `src/constants.ts`
- `.env`

---

### 6.2 Update API URL

**If using TypeScript file (api.ts):**

```typescript
// Before:
const API_BASE_URL = 'http://localhost:8000/api';

// After:
const API_BASE_URL = 'https://trading-bot-api.onrender.com/api';
```

**If using .env file:**

```bash
# Before:
API_URL=http://localhost:8000/api

# After:
API_URL=https://trading-bot-api.onrender.com/api
```

**⚠️ Replace `trading-bot-api` with YOUR actual Render URL!**

---

### 6.3 Test Mobile App

**Action:**
```bash
# Start mobile app
cd mobile-app
npx expo start --tunnel

# Scan QR code with iPhone
```

**What should happen:**
1. App loads on iPhone
2. Can register new user
3. Can login
4. Dashboard loads
5. Shows trading data

**Result:** Mobile app connected ✅

---

## ✅ Deployment Complete!

### What's Running:

```
✅ Backend API
   URL: https://trading-bot-api.onrender.com
   Status: Live
   
✅ Trading Bot Worker
   Status: Running 24/7
   Mode: Paper Trading
   
✅ MongoDB Database
   Provider: Atlas
   Tier: Free M0
   
✅ Mobile App
   Connected to: Deployed API
   Status: Working
```

---

## 📊 What to Do Next

### Immediate (Today):

1. **Monitor Logs**
   - Check API logs daily
   - Check Worker logs daily
   - Look for errors

2. **Test Everything**
   - Create test users
   - Test login/register
   - Test mobile app features
   - Verify bot is monitoring markets

3. **Paper Trading**
   - Let bot run for 1-2 weeks
   - Monitor performance
   - Check trading signals
   - Verify risk management

### This Week:

1. **Add Telegram Notifications** (Optional)
   - Get bot token from BotFather
   - Add to environment variables
   - Test notifications

2. **Set Up Monitoring**
   - Enable Render email alerts
   - Check logs daily
   - Monitor MongoDB usage

3. **Test Mobile App Thoroughly**
   - All screens work
   - API calls succeed
   - Data displays correctly

### Next Week:

1. **Add Payment Integration** (Optional)
   - Stripe for global payments
   - PayStack for African payments
   - Test payment flow

2. **Consider Upgrading**
   - If happy with free tier, stay on it
   - If need better performance, upgrade to Starter ($14/mo)
   - No cold starts on paid tier

3. **Go Live** (When Ready)
   - After 1-2 weeks of successful paper trading
   - Change `PAPER_TRADING` to `False`
   - Start with small capital
   - Monitor VERY closely

---

## 🚨 Common Issues & Solutions

### Issue 1: "Service Unavailable" on API

**Cause:** Free tier spins down after 15 min inactivity

**Solution:**
- Wait 30 seconds, try again (it's waking up)
- Or upgrade to Starter tier ($7/mo) for always-on

---

### Issue 2: Worker Logs Show "MongoDB Connection Failed"

**Cause:** Wrong connection string or network access

**Solution:**
1. Check MONGODB_URI in environment variables
2. Verify password is correct (no typos)
3. Check MongoDB Atlas → Network Access → 0.0.0.0/0 is added
4. Try connection string in MongoDB Compass to test

---

### Issue 3: "Invalid OKX API Key"

**Cause:** Wrong credentials or expired key

**Solution:**
1. Verify all 3 values: API_KEY, SECRET_KEY, PASSPHRASE
2. Check key is still active in OKX dashboard
3. Verify permissions: Read + Trade (not Withdraw)
4. Create new API key if needed

---

### Issue 4: Mobile App Can't Connect

**Cause:** Wrong API URL or CORS issue

**Solution:**
1. Verify API URL in mobile app matches Render URL
2. Test API health endpoint in browser
3. Check API logs for CORS errors
4. Ensure API is "Live" in Render dashboard

---

### Issue 5: Build Failed

**Cause:** Missing dependencies or Python version

**Solution:**
1. Check build logs for specific error
2. Verify `requirements.txt` has all dependencies
3. Python version is set in `render.yaml` (3.11.0)
4. Try manual deploy: Render Dashboard → Service → Manual Deploy

---

## 💰 Pricing Summary

### Current Setup (Free):

```
MongoDB Atlas M0: $0/month
Render API (Free): $0/month
Render Worker (Free): $0/month
─────────────────────────────
Total: $0/month
```

**Limitations:**
- API spins down after 15 min (30s wake-up time)
- 750 hours/month per service
- Limited resources

### Recommended (Production):

```
MongoDB Atlas M0: $0/month (still free!)
Render API (Starter): $7/month
Render Worker (Starter): $7/month
─────────────────────────────
Total: $14/month
```

**Benefits:**
- Always on (no cold starts)
- Better performance
- More reliable
- Worth it for real users

### How to Upgrade:

```
1. Render Dashboard → Service
2. Settings → Instance Type
3. Select "Starter"
4. Save Changes
5. Done!
```

---

## 📝 Deployment Checklist

Print this and check off as you go:

### MongoDB Atlas:
- [ ] Account created
- [ ] Free M0 cluster created
- [ ] Database user created (saved password!)
- [ ] Network access: 0.0.0.0/0
- [ ] Connection string copied and saved

### OKX API:
- [ ] Account created
- [ ] API key created
- [ ] Permissions: Read + Trade only
- [ ] All 3 values saved (key, secret, passphrase)

### Render - Deployment:
- [ ] Account created (signed up with GitHub)
- [ ] Repository connected
- [ ] Blueprint deployed
- [ ] API service shows "Live"
- [ ] Worker service shows "Live"

### Render - API Service:
- [ ] MONGODB_URI added
- [ ] OKX_API_KEY added
- [ ] OKX_SECRET_KEY added
- [ ] OKX_PASSPHRASE added
- [ ] PAPER_TRADING set to True
- [ ] JWT_SECRET_KEY exists
- [ ] Service restarted
- [ ] Health check works
- [ ] API docs accessible

### Render - Worker Service:
- [ ] MONGODB_URI added
- [ ] OKX_API_KEY added
- [ ] OKX_SECRET_KEY added
- [ ] OKX_PASSPHRASE added
- [ ] PAPER_TRADING set to True
- [ ] Service restarted
- [ ] Logs show MongoDB connected
- [ ] Logs show OKX connected
- [ ] Monitoring markets

### Mobile App:
- [ ] API URL updated to Render URL
- [ ] App tested on device
- [ ] Can register new user
- [ ] Can login
- [ ] Dashboard loads
- [ ] Data displays correctly

### Verification:
- [ ] API health endpoint works
- [ ] Can create users via API
- [ ] Can login via API
- [ ] Worker logs show trading activity
- [ ] No errors in logs
- [ ] Mobile app fully functional

---

## 🎉 Success!

If you've checked all the boxes above, congratulations! 🎊

**You now have:**
- ✅ Fully deployed trading bot API
- ✅ 24/7 running trading bot worker
- ✅ Cloud database (MongoDB Atlas)
- ✅ Mobile app connected to cloud
- ✅ Everything running in production!

**Your URLs:**
```
API: https://trading-bot-api.onrender.com
Docs: https://trading-bot-api.onrender.com/docs
Dashboard: https://trading-bot-api.onrender.com/static/user_dashboard.html
```

**Next Steps:**
1. Monitor for 1-2 weeks in paper trading mode
2. Test all features thoroughly
3. Add payment integration (optional)
4. When confident, switch to live trading
5. Start making money! 💰

---

## 📚 Additional Resources

- **DEPLOY_NOW.md** - Complete deployment guide
- **ENV_VARS_CHECKLIST.md** - Environment variables reference
- **RENDER_DEPLOYMENT.md** - Detailed Render guide
- **START_NOW.md** - Quick start guide

---

**You did it! Your trading bot is live! 🚀**

**Remember:** Start with paper trading, test thoroughly, monitor closely!

**Good luck! 💪**
