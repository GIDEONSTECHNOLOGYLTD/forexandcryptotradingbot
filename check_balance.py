#!/usr/bin/env python3
"""
Diagnostic Tool: Check OKX Balance and Account Status
"""
import ccxt
import config
from datetime import datetime

def check_okx_balance():
    """Check OKX balance and provide detailed breakdown"""
    
    print("=" * 70)
    print("🔍 OKX BALANCE DIAGNOSTIC REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize OKX connection
        print("🔌 Connecting to OKX...")
        exchange = ccxt.okx({
            'apiKey': config.OKX_API_KEY,
            'secret': config.OKX_SECRET_KEY,
            'password': config.OKX_PASSPHRASE,
            'enableRateLimit': True
        })
        
        print("✅ Connected successfully")
        print()
        
        # Fetch balance
        print("📊 Fetching balance information...")
        balance = exchange.fetch_balance()
        
        print("=" * 70)
        print("💰 BALANCE SUMMARY")
        print("=" * 70)
        
        # USDT Balance
        usdt_total = balance['total'].get('USDT', 0)
        usdt_free = balance['free'].get('USDT', 0)
        usdt_used = balance['used'].get('USDT', 0)
        
        print(f"USDT Balance:")
        print(f"  Total:     ${usdt_total:,.2f}")
        print(f"  Available: ${usdt_free:,.2f}")
        print(f"  Locked:    ${usdt_used:,.2f}")
        print()
        
        # Status check
        if usdt_total < 0:
            print("🚨 CRITICAL: NEGATIVE BALANCE DETECTED!")
            print(f"   You OWE OKX: ${abs(usdt_total):,.2f}")
            print()
            print("⚠️  POSSIBLE CAUSES:")
            print("   1. Margin/Futures trading losses exceeded balance")
            print("   2. Liquidation occurred on leveraged position")
            print("   3. Accumulated funding fees from perpetual contracts")
            print("   4. Outstanding loan from margin trading")
            print()
            print("🔧 REQUIRED ACTIONS:")
            print("   1. Log into OKX immediately: https://www.okx.com")
            print("   2. Check 'Assets' → 'Trading Account'")
            print("   3. Review 'Bills' to see transaction history")
            print("   4. Deposit funds to clear the debt")
            print("   5. Consider disabling margin/futures trading")
            print()
        elif usdt_total == 0:
            print("⚠️  ZERO BALANCE")
            print("   No funds available for trading")
            print("   Deposit USDT to start trading")
            print()
        elif usdt_total < 7:
            print("⚠️  INSUFFICIENT BALANCE FOR REAL TRADING")
            print(f"   Current: ${usdt_total:.2f}")
            print("   Required: $7 minimum (OKX $5 order minimum)")
            print()
            print("💡 OPTIONS:")
            print("   1. Deposit more USDT (recommended $50+)")
            print("   2. Use Paper Trading to practice")
            print()
        else:
            print("✅ SUFFICIENT BALANCE FOR TRADING")
            print(f"   Current: ${usdt_total:.2f}")
            print(f"   Recommended: $50+ for flexible trading")
            print()
        
        # All non-zero assets
        print("=" * 70)
        print("🪙 ALL ASSETS")
        print("=" * 70)
        has_assets = False
        for currency, amount in balance['total'].items():
            if amount != 0:  # Show both positive and negative
                has_assets = True
                free = balance['free'].get(currency, 0)
                used = balance['used'].get(currency, 0)
                status = "🚨" if amount < 0 else "✅"
                print(f"{status} {currency}:")
                print(f"     Total: {amount:,.8f}")
                print(f"     Free:  {free:,.8f}")
                print(f"     Used:  {used:,.8f}")
                print()
        
        if not has_assets:
            print("   No assets found")
            print()
        
        # Account type info
        print("=" * 70)
        print("📋 ACCOUNT INFO")
        print("=" * 70)
        try:
            # Try to get account configuration
            account_config = exchange.private_get_account_config()
            print(f"Account Level: {account_config.get('data', [{}])[0].get('acctLv', 'Unknown')}")
            print(f"Position Mode: {account_config.get('data', [{}])[0].get('posMode', 'Unknown')}")
        except:
            print("Unable to fetch account configuration")
        print()
        
        # Trading recommendations
        print("=" * 70)
        print("💡 RECOMMENDATIONS")
        print("=" * 70)
        
        if usdt_total < 0:
            print("🚨 URGENT: Clear your negative balance immediately!")
            print("   1. Deposit ${:,.2f} to OKX".format(abs(usdt_total) + 10))
            print("   2. Review what caused the loss")
            print("   3. Disable margin/futures trading")
            print("   4. Use SPOT trading only (no leverage)")
            print()
        elif usdt_total < 7:
            print("⚠️  Cannot trade with current balance")
            print("   → Use Paper Trading to practice first")
            print("   → Deposit $50+ for real trading later")
            print()
        elif usdt_total < 50:
            print("✅ Can trade, but limited")
            print("   → Current balance: ${:,.2f}".format(usdt_total))
            print("   → Consider depositing more for flexibility")
            print("   → $100+ recommended for better trading")
            print()
        else:
            print("✅ Good balance for trading!")
            print("   → Current balance: ${:,.2f}".format(usdt_total))
            print("   → Ready for automated trading")
            print("   → Consider starting with small positions")
            print()
        
        return usdt_total
        
    except Exception as e:
        print("❌ ERROR CHECKING BALANCE")
        print(f"   {str(e)}")
        print()
        print("💡 TROUBLESHOOTING:")
        print("   1. Check your API keys in config.py")
        print("   2. Ensure API keys have 'Read' permission")
        print("   3. Check OKX API key status on website")
        print("   4. Verify internet connection")
        print()
        return None

if __name__ == "__main__":
    balance = check_okx_balance()
    
    print("=" * 70)
    print("🔍 DIAGNOSIS COMPLETE")
    print("=" * 70)
    
    if balance is not None:
        if balance < 0:
            print("❌ Status: CRITICAL - Negative Balance")
        elif balance < 7:
            print("⚠️  Status: INSUFFICIENT - Use Paper Trading")
        elif balance < 50:
            print("⚠️  Status: LIMITED - Consider Depositing More")
        else:
            print("✅ Status: READY FOR TRADING")
    else:
        print("❌ Status: ERROR - Could Not Check Balance")
    
    print("=" * 70)
