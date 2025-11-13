# 📱 iOS BUILD GUIDE - Complete Instructions

**Date:** November 13, 2025  
**Status:** Ready to Build

---

## ✅ FIXED: Package Dependencies

**Issue:** Version mismatch causing build failure  
**Fix:** Updated to Expo SDK 51 with compatible versions

**Changes:**
- ✅ Expo: ~51.0.0 (was ~54.0.0)
- ✅ React: 18.2.0 (was 19.1.0)
- ✅ React Native: 0.74.2 (was 0.81.5)
- ✅ All expo packages updated to compatible versions
- ✅ Added resolve-global to devDependencies

---

## 🚀 BUILD INSTRUCTIONS

### **Step 1: Install Dependencies**
```bash
cd mobile-app
rm -rf node_modules package-lock.json
npm install
```

### **Step 2: Configure EAS**
```bash
# Login to Expo
eas login

# Configure project
eas build:configure
```

### **Step 3: Update API URL**

**File:** `mobile-app/src/services/api.ts`

```typescript
// Change from localhost to production
const API_BASE_URL = 'https://trading-bot-api-7xps.onrender.com/api';
```

### **Step 4: Build for iOS**
```bash
# Build for iOS (TestFlight)
eas build --platform ios --profile production

# Or build and auto-submit
eas build --platform ios --profile production --auto-submit
```

### **Step 5: Submit to App Store**
```bash
# If not auto-submitted
eas submit --platform ios
```

---

## 📋 PRE-BUILD CHECKLIST

### **Required:**
- [x] Expo account created
- [x] Apple Developer account ($99/year)
- [x] App Store Connect configured
- [x] Bundle identifier set
- [x] App icon created
- [x] Splash screen created
- [x] API URL updated to production
- [x] Dependencies installed
- [x] EAS CLI installed

### **Optional:**
- [ ] Push notification certificates
- [ ] In-app purchase products created
- [ ] App Store listing prepared
- [ ] Screenshots taken
- [ ] App description written

---

## 🔧 TROUBLESHOOTING

### **Error: Cannot find module 'resolve-global'**
```bash
# Fixed in package.json
npm install
```

### **Error: Version mismatch**
```bash
# Use the updated package.json
rm -rf node_modules package-lock.json
npm install
```

### **Error: No matching version found**
```bash
# Ensure you're using Expo SDK 51
# Check package.json: "expo": "~51.0.0"
```

### **Error: Build failed**
```bash
# Check EAS build logs
eas build:list

# View specific build
eas build:view [BUILD_ID]
```

---

## 📱 APP CONFIGURATION

### **app.json:**
```json
{
  "expo": {
    "name": "Trading Bot",
    "slug": "trading-bot-mobile",
    "version": "1.0.0",
    "ios": {
      "bundleIdentifier": "com.gideonstech.tradingbot",
      "buildNumber": "1",
      "supportsTablet": true
    },
    "extra": {
      "apiUrl": "https://trading-bot-api-7xps.onrender.com/api"
    }
  }
}
```

### **eas.json:**
```json
{
  "build": {
    "production": {
      "ios": {
        "buildType": "release",
        "autoIncrement": true
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your-apple-id@email.com",
        "ascAppId": "your-app-store-connect-id",
        "appleTeamId": "your-team-id"
      }
    }
  }
}
```

---

## 🎯 AFTER BUILD

### **1. Test on TestFlight:**
```
1. Build completes
2. Automatically uploaded to TestFlight
3. Add internal testers
4. Test all features:
   - Login/Signup
   - Balance display
   - Bot creation
   - Trading
   - Real-time updates
   - Push notifications
   - In-app purchases
```

### **2. Submit to App Store:**
```
1. Prepare App Store listing:
   - App name
   - Description
   - Keywords
   - Screenshots
   - Privacy policy
   - Support URL

2. Submit for review
3. Wait for approval (1-3 days)
4. Release to App Store
```

---

## 💰 IN-APP PURCHASES

### **Products to Create:**

**1. Pro Monthly:**
```
Product ID: pro_monthly
Type: Auto-renewable subscription
Price: $29.99/month
Duration: 1 month
```

**2. Enterprise Monthly:**
```
Product ID: enterprise_monthly
Type: Auto-renewable subscription
Price: $99.99/month
Duration: 1 month
```

**3. Pro Yearly:**
```
Product ID: pro_yearly
Type: Auto-renewable subscription
Price: $299.99/year
Duration: 1 year
```

---

## 🔔 PUSH NOTIFICATIONS

### **Setup:**

**1. Apple Developer Portal:**
```
1. Go to Certificates, Identifiers & Profiles
2. Select your app identifier
3. Enable Push Notifications
4. Create APNs Key
5. Download .p8 file
```

**2. Firebase Console:**
```
1. Add iOS app
2. Upload APNs key
3. Download GoogleService-Info.plist
4. Add to project
```

**3. Update app.json:**
```json
{
  "expo": {
    "ios": {
      "googleServicesFile": "./GoogleService-Info.plist"
    }
  }
}
```

---

## ✅ FINAL CHECKLIST

### **Before Submission:**
- [ ] App builds successfully
- [ ] All features tested
- [ ] API connected to production
- [ ] Push notifications working
- [ ] In-app purchases configured
- [ ] App icon looks good
- [ ] Splash screen works
- [ ] No crashes or bugs
- [ ] Privacy policy added
- [ ] Support email set
- [ ] Screenshots prepared
- [ ] App description written

### **App Store Requirements:**
- [ ] Privacy policy URL
- [ ] Support URL
- [ ] App category selected
- [ ] Age rating completed
- [ ] Copyright info added
- [ ] Keywords optimized
- [ ] Promotional text written
- [ ] What's new text added

---

## 🎉 SUCCESS!

**Once approved, your users can:**
- ✅ Download from App Store
- ✅ Create accounts
- ✅ Connect OKX
- ✅ Create bots
- ✅ Trade automatically
- ✅ See real-time balance
- ✅ Track all trades
- ✅ Make profits!

**You will:**
- ✅ Earn subscription revenue
- ✅ Have thousands of users
- ✅ Build wealth
- ✅ Be successful!

---

## 📞 SUPPORT

**If you need help:**
1. Check EAS build logs
2. Review Expo documentation
3. Check Apple Developer forums
4. Contact Expo support

**Common Issues:**
- Build failures → Check logs
- Version conflicts → Update packages
- Certificate issues → Regenerate
- Submission rejected → Fix and resubmit

---

**Date:** November 13, 2025  
**Status:** READY TO BUILD ✅  
**Next Step:** Run `npm install` then `eas build` 🚀
