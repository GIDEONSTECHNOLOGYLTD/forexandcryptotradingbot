# 📱 Complete Expo iOS App Setup Guide

## Step-by-Step Setup for Apple Developer with Expo

---

## 🎯 Overview

You'll create a fully functional iOS trading bot app that can be tested immediately on your iPhone using Expo Go, then build a standalone app for TestFlight/App Store.

**Timeline:**
- Basic setup: 15-30 minutes
- First test on iPhone: 5 minutes
- TestFlight build: 30-45 minutes

---

## 📋 Prerequisites

### ✅ What You Need
1. **Mac Computer** (required for iOS development)
2. **Node.js** (v18 or higher)
3. **Apple Developer Account** (you have this!)
   - Account ID
   - Team ID
   - App-specific password
4. **iPhone** for testing
5. **Expo account** (free - we'll create)

---

## 🚀 Part 1: Install Required Tools

### Step 1: Install Node.js & npm
```bash
# Check if you have Node.js
node --version  # Should be v18+
npm --version

# If not installed, install via Homebrew
brew install node

# Verify installation
node --version
npm --version
```

### Step 2: Install Expo CLI
```bash
# Install Expo CLI globally
npm install -g expo-cli

# Install EAS CLI (for building)
npm install -g eas-cli

# Verify installation
expo --version
eas --version
```

### Step 3: Create Expo Account
```bash
# Sign up for free Expo account
expo register

# Or login if you have account
expo login
```

---

## 🎨 Part 2: Setup Your Project

### Step 1: Navigate to Mobile App Directory
```bash
cd /Users/gideonaina/Documents/GitHub/forexandcryptotradingbot/mobile-app
```

### Step 2: Install Dependencies
```bash
# Install all npm packages
npm install

# This will install:
# - React Native & Expo
# - Navigation libraries
# - Charts & UI components
# - API & storage libraries
```

### Step 3: Configure Environment Variables

Create `.env` file in mobile-app directory:

```bash
# Create .env file
cat > .env << 'EOF'
# Backend API URL
API_URL=http://YOUR-BACKEND-IP:8000/api

# For local testing (find your IP):
# Run: ipconfig getifaddr en0
# Then: API_URL=http://192.168.1.XXX:8000/api

# For production:
# API_URL=https://your-domain.com/api

# Environment
ENVIRONMENT=development
EOF
```

**Find Your Local IP:**
```bash
# On Mac, get your IP address
ipconfig getifaddr en0
# Example output: 192.168.1.105

# Update API_URL in .env to:
# API_URL=http://192.168.1.105:8000/api
```

### Step 4: Update app.json with Your Details

Edit `mobile-app/app.json`:

```json
{
  "expo": {
    "name": "Trading Bot Pro",
    "slug": "trading-bot-pro",
    "owner": "YOUR_EXPO_USERNAME",  // ← Change this
    "ios": {
      "bundleIdentifier": "com.YOURCOMPANY.tradingbot"  // ← Change this
    },
    "extra": {
      "eas": {
        "projectId": "will-be-generated"  // ← Will update after eas init
      }
    }
  }
}
```

---

## 📱 Part 3: Test on Your iPhone (5 Minutes!)

### Step 1: Install Expo Go on iPhone
1. Open App Store on your iPhone
2. Search for "Expo Go"
3. Install the app (it's free)
4. Open Expo Go and sign in with your Expo account

### Step 2: Start Development Server
```bash
# In mobile-app directory
npm start

# Or specifically for iOS
npm run ios
```

### Step 3: Scan QR Code
1. You'll see a QR code in the terminal
2. Open Camera app on your iPhone
3. Point it at the QR code
4. Tap the notification to open in Expo Go
5. **App loads in 5-10 seconds!** 🎉

### Step 4: Test the App
- Login screen should appear
- Navigate between tabs
- Test all functionality
- Changes you make in code will instantly reflect on your phone!

---

## 🏗️ Part 4: Build Standalone App for TestFlight

### Step 1: Initialize EAS Build
```bash
# In mobile-app directory
eas init

# This creates your project ID and updates app.json
```

### Step 2: Configure Apple Developer Credentials

Create `eas.json` (already created, but customize if needed):

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": true
      }
    },
    "preview": {
      "distribution": "internal",
      "ios": {
        "simulator": false
      }
    },
    "production": {
      "ios": {
        "bundleIdentifier": "com.YOURCOMPANY.tradingbot"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "YOUR_APPLE_ID",
        "ascAppId": "YOUR_APP_STORE_CONNECT_ID",
        "appleTeamId": "YOUR_TEAM_ID"
      }
    }
  }
}
```

### Step 3: Get Apple Developer Information

**Find Your Team ID:**
1. Go to https://developer.apple.com/account
2. Click "Membership" in sidebar
3. Your **Team ID** is shown (10 characters)

**Create App-Specific Password:**
1. Go to https://appleid.apple.com
2. Sign in
3. Security > App-Specific Passwords
4. Generate new password
5. **Save it securely!**

**Create App in App Store Connect:**
1. Go to https://appstoreconnect.apple.com
2. My Apps > "+" > New App
3. Platform: iOS
4. Name: Trading Bot Pro
5. Bundle ID: com.YOURCOMPANY.tradingbot (must match app.json)
6. SKU: any unique identifier
7. Access: Full Access
8. Copy the **App ID** (numbers only)

### Step 4: Build the App
```bash
# Login to Apple account
eas login

# Configure Apple credentials (first time only)
eas build:configure

# Build for iOS
eas build --platform ios --profile production

# EAS will ask for:
# - Apple ID: your@email.com
# - Apple ID password: <use app-specific password>
# - Team ID: <your 10-character team ID>
#
# Build takes 15-30 minutes
```

### Step 5: Download & Install on TestFlight

After build completes:

```bash
# Submit to TestFlight
eas submit --platform ios

# Or manually:
# 1. Download .ipa file from Expo dashboard
# 2. Upload to App Store Connect via Transporter app
```

**Install on iPhone:**
1. Open TestFlight app on iPhone
2. Your app appears automatically
3. Tap Install
4. **Full app ready to test!** 🎉

---

## ⚙️ Part 5: Environment Configuration

### Development Environment Setup

**Option 1: Test with Local Backend (Recommended for Development)**

```bash
# 1. Start your backend
cd /Users/gideonaina/Documents/GitHub/forexandcryptotradingbot
docker-compose up -d

# 2. Get your Mac's IP address
ipconfig getifaddr en0
# Example: 192.168.1.105

# 3. Update mobile-app/.env
API_URL=http://192.168.1.105:8000/api

# 4. Make sure your iPhone is on same WiFi network

# 5. Start mobile app
cd mobile-app
npm start
```

**Option 2: Test with Production Backend**

```bash
# Update mobile-app/.env
API_URL=https://your-production-domain.com/api

# Start mobile app
npm start
```

### Production Environment Setup

For TestFlight/App Store build:

```bash
# Update mobile-app/src/services/api.ts
const API_BASE_URL = 'https://your-production-domain.com/api';

# Rebuild
eas build --platform ios --profile production
```

---

## 🔧 Part 6: Common Issues & Solutions

### Issue: "Unable to connect to backend"

**Solution:**
```bash
# 1. Check your IP address
ipconfig getifaddr en0

# 2. Update .env with correct IP
API_URL=http://YOUR_IP:8000/api

# 3. Ensure iPhone is on same WiFi

# 4. Check backend is running
curl http://YOUR_IP:8000/health

# 5. Restart Expo
npm start
```

### Issue: "App won't load on iPhone"

**Solution:**
```bash
# 1. Clear Expo cache
expo start -c

# 2. Restart Expo Go app on iPhone

# 3. Make sure you're on same network

# 4. Check firewall isn't blocking port 19000
```

### Issue: "Build failed on EAS"

**Solution:**
```bash
# 1. Check Apple Developer credentials
eas credentials

# 2. Verify bundle identifier matches
# in app.json and App Store Connect

# 3. Check build logs
eas build:list

# 4. Try again
eas build --platform ios --clear-cache
```

### Issue: "Cannot find module errors in IDE"

**Solution:**
```bash
# Install dependencies
cd mobile-app
npm install

# The lint errors will resolve after installation
```

---

## 📸 Part 7: Adding App Icons & Splash Screen

### Create App Assets

**Required Sizes:**
- App Icon: 1024x1024px (PNG, no transparency)
- Splash Screen: 1242x2688px (PNG)

**Quick Generation:**
```bash
# Use online tool or create manually

# Place files in mobile-app/assets/
# - icon.png (1024x1024)
# - splash.png (1242x2688)
# - adaptive-icon.png (1024x1024, Android)

# Expo will auto-generate all required sizes
```

---

## 🚀 Part 8: Quick Start Commands

### Daily Development
```bash
# Start development server
cd mobile-app
npm start

# Scan QR code with iPhone
# Changes reflect instantly!
```

### Build for TestFlight
```bash
# Build
eas build --platform ios

# Submit
eas submit --platform ios

# Or auto-submit
eas build --platform ios --auto-submit
```

### Update Live App (Over-the-Air)
```bash
# Make your code changes

# Publish update (users get it without App Store review!)
eas update --branch production --message "Fixed bugs"

# Users get update next time they open app
```

---

## 📝 Part 9: Environment Variables Reference

### Complete .env Template

```bash
# API Configuration
API_URL=http://192.168.1.XXX:8000/api
API_TIMEOUT=10000

# Environment
ENVIRONMENT=development

# Payment Configuration (for production)
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
PAYSTACK_PUBLIC_KEY=pk_test_xxx
COINGATE_PUBLIC_KEY=xxx

# Features
ENABLE_NOTIFICATIONS=true
ENABLE_BIOMETRICS=true
ENABLE_DARK_MODE=true

# Debug
DEBUG_MODE=true
LOG_LEVEL=debug
```

### Loading Environment Variables in Code

```typescript
// mobile-app/src/config/env.ts
import Constants from 'expo-constants';

export const ENV = {
  API_URL: Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000/api',
  ENVIRONMENT: Constants.expoConfig?.extra?.environment || 'development',
  // Add more as needed
};
```

---

## 🎉 Part 10: You're Ready!

### What You Can Do Now:

✅ **Test Immediately on iPhone**
```bash
npm start
# Scan QR code → Test in 5 seconds!
```

✅ **Make Changes Instantly**
```bash
# Edit any file
# Save
# App reloads automatically on iPhone!
```

✅ **Build for TestFlight**
```bash
eas build --platform ios
# Get .ipa in 20-30 minutes
```

✅ **Submit to App Store**
```bash
eas submit --platform ios
# App goes to review
```

---

## 📊 Next Steps

### Week 1: Development
1. ✅ Test app on your iPhone
2. ✅ Connect to backend
3. ✅ Test all features
4. ✅ Fix bugs
5. ✅ Add custom features

### Week 2: TestFlight
1. ✅ Build with EAS
2. ✅ Submit to TestFlight
3. ✅ Test with beta users
4. ✅ Collect feedback
5. ✅ Iterate

### Week 3: App Store
1. ✅ Final testing
2. ✅ Add screenshots
3. ✅ Write App Store description
4. ✅ Submit for review
5. ✅ Launch! 🚀

---

## 💡 Pro Tips

### 1. Fast Iteration
```bash
# Use Expo Go for fastest development
# Changes reflect in 1-2 seconds!
npm start
```

### 2. Over-the-Air Updates
```bash
# Update app WITHOUT App Store review
eas update

# Users get updates instantly
# Perfect for bug fixes!
```

### 3. Environment Switching
```bash
# Development
API_URL=http://192.168.1.XXX:8000/api

# Staging
API_URL=https://staging.yourdomain.com/api

# Production
API_URL=https://yourdomain.com/api
```

### 4. Debugging
```bash
# Open React Native Debugger
# Press 'j' in Expo terminal

# View logs
# Press 'r' to reload
# Press 'm' for menu
```

---

## 🆘 Need Help?

### Resources
- Expo Docs: https://docs.expo.dev
- EAS Build: https://docs.expo.dev/build/introduction
- React Native: https://reactnative.dev
- Your backend API: http://localhost:8000/docs

### Quick Debug
```bash
# Check Expo status
expo doctor

# Clear cache
expo start -c

# Reset everything
rm -rf node_modules
npm install
expo start -c
```

---

## ✅ Complete Setup Checklist

### Initial Setup
- [ ] Install Node.js
- [ ] Install Expo CLI
- [ ] Create Expo account
- [ ] Install dependencies (`npm install`)
- [ ] Configure .env file

### iPhone Testing
- [ ] Install Expo Go on iPhone
- [ ] Connect to same WiFi
- [ ] Start dev server (`npm start`)
- [ ] Scan QR code
- [ ] Test app functionality

### TestFlight Build
- [ ] Run `eas init`
- [ ] Configure Apple credentials
- [ ] Create app in App Store Connect
- [ ] Run `eas build`
- [ ] Submit to TestFlight
- [ ] Install and test

### Production
- [ ] Update environment to production
- [ ] Test thoroughly
- [ ] Submit to App Store
- [ ] Launch! 🚀

---

**You're all set! Start with `npm start` and test on your iPhone right now!** 📱
