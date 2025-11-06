# 💳📱 Payment Systems & iOS App - Complete Guide

## 🎉 What Was Added

### 1. PayStack Integration (African Payments)
- File: `paystack_integration.py`
- **Perfect for:** Nigeria, Ghana, South Africa, Kenya
- **Currencies:** NGN, USD, GHS, ZAR, KES
- **Plans:** ₦15,000/month or $29/month

### 2. Cryptocurrency Payments
- File: `crypto_payment.py`
- **Accept:** Bitcoin, Ethereum, USDT, USDC, BNB, Litecoin
- **Benefits:** Global reach, low fees (1-3%), perfect for traders
- **Gateways:** CoinGate, NOWPayments, or direct wallet

### 3. Full iOS App (Expo/React Native)
- Directory: `mobile-app/`
- **Test immediately** on your iPhone with Expo Go
- **Full functionality:** Trading, portfolio, payments, notifications
- **Ready for:** TestFlight and App Store

---

## 🚀 Quick Start (Choose Your Path)

### Path 1: iOS App First (5 Minutes!)
```bash
# 1. Install dependencies
cd mobile-app
npm install

# 2. Start development server
npm start

# 3. Scan QR code with iPhone camera
# 4. App opens in Expo Go - test immediately!
```

### Path 2: Setup Payment Methods
```bash
# Choose one or all:

# PayStack (African markets)
python paystack_integration.py

# Crypto Payments (Global)
python crypto_payment.py

# Stripe (Already integrated)
python payment_integration.py
```

---

## 💳 Payment Integration Guide

### PayStack Setup (5 Minutes)

**Step 1: Create Account**
```bash
1. Go to: https://paystack.com
2. Sign up (free)
3. Verify your business
4. Get API keys from Dashboard > Settings > API Keys
```

**Step 2: Configure Environment**
```bash
# Add to .env
PAYSTACK_SECRET_KEY=sk_test_xxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxx
```

**Step 3: Create Subscription Plans**
```bash
# In PayStack Dashboard:
1. Go to Plans
2. Create "Pro Plan":
   - Name: Pro Plan
   - Amount: ₦15,000 (or $29)
   - Interval: Monthly
   - Copy Plan Code

3. Create "Enterprise Plan":
   - Name: Enterprise Plan
   - Amount: ₦50,000 (or $99)
   - Interval: Monthly
   - Copy Plan Code

# Add to .env:
PAYSTACK_PRO_NGN_CODE=PLN_xxxx
PAYSTACK_ENTERPRISE_NGN_CODE=PLN_xxxx
```

**Step 4: Test Payment**
```python
from paystack_integration import PayStackProcessor

processor = PayStackProcessor()

# Initialize transaction
payment = processor.initialize_transaction(
    email="customer@example.com",
    amount=1500000,  # ₦15,000 in kobo
    currency="NGN"
)

print(f"Payment URL: {payment['authorization_url']}")
# Send this URL to customer
```

### Crypto Payment Setup (10 Minutes)

**Option 1: CoinGate (Recommended)**
```bash
# 1. Create account: https://coingate.com
# 2. Get API key from Dashboard
# 3. Add to .env:
COINGATE_API_KEY=your_api_key

# Test:
python crypto_payment.py
```

**Option 2: NOWPayments**
```bash
# 1. Create account: https://nowpayments.io
# 2. Get API key from Settings
# 3. Add to .env:
NOWPAYMENTS_API_KEY=your_api_key
```

**Option 3: Direct Wallet (Advanced)**
```bash
# 1. Create crypto wallets:
#    - Bitcoin wallet
#    - Ethereum wallet
#    - USDT wallet (ERC20 or TRC20)

# 2. Add to .env:
BTC_WALLET_ADDRESS=your_btc_address
ETH_WALLET_ADDRESS=your_eth_address
USDT_ERC20_ADDRESS=your_usdt_address

# 3. Monitor payments manually or use blockchain API
```

**Test Crypto Payment**
```python
from crypto_payment import CryptoPaymentProcessor

processor = CryptoPaymentProcessor(gateway='coingate')

# Create payment
payment = processor.create_payment(
    amount_usd=29.0,
    currency='BTC',
    order_id='ORDER123',
    success_url='https://yourapp.com/success'
)

print(f"Payment URL: {payment['payment_url']}")
print(f"Customer pays in Bitcoin")
```

---

## 📱 iOS App Setup (Step-by-Step)

### Prerequisites
```bash
# Check Node.js
node --version  # Should be v18+

# If not installed:
brew install node

# Install Expo CLI
npm install -g expo-cli
npm install -g eas-cli

# Create Expo account
expo register
# or
expo login
```

### Setup Project
```bash
# 1. Navigate to mobile app
cd /Users/gideonaina/Documents/GitHub/forexandcryptotradingbot/mobile-app

# 2. Install dependencies
npm install
# This installs React Native, Expo, navigation, charts, etc.

# 3. Configure environment
# Get your Mac's IP address:
ipconfig getifaddr en0
# Example: 192.168.1.105

# Create .env file:
cat > .env << 'EOF'
API_URL=http://192.168.1.105:8000/api
ENVIRONMENT=development
EOF

# 4. Update app.json with your details
nano app.json
# Change "owner" to your Expo username
# Change "bundleIdentifier" to your unique ID
```

### Test on iPhone (Immediate!)
```bash
# 1. Install "Expo Go" from App Store on your iPhone

# 2. Start development server
npm start

# 3. Scan QR code with iPhone camera
# 4. App opens in Expo Go automatically!
# 5. Test all features immediately! 🎉
```

### Build for TestFlight
```bash
# 1. Initialize EAS
eas init

# 2. Configure Apple credentials
eas build:configure

# 3. Build for iOS
eas build --platform ios

# Enter when prompted:
# - Apple ID: your@email.com
# - Apple ID password: (use app-specific password)
# - Team ID: (10-character ID from developer.apple.com)

# Build takes 20-30 minutes

# 4. Submit to TestFlight
eas submit --platform ios
```

**Get Apple Info:**
- **Team ID**: https://developer.apple.com/account → Membership
- **App-Specific Password**: https://appleid.apple.com → Security → App-Specific Passwords
- **Create App**: https://appstoreconnect.apple.com → My Apps → New App

---

## 🔄 Integration with Backend

### Connect Mobile App to Backend

**Update API Service:**
```typescript
// mobile-app/src/services/api.ts
const API_BASE_URL = __DEV__ 
  ? 'http://192.168.1.XXX:8000/api'  // Your Mac IP
  : 'https://your-domain.com/api';    // Production
```

### Add Payment Endpoints to Backend

**Update `web_dashboard.py`:**
```python
from paystack_integration import PayStackProcessor
from crypto_payment import CryptoPaymentProcessor

paystack = PayStackProcessor()
crypto = CryptoPaymentProcessor()

@app.post("/api/payments/paystack/initialize")
async def initialize_paystack_payment(
    amount: float,
    email: str,
    plan: str
):
    payment = paystack.initialize_transaction(
        email=email,
        amount=int(amount * 100),  # Convert to kobo
        currency="NGN"
    )
    return payment

@app.post("/api/payments/crypto/create")
async def create_crypto_payment(
    amount_usd: float,
    currency: str,
    order_id: str
):
    payment = crypto.create_payment(
        amount_usd=amount_usd,
        currency=currency,
        order_id=order_id
    )
    return payment

@app.get("/api/payments/{payment_id}/verify")
async def verify_payment(payment_id: str, method: str):
    if method == "paystack":
        return paystack.verify_transaction(payment_id)
    elif method == "crypto":
        return crypto.verify_payment(payment_id)
```

---

## 📊 Complete Payment Flow

### User Journey (All Methods)

```
1. User opens app
2. Navigates to "Upgrade Plan"
3. Selects plan (Pro $29 or Enterprise $99)
4. Chooses payment method:
   ├─ Stripe (Card)
   ├─ PayStack (Card/Bank - Africa)
   └─ Crypto (BTC/ETH/USDT)

5a. Stripe Flow:
    → Card form → Payment → Instant confirmation

5b. PayStack Flow:
    → Redirected to PayStack → Choose bank/card → Pay → Confirmation

5c. Crypto Flow:
    → Shows wallet address + amount → User sends crypto → Wait for confirmation

6. Subscription activated
7. User gets Pro/Enterprise features
```

---

## 💰 Revenue Comparison

### Payment Method Fees

| Method | Fee | Best For |
|--------|-----|----------|
| **Stripe** | 2.9% + $0.30 | US, Europe, Global cards |
| **PayStack** | 1.5% (NGN) | Nigeria, Ghana, SA, Kenya |
| **Crypto** | 1-3% | Global, privacy-focused |
| **Direct Wallet** | ~$1 network fee | Tech-savvy users |

### Example Revenue (100 Users, $29/month)

| Method | Gross | Fees | Net |
|--------|-------|------|-----|
| Stripe | $2,900 | $114 | $2,786 |
| PayStack | $2,900 | $44 | $2,856 |
| Crypto (CoinGate) | $2,900 | $58 | $2,842 |
| Direct Wallet | $2,900 | $100 | $2,800 |

**Recommendation:** Offer all three! Users choose their preferred method.

---

## 🎯 Implementation Priority

### Week 1: Mobile App Testing
```bash
# Day 1-2: Setup & Test
cd mobile-app
npm install
npm start
# Test on iPhone with Expo Go

# Day 3-4: Connect to Backend
# Update API URL
# Test API calls
# Verify all features work

# Day 5-7: Build & TestFlight
eas build --platform ios
eas submit
# Test with beta users
```

### Week 2: Payment Integration
```bash
# Day 1-2: PayStack
# Setup account
# Test transactions
# Add to app

# Day 3-4: Crypto
# Setup CoinGate/NOWPayments
# Test payments
# Add to app

# Day 5-7: Testing
# Test all payment methods
# Verify webhooks
# Test subscriptions
```

### Week 3: Launch
```bash
# Day 1-3: Final Testing
# Test complete user journey
# Fix bugs
# Optimize UI

# Day 4-5: App Store Submit
# Create screenshots
# Write description
# Submit for review

# Day 6-7: Marketing
# Launch announcement
# Get first users
# Start making money! 💰
```

---

## ✅ Quick Checklist

### Mobile App
- [ ] Install Node.js & Expo CLI
- [ ] Run `npm install` in mobile-app
- [ ] Update .env with backend URL
- [ ] Test with Expo Go on iPhone
- [ ] Build with EAS for TestFlight
- [ ] Submit to App Store

### PayStack
- [ ] Create PayStack account
- [ ] Get API keys
- [ ] Create subscription plans
- [ ] Add to .env
- [ ] Test transaction
- [ ] Add to backend API

### Crypto Payments
- [ ] Choose gateway (CoinGate/NOWPayments)
- [ ] Get API key
- [ ] Test payment
- [ ] Add to .env
- [ ] Add to backend API
- [ ] Test complete flow

---

## 🆘 Quick Troubleshooting

### Mobile App Won't Start
```bash
# Clear cache
expo start -c

# Reinstall
rm -rf node_modules
npm install
```

### Can't Connect to Backend
```bash
# Check your IP
ipconfig getifaddr en0

# Update API_URL in .env
# Make sure iPhone on same WiFi

# Test backend is running
curl http://YOUR_IP:8000/health
```

### Payment Not Working
```bash
# PayStack
python -c "from paystack_integration import PayStackProcessor; p = PayStackProcessor(); print(p)"

# Crypto
python -c "from crypto_payment import CryptoPaymentProcessor; p = CryptoPaymentProcessor(); print(p)"

# Check .env has correct keys
```

---

## 🎉 You're Ready!

Everything is set up. Now you can:

1. **Test iOS app on your iPhone immediately**
   ```bash
   cd mobile-app && npm start
   ```

2. **Accept payments from anywhere**
   - Stripe (global cards)
   - PayStack (African markets)
   - Crypto (worldwide, anonymous)

3. **Deploy to App Store**
   ```bash
   eas build --platform ios
   ```

**Start with the mobile app - test it in 5 minutes!** 🚀
