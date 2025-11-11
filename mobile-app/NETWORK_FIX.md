# 🌐 NETWORK CONNECTION FIX

## ✅ YOUR NETWORK INFO:

**Mac IP Address:** `172.20.10.8`
**Network:** `172.20.10.x` (likely WiFi hotspot or local network)

---

## 🚀 START EXPO NORMALLY:

```bash
cd mobile-app
npx expo start
```

**Then:**
1. Wait for QR code to appear
2. Make sure your iPhone is on the **same WiFi network** as your Mac
3. Scan QR code with Expo Go

---

## 📱 IMPORTANT - CHECK YOUR IPHONE:

### Make Sure:
1. **WiFi is ON** (not just cellular)
2. **Connected to same network** as Mac
3. **Not using VPN**
4. **Expo Go app is installed**

### To Check Network on iPhone:
- Settings → WiFi
- Should show connected to same network as Mac
- IP should be `172.20.10.x` (same subnet)

---

## 🔧 IF STILL CAN'T CONNECT:

### Option 1: Use Your Mac as Hotspot
1. Mac → System Preferences → Sharing
2. Enable "Internet Sharing"
3. Share WiFi to WiFi
4. Connect iPhone to Mac's hotspot
5. Restart Expo

### Option 2: Disable Firewall Temporarily
```bash
# Check firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# If ON, temporarily disable:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# Start Expo
npx expo start

# Re-enable after testing:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
```

### Option 3: Use iOS Simulator (If Available)
```bash
npx expo start
# Press 'i' to open iOS simulator
```

---

## ✅ EXPECTED RESULT:

Once connected:
- ✅ App loads on your iPhone
- ✅ Shows TBP logo (purple gradient)
- ✅ All screens accessible
- ✅ No more connection errors

---

## 🎯 DO THIS NOW:

1. **Check iPhone WiFi** - Same network as Mac?
2. **Start Expo:**
   ```bash
   npx expo start
   ```
3. **Scan QR code** with Expo Go
4. **Wait for app to load**

**If it works, you'll see your app with TBP logo!** 🚀
