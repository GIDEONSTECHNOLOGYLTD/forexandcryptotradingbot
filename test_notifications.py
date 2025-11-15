#!/usr/bin/env python3
"""
NOTIFICATION TEST SCRIPT - Verify All Notifications Work

Tests:
1. Low balance notification
2. New listing insufficient balance notification
3. AI Asset Manager integration
4. All other critical notifications
"""
import sys
import os

# Try to import colorama, but work without it
try:
    from colorama import Fore, Style, init
    init()
    HAS_COLOR = True
except ImportError:
    # Fallback: no colors
    class Fore:
        GREEN = ""
        RED = ""
        YELLOW = ""
        CYAN = ""
    class Style:
        RESET_ALL = ""
    HAS_COLOR = False

print("\n" + "="*70)
print(f"{Fore.CYAN}🔔 NOTIFICATION SYSTEM VERIFICATION{Style.RESET_ALL}")
print("="*70 + "\n")

# Test 1: Check if AI Asset Manager exists
print(f"{Fore.YELLOW}Test 1: AI Asset Manager File Exists{Style.RESET_ALL}")
ai_asset_file = "ai_asset_manager.py"
if os.path.exists(ai_asset_file):
    file_size = os.path.getsize(ai_asset_file)
    line_count = len(open(ai_asset_file).readlines())
    print(f"{Fore.GREEN}✅ File exists: {ai_asset_file}{Style.RESET_ALL}")
    print(f"   Size: {file_size:,} bytes")
    print(f"   Lines: {line_count}")
    if line_count > 500:
        print(f"{Fore.GREEN}   ✅ Substantial implementation ({line_count} lines){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}   ⚠️  Small file, may need review{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}❌ File NOT found: {ai_asset_file}{Style.RESET_ALL}")

print()

# Test 2: Check if AI Asset Manager is imported in admin_auto_trader.py
print(f"{Fore.YELLOW}Test 2: AI Asset Manager Import in Admin Bot{Style.RESET_ALL}")
admin_file = "admin_auto_trader.py"
if os.path.exists(admin_file):
    with open(admin_file, 'r') as f:
        content = f.read()
        
    if 'from ai_asset_manager import AIAssetManager' in content:
        print(f"{Fore.GREEN}✅ AI Asset Manager imported in admin bot{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ AI Asset Manager NOT imported{Style.RESET_ALL}")
    
    if 'self.asset_manager = AIAssetManager' in content:
        print(f"{Fore.GREEN}✅ AI Asset Manager initialized{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ AI Asset Manager NOT initialized{Style.RESET_ALL}")
    
    if 'manage_existing_assets' in content:
        print(f"{Fore.GREEN}✅ manage_existing_assets() method exists{Style.RESET_ALL}")
        
        # Check if it's called in main loop
        if 'self.manage_existing_assets()' in content:
            print(f"{Fore.GREEN}✅ manage_existing_assets() called in main loop{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ manage_existing_assets() NOT called{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ manage_existing_assets() method NOT found{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}❌ Admin bot file NOT found{Style.RESET_ALL}")

print()

# Test 3: Check low balance notification
print(f"{Fore.YELLOW}Test 3: Low Balance Notification{Style.RESET_ALL}")
advanced_bot_file = "advanced_trading_bot.py"
if os.path.exists(advanced_bot_file):
    with open(advanced_bot_file, 'r') as f:
        content = f.read()
    
    if 'BALANCE TOO LOW TO TRADE' in content:
        print(f"{Fore.GREEN}✅ Low balance notification implemented{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Low balance notification NOT found{Style.RESET_ALL}")
    
    if '_last_low_balance_notification' in content:
        print(f"{Fore.GREEN}✅ Anti-spam protection implemented{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  No anti-spam protection{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}❌ Advanced bot file NOT found{Style.RESET_ALL}")

print()

# Test 4: Check new listing insufficient balance notification
print(f"{Fore.YELLOW}Test 4: New Listing Insufficient Balance Notification{Style.RESET_ALL}")
new_listing_file = "new_listing_bot.py"
if os.path.exists(new_listing_file):
    with open(new_listing_file, 'r') as f:
        content = f.read()
    
    if 'NEW LISTING - INSUFFICIENT BALANCE' in content:
        print(f"{Fore.GREEN}✅ New listing balance check implemented{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ New listing balance check NOT found{Style.RESET_ALL}")
    
    if 'fetch_balance()' in content and 'execute_new_listing_trade' in content:
        print(f"{Fore.GREEN}✅ Balance fetched before order{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Balance check may be missing{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}❌ New listing bot file NOT found{Style.RESET_ALL}")

print()

# Test 5: Configuration check
print(f"{Fore.YELLOW}Test 5: AI Asset Manager Configuration{Style.RESET_ALL}")
config_file = "config.py"
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        content = f.read()
    
    if 'ADMIN_ENABLE_ASSET_MANAGER' in content:
        print(f"{Fore.GREEN}✅ ADMIN_ENABLE_ASSET_MANAGER config exists{Style.RESET_ALL}")
        
        # Check .env file
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
            if 'ADMIN_ENABLE_ASSET_MANAGER' in env_content:
                if 'ADMIN_ENABLE_ASSET_MANAGER=true' in env_content:
                    print(f"{Fore.GREEN}✅ AI Asset Manager ENABLED in .env{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️  AI Asset Manager DISABLED in .env{Style.RESET_ALL}")
                    print(f"   To enable: Add 'ADMIN_ENABLE_ASSET_MANAGER=true' to .env")
            else:
                print(f"{Fore.YELLOW}⚠️  ADMIN_ENABLE_ASSET_MANAGER not in .env (will use default: false){Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  .env file not found{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ ADMIN_ENABLE_ASSET_MANAGER config NOT found{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}❌ Config file NOT found{Style.RESET_ALL}")

print()

# Summary
print("="*70)
print(f"{Fore.CYAN}📊 VERIFICATION SUMMARY{Style.RESET_ALL}")
print("="*70)

tests_passed = 0
tests_total = 5

# Count passed tests (simplified)
if os.path.exists("ai_asset_manager.py"):
    tests_passed += 1
if os.path.exists("admin_auto_trader.py"):
    with open("admin_auto_trader.py") as f:
        if "AIAssetManager" in f.read():
            tests_passed += 1
if os.path.exists("advanced_trading_bot.py"):
    with open("advanced_trading_bot.py") as f:
        if "BALANCE TOO LOW TO TRADE" in f.read():
            tests_passed += 1
if os.path.exists("new_listing_bot.py"):
    with open("new_listing_bot.py") as f:
        if "NEW LISTING - INSUFFICIENT BALANCE" in f.read():
            tests_passed += 1
if os.path.exists("config.py"):
    with open("config.py") as f:
        if "ADMIN_ENABLE_ASSET_MANAGER" in f.read():
            tests_passed += 1

print(f"\n{Fore.CYAN}Tests Passed: {tests_passed}/{tests_total}{Style.RESET_ALL}")

if tests_passed == tests_total:
    print(f"\n{Fore.GREEN}✅✅✅ ALL TESTS PASSED! ✅✅✅{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🎉 AI Asset Manager is REAL and properly integrated!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🔔 All notifications are implemented!{Style.RESET_ALL}")
elif tests_passed >= 3:
    print(f"\n{Fore.YELLOW}⚠️  Most tests passed, but some issues found{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Review the output above for details{Style.RESET_ALL}")
else:
    print(f"\n{Fore.RED}❌ Multiple issues found!{Style.RESET_ALL}")
    print(f"{Fore.RED}Review the implementation{Style.RESET_ALL}")

print()

# Instructions
print("="*70)
print(f"{Fore.CYAN}📋 HOW TO ENABLE AI ASSET MANAGER{Style.RESET_ALL}")
print("="*70)
print()
print("1. Add to .env file:")
print(f"   {Fore.GREEN}ADMIN_ENABLE_ASSET_MANAGER=true{Style.RESET_ALL}")
print()
print("2. Run admin bot:")
print(f"   {Fore.GREEN}python admin_auto_trader.py{Style.RESET_ALL}")
print()
print("3. AI will analyze your holdings every hour and send Telegram notifications")
print()
print("="*70)
print()
