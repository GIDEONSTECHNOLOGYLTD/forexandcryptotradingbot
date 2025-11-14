# 🔍 Telegram Credential Debugging Guide

## 🚨 Issue
You added `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to Render but bot still shows:
```
⚠️  Telegram notifications disabled (no credentials)
```

## ✅ Debug Code Added

I've added debugging to show **exactly** what the bot sees. After the next deploy, you'll see:

```
🔍 Environment Variables Check:
  TELEGRAM_BOT_TOKEN: ✅ Set  OR  ❌ Not Set
  TELEGRAM_CHAT_ID: ✅ Set  OR  ❌ Not Set
  OKX_API_KEY: ✅ Set  OR  ❌ Not Set

🔍 Telegram Config Debug:
  Bot Token: ✅ Found (123456789:...)  OR  ❌ Missing
  Chat ID: ✅ Found (987654321)  OR  ❌ Missing
```

---

## 🔧 How to Check Your Render Setup

### Step 1: Verify Environment Variables on Render

1. **Go to**: https://dashboard.render.com/
2. **Click on**: Your `advanced-trading-bot` service
3. **Click**: "Environment" in the left sidebar
4. **Check for these EXACT variable names**:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

### Step 2: Common Issues

#### ❌ Wrong Service
- Make sure you added them to the **advanced-trading-bot** service
- NOT the main trading-bot-api service
- You should have TWO services on Render

#### ❌ Typos in Variable Names
Variable names are **case-sensitive**. Must be EXACTLY:
- ✅ `TELEGRAM_BOT_TOKEN` (correct)
- ❌ `TELEGRAM_TOKEN` (wrong)
- ❌ `telegram_bot_token` (wrong)
- ❌ `TelegramBotToken` (wrong)

#### ❌ Empty Values
- Click on each variable to see the value
- Make sure the value is NOT empty
- Bot token looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- Chat ID looks like: `987654321` (just numbers)

#### ❌ Extra Spaces
- Make sure there are NO spaces before or after the values
- ❌ ` 123456789:ABC...` (space at start)
- ✅ `123456789:ABC...` (no spaces)

#### ❌ Service Didn't Redeploy
- After adding environment variables, Render should auto-redeploy
- Check the "Events" tab to see if deployment happened
- You can manually redeploy by clicking "Manual Deploy" → "Deploy latest commit"

---

## 📋 Step-by-Step Verification Checklist

### On Render Dashboard:

- [ ] I'm viewing the **advanced-trading-bot** service (not trading-bot-api)
- [ ] I see `TELEGRAM_BOT_TOKEN` in the Environment tab
- [ ] I see `TELEGRAM_CHAT_ID` in the Environment tab
- [ ] Both variables have values (not empty)
- [ ] No extra spaces in the values
- [ ] Service has redeployed after adding variables (check "Events" tab)

### In Render Logs:

After the new deploy with debug code, check the logs for:

```
🔍 Environment Variables Check:
  TELEGRAM_BOT_TOKEN: ✅ Set
  TELEGRAM_CHAT_ID: ✅ Set
```

If you see `❌ Not Set`, then Render doesn't have those variables.

---

## 🎯 Quick Fix

### Option 1: Re-add Variables (Sometimes Fixes It)

1. Go to Render → advanced-trading-bot → Environment
2. **Delete** both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
3. **Save Changes** (triggers redeploy)
4. **Wait** for redeploy to finish
5. **Add them back**:
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token
   - Key: `TELEGRAM_CHAT_ID`
   - Value: Your chat ID
6. **Save Changes** (triggers another redeploy)
7. **Wait** 2-3 minutes for redeploy
8. **Check logs** for the debug output

### Option 2: Manual Redeploy

1. Go to Render → advanced-trading-bot
2. Click "Manual Deploy" button
3. Select "Deploy latest commit"
4. Wait for deployment to complete
5. Check logs for debug output

---

## 🔬 What to Share

After the next deploy, share these logs with me:

1. The **Environment Variables Check** section
2. The **Telegram Config Debug** section

This will tell us exactly what's wrong!

---

## ✅ Expected Output (When Working)

```
🔍 Environment Variables Check:
  TELEGRAM_BOT_TOKEN: ✅ Set
  TELEGRAM_CHAT_ID: ✅ Set
  OKX_API_KEY: ✅ Set

🔍 Telegram Config Debug:
  Bot Token: ✅ Found (7891011121:...)
  Chat ID: ✅ Found (1234567890)

✅ Telegram notifications enabled
```

---

## 📸 Screenshots to Take

1. **Render Environment Tab** - Show all environment variables
2. **Render Logs** - Show the debug output after deployment

Send these to verify the setup!
