# 🎛️ New Listing Bot - Configuration Guide

## ✅ NOT Hardcoded - Fully Configurable!

The **$50 amount is NOT hardcoded**. You can customize all settings easily!

---

## 📋 Configuration Options

### Method 1: Environment Variables (Recommended for Render)

Add these to your Render environment variables:

```bash
NEW_LISTING_BUY_AMOUNT=50          # How much USDT to invest per new listing
NEW_LISTING_TAKE_PROFIT=30         # Take profit at +X%
NEW_LISTING_STOP_LOSS=15           # Stop loss at -X%
NEW_LISTING_MAX_HOLD=3600          # Max hold time (seconds)
NEW_LISTING_CHECK_INTERVAL=60      # Check for new listings every X seconds
```

### Method 2: Local .env File

For local development, add to your `.env` file:

```bash
# New Listing Bot Configuration
NEW_LISTING_BUY_AMOUNT=50
NEW_LISTING_TAKE_PROFIT=30
NEW_LISTING_STOP_LOSS=15
NEW_LISTING_MAX_HOLD=3600
NEW_LISTING_CHECK_INTERVAL=60
```

### Method 3: Edit config.py Directly

If you prefer, edit the defaults in `config.py`:

```python
# New Listing Bot Configuration
NEW_LISTING_BUY_AMOUNT = 50.0      # Change this value
NEW_LISTING_TAKE_PROFIT = 30.0     # Change this value
NEW_LISTING_STOP_LOSS = 15.0       # Change this value
NEW_LISTING_MAX_HOLD = 3600        # Change this value
NEW_LISTING_CHECK_INTERVAL = 60    # Change this value
```

---

## 💡 Recommended Settings by Balance

### If you have $16-50 USDT:
```bash
NEW_LISTING_BUY_AMOUNT=10          # Start small
NEW_LISTING_TAKE_PROFIT=50         # Higher profit target
NEW_LISTING_STOP_LOSS=20           # Wider stop loss
NEW_LISTING_MAX_HOLD=1800          # 30 minutes max
```

### If you have $50-200 USDT:
```bash
NEW_LISTING_BUY_AMOUNT=50          # Default (safe)
NEW_LISTING_TAKE_PROFIT=30         # Balanced target
NEW_LISTING_STOP_LOSS=15           # Reasonable stop
NEW_LISTING_MAX_HOLD=3600          # 1 hour max
```

### If you have $200-1000 USDT:
```bash
NEW_LISTING_BUY_AMOUNT=100         # More aggressive
NEW_LISTING_TAKE_PROFIT=25         # Quick profits
NEW_LISTING_STOP_LOSS=15           # Tight stop
NEW_LISTING_MAX_HOLD=3600          # 1 hour max
```

### If you have $1000+ USDT:
```bash
NEW_LISTING_BUY_AMOUNT=200         # Larger positions
NEW_LISTING_TAKE_PROFIT=20         # Quick scalp
NEW_LISTING_STOP_LOSS=10           # Very tight
NEW_LISTING_MAX_HOLD=1800          # 30 minutes
```

---

## 🎯 Setting Explanations

### NEW_LISTING_BUY_AMOUNT
**What it does**: Amount in USDT to invest in EACH new listing
**Default**: 50
**Range**: 10 - 1000 (depends on your capital)
**Example**: If set to `100`, bot will buy $100 worth of each promising new listing

### NEW_LISTING_TAKE_PROFIT
**What it does**: Percentage gain to automatically sell
**Default**: 30 (means +30%)
**Range**: 10 - 200
**Example**: If set to `50`, bot sells when price is up 50%

### NEW_LISTING_STOP_LOSS
**What it does**: Percentage loss to automatically cut losses
**Default**: 15 (means -15%)
**Range**: 5 - 50
**Example**: If set to `20`, bot sells when price is down 20%

### NEW_LISTING_MAX_HOLD
**What it does**: Maximum time to hold position (in seconds)
**Default**: 3600 (1 hour)
**Range**: 600 - 86400 (10 minutes to 24 hours)
**Example**: If set to `1800`, bot will close position after 30 minutes regardless of P&L

### NEW_LISTING_CHECK_INTERVAL
**What it does**: How often to check OKX for new listings (in seconds)
**Default**: 60 (every minute)
**Range**: 10 - 300 (10 seconds to 5 minutes)
**Example**: If set to `30`, bot checks for new listings every 30 seconds

---

## 🔄 How to Change Settings on Render

### Step 1: Go to Render Dashboard
```
https://dashboard.render.com/
```

### Step 2: Select Your Service
Click on the service running your bot

### Step 3: Go to Environment Tab
Click "Environment" in the left sidebar

### Step 4: Add/Edit Variables
- Click "Add Environment Variable"
- **Key**: `NEW_LISTING_BUY_AMOUNT`
- **Value**: `25` (or your desired amount)
- Click "Save Changes"

### Step 5: Wait for Redeploy
Render will automatically redeploy with the new settings (takes 2-3 minutes)

### Step 6: Verify in Logs
Check logs for:
```
🚀 **New Listing Bot Started!**
💰 Buy Amount: $25 USDT  ← Your new amount
```

---

## 📊 Configuration Priority

If you set the same variable in multiple places, this is the priority:

1. **Environment Variables** (Render/production) ← Highest priority
2. **Local .env file** (development)
3. **config.py defaults** (fallback) ← Lowest priority

Example:
- Render has: `NEW_LISTING_BUY_AMOUNT=100`
- .env has: `NEW_LISTING_BUY_AMOUNT=50`
- config.py has: `NEW_LISTING_BUY_AMOUNT=50`

**Result**: Bot will use **$100** (from Render)

---

## ⚠️ Important Warnings

### 1. Balance Must Be Higher Than Buy Amount
If you set `NEW_LISTING_BUY_AMOUNT=100` but only have $50 USDT:
- ❌ Bot will detect new listings
- ❌ Bot will try to buy
- ❌ Order will fail (insufficient balance)
- ❌ You'll miss the opportunity

**Solution**: Set buy amount LOWER than your available balance

### 2. Take Profit vs Stop Loss
Make sure take profit is HIGHER than stop loss:
- ✅ Take Profit: 30%, Stop Loss: 15% (Good)
- ❌ Take Profit: 10%, Stop Loss: 20% (Bad)

### 3. Check Interval
Don't set check interval too low (< 10 seconds):
- Can cause rate limiting
- May get banned by exchange
- Wastes API calls

**Recommended**: 30-60 seconds

---

## 🧪 Testing Your Configuration

### Test 1: Check Telegram Message
After changing settings, restart the bot and check Telegram:

```
🚀 **New Listing Bot Started!**
💰 Buy Amount: $YOUR_AMOUNT USDT  ← Verify this
🎯 Take Profit: YOUR_PERCENT%      ← Verify this
🛑 Stop Loss: YOUR_PERCENT%        ← Verify this
```

### Test 2: Check Logs
Look for initialization message:

```
🚀 Starting New Listing Bot
   Check Interval: 60s
   Investment per listing: $YOUR_AMOUNT
   Take Profit: +YOUR_PERCENT%
   Stop Loss: -YOUR_PERCENT%
```

---

## 💰 Capital Management Tips

### Rule 1: Never Invest More Than 20% Per Trade
If you have $100 USDT, don't set buy amount above $20

### Rule 2: Keep Buffer for Multiple Listings
If you have $100 and set buy amount to $50:
- Can only catch 2 new listings
- Better to set to $20-30 (catch 3-5 listings)

### Rule 3: Scale Up Gradually
- Start with $10-20 per listing
- Test for a week
- If profitable, increase to $50
- Keep increasing as you profit

---

## 📋 Quick Reference Card

```
╔══════════════════════════════════════════════════════════════╗
║               NEW LISTING BOT - QUICK SETTINGS               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Conservative (Safe):                                        ║
║    Buy: $10-20 | Take Profit: 40-50% | Stop: 20%           ║
║                                                              ║
║  Balanced (Default):                                         ║
║    Buy: $50 | Take Profit: 30% | Stop: 15%                 ║
║                                                              ║
║  Aggressive (Risky):                                         ║
║    Buy: $100+ | Take Profit: 20% | Stop: 10%               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## ✅ Summary

**The $50 is NOT hardcoded!** You can change it:
- ✅ Via Render environment variables
- ✅ Via local .env file
- ✅ Via config.py

**Current defaults**:
- Buy Amount: $50 USDT
- Take Profit: +30%
- Stop Loss: -15%
- Max Hold: 1 hour

**Customize based on your capital and risk tolerance!** 🚀
