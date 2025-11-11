# 📱 MOBILE APP ASSETS - QUICK FIX

## 🚨 MISSING ASSETS CAUSING BUILD FAILURE

The iOS build failed because these image files are missing:
- `./assets/icon.png` (1024x1024)
- `./assets/splash.png` (1284x2778)
- `./assets/adaptive-icon.png` (1024x1024)
- `./assets/favicon.png` (48x48)
- `./assets/notification-icon.png` (96x96)

---

## ✅ QUICK FIX - USE EXPO'S DEFAULT ASSETS

Run this command to generate default assets:

```bash
cd mobile-app
npx expo prebuild --clean
```

This will create default Expo assets automatically.

---

## 🎨 OR CREATE CUSTOM ASSETS

### Option 1: Use Online Tool (5 minutes)
1. Go to: https://www.appicon.co/
2. Upload your logo (1024x1024 PNG)
3. Download the generated assets
4. Extract to `mobile-app/assets/` folder

### Option 2: Use Figma Template (10 minutes)
1. Download Expo asset template: https://www.figma.com/community/file/1155362909441341285
2. Customize with your branding
3. Export all required sizes
4. Place in `mobile-app/assets/` folder

### Option 3: Quick Placeholder (1 minute)
Create simple colored squares as placeholders:

```bash
cd mobile-app/assets

# Create 1024x1024 icon (blue square with "TB" text)
convert -size 1024x1024 xc:#667eea -gravity center -pointsize 400 -fill white -annotate +0+0 "TB" icon.png

# Create splash screen (gradient)
convert -size 1284x2778 gradient:#667eea-#764ba2 splash.png

# Copy icon for adaptive icon
cp icon.png adaptive-icon.png

# Create smaller versions
convert icon.png -resize 48x48 favicon.png
convert icon.png -resize 96x96 notification-icon.png
```

---

## 🔧 MANUAL FIX (If ImageMagick not installed)

Create these files manually or download from:
https://github.com/expo/expo/tree/main/templates/expo-template-blank/assets

Then copy to your `mobile-app/assets/` folder.

---

## ✅ VERIFY ASSETS

After creating assets, verify they exist:

```bash
cd mobile-app
ls -la assets/

# Should show:
# icon.png (1024x1024)
# splash.png (1284x2778)  
# adaptive-icon.png (1024x1024)
# favicon.png (48x48)
# notification-icon.png (96x96)
```

---

## 🚀 REBUILD AFTER FIXING

```bash
cd mobile-app
eas build --platform ios --profile production
```

---

## 💡 RECOMMENDED: Use Expo's Asset Generator

The easiest way is to let Expo generate default assets:

```bash
cd mobile-app

# This creates all required assets automatically
npx expo prebuild --clean

# Then build
eas build --platform ios --profile production
```

This will create professional-looking default assets that you can replace later.
