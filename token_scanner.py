"""
Token Scanner Module
Scans for potential trading opportunities across multiple tokens
"""
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import config
from colorama import Fore, Style


class TokenScanner:
    def __init__(self, exchange):
        self.exchange = exchange
        self.opportunities = []
        
    def scan_markets(self):
        """Scan all available markets for trading opportunities"""
        print(f"\n{Fore.CYAN}🔍 Scanning markets for opportunities...{Style.RESET_ALL}")
        
        try:
            # Fetch all tickers
            tickers = self.exchange.fetch_tickers()
            opportunities = []
            
            for symbol, ticker in tickers.items():
                # Filter based on quote currency
                quote_currency = symbol.split('/')[-1] if '/' in symbol else ''
                if quote_currency not in config.QUOTE_CURRENCIES:
                    continue
                
                # Check volume threshold
                volume_usd = ticker.get('quoteVolume', 0)
                if volume_usd < config.MIN_VOLUME_USD:
                    continue
                
                # Calculate price change
                price_change = ticker.get('percentage', 0)
                if price_change is None:
                    continue
                
                # Score the opportunity
                score = self.calculate_opportunity_score(ticker, symbol)
                
                if score > 0:
                    opportunities.append({
                        'symbol': symbol,
                        'price': ticker.get('last', 0),
                        'volume_24h': volume_usd,
                        'price_change_24h': price_change,
                        'score': score,
                        'timestamp': datetime.now()
                    })
            
            # Sort by score
            opportunities.sort(key=lambda x: x['score'], reverse=True)
            self.opportunities = opportunities[:10]  # Keep top 10
            
            return self.opportunities
            
        except Exception as e:
            print(f"{Fore.RED}Error scanning markets: {e}{Style.RESET_ALL}")
            return []
    
    def calculate_opportunity_score(self, ticker, symbol):
        """
        Calculate a score for the trading opportunity
        Higher score = better opportunity
        """
        score = 0
        
        try:
            # Volume score (higher volume = better)
            volume_usd = ticker.get('quoteVolume', 0)
            if volume_usd > 10000000:  # > 10M
                score += 3
            elif volume_usd > 5000000:  # > 5M
                score += 2
            elif volume_usd > 1000000:  # > 1M
                score += 1
            
            # Price change score (moderate movement preferred)
            price_change = abs(ticker.get('percentage', 0))
            if 2 <= price_change <= 5:
                score += 3
            elif 5 < price_change <= 10:
                score += 2
            elif price_change > 10:
                score += 1  # Too volatile
            
            # Volatility score (check bid-ask spread)
            bid = ticker.get('bid', 0)
            ask = ticker.get('ask', 0)
            if bid and ask:
                spread_percent = ((ask - bid) / bid) * 100
                if spread_percent < 0.1:  # Tight spread
                    score += 2
                elif spread_percent < 0.5:
                    score += 1
            
            return score
            
        except Exception as e:
            return 0
    
    def get_top_opportunities(self, limit=5):
        """Get top N opportunities"""
        return self.opportunities[:limit]
    
    def display_opportunities(self):
        """Display found opportunities"""
        if not self.opportunities:
            print(f"{Fore.YELLOW}No opportunities found.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}📊 Top Trading Opportunities:{Style.RESET_ALL}")
        print(f"{'Symbol':<15} {'Price':<12} {'24h Change':<12} {'Volume (24h)':<15} {'Score':<8}")
        print("-" * 70)
        
        for opp in self.opportunities[:5]:
            symbol = opp['symbol']
            price = f"${opp['price']:.4f}"
            change = f"{opp['price_change_24h']:+.2f}%"
            volume = f"${opp['volume_24h']:,.0f}"
            score = f"{opp['score']}/10"
            
            # Color code based on price change
            if opp['price_change_24h'] > 0:
                change_color = Fore.GREEN
            else:
                change_color = Fore.RED
            
            print(f"{symbol:<15} {price:<12} {change_color}{change:<12}{Style.RESET_ALL} {volume:<15} {score:<8}")
