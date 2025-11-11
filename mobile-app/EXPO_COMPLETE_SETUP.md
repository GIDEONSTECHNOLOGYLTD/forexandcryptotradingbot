# 🚀 Complete Expo Setup Guide - iOS & Android

## 📋 Prerequisites Checklist

You mentioned you have:
- ✅ Apple Developer Account login
- ✅ Apple Team ID
- ✅ All necessary credentials

Let's set everything up!

---

## 🎯 Step 1: Install Expo CLI & EAS CLI

```bash
# Navigate to mobile app directory
cd mobile-app

# Install Expo CLI globally (if not already installed)
npm install -g expo-cli

# Install EAS CLI (for building and deploying)
npm install -g eas-cli

# Login to Expo
expo login
# Enter your Expo username and password

# Login to EAS
eas login
# Use same credentials
```

---

## 🍎 Step 2: Configure iOS (Apple)

### A. Update app.json with Your Details

I'll create an updated version for you. You need to provide:
- **Apple Team ID**: Found in Apple Developer Account → Membership
- **Bundle Identifier**: Unique ID (e.g., com.gideonstech.tradingbot)
- **Expo Username**: Your Expo account username

### B. Create eas.json

```bash
# In mobile-app directory
eas build:configure
```

This creates `eas.json` with build profiles.

---

## 🤖 Step 3: Configure Android

### A. Generate Keystore

```bash
# EAS will generate this automatically, or you can create manually:
keytool -genkeypair -v -storetype PKCS12 -keystore tradingbot.keystore -alias tradingbot -keyalg RSA -keysize 2048 -validity 10000
```

Save the keystore password securely!

---

## 📱 Step 4: Build Your App

### For iOS (TestFlight/App Store)

```bash
# Development build (for testing)
eas build --platform ios --profile development

# Production build (for App Store)
eas build --platform ios --profile production
```

### For Android (Google Play)

```bash
# Development build
eas build --platform android --profile development

# Production build (for Google Play)
eas build --platform android --profile production
```

### Build Both Platforms

```bash
eas build --platform all --profile production
```

---

## 🔧 Step 5: Submit to App Stores

### iOS - App Store Connect

```bash
# Submit to TestFlight/App Store
eas submit --platform ios

# Follow prompts to:
# 1. Select the build
# 2. Enter Apple ID credentials
# 3. Select App Store Connect app
```

### Android - Google Play Console

```bash
# Submit to Google Play
eas submit --platform android

# Follow prompts to:
# 1. Select the build
# 2. Upload to Play Console
```

---

## 📝 Configuration Files I'll Create

### 1. Updated app.json
### 2. eas.json (build configuration)
### 3. .env file (environment variables)
### 4. Build scripts

---

## 🎯 Quick Start Commands

After setup, use these commands:

```bash
# Start development server
npm start

# Run on iOS simulator
npm run ios

# Run on Android emulator
npm run android

# Build for production
npm run build:ios
npm run build:android

# Submit to stores
npm run submit:ios
npm run submit:android
```

---

## 📊 What You Need to Provide

Please provide these details so I can configure everything:

1. **Apple Team ID**: 
   - Go to https://developer.apple.com/account
   - Click "Membership"
   - Copy your Team ID (10 characters, e.g., "ABC123XYZ4")

2. **Bundle Identifier**:
   - Suggested: `com.gideonstech.tradingbot`
   - Or your preferred format

3. **Expo Username**:
   - Your Expo account username

4. **App Name**:
   - Current: "Trading Bot Pro"
   - Keep or change?

5. **Company Name**:
   - For copyright and legal info

6. **Google Play Package Name**:
   - Suggested: `com.gideonstech.tradingbot`
   - Must match iOS bundle identifier format

---

## 🚀 Let's Start!

Tell me:
1. Your Apple Team ID
2. Your Expo username
3. Preferred bundle identifier (or use suggested)

And I'll configure everything for you!
