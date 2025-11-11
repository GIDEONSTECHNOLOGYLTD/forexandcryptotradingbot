"""
Background job to check pending crypto payments
Runs every minute to automatically confirm payments
"""
import asyncio
import time
from datetime import datetime
from colorama import Fore, Style
from okx_payment_handler import payment_handler

async def check_payments_loop():
    """Main loop to check payments every minute"""
    print(f"{Fore.GREEN}╔════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.GREEN}║           CRYPTO PAYMENT CHECKER - STARTED                         ║{Style.RESET_ALL}")
    print(f"{Fore.GREEN}╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    print()
    
    iteration = 0
    
    while True:
        try:
            iteration += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"{Fore.CYAN}[{current_time}] Checking pending payments... (Iteration {iteration}){Style.RESET_ALL}")
            
            # Check all pending payments
            confirmed_count = payment_handler.check_all_pending_payments()
            
            if confirmed_count > 0:
                print(f"{Fore.GREEN}✅ Confirmed {confirmed_count} payment(s)!{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⏳ No new payments confirmed{Style.RESET_ALL}")
            
            # Wait 60 seconds before next check
            await asyncio.sleep(60)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Payment checker stopped by user{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ Error checking payments: {e}{Style.RESET_ALL}")
            # Wait 60 seconds before retrying
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(check_payments_loop())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down payment checker...{Style.RESET_ALL}")
