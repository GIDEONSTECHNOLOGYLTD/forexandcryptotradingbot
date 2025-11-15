# 🤖 HOW TO ENABLE AI ASSET MANAGER

## ✅ COMPLETE GUIDE - TWO METHODS

---

## METHOD 1: Enable on Render (Recommended) ⭐

### **Step 1: Go to Render Dashboard**
1. Open https://dashboard.render.com
2. Find your `trading-bot-api-7xps` service
3. Click on it

### **Step 2: Add Environment Variables**
1. Click "Environment" in left sidebar
2. Click "Add Environment Variable"
3. Add these three variables:

```
Name: ADMIN_ENABLE_ASSET_MANAGER
Value: true

Name: ADMIN_ASSET_MANAGER_AUTO_SELL
Value: false

Name: ADMIN_ASSET_MANAGER_MIN_PROFIT
Value: 3
```

4. Click "Save Changes"
5. Render will auto-restart (2-3 minutes)

### **Step 3: Verify It's Running**
Check your logs on Render:
```
✅ AI Asset Manager initialized
🤖 Running AI Asset Manager...
   Mode: RECOMMENDATIONS ONLY
   Min Profit: 3.0%
```

---

## METHOD 2: Update .env File (If You Have Access)

### **If you have .env file locally:**

```bash
# Add to .env file:
ADMIN_ENABLE_ASSET_MANAGER=true
ADMIN_ASSET_MANAGER_AUTO_SELL=false
ADMIN_ASSET_MANAGER_MIN_PROFIT=3
```

Then deploy:
```bash
git add .env
git commit -m "Enable AI Asset Manager"
git push origin main
```

---

## 🎯 WHAT HAPPENS AFTER ENABLING

### **Backend Behavior:**

**Every Hour:**
```
1. Backend checks: "Is AI Asset Manager enabled?"
2. If YES:
   a. Fetch all holdings from OKX
   b. For each holding (ALLO, BNB, BTC, LTC, MET, PI, STRK, TON):
      - Calculate RSI
      - Calculate MACD
      - Calculate Bollinger Bands
      - Analyze order book
      - Multi-timeframe analysis
      - Volatility check
   c. Generate recommendations
   d. If auto_sell=true AND profit >= 3%:
      Execute sell
   e. Send Telegram notification with results
3. Sleep 1 hour
4. Repeat
```

### **What You'll See:**

**Telegram Notification (hourly):**
```
🤖 AI ASSET MANAGER REPORT

Holdings Analyzed: 8
Recommendations:
• STRK: SELL (+16.34% profit) ✅
• TON: HOLD (-7.75%) 🔒
• BTC: HOLD (-1.20%) 🔒
• BNB: HOLD (-0.66%) 🔒
• LTC: HOLD (-0.30%) 🔒
• ALLO: HOLD (-13.40%) 🔒
• MET: HOLD (-7.45%) 🔒
• PI: HOLD (-0.06%) 🔒

💡 Mode: RECOMMENDATIONS ONLY
No auto-sells executed (manual control)

⏰ Next check: 1 hour
```

**iOS App:**
```
Status: Active ✅
Holdings Analyzed: 8
0 SELL | 7 HOLD | 0 BUY

Tap any holding to see detailed analysis
```

---

## 🔧 CONFIGURATION OPTIONS

### **ADMIN_ENABLE_ASSET_MANAGER**
- `true` = AI analyzes holdings every hour
- `false` = AI disabled (default)

### **ADMIN_ASSET_MANAGER_AUTO_SELL**
- `false` = Recommendations only (SAFE - start here!)
- `true` = Auto-sells profitable positions

### **ADMIN_ASSET_MANAGER_MIN_PROFIT**
- `3` = Only auto-sells if profit >= 3% (default)
- `5` = Only auto-sells if profit >= 5% (more conservative)
- `1` = Only auto-sells if profit >= 1% (more aggressive)

---

## ⚠️ RECOMMENDED SETTINGS

### **For First Time (Safe Mode):**
```
ADMIN_ENABLE_ASSET_MANAGER=true   ← Enable analysis
ADMIN_ASSET_MANAGER_AUTO_SELL=false   ← NO auto-sell (safe)
ADMIN_ASSET_MANAGER_MIN_PROFIT=3   ← 3% minimum
```

**Result:**
- ✅ Hourly analysis runs
- ✅ Recommendations sent via Telegram
- ✅ You review and manually sell
- ✅ NO automatic selling
- ✅ Safe and controlled

### **After You're Comfortable (Auto Mode):**
```
ADMIN_ENABLE_ASSET_MANAGER=true
ADMIN_ASSET_MANAGER_AUTO_SELL=true   ← Enable auto-sell
ADMIN_ASSET_MANAGER_MIN_PROFIT=3
```

**Result:**
- ✅ Hourly analysis runs
- ✅ Auto-sells profitable positions (≥3%)
- ✅ Telegram notification on each sell
- ✅ Losers protected (never sold at loss)
- ✅ Fully automated profit-taking

---

## 📱 iOS APP INTEGRATION

### **After Backend is Enabled:**

**iOS App Shows:**
1. Status: Active ✅
2. Holdings with AI analysis
3. Technical indicators (RSI, MACD, etc.)
4. Profit/loss per holding
5. AI recommendations (SELL/HOLD/BUY)
6. Manual sell button for profitable positions

**iOS App Controls:**
- Toggle analysis on/off per user
- Enable/disable auto-sell per user
- Adjust min profit % per user
- View detailed analysis
- Execute manual sells

**Backend + iOS = Perfect Combo:**
- Backend runs hourly automatically
- iOS shows results beautifully
- You control everything
- Best of both worlds!

---

## ✅ VERIFICATION

### **After Enabling, Check These:**

**1. Render Logs:**
```
✅ AI Asset Manager initialized
🤖 Running AI Asset Manager...
   Mode: RECOMMENDATIONS ONLY
   Min Profit: 3.0%
Analyzing holdings...
✅ Asset management complete
```

**2. Telegram:**
```
🤖 AI ASSET MANAGER REPORT
Holdings Analyzed: 8
...
```

**3. iOS App:**
```
Status: Active ✅
Holdings Analyzed: 8
...
```

---

## 🎯 SUMMARY

**To Enable:**
1. Add 3 env variables on Render
2. Restart service
3. Check logs for confirmation
4. Open iOS app to see results

**Timeline:**
- Enable: 2 minutes
- Restart: 3 minutes
- First analysis: Within 1 hour
- Total: ~1 hour to see first results

**Safety:**
- Start with auto_sell=false (safe mode)
- Review recommendations first
- Enable auto-sell when comfortable
- Never sells at loss (protected!)

---

## 🚀 READY TO ENABLE?

**Quick Steps:**
1. Go to Render
2. Add 3 env variables
3. Save
4. Wait 1 hour
5. Check Telegram for first report!

**Your holdings (STRK, TON, BTC, etc.) will be analyzed hourly!** ✅
