# SUBSCRIPTION FLOW & LIMITS

## 🎯 CURRENT SUBSCRIPTION TIERS:

### 1. FREE (Trial)
**Features:**
- ✅ 1 bot allowed
- ✅ Paper trading unlimited
- ✅ **1 REAL TRADE allowed** (trial)
- ❌ Limited to 1 bot
- ❌ No advanced strategies
- ❌ No API access

**Purpose:** Let users test the platform with 1 real trade

### 2. PRO ($29/month)
**Features:**
- ✅ 3 bots allowed
- ✅ Unlimited paper trading
- ✅ Unlimited real trading
- ✅ All strategies
- ✅ Priority support
- ❌ No API access

### 3. ENTERPRISE ($99/month)
**Features:**
- ✅ Unlimited bots
- ✅ Unlimited paper trading
- ✅ Unlimited real trading
- ✅ All strategies
- ✅ API access
- ✅ Custom strategies
- ✅ 24/7 support

### 4. ADMIN (Special)
**Features:**
- ✅ Everything from Enterprise
- ✅ Access to all users' bots
- ✅ System OKX credentials
- ✅ Admin dashboard
- ✅ User management
- ✅ Always Enterprise subscription

---

## 📊 SUBSCRIPTION LIMITS:

### Bot Creation Limits:
```javascript
{
  free: 1,
  pro: 3,
  enterprise: 999,
  admin: 999
}
```

### Real Trading Limits:
```javascript
{
  free: {
    allowed: true,
    max_trades: 1,  // Only 1 real trade
    message: "Upgrade to Pro for unlimited trading"
  },
  pro: {
    allowed: true,
    max_trades: -1,  // Unlimited
  },
  enterprise: {
    allowed: true,
    max_trades: -1,  // Unlimited
  },
  admin: {
    allowed: true,
    max_trades: -1,  // Unlimited
  }
}
```

---

## 🔄 USER FLOW:

### New User Journey:
```
1. Sign up → Free account
2. Create 1 bot (paper trading by default)
3. Test with paper trading
4. Switch to real trading
5. Make 1 real trade (trial)
6. See "Upgrade to Pro" message
7. Subscribe to Pro/Enterprise
8. Unlimited real trading
```

### Admin Journey:
```
1. Login as admin
2. Auto-connected to system OKX
3. Always Enterprise subscription
4. Unlimited everything
5. Can manage all users
```

---

## 🚀 IMPLEMENTATION:

### 1. Check Subscription Before Bot Start:
```python
@app.post("/api/bots/{bot_id}/start")
async def start_bot(bot_id: str, user: dict = Depends(get_current_user)):
    # Get bot config
    bot = bot_instances_collection.find_one({"_id": ObjectId(bot_id)})
    
    # Check if real trading
    if not bot.get('config', {}).get('paper_trading', True):
        # Check subscription limits
        subscription = user.get('subscription', 'free')
        
        if subscription == 'free':
            # Count user's real trades
            real_trades = db.trades.count_documents({
                "user_id": str(user["_id"]),
                "paper_trading": False
            })
            
            if real_trades >= 1:
                raise HTTPException(
                    status_code=403,
                    detail="Free trial limit reached. Upgrade to Pro for unlimited trading."
                )
    
    # Start bot...
```

### 2. Show Upgrade Message in App:
```typescript
// In TradingScreen or BotDetails
if (user.subscription === 'free' && !bot.paper_trading) {
  const trades = await api.getUserTrades();
  if (trades.length >= 1) {
    Alert.alert(
      'Upgrade Required',
      'You've used your 1 free real trade. Upgrade to Pro for unlimited trading!',
      [
        { text: 'Maybe Later' },
        { text: 'Upgrade Now', onPress: () => navigation.navigate('Payment') }
      ]
    );
  }
}
```

### 3. Bot Creation Limits:
```python
@app.post("/api/bots/create")
async def create_bot(config: BotConfig, user: dict = Depends(get_current_user)):
    # Check bot limits
    subscription = user.get('subscription', 'free')
    bot_limits = {
        'free': 1,
        'pro': 3,
        'enterprise': 999,
        'admin': 999
    }
    
    current_bots = bot_instances_collection.count_documents({"user_id": str(user["_id"])})
    
    if current_bots >= bot_limits.get(subscription, 1):
        raise HTTPException(
            status_code=403,
            detail=f"Bot limit reached. Upgrade to create more bots."
        )
    
    # Create bot...
```

---

## 🎯 BENEFITS OF THIS FLOW:

### For Users:
1. ✅ Can try real trading with 1 trade
2. ✅ See actual results before paying
3. ✅ Clear upgrade path
4. ✅ No credit card required for trial

### For Business:
1. ✅ Users experience real trading
2. ✅ Higher conversion rate
3. ✅ Clear value demonstration
4. ✅ Prevents abuse (only 1 trade)

---

## 🔧 WHAT NEEDS TO BE IMPLEMENTED:

1. ✅ Admin always has Enterprise (DONE)
2. ⏳ Check real trade count for free users
3. ⏳ Show upgrade message after 1 trade
4. ⏳ Enforce bot creation limits
5. ⏳ Add subscription info to user profile
6. ⏳ Clear upgrade flow in app

---

## 📱 UI CHANGES NEEDED:

### 1. Bot Config Screen:
- Show subscription tier
- Show remaining bots
- Show "Upgrade" button if at limit

### 2. Trading Screen:
- Show trade count for free users
- Show "1/1 real trades used"
- Upgrade button

### 3. Profile Screen:
- Show subscription details
- Show limits
- Upgrade button

---

## 🚨 CURRENT ISSUES TO FIX:

1. ❌ Admin subscription changed to Pro
   - **Fix:** Force Enterprise on startup ✅

2. ❌ No trial real trade for free users
   - **Fix:** Allow 1 real trade for free tier

3. ❌ No bot creation limits enforced
   - **Fix:** Check limits before creating

4. ❌ No clear upgrade flow
   - **Fix:** Add upgrade prompts

---

This flow balances user experience with monetization!
