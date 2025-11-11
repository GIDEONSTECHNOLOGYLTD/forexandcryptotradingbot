# 🚀 Quick Start - Deploy Your Trading Bot App

## ⚡ Super Fast Setup (5 Minutes)

### Step 1: Run Setup Script

```bash
cd mobile-app
./setup-expo.sh
```

This installs everything you need!

---

### Step 2: Login to Expo

```bash
# Login to Expo
expo login

# Login to EAS (use same credentials)
eas login
```

**Don't have an Expo account?**
- Go to https://expo.dev/signup
- Create free account
- Use that to login

---

### Step 3: Configure Your App

#### A. Update app.json

Replace these values in `app.json`:

```json
{
  "expo": {
    "name": "Trading Bot Pro",
    "slug": "trading-bot-pro",
    "ios": {
      "bundleIdentifier": "com.gideonstech.tradingbot",  // ← Your bundle ID
      "buildNumber": "1.0.0"
    },
    "android": {
      "package": "com.gideonstech.tradingbot"  // ← Same as iOS
    },
    "extra": {
      "eas": {
        "projectId": "YOUR_PROJECT_ID"  // ← Will be generated
      }
    },
    "owner": "your-expo-username"  // ← Your Expo username
  }
}
```

#### B. Update eas.json

Replace these values in `eas.json`:

```json
{
  "submit": {
    "production": {
      "ios": {
        "appleId": "your-apple-id@email.com",  // ← Your Apple ID
        "appleTeamId": "YOUR_TEAM_ID"  // ← Your Apple Team ID (10 chars)
      }
    }
  }
}
```

#### C. Create .env file

```bash
cp .env.example .env
```

Then edit `.env` with your values.

---

### Step 4: Initialize EAS Project

```bash
eas build:configure
```

This creates your Expo project and updates `app.json` with project ID.

---

### Step 5: Build Your App

#### For iOS (TestFlight/App Store)

```bash
# Development build (for testing)
eas build --platform ios --profile development

# Production build (for App Store)
eas build --platform ios --profile production
```

**First time?** EAS will ask:
- ✅ Generate new credentials? → Yes
- ✅ Use Apple Team ID? → Enter your Team ID

#### For Android (Google Play)

```bash
# Development build
eas build --platform android --profile development

# Production build (for Google Play)
eas build --platform android --profile production
```

**First time?** EAS will ask:
- ✅ Generate new keystore? → Yes

---

### Step 6: Download & Test

After build completes:

1. **iOS**: Download IPA file or install via TestFlight
2. **Android**: Download APK/AAB file

Test on your device!

---

### Step 7: Submit to App Stores

#### iOS - App Store Connect

```bash
eas submit --platform ios
```

Follow prompts:
1. Select your build
2. Enter Apple ID password
3. Select app in App Store Connect

#### Android - Google Play Console

```bash
eas submit --platform android
```

Follow prompts:
1. Select your build
2. Upload service account key
3. Select track (internal/beta/production)

---

## 🎯 What You Need

### For iOS:
- ✅ Apple Developer Account ($99/year)
- ✅ Apple Team ID (from developer.apple.com/account)
- ✅ App created in App Store Connect
- ✅ App-specific password (for submission)

### For Android:
- ✅ Google Play Developer Account ($25 one-time)
- ✅ App created in Play Console
- ✅ Service account key (for automated submission)

---

## 📱 Testing Before Submission

### iOS - TestFlight

```bash
# Build for TestFlight
eas build --platform ios --profile production

# Submit to TestFlight
eas submit --platform ios --latest
```

Then:
1. Go to App Store Connect
2. Select your app → TestFlight
3. Add internal testers
4. They get email to install

### Android - Internal Testing

```bash
# Build APK for testing
eas build --platform android --profile preview

# Download and install on device
```

Or submit to Play Console internal track:
```bash
eas submit --platform android --track internal
```

---

## 🔧 Troubleshooting

### "No bundle identifier found"
→ Make sure `bundleIdentifier` is set in `app.json`

### "Invalid Apple Team ID"
→ Get it from https://developer.apple.com/account → Membership

### "Build failed"
→ Check logs: `eas build:list`
→ View specific build: `eas build:view [build-id]`

### "Submission failed"
→ Make sure app exists in App Store Connect/Play Console
→ Check credentials are correct

---

## 🎉 Success Checklist

- [ ] Expo/EAS CLI installed
- [ ] Logged in to Expo
- [ ] app.json configured
- [ ] eas.json configured
- [ ] .env file created
- [ ] iOS build successful
- [ ] Android build successful
- [ ] Tested on device
- [ ] Submitted to TestFlight/Play Console
- [ ] App live in stores! 🚀

---

## 📞 Need Help?

Check these files:
- `EXPO_COMPLETE_SETUP.md` - Detailed setup guide
- `EXPO_SETUP_GUIDE.md` - Original guide
- Expo docs: https://docs.expo.dev
- EAS docs: https://docs.expo.dev/eas

---

## 🚀 Quick Commands Reference

```bash
# Development
npm start                    # Start dev server
npm run ios                  # Run on iOS simulator
npm run android              # Run on Android emulator

# Building
npm run build:ios            # Build for iOS
npm run build:android        # Build for Android
eas build --platform all     # Build both platforms

# Submission
npm run submit:ios           # Submit to App Store
npm run submit:android       # Submit to Play Store

# Status
eas build:list               # List all builds
eas build:view [id]          # View specific build
eas submit:list              # List submissions
```

---

**Ready to deploy? Let's go! 🚀**
