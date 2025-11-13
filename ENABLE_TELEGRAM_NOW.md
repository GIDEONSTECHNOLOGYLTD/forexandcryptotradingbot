# 🔔 ENABLE TELEGRAM NOTIFICATIONS - 2 MINUTES!

## Your Bot Just Made a REAL TRADE!
You need notifications to know when it exits! Here's how:

---

## Step 1: Get Telegram Bot Token (1 minute)

1. **Open Telegram app** on your phone
2. **Search for:** `@BotFather`
3. **Send:** `/newbot`
4. **Name your bot:** "My Trading Bot" (or any name)
5. **Username:** `your_trading_bot` (must end in 'bot')
6. **Copy the token** - looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

---

## Step 2: Get Your Chat ID (30 seconds)

1. **Search for:** `@userinfobot` in Telegram
2. **Send:** `/start`
3. **Copy your ID** - looks like: `123456789`

---

## Step 3: Add to Render.com (30 seconds)

1. Go to: https://dashboard.render.com
2. Click your **trading-bot-api** service
3. Click **Environment** tab
4. Click **Add Environment Variable**

Add these TWO variables:

```
TELEGRAM_BOT_TOKEN = 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID = 123456789
```

5. Click **Save Changes**
6. Service will auto-redeploy (1 minute)

---

## Step 4: TEST IT! (10 seconds)

Once redeployed:
1. Start your admin bot in the dashboard
2. Check Telegram - you should get:
   ```
   🤖 Bot Started

   Symbol: BTC/USDT
   Mode: 💰 REAL
   Capital: $900
   Take Profit: +30%
   Stop Loss: -15%

   Bot is now monitoring the market!
   ```

---

## What You'll Get Notifications For:

✅ **Bot Started** - Confirmation with config
✅ **Bot Stopped** - Runtime summary
✅ **BUY Trade** - Entry price, amount, targets
✅ **SELL Trade** - Exit price, profit/loss %
✅ **New Listing** (Admin bot only)
✅ **Error Alerts** - If something goes wrong

---

## Current Trade Status:

**YOU HAVE AN OPEN POSITION RIGHT NOW!**

```
Entry: $98,562.70
Current BTC Price: ~$98,000-99,000
Status: Waiting for TP or SL

If BTC goes to $128,131 → +$270 profit! 🎉
If BTC drops to $83,778 → -$135 loss 😔
```

**ENABLE TELEGRAM NOW TO GET THE EXIT NOTIFICATION!**

Otherwise you won't know when the trade closes!

---

## URGENT: Do This NOW!

1. Get Telegram bot token (1 min)
2. Get your chat ID (30 sec)
3. Add to Render (30 sec)
4. Wait for redeploy (1 min)
5. **GET NOTIFICATIONS!** 🔔

**Total Time: 3 MINUTES!**

---

## After Setup:

Your phone will buzz EVERY TIME:
- Bot starts/stops
- Trade executes
- Profit is taken
- Loss is stopped
- Error occurs

**YOU'LL NEVER MISS A TRADE AGAIN!** 📱💰
