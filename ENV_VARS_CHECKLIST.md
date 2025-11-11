# 🔑 Environment Variables Checklist for Render

## ✅ Quick Reference - Copy This!

Use this checklist when setting up environment variables in Render Dashboard.

---

## 📋 REQUIRED Variables (Must Have!)

### For Both Services (API + Worker)

| Variable Name | Where to Get It | Example Value | Notes |
|--------------|-----------------|---------------|-------|
| `MONGODB_URI` | MongoDB Atlas | `mongodb+srv://user:pass@cluster.mongodb.net/` | Connection string from Atlas |
| `OKX_API_KEY` | OKX.com → API | `a1b2c3d4-e5f6-7890-abcd` | From OKX API management |
| `OKX_SECRET_KEY` | OKX.com → API | `ABC123XYZ789...` | From OKX API management |
| `OKX_PASSPHRASE` | OKX.com → API | `MySecurePass123` | Created when making OKX API |
| `PAPER_TRADING` | Set manually | `True` | Start with True! |

### For API Service Only

| Variable Name | Where to Get It | Example Value | Notes |
|--------------|-----------------|---------------|-------|
| `JWT_SECRET_KEY` | Auto-generated | (auto) | Render generates this |

---

## 🎯 How to Add in Render

### For API Service (trading-bot-api):

```bash
# 1. Go to Render Dashboard
# 2. Click "trading-bot-api"
# 3. Click "Environment" tab
# 4. Click "Add Environment Variable"
# 5. Add each variable:

Key: MONGODB_URI
Value: mongodb+srv://tradingbot:YourPassword@cluster.mongodb.net/?retryWrites=true&w=majority

Key: OKX_API_KEY
Value: your-okx-api-key-here

Key: OKX_SECRET_KEY
Value: your-okx-secret-key-here

Key: OKX_PASSPHRASE
Value: your-okx-passphrase-here

Key: PAPER_TRADING
Value: True

# JWT_SECRET_KEY is already auto-generated - leave it!

# 6. Click "Save Changes"
```

### For Worker Service (trading-bot-worker):

```bash
# 1. Go to Render Dashboard
# 2. Click "trading-bot-worker"
# 3. Click "Environment" tab
# 4. Click "Add Environment Variable"
# 5. Add each variable:

Key: MONGODB_URI
Value: mongodb+srv://tradingbot:YourPassword@cluster.mongodb.net/?retryWrites=true&w=majority

Key: OKX_API_KEY
Value: your-okx-api-key-here

Key: OKX_SECRET_KEY
Value: your-okx-secret-key-here

Key: OKX_PASSPHRASE
Value: your-okx-passphrase-here

Key: PAPER_TRADING
Value: True

# 6. Click "Save Changes"
```

---

## 🔐 How to Get Each Value

### 1. MONGODB_URI

**Steps:**
1. Go to https://www.mongodb.com/cloud/atlas
2. Login to your account
3. Click "Database" in left sidebar
4. Click "Connect" on your cluster
5. Choose "Connect your application"
6. Copy the connection string
7. Replace `<password>` with your database user password

**Format:**
```
mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority
```

**Example:**
```
mongodb+srv://tradingbot:MySecurePass123@trading-bot-cluster.abc123.mongodb.net/?retryWrites=true&w=majority
```

### 2. OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE

**Steps:**
1. Go to https://www.okx.com
2. Login to your account
3. Click Profile (top right)
4. Go to "API" section
5. Click "Create API Key"
6. **Permissions:** Select "Read" and "Trade" (DO NOT select "Withdraw"!)
7. **IP Whitelist:** Leave empty for now (or add Render IPs later)
8. **Passphrase:** Create a strong passphrase (you'll need to remember this!)
9. Click "Confirm"
10. Save all 3 values:
    - API Key
    - Secret Key
    - Passphrase

**⚠️ IMPORTANT:**
- Save these immediately! Secret key is only shown once!
- Never share these keys
- Never commit to git
- Only use in Render environment variables

### 3. JWT_SECRET_KEY

**Already handled by Render!**
- Render auto-generates this when you use Blueprint
- You don't need to set it manually
- If it's missing, Render will create it

### 4. PAPER_TRADING

**Just set it manually:**
```
Key: PAPER_TRADING
Value: True
```

**⚠️ IMPORTANT:**
- Start with `True` (paper trading mode)
- Test for at least 1-2 weeks
- Only change to `False` when you're confident
- Monitor closely when switching to live trading

---

## 💳 Optional Variables (Add Later)

### Payment Integration (When Ready)

#### Stripe (Global Credit Cards)

| Variable | Where to Get | Example |
|----------|-------------|---------|
| `STRIPE_SECRET_KEY` | https://stripe.com → Developers → API Keys | `sk_test_...` or `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe → Webhooks → Add endpoint | `whsec_...` |

**Steps:**
1. Sign up at https://stripe.com
2. Go to Developers → API Keys
3. Copy "Secret key" (use test key first!)
4. For webhooks:
   - Go to Developers → Webhooks
   - Add endpoint: `https://your-api.onrender.com/api/stripe/webhook`
   - Copy webhook signing secret

#### PayStack (African Payments)

| Variable | Where to Get | Example |
|----------|-------------|---------|
| `PAYSTACK_SECRET_KEY` | https://paystack.com → Settings → API Keys | `sk_test_...` or `sk_live_...` |

**Steps:**
1. Sign up at https://paystack.com
2. Go to Settings → API Keys & Webhooks
3. Copy "Secret key" (use test key first!)

#### Crypto Payments

| Variable | Where to Get | Example |
|----------|-------------|---------|
| `COINGATE_API_KEY` | https://coingate.com → Account → API | Your API key |

**Steps:**
1. Sign up at https://coingate.com
2. Go to Account → API
3. Create API token
4. Copy token

### Telegram Notifications (Optional)

| Variable | Where to Get | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | BotFather on Telegram | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `TELEGRAM_CHAT_ID` | Your Telegram chat | `123456789` |

**Steps:**
1. Open Telegram
2. Search for "@BotFather"
3. Send `/newbot`
4. Follow instructions
5. Copy bot token
6. For chat ID:
   - Send message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in response

---

## ✅ Verification Checklist

After adding all variables, verify:

### API Service:
- [ ] MONGODB_URI is set
- [ ] OKX_API_KEY is set
- [ ] OKX_SECRET_KEY is set
- [ ] OKX_PASSPHRASE is set
- [ ] JWT_SECRET_KEY exists (auto-generated)
- [ ] PAPER_TRADING is set to True
- [ ] Service restarted after adding variables
- [ ] No errors in logs

### Worker Service:
- [ ] MONGODB_URI is set (same as API)
- [ ] OKX_API_KEY is set (same as API)
- [ ] OKX_SECRET_KEY is set (same as API)
- [ ] OKX_PASSPHRASE is set (same as API)
- [ ] PAPER_TRADING is set to True
- [ ] Service restarted after adding variables
- [ ] Logs show "Connected to MongoDB"
- [ ] Logs show "Connected to OKX"

---

## 🔍 Testing Your Variables

### Test MongoDB Connection

```bash
# Check worker logs in Render Dashboard
# Should see:
✅ "Connected to MongoDB successfully"
✅ "Database: trading_bot"

# If you see errors:
❌ "Failed to connect to MongoDB"
→ Check MONGODB_URI is correct
→ Check password has no special characters that need encoding
→ Check network access in MongoDB Atlas (0.0.0.0/0)
```

### Test OKX Connection

```bash
# Check worker logs in Render Dashboard
# Should see:
✅ "Connected to OKX API"
✅ "Account balance: ..."
✅ "Paper trading mode: True"

# If you see errors:
❌ "Invalid API key"
→ Check OKX_API_KEY is correct
❌ "Invalid signature"
→ Check OKX_SECRET_KEY is correct
❌ "Invalid passphrase"
→ Check OKX_PASSPHRASE is correct
```

### Test API Health

```bash
# Open in browser:
https://trading-bot-api.onrender.com/health

# Should return:
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "2.0.0"
}

# If 500 error:
→ Check logs for specific error
→ Verify all required env vars are set
```

---

## 🚨 Common Issues & Fixes

### Issue: "MongoDB connection failed"

**Possible causes:**
1. Wrong connection string
2. Wrong password
3. Network access not configured
4. Special characters in password

**Fixes:**
```bash
# 1. Verify connection string format:
mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority

# 2. Check password:
# - No spaces
# - If special characters, URL encode them
# - Example: p@ssw0rd → p%40ssw0rd

# 3. MongoDB Atlas → Network Access:
# - Must have 0.0.0.0/0 (allow from anywhere)

# 4. MongoDB Atlas → Database Access:
# - User must have "Read and write to any database" permission
```

### Issue: "OKX API authentication failed"

**Possible causes:**
1. Wrong API key
2. Wrong secret key
3. Wrong passphrase
4. API key expired or deleted

**Fixes:**
```bash
# 1. Verify all 3 values are correct
# 2. Check API key is still active in OKX
# 3. Verify permissions: Read + Trade (not Withdraw)
# 4. If still failing, create new API key
```

### Issue: "JWT token error"

**Possible causes:**
1. JWT_SECRET_KEY not set
2. JWT_SECRET_KEY too short

**Fixes:**
```bash
# Should be auto-generated by Render
# If missing, add manually:
Key: JWT_SECRET_KEY
Value: (generate a long random string, min 32 characters)

# Example:
JWT_SECRET_KEY=your_very_long_random_secret_key_min_32_chars_abc123xyz789
```

---

## 📝 Environment Variables Template

Copy this template and fill in your values:

```bash
# ============================================
# REQUIRED - Both API and Worker Services
# ============================================

MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority
OKX_API_KEY=your_okx_api_key_here
OKX_SECRET_KEY=your_okx_secret_key_here
OKX_PASSPHRASE=your_okx_passphrase_here
PAPER_TRADING=True

# ============================================
# REQUIRED - API Service Only
# ============================================

JWT_SECRET_KEY=auto_generated_by_render

# ============================================
# OPTIONAL - Add When Ready
# ============================================

# Stripe Payments
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# PayStack Payments
PAYSTACK_SECRET_KEY=sk_test_your_paystack_key

# Crypto Payments
COINGATE_API_KEY=your_coingate_api_key

# Telegram Notifications
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

---

## 🎯 Quick Setup Checklist

Use this when deploying:

1. **MongoDB Atlas Setup:**
   - [ ] Account created
   - [ ] Free M0 cluster created
   - [ ] Database user created (username + password)
   - [ ] Network access: 0.0.0.0/0
   - [ ] Connection string copied

2. **OKX API Setup:**
   - [ ] Account created
   - [ ] API key created
   - [ ] Permissions: Read + Trade only
   - [ ] All 3 values saved (key, secret, passphrase)

3. **Render - API Service:**
   - [ ] MONGODB_URI added
   - [ ] OKX_API_KEY added
   - [ ] OKX_SECRET_KEY added
   - [ ] OKX_PASSPHRASE added
   - [ ] PAPER_TRADING set to True
   - [ ] JWT_SECRET_KEY exists
   - [ ] Service restarted
   - [ ] Health check passes

4. **Render - Worker Service:**
   - [ ] MONGODB_URI added
   - [ ] OKX_API_KEY added
   - [ ] OKX_SECRET_KEY added
   - [ ] OKX_PASSPHRASE added
   - [ ] PAPER_TRADING set to True
   - [ ] Service restarted
   - [ ] Logs show MongoDB connected
   - [ ] Logs show OKX connected

5. **Verification:**
   - [ ] API responds to /health
   - [ ] API docs accessible at /docs
   - [ ] Worker logs show trading activity
   - [ ] No errors in logs
   - [ ] Mobile app can connect

---

## 💡 Pro Tips

### 1. Use Strong Passwords

```bash
# For MongoDB:
# - Min 12 characters
# - Mix of letters, numbers, symbols
# - Avoid special characters that need URL encoding

# Good: MySecurePass123!
# Bad: p@ss (too short, needs encoding)
```

### 2. Keep Credentials Safe

```bash
# ✅ DO:
- Store in password manager
- Use Render environment variables
- Keep .env in .gitignore

# ❌ DON'T:
- Commit to git
- Share in chat/email
- Hardcode in files
```

### 3. Test Before Live

```bash
# Always test with:
PAPER_TRADING=True

# Only switch to live when:
- Tested for 1-2 weeks
- Verified strategies work
- Comfortable with bot behavior
- Ready to monitor closely
```

### 4. Monitor Regularly

```bash
# Check daily:
- Render logs (API + Worker)
- MongoDB data
- Trading performance
- Error messages

# Set up alerts:
- Render email notifications
- Telegram notifications
- Error tracking
```

---

## 🆘 Need Help?

### Can't Find a Value?

1. **MongoDB URI:** Check MongoDB Atlas → Database → Connect
2. **OKX Keys:** Check OKX.com → Profile → API
3. **JWT Secret:** Auto-generated by Render (check Environment tab)

### Variables Not Working?

1. Check spelling (case-sensitive!)
2. Check for extra spaces
3. Verify format is correct
4. Restart service after adding
5. Check logs for specific errors

### Still Stuck?

1. Review `DEPLOY_NOW.md` for detailed steps
2. Check Render logs for error messages
3. Verify MongoDB Atlas network access
4. Test OKX API keys in OKX dashboard
5. Make sure all required variables are set

---

**Use this checklist every time you deploy!** ✅

**Remember:** Required variables must be set for both API and Worker services!
