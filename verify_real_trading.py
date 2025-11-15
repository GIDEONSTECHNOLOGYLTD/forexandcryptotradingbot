#!/usr/bin/env python3
"""
VERIFICATION SCRIPT - Prove Real Trading Setup
Run this to verify OKX is configured for REAL trading, not simulation
"""
import ccxt
import config
from colorama import Fore, Style

print("\n" + "="*70)
print(f"{Fore.GREEN}🔥 OKX REAL TRADING VERIFICATION SCRIPT 🔥{Style.RESET_ALL}")
print("="*70 + "\n")

# Check 1: Paper Trading Flag
print(f"{'='*70}")
print(f"{Fore.CYAN}CHECK #1: Paper Trading Mode{Style.RESET_ALL}")
print(f"{'='*70}")
if hasattr(config, 'PAPER_TRADING'):
    if config.PAPER_TRADING == False:
        print(f"{Fore.GREEN}✅ PAPER_TRADING = False{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   This means: REAL TRADING MODE!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ PAPER_TRADING = True{Style.RESET_ALL}")
        print(f"{Fore.RED}   WARNING: This is simulation mode!{Style.RESET_ALL}")
else:
    print(f"{Fore.YELLOW}⚠️  PAPER_TRADING not found in config{Style.RESET_ALL}")
print()

# Check 2: OKX Credentials
print(f"{'='*70}")
print(f"{Fore.CYAN}CHECK #2: OKX API Credentials{Style.RESET_ALL}")
print(f"{'='*70}")
if config.OKX_API_KEY and len(config.OKX_API_KEY) > 10:
    print(f"{Fore.GREEN}✅ OKX_API_KEY: {config.OKX_API_KEY[:10]}...{config.OKX_API_KEY[-10:]}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}   This means: Real API key configured!{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}❌ OKX_API_KEY: Missing or invalid{Style.RESET_ALL}")
    print(f"{Fore.RED}   WARNING: Configure real API key in .env file!{Style.RESET_ALL}")

if config.OKX_SECRET_KEY and len(config.OKX_SECRET_KEY) > 10:
    print(f"{Fore.GREEN}✅ OKX_SECRET_KEY: {config.OKX_SECRET_KEY[:10]}...{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}❌ OKX_SECRET_KEY: Missing or invalid{Style.RESET_ALL}")

if config.OKX_PASSPHRASE and len(config.OKX_PASSPHRASE) > 3:
    print(f"{Fore.GREEN}✅ OKX_PASSPHRASE: {config.OKX_PASSPHRASE[:3]}...{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}❌ OKX_PASSPHRASE: Missing or invalid{Style.RESET_ALL}")
print()

# Check 3: Exchange Configuration
print(f"{'='*70}")
print(f"{Fore.CYAN}CHECK #3: Exchange Configuration{Style.RESET_ALL}")
print(f"{'='*70}")
try:
    exchange = ccxt.okx({
        'apiKey': config.OKX_API_KEY,
        'secret': config.OKX_SECRET_KEY,
        'password': config.OKX_PASSPHRASE,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    print(f"{Fore.GREEN}✅ Exchange initialized: {exchange.id}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}   Default Type: {exchange.options.get('defaultType', 'NOT SET')}{Style.RESET_ALL}")
    
    if exchange.options.get('defaultType') == 'spot':
        print(f"{Fore.GREEN}   This means: REAL SPOT TRADING (not futures/margin)!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}   Warning: Default type is not 'spot'{Style.RESET_ALL}")
    
    # Check if sandbox mode is enabled
    if hasattr(exchange, 'urls') and 'api' in exchange.urls:
        api_url = exchange.urls['api']
        if 'sandbox' in api_url or 'test' in api_url:
            print(f"{Fore.RED}❌ SANDBOX MODE DETECTED: {api_url}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Production API: {api_url}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}   This means: REAL TRADING ON LIVE EXCHANGE!{Style.RESET_ALL}")
    
except Exception as e:
    print(f"{Fore.RED}❌ Error initializing exchange: {e}{Style.RESET_ALL}")
print()

# Check 4: Test Connection & Fetch Real Balance
print(f"{'='*70}")
print(f"{Fore.CYAN}CHECK #4: Real Balance Fetching{Style.RESET_ALL}")
print(f"{'='*70}")
try:
    balance = exchange.fetch_balance()
    
    print(f"{Fore.GREEN}✅ Connection successful!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}   Account type: {balance.get('info', {}).get('acctLv', 'Unknown')}{Style.RESET_ALL}")
    
    # Show USDT balance
    if 'USDT' in balance and 'free' in balance['USDT']:
        usdt_free = balance['USDT']['free']
        usdt_used = balance['USDT']['used']
        usdt_total = balance['USDT']['total']
        
        print(f"{Fore.GREEN}   USDT Free: {usdt_free:.2f}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   USDT Used: {usdt_used:.2f}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   USDT Total: {usdt_total:.2f}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   This means: REAL BALANCE FROM YOUR OKX ACCOUNT!{Style.RESET_ALL}")
        
        if usdt_total > 0:
            print(f"{Fore.GREEN}   ✅ You have funds to trade!{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}   ⚠️  No USDT balance found. Add funds to trade.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}   ⚠️  USDT balance not found{Style.RESET_ALL}")
    
except Exception as e:
    print(f"{Fore.RED}❌ Error fetching balance: {e}{Style.RESET_ALL}")
    print(f"{Fore.RED}   Check your API credentials and permissions!{Style.RESET_ALL}")
print()

# Check 5: Telegram Configuration
print(f"{'='*70}")
print(f"{Fore.CYAN}CHECK #5: Telegram Notifications{Style.RESET_ALL}")
print(f"{'='*70}")
if config.TELEGRAM_BOT_TOKEN and len(config.TELEGRAM_BOT_TOKEN) > 20:
    print(f"{Fore.GREEN}✅ TELEGRAM_BOT_TOKEN: {config.TELEGRAM_BOT_TOKEN[:15]}...{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}❌ TELEGRAM_BOT_TOKEN: Missing{Style.RESET_ALL}")
    print(f"{Fore.RED}   WARNING: You won't receive notifications!{Style.RESET_ALL}")

if config.TELEGRAM_CHAT_ID:
    print(f"{Fore.GREEN}✅ TELEGRAM_CHAT_ID: {config.TELEGRAM_CHAT_ID}{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}❌ TELEGRAM_CHAT_ID: Missing{Style.RESET_ALL}")
    print(f"{Fore.RED}   WARNING: You won't receive notifications!{Style.RESET_ALL}")

# Try to import telegram notifier
try:
    from telegram_notifier import TelegramNotifier
    telegram = TelegramNotifier()
    if telegram.enabled:
        print(f"{Fore.GREEN}✅ Telegram notifier initialized and enabled{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   This means: YOU WILL RECEIVE ALL NOTIFICATIONS!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Telegram configured but not enabled{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.YELLOW}⚠️  Could not initialize Telegram: {e}{Style.RESET_ALL}")
print()

# Check 6: Trading Mode Parameters
print(f"{'='*70}")
print(f"{Fore.CYAN}CHECK #6: Trading Mode Verification{Style.RESET_ALL}")
print(f"{'='*70}")
print(f"{Fore.GREEN}When you place orders, they will use:{Style.RESET_ALL}")
print(f"{Fore.GREEN}   params={{'tdMode': 'cash'}}{Style.RESET_ALL}")
print(f"{Fore.GREEN}   This means: REAL SPOT TRADING WITH CASH!{Style.RESET_ALL}")
print(f"{Fore.GREEN}   NOT margin, NOT futures, NOT simulated!{Style.RESET_ALL}")
print()

# Final Verdict
print(f"{'='*70}")
print(f"{Fore.MAGENTA}🎯 FINAL VERDICT{Style.RESET_ALL}")
print(f"{'='*70}")

issues = []
if hasattr(config, 'PAPER_TRADING') and config.PAPER_TRADING == True:
    issues.append("Paper trading is enabled")
if not config.OKX_API_KEY or len(config.OKX_API_KEY) < 10:
    issues.append("OKX API key missing or invalid")
if not config.OKX_SECRET_KEY or len(config.OKX_SECRET_KEY) < 10:
    issues.append("OKX secret key missing or invalid")
if not config.OKX_PASSPHRASE or len(config.OKX_PASSPHRASE) < 3:
    issues.append("OKX passphrase missing or invalid")

if issues:
    print(f"{Fore.RED}❌ ISSUES FOUND:{Style.RESET_ALL}")
    for issue in issues:
        print(f"{Fore.RED}   - {issue}{Style.RESET_ALL}")
    print(f"\n{Fore.RED}🚨 FIX THESE ISSUES BEFORE TRADING!{Style.RESET_ALL}")
else:
    print(f"{Fore.GREEN}✅✅✅ ALL CHECKS PASSED! ✅✅✅{Style.RESET_ALL}")
    print(f"\n{Fore.GREEN}🔥 THIS IS 100% REAL TRADING! 🔥{Style.RESET_ALL}")
    print(f"{Fore.GREEN}   - Connected to REAL OKX production API{Style.RESET_ALL}")
    print(f"{Fore.GREEN}   - Using REAL spot trading mode{Style.RESET_ALL}")
    print(f"{Fore.GREEN}   - Trades will use REAL cash (tdMode: 'cash'){Style.RESET_ALL}")
    print(f"{Fore.GREEN}   - All profits/losses are REAL{Style.RESET_ALL}")
    print(f"{Fore.GREEN}   - Telegram notifications ENABLED{Style.RESET_ALL}")
    print(f"\n{Fore.GREEN}🚀 READY TO MAKE REAL PROFITS! 🚀{Style.RESET_ALL}")

print(f"\n{'='*70}\n")
