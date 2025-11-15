"""
AI ASSET MANAGER - Intelligently Manage Your Existing OKX Holdings

This AI analyzes ALL your current assets in OKX and makes smart decisions:
- Studies your positions (profitable and losing)
- Determines optimal exit strategies
- Suggests when to sell for profit
- Helps you exit losing positions strategically
- Frees up capital stuck in assets
"""
import ccxt
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from colorama import Fore, Style
import config

logger = logging.getLogger(__name__)

# Import AI engines
try:
    from advanced_ai_engine import AdvancedAIEngine
    AI_ENGINE_AVAILABLE = True
except ImportError:
    AI_ENGINE_AVAILABLE = False
    logger.warning("Advanced AI Engine not available")

try:
    from telegram_notifier import TelegramNotifier
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("Telegram notifications not available")


class AIAssetManager:
    """
    AI-powered manager for your existing OKX holdings
    Analyzes positions and suggests optimal exit strategies
    """
    
    def __init__(self, exchange: ccxt.Exchange, db=None, telegram=None):
        """
        Initialize AI Asset Manager
        
        Args:
            exchange: CCXT exchange instance
            db: Database instance
            telegram: TelegramNotifier instance
        """
        self.exchange = exchange
        self.db = db
        
        # Initialize Telegram
        if telegram:
            self.telegram = telegram
        elif TELEGRAM_AVAILABLE:
            self.telegram = TelegramNotifier()
        else:
            self.telegram = None
        
        # Initialize AI Engine
        if AI_ENGINE_AVAILABLE:
            self.ai_engine = AdvancedAIEngine(exchange)
            logger.info("✅ AI Engine initialized for asset management")
        else:
            self.ai_engine = None
            logger.warning("⚠️ AI Engine not available - using basic analysis")
        
        # Asset management settings
        self.min_profit_target = 3  # Minimum 3% profit to consider selling
        self.max_acceptable_loss = -10  # Max loss before forced exit consideration
        self.check_interval = 300  # Check every 5 minutes
        self.min_asset_value = 1  # Minimum $1 value to manage
        
        # Track managed assets
        self.managed_assets = {}
        self.last_analysis_time = {}
        
        logger.info("🤖 AI Asset Manager initialized")
    
    def fetch_all_holdings(self) -> List[Dict]:
        """
        Fetch ALL your current holdings from OKX
        
        Returns:
            List of holdings with details
        """
        try:
            balance = self.exchange.fetch_balance()
            holdings = []
            
            # Get all non-zero balances
            for currency, amounts in balance.items():
                if currency in ['free', 'used', 'total', 'info']:
                    continue
                
                total_amount = amounts.get('total', 0)
                if total_amount <= 0:
                    continue
                
                # Skip USDT (it's your quote currency)
                if currency == 'USDT':
                    continue
                
                free_amount = amounts.get('free', 0)
                used_amount = amounts.get('used', 0)
                
                # Get current price
                try:
                    symbol = f"{currency}/USDT"
                    ticker = self.exchange.fetch_ticker(symbol)
                    current_price = ticker['last']
                    value_usd = total_amount * current_price
                    
                    # Only manage assets worth at least $1
                    if value_usd < self.min_asset_value:
                        continue
                    
                    holding = {
                        'currency': currency,
                        'symbol': symbol,
                        'total_amount': total_amount,
                        'free_amount': free_amount,
                        'used_amount': used_amount,
                        'current_price': current_price,
                        'value_usd': value_usd,
                        'timestamp': datetime.utcnow()
                    }
                    
                    holdings.append(holding)
                    logger.info(f"📊 Holding: {currency} - {total_amount:.6f} (${value_usd:.2f})")
                    
                except Exception as e:
                    logger.warning(f"Could not get price for {currency}: {e}")
                    continue
            
            return holdings
            
        except Exception as e:
            logger.error(f"Error fetching holdings: {e}")
            return []
    
    def analyze_holding(self, holding: Dict) -> Dict:
        """
        AI analysis of a single holding
        
        Args:
            holding: Holding details
            
        Returns:
            Analysis with recommendations
        """
        currency = holding['currency']
        symbol = holding['symbol']
        current_price = holding['current_price']
        value_usd = holding['value_usd']
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🤖 AI ANALYZING: {symbol}")
        logger.info(f"{'='*70}")
        
        try:
            # Try to get historical data to estimate entry
            # If we can't find entry, we'll analyze current situation
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1d', limit=30)
            
            if not ohlcv:
                logger.warning(f"No historical data for {symbol}")
                return self._basic_analysis(holding)
            
            # Get price history
            prices = [candle[4] for candle in ohlcv]  # Close prices
            avg_price_7d = sum(prices[-7:]) / 7
            avg_price_30d = sum(prices) / len(prices)
            highest_30d = max(prices)
            lowest_30d = min(prices)
            
            # Calculate where current price is relative to range
            price_range = highest_30d - lowest_30d
            if price_range > 0:
                position_in_range = (current_price - lowest_30d) / price_range * 100
            else:
                position_in_range = 50
            
            # AI-based decision making
            recommendation = "HOLD"
            reasoning = []
            urgency = "LOW"
            
            # 1. Price position analysis
            if position_in_range > 80:
                recommendation = "SELL"
                reasoning.append(f"Price near 30-day high ({position_in_range:.1f}% of range)")
                urgency = "HIGH"
            elif position_in_range < 20:
                recommendation = "HOLD"
                reasoning.append(f"Price near 30-day low ({position_in_range:.1f}% of range)")
                reasoning.append("Wait for recovery")
            
            # 2. Trend analysis
            if current_price > avg_price_7d and avg_price_7d > avg_price_30d:
                if recommendation != "SELL":
                    recommendation = "HOLD"
                reasoning.append("Uptrend detected - price rising")
            elif current_price < avg_price_7d and avg_price_7d < avg_price_30d:
                if recommendation != "SELL":
                    recommendation = "CONSIDER_SELL"
                reasoning.append("Downtrend detected - price falling")
                urgency = "MEDIUM"
            
            # 3. Use Advanced AI if available
            if self.ai_engine:
                try:
                    # Multi-timeframe analysis
                    ai_analysis = self.ai_engine.should_enter_trade(symbol, 'sell', confidence=60)
                    
                    if ai_analysis['should_enter']:
                        recommendation = "SELL"
                        reasoning.append(f"AI recommends selling (Confidence: {ai_analysis['confidence_adjusted']}%)")
                        urgency = "HIGH"
                    
                    reasoning.append(f"AI: {ai_analysis['reason']}")
                    
                except Exception as e:
                    logger.warning(f"AI analysis failed: {e}")
            
            # 4. Value-based decision
            if value_usd < 5:
                recommendation = "SELL"
                reasoning.append(f"Small position (${value_usd:.2f}) - consider closing")
                urgency = "LOW"
            
            analysis = {
                'symbol': symbol,
                'currency': currency,
                'current_price': current_price,
                'value_usd': value_usd,
                'avg_price_7d': avg_price_7d,
                'avg_price_30d': avg_price_30d,
                'highest_30d': highest_30d,
                'lowest_30d': lowest_30d,
                'position_in_range': position_in_range,
                'recommendation': recommendation,
                'reasoning': reasoning,
                'urgency': urgency,
                'timestamp': datetime.utcnow()
            }
            
            logger.info(f"📊 Analysis complete:")
            logger.info(f"   Current: ${current_price:.6f}")
            logger.info(f"   7-day avg: ${avg_price_7d:.6f}")
            logger.info(f"   30-day avg: ${avg_price_30d:.6f}")
            logger.info(f"   Position in range: {position_in_range:.1f}%")
            logger.info(f"   Recommendation: {recommendation} (Urgency: {urgency})")
            logger.info(f"   Reasoning: {', '.join(reasoning)}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return self._basic_analysis(holding)
    
    def _basic_analysis(self, holding: Dict) -> Dict:
        """
        Basic analysis when advanced analysis fails
        
        Args:
            holding: Holding details
            
        Returns:
            Basic analysis
        """
        return {
            'symbol': holding['symbol'],
            'currency': holding['currency'],
            'current_price': holding['current_price'],
            'value_usd': holding['value_usd'],
            'recommendation': 'HOLD',
            'reasoning': ['Insufficient data for detailed analysis'],
            'urgency': 'LOW',
            'timestamp': datetime.utcnow()
        }
    
    def send_analysis_notification(self, analysis: Dict, holding: Dict):
        """
        Send Telegram notification with analysis results
        
        Args:
            analysis: Analysis results
            holding: Holding details
        """
        if not self.telegram or not self.telegram.enabled:
            return
        
        symbol = analysis['symbol']
        recommendation = analysis['recommendation']
        urgency = analysis['urgency']
        value_usd = analysis['value_usd']
        current_price = analysis['current_price']
        
        # Emoji based on recommendation
        if recommendation == 'SELL':
            emoji = "🔴"
            action = "SELL NOW"
        elif recommendation == 'CONSIDER_SELL':
            emoji = "⚠️"
            action = "Consider Selling"
        else:
            emoji = "🟢"
            action = "HOLD"
        
        # Urgency indicator
        urgency_emoji = {
            'HIGH': '🚨',
            'MEDIUM': '⚠️',
            'LOW': '💡'
        }.get(urgency, '💡')
        
        try:
            message = (
                f"{emoji} <b>AI ASSET ANALYSIS</b>\n\n"
                f"🪙 Asset: <b>{symbol}</b>\n"
                f"💰 Current Price: ${current_price:.6f}\n"
                f"💵 Total Value: <b>${value_usd:.2f}</b>\n"
                f"📊 Amount: {holding['total_amount']:.6f}\n\n"
                f"🤖 <b>AI Recommendation: {action}</b>\n"
                f"{urgency_emoji} Urgency: {urgency}\n\n"
                f"<b>📋 Reasoning:</b>\n"
            )
            
            for reason in analysis['reasoning'][:3]:  # Top 3 reasons
                message += f"  • {reason}\n"
            
            if analysis.get('avg_price_7d'):
                message += f"\n📈 <b>Price Levels:</b>\n"
                message += f"  7-day avg: ${analysis['avg_price_7d']:.6f}\n"
                message += f"  30-day avg: ${analysis['avg_price_30d']:.6f}\n"
                message += f"  Position: {analysis['position_in_range']:.1f}% of 30d range\n"
            
            message += f"\n⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
            
            self.telegram.send_message(message)
            logger.info(f"📱 Analysis notification sent for {symbol}")
            
        except Exception as e:
            logger.warning(f"Failed to send analysis notification: {e}")
    
    def execute_smart_sell(self, holding: Dict, analysis: Dict) -> bool:
        """
        Execute smart sell order for a holding
        
        Args:
            holding: Holding details
            analysis: Analysis results
            
        Returns:
            True if successful
        """
        symbol = holding['symbol']
        amount = holding['free_amount']  # Only sell free (not locked) amount
        current_price = holding['current_price']
        
        if amount <= 0:
            logger.warning(f"No free amount to sell for {symbol}")
            return False
        
        try:
            logger.info(f"🔴 SELLING {symbol}: {amount:.6f} @ ${current_price:.6f}")
            
            # Execute market sell order
            order = self.exchange.create_market_sell_order(
                symbol,
                amount,
                params={'tdMode': 'cash'}  # SPOT trading
            )
            
            value_usd = amount * current_price
            
            logger.info(f"✅ SELL order executed: {symbol}")
            
            # Send Telegram notification
            if self.telegram and self.telegram.enabled:
                self.telegram.send_message(
                    f"🔴 <b>AI ASSET SOLD</b>\n\n"
                    f"🪙 Symbol: <b>{symbol}</b>\n"
                    f"💰 Price: ${current_price:.6f}\n"
                    f"📊 Amount: {amount:.6f}\n"
                    f"💵 Value: <b>${value_usd:.2f}</b>\n\n"
                    f"🤖 AI Recommendation: {analysis['recommendation']}\n"
                    f"📋 Reason: {analysis['reasoning'][0] if analysis['reasoning'] else 'AI Decision'}\n\n"
                    f"✅ Order executed successfully!\n"
                    f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to sell {symbol}: {e}")
            
            # Send error notification
            if self.telegram and self.telegram.enabled:
                self.telegram.send_message(
                    f"🚨 <b>ASSET SELL FAILED</b>\n\n"
                    f"🪙 Symbol: {symbol}\n"
                    f"📊 Amount: {amount:.6f}\n"
                    f"💰 Price: ${current_price:.6f}\n\n"
                    f"❌ Error: {str(e)}\n\n"
                    f"⚠️ Position NOT closed!\n"
                    f"💡 Check OKX manually\n\n"
                    f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                )
            
            return False
    
    def analyze_and_manage_all_assets(self, auto_sell: bool = False):
        """
        Analyze all holdings and manage them
        
        Args:
            auto_sell: If True, automatically sell when AI recommends
        """
        logger.info("\n" + "="*70)
        logger.info(f"{Fore.CYAN}🤖 AI ASSET MANAGER - ANALYZING YOUR PORTFOLIO{Style.RESET_ALL}")
        logger.info("="*70 + "\n")
        
        # Send start notification
        if self.telegram and self.telegram.enabled:
            self.telegram.send_message(
                "🤖 <b>AI ASSET MANAGER STARTED</b>\n\n"
                "📊 Analyzing all your OKX holdings...\n"
                "💡 You'll receive recommendations for each asset\n\n"
                f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
            )
        
        # Fetch all holdings
        holdings = self.fetch_all_holdings()
        
        if not holdings:
            logger.info("No holdings found or all holdings below minimum value")
            return
        
        logger.info(f"Found {len(holdings)} holdings to analyze\n")
        
        # Analyze each holding
        analyses = []
        for holding in holdings:
            analysis = self.analyze_holding(holding)
            analyses.append((holding, analysis))
            
            # Send notification for each analysis
            self.send_analysis_notification(analysis, holding)
            
            # Auto-sell if recommended and enabled
            if auto_sell and analysis['recommendation'] == 'SELL':
                logger.info(f"🤖 Auto-sell enabled and AI recommends SELL")
                self.execute_smart_sell(holding, analysis)
            
            time.sleep(2)  # Rate limiting
        
        # Send summary
        self._send_summary_notification(analyses)
    
    def _send_summary_notification(self, analyses: List[tuple]):
        """
        Send summary notification with all recommendations
        
        Args:
            analyses: List of (holding, analysis) tuples
        """
        if not self.telegram or not self.telegram.enabled:
            return
        
        total_value = sum(h['value_usd'] for h, a in analyses)
        sell_count = sum(1 for h, a in analyses if a['recommendation'] == 'SELL')
        hold_count = sum(1 for h, a in analyses if a['recommendation'] == 'HOLD')
        consider_count = sum(1 for h, a in analyses if a['recommendation'] == 'CONSIDER_SELL')
        
        try:
            message = (
                "📊 <b>AI PORTFOLIO ANALYSIS SUMMARY</b>\n\n"
                f"💰 Total Portfolio Value: <b>${total_value:.2f}</b>\n"
                f"🪙 Assets Analyzed: {len(analyses)}\n\n"
                f"<b>Recommendations:</b>\n"
                f"🔴 SELL: {sell_count} assets\n"
                f"⚠️ Consider Selling: {consider_count} assets\n"
                f"🟢 HOLD: {hold_count} assets\n\n"
            )
            
            # List assets recommended to sell
            if sell_count > 0:
                message += "<b>💡 Recommended to SELL:</b>\n"
                for holding, analysis in analyses:
                    if analysis['recommendation'] == 'SELL':
                        message += f"  • {holding['symbol']}: ${holding['value_usd']:.2f}\n"
            
            message += f"\n⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
            
            self.telegram.send_message(message)
            logger.info("📱 Summary notification sent")
            
        except Exception as e:
            logger.warning(f"Failed to send summary: {e}")
    
    def run_continuous_monitoring(self, auto_sell: bool = False):
        """
        Continuously monitor and manage assets
        
        Args:
            auto_sell: If True, automatically sell when AI recommends
        """
        logger.info(f"{Fore.GREEN}🤖 Starting continuous asset monitoring...{Style.RESET_ALL}")
        logger.info(f"Check interval: {self.check_interval} seconds")
        logger.info(f"Auto-sell: {'ENABLED' if auto_sell else 'DISABLED'}")
        
        try:
            while True:
                self.analyze_and_manage_all_assets(auto_sell=auto_sell)
                
                logger.info(f"\n⏳ Waiting {self.check_interval} seconds until next check...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info(f"{Fore.YELLOW}⏸️  Asset manager stopped by user{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Error in continuous monitoring: {e}")


# Standalone execution
if __name__ == "__main__":
    from colorama import init
    init()
    
    print("\n" + "="*70)
    print(f"{Fore.CYAN}🤖 AI ASSET MANAGER - Manage Your OKX Holdings{Style.RESET_ALL}")
    print("="*70 + "\n")
    
    # Initialize exchange
    exchange = ccxt.okx({
        'apiKey': config.OKX_API_KEY,
        'secret': config.OKX_SECRET_KEY,
        'password': config.OKX_PASSPHRASE,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    # Initialize asset manager
    manager = AIAssetManager(exchange)
    
    print("Options:")
    print("1. Analyze all holdings (recommendations only)")
    print("2. Analyze + Auto-sell when AI recommends")
    print("3. Continuous monitoring (recommendations only)")
    print("4. Continuous monitoring + Auto-sell")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        manager.analyze_and_manage_all_assets(auto_sell=False)
    elif choice == '2':
        confirm = input("⚠️  This will AUTO-SELL assets! Confirm? (yes/no): ")
        if confirm.lower() == 'yes':
            manager.analyze_and_manage_all_assets(auto_sell=True)
    elif choice == '3':
        manager.run_continuous_monitoring(auto_sell=False)
    elif choice == '4':
        confirm = input("⚠️  This will AUTO-SELL assets continuously! Confirm? (yes/no): ")
        if confirm.lower() == 'yes':
            manager.run_continuous_monitoring(auto_sell=True)
    else:
        print("Invalid choice")
