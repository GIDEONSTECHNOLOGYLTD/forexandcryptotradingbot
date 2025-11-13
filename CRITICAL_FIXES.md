# Critical Fixes Required

## Issues Identified:
1. ✅ Trade history - Admin bot doesn't show, only user bots
2. ✅ Some bots show "unknown" in trade history
3. ✅ Biometric doesn't trigger on login
4. ✅ In-app purchase not visible in iOS production
5. ✅ Need to close/reopen app when switching accounts
6. ✅ Push to GitHub after fixes

## Solutions:

### 1. Trade History - Admin Bot Not Showing
**Problem:** Trades don't have `bot_type` or `is_admin_bot` field
**Fix:** 
- Backend: Add `bot_type` and `bot_name` to trades when created
- Frontend: Filter by `bot_type === 'admin_auto_trader'`
- Web: Update admin_dashboard.html filter logic
- iOS: Update TradeHistoryScreen.tsx filter logic

### 2. Unknown Bot Names
**Problem:** Trade records missing `bot_name` field
**Fix:**
- Ensure all trade creation includes bot_name
- Add fallback to "Unknown Bot" if missing
- Display bot type prominently

### 3. Biometric Not Triggering
**Problem:** Biometric check not called on login
**Fix:**
- Add biometric check in LoginScreen after successful login
- Check if biometric is enabled before navigating
- Store biometric preference properly

### 4. In-App Purchase Not Visible
**Problem:** IAP hidden in production builds
**Fix:**
- Remove development-only conditionals
- Always show IAP option
- Add proper App Store Connect configuration check

### 5. Account Switching Requires App Restart
**Problem:** State not cleared on logout
**Fix:**
- Clear all AsyncStorage on logout
- Reset navigation state
- Clear API tokens
- Force re-render of all screens

## Implementation Order:
1. Backend trade history fixes
2. iOS TradeHistoryScreen fixes
3. Web admin_dashboard.html fixes
4. Biometric authentication fixes
5. IAP visibility fixes
6. Logout/account switching fixes
7. Commit and push

## Files to Modify:
- `/web_dashboard.py` - Trade history endpoint
- `/mobile-app/src/screens/TradeHistoryScreen.tsx` - iOS trade history
- `/static/admin_dashboard.html` - Web trade history
- `/mobile-app/src/screens/LoginScreen.tsx` - Biometric trigger
- `/mobile-app/src/screens/PaymentScreen.tsx` - IAP visibility
- `/mobile-app/src/screens/SettingsScreen.tsx` - Logout logic
- `/mobile-app/src/services/api.ts` - Token management
