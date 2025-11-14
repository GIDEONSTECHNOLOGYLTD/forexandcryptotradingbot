#!/usr/bin/env python3
"""
Quick Status Check - See your balance, positions, and daily P&L
Run this anytime to see exactly where you stand!
"""
from advanced_trading_bot import AdvancedTradingBot
from colorama import Fore, Style, init
import config

init()

def main():
    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"💰 TRADING BOT STATUS CHECK")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    try:
        # Create bot instance
        bot = AdvancedTradingBot()
        
        # Display comprehensive status
        bot.display_trading_status()
        
        # Additional safety info
        print(f"{Fore.CYAN}🛡️ PROTECTION SETTINGS:{Style.RESET_ALL}")
        print(f"  Daily Loss Limit: {config.MAX_DAILY_LOSS_PERCENT}%")
        print(f"  Stop Loss Per Trade: {config.STOP_LOSS_PERCENT}%")
        print(f"  Max Position Size: {config.MAX_POSITION_SIZE_PERCENT}%")
        print(f"  Max Open Positions: {config.MAX_OPEN_POSITIONS}")
        print()
        
        # Calculate safety metrics
        if bot.risk_manager.current_capital > 0:
            loss_limit_dollars = bot.risk_manager.current_capital * (config.MAX_DAILY_LOSS_PERCENT / 100)
            remaining_loss_buffer = loss_limit_dollars + bot.risk_manager.daily_pnl
            
            print(f"{Fore.YELLOW}📊 RISK METRICS:{Style.RESET_ALL}")
            print(f"  Max Daily Loss Allowed: ${loss_limit_dollars:.2f}")
            print(f"  Loss Buffer Remaining: ${remaining_loss_buffer:.2f}")
            
            if remaining_loss_buffer < loss_limit_dollars * 0.3:
                print(f"\n{Fore.RED}⚠️  WARNING: Low loss buffer! Circuit breaker will trigger soon.{Style.RESET_ALL}")
            elif remaining_loss_buffer < loss_limit_dollars * 0.5:
                print(f"\n{Fore.YELLOW}⚠️  CAUTION: Approaching daily loss limit.{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}✅ Good buffer remaining{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}💡 TIP: Run this script anytime to check your status!{Style.RESET_ALL}\n")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Make sure you have:") 
        print(f"1. Set up OKX API keys in .env")
        print(f"2. OKX account has USDT balance")
        print(f"3. API keys have trading permissions{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
