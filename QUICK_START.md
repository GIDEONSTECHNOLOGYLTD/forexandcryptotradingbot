# 🚀 Quick Start Guide

## ✅ Fixed: "Too Many Open Files" Error

The mobile app error has been fixed! Here's how to start it:

---

## 📱 Start Mobile App (2 Commands!)

### Option 1: Use the start script (Easiest)
```bash
cd mobile-app
./start-app.sh
```

### Option 2: Manual commands
```bash
cd mobile-app

# Fix file limit (macOS issue)
ulimit -n 65536

# Start with cleared cache
npm start -- --clear
```

### What This Does:
1. ✅ Increases macOS file limit to 65,536
2. ✅ Clears Metro bundler cache
3. ✅ Starts Expo development server
4. ✅ Shows QR code to scan

---

## 📱 Test on iPhone (30 seconds!)

1. **Install Expo Go** on your iPhone (App Store - free)

2. **Make sure iPhone and Mac are on same WiFi**

3. **Scan the QR code** that appears in terminal
   - Use iPhone Camera app
   - Or use Expo Go app's "Scan QR Code" button

4. **App opens on iPhone!** 🎉

---

## 🚀 Deploy Backend to Render (10 minutes)

### Step 1: Create Render Account
```bash
# Go to: https://render.com
# Sign up with GitHub (free)
```

### Step 2: Create MongoDB Atlas
```bash
# Go to: https://www.mongodb.com/cloud/atlas
# Create free M0 cluster
# Get connection string
```

### Step 3: Deploy from GitHub
```bash
# In Render Dashboard:
# 1. Click "New +"
# 2. Select "Blueprint"
# 3. Connect your GitHub repo
# 4. Render auto-detects render.yaml
# 5. Add environment variables:
#    - MONGODB_URI
#    - OKX_API_KEY
#    - OKX_SECRET_KEY
#    - OKX_PASSPHRASE
#    - JWT_SECRET_KEY
# 6. Click "Apply"

# ✅ Backend deploys automatically!
# ✅ Get URL: https://trading-bot-api.onrender.com
```

### Step 4: Update Mobile App
```bash
# Edit mobile-app/.env
API_URL=https://trading-bot-api.onrender.com/api

# Restart app
cd mobile-app
./start-app.sh
```

---

## 🎯 Complete Flow (30 Minutes Total)

### 1. Test Locally (5 min)
```bash
# Start backend
docker-compose up -d

# Start mobile app
cd mobile-app
./start-app.sh

# Scan QR on iPhone
# ✅ Test locally
```

### 2. Deploy to Render (10 min)
```bash
# Push code
git add .
git commit -m "Ready for deployment"
git push

# Deploy on Render
# (follow Step 3 above)
```

### 3. Test Production (5 min)
```bash
# Update mobile app API URL
# Restart app
# Test on iPhone
# ✅ Works with cloud backend!
```

### 4. Setup Payments (10 min)
```bash
# Choose payment method:

# PayStack (Africa):
https://paystack.com

# Crypto (Global):
https://coingate.com

# Stripe (Already integrated!)
https://stripe.com
```

---

## ⚡ Super Quick Test (2 Minutes!)

```bash
# Just want to see the app RIGHT NOW?

cd mobile-app
./start-app.sh

# Scan QR code with iPhone
# Done! 🎉
```

---

## 🐛 Troubleshooting

### "EMFILE: too many open files"
```bash
# Already fixed with start-app.sh!
# If still happens:
ulimit -n 65536
npm start -- --clear
```

### Can't connect to backend
```bash
# Get your Mac's IP:
ipconfig getifaddr en0

# Update mobile-app/.env:
API_URL=http://YOUR_IP:8000/api

# Make sure iPhone on same WiFi
```

### Expo Go won't scan QR
```bash
# Open Expo Go app
# Press "Scan QR Code" button
# Point camera at terminal QR code
```

### Build errors
```bash
# Clear everything:
cd mobile-app
rm -rf node_modules .expo
npm install
./start-app.sh
```

---

## 📊 What You Have Now

✅ Backend (Python/FastAPI)
✅ iOS App (React Native/Expo)  
✅ 3 Payment methods (Stripe, PayStack, Crypto)
✅ Docker deployment
✅ Render cloud deployment (1-click)
✅ MongoDB Atlas (free tier)
✅ Complete documentation

**Total setup time: 30 minutes**
**Total cost to start: $0** (all free tiers!)

---

## 🎉 Next Steps

### Today:
1. ✅ Start mobile app: `./start-app.sh`
2. ✅ Test on iPhone
3. ✅ Deploy to Render

### This Week:
4. ✅ Setup payment method
5. ✅ Build for TestFlight
6. ✅ Get beta users

### Next Week:
7. ✅ Submit to App Store
8. ✅ Launch!
9. ✅ Make money! 💰

---

## 💡 Pro Tips

**1. Fast Development**
```bash
# Code changes reload instantly on iPhone
# No rebuild needed!
```

**2. Free Hosting**
```bash
# Render free tier:
# - Backend: Free (with sleep)
# - MongoDB: Free (Atlas M0)
# - Total: $0/month

# Paid tier when ready:
# - Render: $7/month per service
# - Total: ~$14/month for production
```

**3. Easy Updates**
```bash
# Backend update:
git push  # Auto-deploys on Render

# Mobile app update:
eas update  # Users get it without App Store review!
```

---

**You're ready! Run `./start-app.sh` and test on your iPhone now!** 📱🚀
