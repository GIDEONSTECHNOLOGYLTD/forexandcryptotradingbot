# ⚡ QUICK DEPLOY CARD - 30 Minute Deployment

**Print this page and follow along!**

---

## 🎯 What You're Deploying

```
Backend API + Frontend → Render (together!)
Trading Bot Worker → Render
Database → MongoDB Atlas (free)
Mobile App → Connects to deployed API
```

**Total Cost:** $0 (free tier) or $14/month (recommended)

---

## ✅ Before You Start - Gather These:

- [ ] GitHub account (for Render login)
- [ ] Email for MongoDB Atlas
- [ ] OKX account (for trading API)
- [ ] 30-45 minutes of time

---

## 📋 STEP 1: MongoDB Atlas (10 min)

### Quick Actions:

1. **Sign up:** https://www.mongodb.com/cloud/atlas/register
2. **Create cluster:** Choose "Shared" → "M0 FREE" → AWS → us-east-1
3. **Create user:** Username: `tradingbot`, Auto-generate password → **SAVE IT!**
4. **Network:** Allow access from anywhere (0.0.0.0/0)
5. **Get connection string:** Click "Connect" → "Connect your application" → Copy

**Your connection string:**
```
mongodb+srv://tradingbot:PASSWORD@cluster.mongodb.net/?retryWrites=true&w=majority
```

**✅ Save this connection string!**

---

## 📋 STEP 2: OKX API Keys (5 min)

### Quick Actions:

1. **Login:** https://www.okx.com
2. **Go to:** Profile → API Management
3. **Create API:** 
   - Permissions: ✅ Read, ✅ Trade, ❌ Withdraw
   - IP Whitelist: Leave empty
4. **Save 3 values:**
   - API Key
   - Secret Key
   - Passphrase

**✅ Save all 3 values!**

---

## 📋 STEP 3: Deploy to Render (10 min)

### Quick Actions:

1. **Sign up:** https://render.com → "Sign up with GitHub"
2. **New Blueprint:** Click "New +" → "Blueprint"
3. **Connect repo:** Select `forexandcryptotradingbot` → Branch: `main`
4. **Deploy:** Click "Apply"
5. **Wait:** 5-10 minutes for build

**✅ Both services should show "Live"**

---

## 📋 STEP 4: Add Environment Variables (10 min)

### For API Service (trading-bot-api):

**Go to:** Render Dashboard → trading-bot-api → Environment

**Add these variables:**

| Key | Value |
|-----|-------|
| `MONGODB_URI` | Your MongoDB connection string |
| `OKX_API_KEY` | Your OKX API key |
| `OKX_SECRET_KEY` | Your OKX secret key |
| `OKX_PASSPHRASE` | Your OKX passphrase |
| `PAPER_TRADING` | `True` |

**Click "Save Changes"**

---

### For Worker Service (trading-bot-worker):

**Go to:** Render Dashboard → trading-bot-worker → Environment

**Add SAME variables:**

| Key | Value |
|-----|-------|
| `MONGODB_URI` | Same as API |
| `OKX_API_KEY` | Same as API |
| `OKX_SECRET_KEY` | Same as API |
| `OKX_PASSPHRASE` | Same as API |
| `PAPER_TRADING` | `True` |

**Click "Save Changes"**

**✅ Both services will restart**

---

## 📋 STEP 5: Verify (5 min)

### Check API:

**Open in browser:**
```
https://trading-bot-api.onrender.com/health
```

**Should see:**
```json
{"status": "healthy", ...}
```

**Check docs:**
```
https://trading-bot-api.onrender.com/docs
```

**Should see:** FastAPI Swagger UI

---

### Check Worker Logs:

**Go to:** Render Dashboard → trading-bot-worker → Logs

**Should see:**
```
✅ Connected to MongoDB
✅ Connected to OKX
✅ Paper trading mode: True
✅ Monitoring markets...
```

**✅ Everything working!**

---

## 📋 STEP 6: Update Mobile App (5 min)

### Quick Actions:

1. **Open:** `mobile-app/src/services/api.ts` (or similar file)
2. **Change:**
   ```typescript
   // Before:
   const API_BASE_URL = 'http://localhost:8000/api';
   
   // After:
   const API_BASE_URL = 'https://trading-bot-api.onrender.com/api';
   ```
3. **Test:**
   ```bash
   cd mobile-app
   npx expo start --tunnel
   ```
4. **Scan QR** with iPhone

**✅ App should connect to deployed API!**

---

## 🎉 DONE!

### What's Live:

```
✅ API: https://trading-bot-api.onrender.com
✅ Worker: Running 24/7
✅ Database: MongoDB Atlas
✅ Mobile App: Connected
```

---

## 📊 Quick Reference

### Your Deployment URLs:

```
API Health: https://trading-bot-api.onrender.com/health
API Docs: https://trading-bot-api.onrender.com/docs
Dashboard: https://trading-bot-api.onrender.com/static/user_dashboard.html
```

### Environment Variables Needed:

```
MONGODB_URI=mongodb+srv://...
OKX_API_KEY=...
OKX_SECRET_KEY=...
OKX_PASSPHRASE=...
PAPER_TRADING=True
```

### Where to Check Logs:

```
API Logs: Render Dashboard → trading-bot-api → Logs
Worker Logs: Render Dashboard → trading-bot-worker → Logs
```

---

## 🚨 Quick Troubleshooting

### API not responding?
- Check if service is "Live" in Render
- Free tier sleeps after 15 min (wait 30s)
- Check logs for errors

### Worker not connecting?
- Check environment variables are set
- Verify MongoDB connection string
- Verify OKX API keys
- Check logs for specific error

### Mobile app can't connect?
- Verify API URL is correct
- Test API health endpoint in browser
- Check API is "Live" in Render

---

## 💰 Costs

### Free Tier:
```
MongoDB Atlas: $0
Render API: $0
Render Worker: $0
Total: $0/month
```

**Limitation:** API sleeps after 15 min

### Recommended (Production):
```
MongoDB Atlas: $0
Render API: $7/month
Render Worker: $7/month
Total: $14/month
```

**Benefit:** Always on, no cold starts

---

## 📚 Full Guides

For detailed instructions, see:

- **DEPLOY_NOW.md** - Complete deployment guide
- **DEPLOYMENT_WALKTHROUGH.md** - Step-by-step with screenshots
- **ENV_VARS_CHECKLIST.md** - Environment variables reference
- **RENDER_DEPLOYMENT.md** - Render-specific guide

---

## ✅ Deployment Checklist

**Print and check off:**

- [ ] MongoDB Atlas account created
- [ ] Free M0 cluster created
- [ ] Database user created (password saved)
- [ ] Network access configured (0.0.0.0/0)
- [ ] Connection string saved
- [ ] OKX API keys created (all 3 values saved)
- [ ] Render account created
- [ ] Repository connected
- [ ] Blueprint deployed
- [ ] API service "Live"
- [ ] Worker service "Live"
- [ ] Environment variables added to API
- [ ] Environment variables added to Worker
- [ ] API health check works
- [ ] Worker logs show connections
- [ ] Mobile app URL updated
- [ ] Mobile app tested and working

---

## 🎯 Next Steps

### Today:
- [ ] Monitor logs
- [ ] Test all features
- [ ] Verify paper trading mode

### This Week:
- [ ] Let bot run for 1-2 weeks
- [ ] Monitor performance
- [ ] Test mobile app thoroughly

### When Ready:
- [ ] Add payment integration (optional)
- [ ] Upgrade to Starter tier ($14/mo)
- [ ] Switch to live trading (carefully!)

---

## 🆘 Need Help?

**Check logs first:**
- Render Dashboard → Service → Logs

**Common fixes:**
- Verify all environment variables
- Check MongoDB Atlas network access
- Verify OKX API keys are correct
- Restart services in Render

**Still stuck?**
- Review full guides (DEPLOY_NOW.md)
- Check error messages in logs
- Verify all steps completed

---

**You've got this! 🚀**

**Total time: 30-45 minutes**

**Start with Step 1 above!**
