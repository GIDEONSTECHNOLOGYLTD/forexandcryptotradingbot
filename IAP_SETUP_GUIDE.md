# 🍎 **IN-APP PURCHASE SETUP GUIDE**

Complete guide to enable iOS In-App Purchases for your Trading Bot app.

---

## ✅ **CURRENT STATUS:**

- ✅ **Code:** Fully implemented and ready!
- ✅ **Product IDs:** Configured in app
- ✅ **Backend:** Ready to verify purchases
- ⏳ **Apple:** Needs App Store Connect configuration

**Once you complete Apple setup, just delete 3 lines of code and IAP works!**

---

## 📋 **REQUIREMENTS:**

### **1. Apple Developer Account** 🍎
- **Cost:** $99/year
- **Sign up:** https://developer.apple.com/programs/
- **Note:** This is REQUIRED for IAP. No way around it.

### **2. Banking Information** 💳
- **Why:** Apple pays you subscription revenue
- **What:** Bank account + tax info
- **Where:** App Store Connect → Agreements

### **3. App Bundle ID**
Your app already has this configured:
```
Bundle ID: com.gtechldt.tradingbot
```
✅ This matches your app.json!

---

## 🔧 **STEP-BY-STEP SETUP:**

### **STEP 1: Create App in App Store Connect**

1. Go to: https://appstoreconnect.apple.com/
2. Click **"My Apps"** → **"+"** → **"New App"**
3. Fill in details:

```
Platform: iOS
Name: Trading Bot
Primary Language: English
Bundle ID: com.gtechldt.tradingbot  ← CRITICAL: Must match exactly!
SKU: tradingbot-001  ← Any unique ID
```

4. Click **"Create"**

---

### **STEP 2: Create Subscription Products**

#### **A. Create Subscription Group:**

1. In your app, click **"Features"** tab
2. Click **"Subscriptions"**
3. Click **"+"** → **"Create Subscription Group"**
4. Name: `Trading Bot Subscriptions`
5. Click **"Create"**

#### **B. Create Pro Subscription:**

1. Click **"+"** under the subscription group
2. Fill in:

```
Reference Name: Pro Monthly Subscription
Product ID: com.gtechldt.tradingbot.pro.monthly
           ↑ CRITICAL: Must match code exactly!

Subscription Duration: 1 Month
```

3. Click **"Create"**

4. **Add Localization** (English):
```
Subscription Display Name: Pro Trading Plan
Description: Get 3 active bots, real trading with your OKX account, all advanced strategies, and priority email support.
```

5. **Set Price:**
   - Click **"Subscription Prices"**
   - Select **"$29.99 USD"**
   - Click **"Next"** → **"Confirm"**

6. **Add Review Screenshot:**
   - Take screenshot of your subscription screen
   - Upload it (required by Apple)

7. Click **"Save"**

#### **C. Create Enterprise Subscription:**

1. Click **"+"** again under the subscription group
2. Fill in:

```
Reference Name: Enterprise Monthly Subscription
Product ID: com.gtechldt.tradingbot.enterprise.monthly
           ↑ CRITICAL: Must match code exactly!

Subscription Duration: 1 Month
```

3. Click **"Create"**

4. **Add Localization** (English):
```
Subscription Display Name: Enterprise Trading Plan
Description: Unlimited bots, full API access, custom trading strategies, and 24/7 priority support with dedicated account manager.
```

5. **Set Price:**
   - Click **"Subscription Prices"**
   - Select **"$99.99 USD"**
   - Click **"Next"** → **"Confirm"**

6. **Add Review Screenshot:**
   - Upload same or different screenshot

7. Click **"Save"**

---

### **STEP 3: Set Up Agreements & Banking**

⚠️ **CRITICAL: You won't get paid without this!**

1. Go to: https://appstoreconnect.apple.com/agreements
2. Click **"Paid Apps"** agreement
3. Complete ALL sections:

#### **A. Contact Information:**
```
First Name: [Your name]
Last Name: [Your name]
Email: [Your email]
Phone: [Your phone]
Address: [Your address]
```

#### **B. Bank Account:**
```
Bank Name: [Your bank]
Account Number: [Your account]
Routing Number: [If US]
SWIFT/IBAN: [If international]
Account Holder Name: [Must match Apple Developer account]
```

#### **C. Tax Information:**
- Select your country
- Fill in tax forms (W-9 for US, W-8BEN for international)
- Provide tax ID

4. Submit for review

⏳ **Processing Time:** 1-2 business days

---

### **STEP 4: Submit Products for Review**

1. Go back to your subscriptions
2. For **each product**, click **"Submit for Review"**
3. Apple reviews IAP products (1-2 days typically)

---

### **STEP 5: Test with Sandbox (BEFORE Live!)**

#### **A. Create Sandbox Tester:**

1. Go to: https://appstoreconnect.apple.com/access/testers
2. Click **"Sandbox Testers"** → **"+"**
3. Fill in:
```
Email: test@yourdomain.com  ← Must be NEW, never used with Apple
Password: Test1234!
First Name: Test
Last Name: User
Country: United States
```
4. Click **"Invite"**

#### **B. Test on iPhone:**

1. On your iPhone: Settings → App Store
2. Scroll to **"Sandbox Account"**
3. Sign in with: `test@yourdomain.com`
4. Open your Trading Bot app
5. Go to Subscription screen
6. Select **"App Store"** payment
7. Choose Pro or Enterprise
8. **Purchase will be FREE** (sandbox mode)
9. Verify subscription activates!

✅ If this works, you're ready for production!

---

### **STEP 6: Enable IAP in Code**

Once products are **APPROVED** by Apple:

#### **A. Open PaymentScreen.tsx:**

Find line 37 (`initializeIAP` function):

**DELETE THESE LINES (45-47):**
```typescript
console.log('ℹ️ IAP initialization skipped - products not configured yet');
setIsInitializingIAP(false);
return; // ← DELETE THIS + 2 LINES ABOVE
```

**BEFORE:**
```typescript
const initializeIAP = async () => {
  // comments...
  console.log('ℹ️ IAP initialization skipped...');
  setIsInitializingIAP(false);
  return; // ← DELETE THIS
  
  // IAP ENABLED CODE:
  if (isInitializingIAP) return;
  // ... rest of code
};
```

**AFTER:**
```typescript
const initializeIAP = async () => {
  // IAP ENABLED CODE:
  if (isInitializingIAP) return;
  try {
    setIsInitializingIAP(true);
    console.log('🔄 Connecting to App Store...');
    await InAppPurchases.connectAsync();
    // ... rest runs now!
  }
};
```

#### **B. Find line 189 (`handleInAppPurchase` function):**

**DELETE THESE LINES (192-202):**
```typescript
Alert.alert(
  '📱 App Store Purchases Coming Soon!',
  ...
);
return; // ← DELETE THIS + alert above
```

**That's it!** IAP is now enabled! 🎉

---

## 🧪 **TESTING CHECKLIST:**

### **Sandbox Testing:**
- [ ] Created sandbox test account
- [ ] Signed in on device
- [ ] Selected Pro plan → App Store payment
- [ ] Saw Apple purchase dialog
- [ ] Purchase completed (FREE in sandbox)
- [ ] Subscription activated in app
- [ ] Tested Enterprise plan too
- [ ] Tested cancellation

### **Production Testing:**
- [ ] Products approved by Apple
- [ ] Code enabled (return statements removed)
- [ ] Built production app
- [ ] Tested on real device
- [ ] Made REAL purchase (will charge!)
- [ ] Subscription activated
- [ ] Revenue appears in App Store Connect

---

## 💰 **REVENUE & PAYOUTS:**

### **Apple's Cut:**
```
Year 1: Apple takes 30%
→ Pro: $29.99 → You get $21.00
→ Enterprise: $99.99 → You get $70.00

Year 2+: Apple takes 15% (after 1 year of subscription)
→ Pro: $29.99 → You get $25.50
→ Enterprise: $99.99 → You get $85.00
```

### **Payment Schedule:**
- Apple pays you **45 days** after end of month
- Example: January sales → paid March 15th
- Minimum $150 balance required for payout

---

## 🚨 **TROUBLESHOOTING:**

### **"Cannot connect to iTunes Store"**
→ Check internet connection
→ Sign out and sign in to Apple ID
→ Try different Apple ID

### **"Product not available"**
→ Products not approved yet
→ Product IDs don't match code
→ Bundle ID doesn't match
→ App not submitted to App Store

### **"Purchase failed"**
→ Payment method declined
→ Check App Store payment settings
→ Try different payment method

### **Sandbox purchases not working:**
→ Must use NEW email (never used with Apple before)
→ Sign out of real Apple ID first
→ Sign in to sandbox account in Settings → App Store

### **Real purchases not working:**
→ Code still has `return` statements (Step 6 not done)
→ Products not approved by Apple yet
→ App not live on App Store yet

---

## 📱 **PRODUCT IDS REFERENCE:**

Your code uses these exact IDs:

```typescript
const PRODUCT_IDS = {
  pro: 'com.gtechldt.tradingbot.pro.monthly',
  enterprise: 'com.gtechldt.tradingbot.enterprise.monthly'
};
```

⚠️ **App Store Connect products MUST match these EXACTLY!**

No spaces, no typos, case-sensitive!

---

## ✅ **FINAL CHECKLIST:**

Before enabling IAP:
- [ ] Apple Developer account active ($99/year)
- [ ] App created in App Store Connect
- [ ] Bundle ID: `com.gtechldt.tradingbot`
- [ ] Subscription group created
- [ ] Pro product created & approved
- [ ] Enterprise product created & approved
- [ ] Product IDs match code exactly
- [ ] Banking information complete
- [ ] Tax information complete
- [ ] Agreements signed
- [ ] Tested with sandbox
- [ ] Screenshots uploaded
- [ ] Descriptions written
- [ ] Prices set ($29.99 & $99.99)

Once all checked:
- [ ] Delete `return` in `initializeIAP()` (line 47)
- [ ] Delete `Alert` in `handleInAppPurchase()` (lines 192-202)
- [ ] Rebuild app
- [ ] Test on real device
- [ ] Deploy to App Store

---

## 🎯 **SUMMARY:**

**Current State:**
- Code: ✅ Ready (just blocked by return statements)
- Apple: ⏳ Needs configuration

**To Enable:**
1. Configure App Store Connect (30-60 min)
2. Wait for Apple approval (1-2 days)
3. Delete 3 lines of code (30 seconds)
4. Done! 🎉

**Alternative:**
- Use Card payment (Paystack) - Already working! ✅
- Use Crypto payment (USDT) - Already working! ✅

IAP is just an additional option for convenience.

---

## 📧 **NEED HELP?**

Apple Support: https://developer.apple.com/contact/
IAP Documentation: https://developer.apple.com/in-app-purchase/

---

**Good luck! 🚀**
