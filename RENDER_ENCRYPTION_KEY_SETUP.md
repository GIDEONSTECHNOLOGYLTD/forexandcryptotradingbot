# 🔐 RENDER ENCRYPTION KEY SETUP

## 🚨 ISSUE:
Backend crashed because `ENCRYPTION_KEY` environment variable is not set in Render.

## ✅ FIXED:
Added error handling so backend won't crash, but you need to set the key for full functionality.

---

## 🔑 GENERATE ENCRYPTION KEY:

Run this in your terminal:

```python
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Example output:**
```
8ZJQXqU9vZ_Kx7YnM2pL5wR3tN6hG4jF1dS0aB9cE8o=
```

**Copy this key!** ⬆️

---

## 🚀 ADD TO RENDER:

### 1. Go to Render Dashboard
https://dashboard.render.com

### 2. Select Your Service
- Click on `trading-bot-api` service

### 3. Go to Environment
- Click "Environment" tab on the left

### 4. Add New Variable
- Click "Add Environment Variable"
- **Key:** `ENCRYPTION_KEY`
- **Value:** Paste the key you generated (e.g., `8ZJQXqU9vZ_Kx7YnM2pL5wR3tN6hG4jF1dS0aB9cE8o=`)
- Click "Save Changes"

### 5. Deploy
Render will automatically redeploy with the new key.

---

## ✅ WHAT THIS FIXES:

### Before:
```
❌ Backend crashes on startup
❌ Can't encrypt user API keys
❌ Can't fetch user balances
```

### After:
```
✅ Backend starts successfully
✅ User API keys encrypted securely
✅ Balance feature works
✅ Everything operational
```

---

## 🔒 SECURITY:

### Why We Need This:
- Encrypts user OKX API keys in database
- Prevents plain-text storage of sensitive data
- Required for GDPR/security compliance

### Key Requirements:
- Must be 32 url-safe base64-encoded bytes
- Keep it secret (don't commit to git)
- Same key must be used across all services
- If you lose it, encrypted data is unrecoverable

---

## 📋 COMPLETE ENVIRONMENT VARIABLES:

Make sure ALL these are set in Render:

```bash
# Database
MONGODB_URI=mongodb+srv://...

# JWT
JWT_SECRET_KEY=your-jwt-secret

# Encryption (NEW!)
ENCRYPTION_KEY=8ZJQXqU9vZ_Kx7YnM2pL5wR3tN6hG4jF1dS0aB9cE8o=

# OKX Admin Account
OKX_API_KEY=your-okx-api-key
OKX_SECRET_KEY=your-okx-secret
OKX_PASSPHRASE=your-okx-passphrase

# Payment
PAYSTACK_SECRET_KEY=your-paystack-key
```

---

## 🧪 TEST AFTER DEPLOYMENT:

### 1. Check Backend Health
```bash
curl https://trading-bot-api-7xps.onrender.com/health
```

Expected: `{"status": "healthy"}`

### 2. Test Balance Endpoint
```bash
# Login first to get token
curl -X POST https://trading-bot-api-7xps.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@tradingbot.com","password":"admin123"}'

# Use token to get balance
curl https://trading-bot-api-7xps.onrender.com/api/user/balance \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected: Admin OKX balance data

---

## 🎯 PRIORITY:

**HIGH** - Set this NOW to enable:
- ✅ User exchange connections
- ✅ Real-time balance feature
- ✅ Secure API key storage
- ✅ Full platform functionality

---

## 💡 QUICK SETUP:

```bash
# 1. Generate key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Copy output

# 3. Go to Render → trading-bot-api → Environment

# 4. Add: ENCRYPTION_KEY = <paste key>

# 5. Save → Auto-deploys

# 6. DONE! ✅
```

**DO THIS NOW!** 🚀🔐
