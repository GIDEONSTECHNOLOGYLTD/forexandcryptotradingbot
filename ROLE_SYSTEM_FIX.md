# 🔐 ROLE SYSTEM - ADMIN VS USER

## 🚨 CURRENT PROBLEM:

Admin logs into mobile app but sees **user dashboard** instead of admin features.
System doesn't properly recognize admin role and apply different permissions.

---

## ✅ HOW IT SHOULD WORK:

### ADMIN (You):
- **Email:** admin@tradingbot.com
- **Has OKX credentials** in Render env
- **Can do EVERYTHING:**
  - Create unlimited bots
  - Toggle paper trading ON/OFF
  - See ALL users' bots
  - See ALL trades
  - Access admin web dashboard
  - No subscription limits
  - No exchange connection required

### REGULAR USERS:
- **Must connect their own OKX** via Settings → Exchange Connection
- **Subscription limits:**
  - Free: 1 bot, paper trading only
  - Pro: 3 bots, real trading
  - Enterprise: Unlimited bots, real trading
- **See only their own bots**
- **See only their own trades**
- **Cannot access admin dashboard**

---

## 🔧 FIXES NEEDED:

### 1. Mobile App Role Detection
Mobile app needs to:
- Check user role from `/api/users/me`
- Show different UI for admin vs user
- Enable/disable features based on role

### 2. Backend Role Enforcement
Backend needs to:
- Always check `is_admin = user.get("role") == "admin"`
- Apply different rules for admin
- Use admin OKX credentials for admin bots

### 3. Clear Role Separation
- Admin bypasses ALL restrictions
- Users follow subscription rules
- Different dashboards for each role

---

## 📱 MOBILE APP CHANGES NEEDED:

### HomeScreen:
```typescript
// Show admin stats vs user stats
if (user.role === 'admin') {
  // Show system-wide stats
  // All users' bots
  // All trades
} else {
  // Show only user's stats
  // Only user's bots
  // Only user's trades
}
```

### TradingScreen:
```typescript
// Admin sees all bots
// Users see only their bots
if (user.role === 'admin') {
  bots = await api.getAllBots(); // Admin endpoint
} else {
  bots = await api.getMyBots(); // User endpoint
}
```

### BotConfigScreen:
```typescript
// Admin can toggle paper trading
// Users restricted by subscription
if (user.role === 'admin') {
  // Show paper trading toggle
  // No subscription check
} else {
  // Check subscription
  // Enforce limits
}
```

---

## 🎯 IMPLEMENTATION PLAN:

1. **Add user context to mobile app**
2. **Create admin-specific API endpoints**
3. **Add role checks to all screens**
4. **Show/hide features based on role**
5. **Test admin vs user flows**

---

**Let me implement these fixes now!**
