# 🔔 Telegram Notifications Setup for Render

## Problem
Your bot shows: `⚠️ Telegram notifications disabled (no credentials)`

This means the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` environment variables are missing on Render.

---

## Step 1: Create a Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Send the command**: `/newbot`
3. **Follow the instructions** to create your bot:
   - Choose a name (e.g., "My Trading Bot")
   - Choose a username (must end in 'bot', e.g., "mytradingbot123_bot")
4. **Copy the bot token** you receive (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

## Step 2: Get Your Chat ID

1. **Start a chat with your bot** (click the link BotFather sends you)
2. **Send any message** to your bot (e.g., "Hello")
3. **Visit this URL** in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. **Find your chat_id** in the response JSON (looks like: `"chat":{"id":123456789}`)

---

## Step 3: Add to Render Environment Variables

### For the Advanced Trading Bot Service (separate bot running on Render)

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Click on your `advanced-trading-bot` service** (not the main API service)
3. **Go to Environment** (left sidebar)
4. **Add these two environment variables**:
   - **Key**: `TELEGRAM_BOT_TOKEN`
   - **Value**: Your bot token from Step 1
   
   - **Key**: `TELEGRAM_CHAT_ID`
   - **Value**: Your chat ID from Step 2

5. **Click "Save Changes"** - Render will automatically redeploy

### For the Main API Service (optional, if you want notifications from the main service too)

Repeat the same steps for your `trading-bot-api-7xps` service on Render.

---

## Step 4: Verify Setup

After Render redeploys (takes 2-3 minutes):

1. **Check the logs** on Render
2. You should see: `✅ Telegram notifications enabled` instead of the warning
3. You'll receive a **"BOT STARTED"** message on Telegram when the bot starts

---

## What You'll Get

Once configured, you'll receive Telegram notifications for:

- ✅ **Trade Executions** - When the bot opens a position
- 📊 **Position Closures** - When a trade is closed (with profit/loss)
- 🎯 **Trading Signals** - When the bot detects opportunities
- 💰 **Daily Summaries** - Performance reports
- ⚠️ **Error Alerts** - If something goes wrong
- 🤖 **Bot Status** - Start/stop notifications

---

## Testing Notifications

You can test notifications by running:

```bash
python telegram_notifier.py
```

This will send a test message to verify your setup.

---

## Security Note

- Never share your bot token publicly
- Keep your chat ID private
- Your bot will only send messages to your chat ID (nobody else can receive them)

---

## Need Help?

If you see errors like:
- "401 Unauthorized" → Your bot token is incorrect
- "400 Bad Request" → Your chat ID is incorrect
- No messages received → Check both token and chat ID

Run `python telegram_notifier.py` locally to debug before deploying to Render.
