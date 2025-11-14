#!/usr/bin/env python3
"""
Quick utility to stop the underfunded bot
"""
import requests
import sys

# Configuration
API_URL = "https://trading-bot-api-7xps.onrender.com"
BOT_ID = "691649e25d39077924051605"

def stop_bot():
    """Stop the underfunded bot"""
    
    print("🛑 Stopping Underfunded Bot...")
    print(f"Bot ID: {BOT_ID}")
    print(f"API URL: {API_URL}")
    print()
    
    # First, let's login as admin
    print("🔐 Logging in as admin...")
    login_data = {
        "username": "ceo@gideonstechnology.com",
        "password": "your_password_here"  # USER needs to update this
    }
    
    login_response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login failed. Please update the password in this script.")
        print("   Edit stop_bot.py and add your correct password.")
        print()
        print("⚠️ Alternative: Stop the bot from the web dashboard:")
        print(f"   1. Go to: {API_URL}/dashboard")
        print(f"   2. Find bot: TON/USDT • $5")
        print(f"   3. Click the 'Stop' button")
        return False
    
    token = login_response.json().get("access_token")
    print("✅ Logged in successfully")
    print()
    
    # Stop the bot
    print(f"🛑 Stopping bot {BOT_ID}...")
    headers = {"Authorization": f"Bearer {token}"}
    stop_response = requests.post(f"{API_URL}/api/bots/{BOT_ID}/stop", headers=headers)
    
    if stop_response.status_code == 200:
        print("✅ Bot stopped successfully!")
        print()
        print("📊 Bot Status:")
        print("   - Symbol: TON/USDT")
        print("   - Capital: $5 (insufficient)")
        print("   - Trades Made: 0")
        print("   - Profit: $0.00")
        print()
        print("✅ Ready to create a proper bot with adequate capital!")
        return True
    else:
        print(f"❌ Failed to stop bot: {stop_response.status_code}")
        print(f"   Response: {stop_response.text}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🤖 Trading Bot Stopper Utility")
    print("=" * 70)
    print()
    
    success = stop_bot()
    
    if not success:
        print()
        print("💡 Manual Stop Instructions:")
        print("   1. Visit: https://trading-bot-api-7xps.onrender.com/dashboard")
        print("   2. Login with your credentials")
        print("   3. Find 'TON/USDT • $5' bot")
        print("   4. Click the 'Stop' button next to it")
        print()
    
    sys.exit(0 if success else 1)
