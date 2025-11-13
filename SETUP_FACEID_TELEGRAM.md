# Face ID & Telegram Notifications Setup Guide

## ✅ 1. FACE ID / TOUCH ID (Already Working!)

### What's Implemented:
Your iOS app **already has Face ID fully working**! Here's what it does:

### How It Works:

#### On First Login:
1. User logs in with email + password
2. App detects device has Face ID/Touch ID
3. Shows prompt: "Enable Biometric Login?"
4. If user agrees, Face ID is enabled
5. Future logins only need Face ID! 👍

#### On Subsequent App Opens:
1. App detects biometric is enabled
2. Shows Face ID prompt automatically
3. User authenticates with face
4. Logged in instantly! ⚡

### Features Available:
- ✅ Face ID (iPhone X and later)
- ✅ Touch ID (iPhone 8 and earlier)
- ✅ Auto-prompt on first login
- ✅ Secure credential storage
- ✅ Enable/Disable in Settings → Security
- ✅ Fallback to passcode if Face ID fails

### How Users Enable/Disable:
1. Go to **Settings** screen
2. Tap **Security**
3. Toggle **"Biometric Login"** switch
4. Authenticate with Face ID to enable
5. Done! ✅

### Code Locations:
- Service: `mobile-app/src/services/biometrics.ts`
- Login Screen: `mobile-app/src/screens/LoginScreen.tsx`
- Splash Screen: `mobile-app/src/screens/SplashScreen.tsx`
- Security Screen: `mobile-app/src/screens/SecurityScreen.tsx`

---

## 🤖 2. TELEGRAM BOT NOTIFICATIONS

### What You Need to Set Up:

Telegram notifications are **implemented in the backend** but need configuration. Follow these steps:

---

### Step 1: Create a Telegram Bot

1. **Open Telegram** on your phone or desktop

2. **Search for @BotFather** (official Telegram bot)

3. **Send command**: `/newbot`

4. **Choose a name** for your bot (e.g., "Trading Bot Alerts")

5. **Choose a username** (must end in 'bot', e.g., "gtech_trading_bot")

6. **BotFather will give you a TOKEN**:
   ```
   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   ```

7. **SAVE THIS TOKEN!** You'll need it for the .env file

---

### Step 2: Get Your Chat ID

1. **Start a conversation** with your new bot (click the link BotFather provides)

2. **Send any message** to your bot (e.g., "Hello!")

3. **Open this URL in your browser** (replace `<YOUR_TOKEN>` with your bot token):
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```

4. **Find the chat ID** in the response. Look for:
   ```json
   {
     "ok": true,
     "result": [{
       "message": {
         "chat": {
           "id": 123456789,  ← THIS IS YOUR CHAT ID
           "first_name": "Your Name",
           ...
         }
       }
     }]
   }
   ```

5. **SAVE THIS CHAT ID!**

---

### Step 3: Add Credentials to Backend

1. **Open your `.env` file** on the server (where your backend runs)

2. **Add these lines**:
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   TELEGRAM_CHAT_ID=123456789
   ```

3. **Save the file**

4. **Restart your backend server**:
   ```bash
   # On Render or your hosting platform, trigger a redeploy
   # Or if running locally:
   python web_dashboard.py
   ```

---

### Step 4: Test Notifications

1. **Run the test script**:
   ```bash
   python telegram_notifier.py
   ```

2. **You should receive a test message** on Telegram! 🎉

3. **If it works**, you'll see:
   ```
   ✅ Telegram is configured and working!
   📱 Bot token: 123...90
   💬 Chat ID: 123456789
   ✉️ Test message sent successfully!
   ```

---

### What Notifications Will You Receive?

Once configured, you'll get Telegram messages for:

#### 🤖 Bot Events:
- ✅ Bot started
- ⏹️ Bot stopped
- ⚠️ Bot error

#### 💰 Trade Events:
- 🟢 **BUY** executed
  ```
  🟢 BUY Signal
  Symbol: BTC/USDT
  Price: $45,234.56
  Amount: 0.05 BTC
  Total: $2,261.73
  ```

- 🔴 **SELL** executed
  ```
  🔴 SELL Signal
  Symbol: BTC/USDT
  Price: $46,100.00
  Amount: 0.05 BTC
  Total: $2,305.00
  Profit: +$43.27 (+1.91%)
  ```

#### ⚠️ Risk Alerts:
- 📉 Maximum drawdown reached
- 🎯 Take profit target hit
- 🛑 Stop loss triggered
- ⚡ High volatility warning

#### 📊 Daily Summary:
- Total trades: 15
- Win rate: 73%
- Total profit: +$234.56
- Best trade: +$89.32
- Worst trade: -$23.11

---

### Step 5: Enable for Users (Optional)

If you want **each user to get their own notifications**:

1. **Add to User Schema** (already in `mongodb_database.py`):
   ```python
   user = {
       "email": "user@example.com",
       "telegram_chat_id": None,  # Users can add their own
       "notification_preferences": {
           "telegram_enabled": False,
           "email_enabled": True,
           "trade_alerts": True,
           "risk_alerts": True,
           "daily_summary": True
       }
   }
   ```

2. **Add Settings to iOS App**:
   - Go to Settings → Notifications
   - Add "Connect Telegram" button
   - User enters their own Telegram username
   - Backend stores their chat_id

3. **Send Notifications Per User**:
   ```python
   # In bot_engine.py, send to specific user
   notifier = TelegramNotifier(
       chat_id=user['telegram_chat_id']
   )
   notifier.send_trade_alert(trade_data)
   ```

---

## 🎯 Quick Setup Checklist

### Face ID (Already Done! ✅):
- [x] Biometric service implemented
- [x] Login screen integration
- [x] Security settings screen
- [x] Auto-prompt on first login
- **NO SETUP NEEDED - IT JUST WORKS!**

### Telegram Bot:
- [ ] Create bot with @BotFather
- [ ] Get bot token
- [ ] Get your chat ID
- [ ] Add to .env file:
  - `TELEGRAM_BOT_TOKEN=...`
  - `TELEGRAM_CHAT_ID=...`
- [ ] Restart backend server
- [ ] Test with `python telegram_notifier.py`
- [ ] Start trading and receive alerts! 🎉

---

## 📱 Screenshots of What Users See

### Face ID Prompt (First Login):
```
┌─────────────────────────────────┐
│  Enable Biometric Login?       │
│                                 │
│  Use Face ID for quick login   │
│                                 │
│  [Maybe Later]     [Enable]    │
└─────────────────────────────────┘
```

### Face ID Authentication:
```
┌─────────────────────────────────┐
│         🔐                      │
│    Login with Face ID           │
│                                 │
│    [Face icon scanning...]      │
│                                 │
│    Use Passcode                 │
└─────────────────────────────────┘
```

### Telegram Notification Example:
```
🤖 Trading Bot Alert

🟢 BUY Signal Executed

Symbol: BTC/USDT
Price: $45,234.56
Amount: 0.05 BTC
Capital: $2,261.73
Time: 2:34 PM

Strategy: Momentum
Status: Position opened ✅
```

---

## 🚨 Troubleshooting

### Face ID Not Working?

1. **Check device support**:
   - iPhone X or later for Face ID
   - iPhone 5s to 8 Plus for Touch ID

2. **Check iOS Settings**:
   - Settings → Face ID & Passcode
   - Ensure Face ID is enabled for apps

3. **Reset biometric in app**:
   - Settings → Security
   - Turn OFF "Biometric Login"
   - Turn ON again
   - Authenticate to re-enable

### Telegram Not Sending?

1. **Check token format**:
   - Must be like: `1234567890:ABCdefGHI...`
   - No spaces or quotes in .env

2. **Check chat ID**:
   - Must be a number (can be negative)
   - Example: `123456789` or `-987654321`

3. **Test bot manually**:
   - Visit: `https://api.telegram.org/bot<TOKEN>/getMe`
   - Should return bot info

4. **Check backend logs**:
   ```bash
   # Look for Telegram errors
   tail -f logs/app.log | grep -i telegram
   ```

5. **Test notification manually**:
   ```python
   from telegram_notifier import TelegramNotifier
   
   notifier = TelegramNotifier()
   notifier.send_message("Test message from Python!")
   ```

---

## 💡 Pro Tips

### Face ID:
- ✅ Works even if user changes password
- ✅ More secure than storing password
- ✅ Faster than typing password
- ✅ Users can disable anytime in Settings

### Telegram:
- ✅ Get instant alerts on your phone
- ✅ Works worldwide, no SMS fees
- ✅ Can create groups for multiple admins
- ✅ Bot can send charts and images
- ✅ Free, unlimited messages

---

## 🎉 You're All Set!

### Face ID:
**Already working!** Users just need to:
1. Login once with password
2. Enable when prompted
3. Use Face ID forever! 🚀

### Telegram:
**5 minutes to set up:**
1. Create bot → Get token
2. Get chat ID
3. Add to .env
4. Test it
5. Get alerts! 🎉

**Questions?** Check the troubleshooting section above or test the features manually!
