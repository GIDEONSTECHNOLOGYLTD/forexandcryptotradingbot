# 🔧 Fix macOS "Too Many Open Files" Error - PERMANENT SOLUTION

## The Problem
macOS has a low default limit for open files (256), but Expo/Metro needs more.

## ✅ PERMANENT FIX (One-Time Setup)

### Step 1: Increase System Limits
```bash
# Run these commands in Terminal:

# Create the limit file
sudo nano /Library/LaunchDaemons/limit.maxfiles.plist
```

**Paste this content:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>limit.maxfiles</string>
    <key>ProgramArguments</key>
    <array>
      <string>launchctl</string>
      <string>limit</string>
      <string>maxfiles</string>
      <string>65536</string>
      <string>200000</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>ServiceIPC</key>
    <false/>
  </dict>
</plist>
```

**Save:** Press `Ctrl+O`, `Enter`, then `Ctrl+X`

### Step 2: Set Permissions & Load
```bash
# Set correct permissions
sudo chown root:wheel /Library/LaunchDaemons/limit.maxfiles.plist
sudo chmod 644 /Library/LaunchDaemons/limit.maxfiles.plist

# Load the configuration
sudo launchctl load -w /Library/LaunchDaemons/limit.maxfiles.plist

# Verify it worked
launchctl limit maxfiles
# Should show: maxfiles 65536 200000
```

### Step 3: RESTART YOUR MAC
```bash
# This is REQUIRED for changes to take effect
sudo shutdown -r now
```

---

## 🚀 QUICK FIX (Works Until Restart)

If you don't want to restart now, run this in EVERY terminal before starting Expo:

```bash
ulimit -n 65536
cd mobile-app
npx expo start --tunnel
```

**Use --tunnel flag** to avoid file watching issues!

---

## ✅ Test After Restart

```bash
# Check limit
ulimit -n
# Should show: 65536 or higher

# Start Expo with tunnel
cd mobile-app
npx expo start --tunnel

# ✅ Should work without errors!
```

---

## 🎯 Alternative: Use Expo Tunnel Mode

Even simpler - just use tunnel mode (no file watching):

```bash
cd mobile-app
npx expo start --tunnel
```

This works immediately without any system changes!

---

## 📱 Which Method Should You Use?

### Best for Production Testing:
```bash
npx expo start --tunnel
```
✅ Works immediately  
✅ No system changes needed  
✅ Works over internet (not just local WiFi)  
✅ Can test from anywhere  

### Best for Development:
1. Fix system limits (one-time)
2. Restart Mac
3. Use normal `npx expo start`

---

**Recommendation: Use `npx expo start --tunnel` right now to test your app!**
