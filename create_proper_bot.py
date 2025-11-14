#!/usr/bin/env python3
"""
Create a Proper Trading Bot with Adequate Capital
This script helps you create a bot that can actually trade!
"""
import requests
import sys
from datetime import datetime

# Configuration
API_URL = "https://trading-bot-api-7xps.onrender.com"

def create_paper_trading_bot():
    """Create a paper trading bot for safe practice"""
    
    print("=" * 70)
    print("🤖 CREATING PROPER TRADING BOT")
    print("=" * 70)
    print()
    
    # Login
    print("🔐 Logging in as admin...")
    login_data = {
        "username": "ceo@gideonstechnology.com",
        "password": "your_password_here"  # USER needs to update this
    }
    
    login_response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login failed. Please update password in create_proper_bot.py")
        print()
        print("🌐 Alternative: Create bot via web dashboard:")
        print(f"   1. Visit: {API_URL}/dashboard")
        print("   2. Fill out the 'Create New Bot' form")
        print("   3. Choose Paper Trading mode")
        print("   4. Set capital to $1000")
        print("   5. Click 'Create & Start Bot'")
        return False
    
    token = login_response.json().get("access_token")
    print("✅ Logged in successfully")
    print()
    
    # Bot configurations
    print("📋 Available Bot Configurations:")
    print()
    print("1️⃣  Conservative Paper Trading Bot")
    print("   • Symbol: BTC/USDT (stable)")
    print("   • Capital: $1,000 (fake money)")
    print("   • Strategy: Momentum")
    print("   • Risk: Low")
    print()
    print("2️⃣  Aggressive Paper Trading Bot")
    print("   • Symbol: SOL/USDT (volatile)")
    print("   • Capital: $5,000 (fake money)")
    print("   • Strategy: Grid Trading")
    print("   • Risk: High")
    print()
    print("3️⃣  Balanced Paper Trading Bot")
    print("   • Symbol: ETH/USDT (balanced)")
    print("   • Capital: $2,000 (fake money)")
    print("   • Strategy: DCA Bot")
    print("   • Risk: Medium")
    print()
    
    # Create conservative bot by default
    bot_config = {
        "strategy": "momentum",
        "symbol": "BTC/USDT",
        "initial_capital": 1000,
        "paper_trading": True,
        "risk_level": "low"
    }
    
    print("✨ Creating Bot #1 (Conservative Paper Trading)...")
    print()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_URL}/api/bots/create",
        json=bot_config,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        bot_id = result.get("bot_id")
        
        print("✅ Bot Created Successfully!")
        print()
        print("=" * 70)
        print("📊 BOT DETAILS")
        print("=" * 70)
        print(f"Bot ID:       {bot_id}")
        print(f"Symbol:       BTC/USDT")
        print(f"Capital:      $1,000.00 (Paper Trading)")
        print(f"Strategy:     Momentum")
        print(f"Risk Level:   Low (1% per trade)")
        print(f"Mode:         📝 Paper Trading (SAFE)")
        print(f"Created:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Start the bot
        print("🚀 Starting bot...")
        start_response = requests.post(
            f"{API_URL}/api/bots/{bot_id}/start",
            headers=headers
        )
        
        if start_response.status_code == 200:
            print("✅ Bot started successfully!")
            print()
            print("=" * 70)
            print("✨ CONGRATULATIONS!")
            print("=" * 70)
            print()
            print("Your bot is now running with PROPER capital!")
            print()
            print("📈 What happens now:")
            print("   • Bot monitors BTC/USDT price every 10 seconds")
            print("   • Uses momentum strategy to detect opportunities")
            print("   • Makes trades when conditions are right")
            print("   • All trades are SIMULATED (no real money risk)")
            print()
            print("📊 Monitor your bot:")
            print(f"   Dashboard: {API_URL}/dashboard")
            print("   You'll see trades appear in 'Recent Trades'")
            print()
            print("💡 Next Steps:")
            print("   1. Watch how the bot trades")
            print("   2. Learn from paper trading results")
            print("   3. When profitable, upgrade to real trading")
            print("   4. Start with small real capital ($50-100)")
            print()
            print("🎯 Goal: Get comfortable with paper trading first!")
            print()
            return True
        else:
            print(f"⚠️  Bot created but failed to start: {start_response.text}")
            print("   You can start it manually from the dashboard")
            return True
            
    else:
        print(f"❌ Failed to create bot: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

if __name__ == "__main__":
    print()
    print("🤖 PROPER BOT CREATOR")
    print("This will create a bot with ADEQUATE capital that can actually trade!")
    print()
    print("⚠️  IMPORTANT: Edit this file and add your password first!")
    print("   Line 18: password: 'your_password_here'")
    print()
    input("Press ENTER to continue or CTRL+C to exit...")
    print()
    
    success = create_paper_trading_bot()
    
    if not success:
        print()
        print("=" * 70)
        print("💡 MANUAL CREATION STEPS")
        print("=" * 70)
        print("1. Visit: https://trading-bot-api-7xps.onrender.com/dashboard")
        print("2. Login with your credentials")
        print("3. Scroll to 'Create New Bot' section")
        print("4. Fill out the form:")
        print("   - Bot Type: Momentum Strategy")
        print("   - Trading Pair: BTC/USDT")
        print("   - Initial Capital: $1000")
        print("   - Trading Mode: Paper Trading (Safe)")
        print("   - Risk Level: Low (1% per trade)")
        print("5. Click 'Create & Start Bot'")
        print()
    
    sys.exit(0 if success else 1)
