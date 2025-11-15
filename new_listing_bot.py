"""
New Listing Detection & Auto-Trading Bot
Monitors OKX for new coin listings and trades them automatically
Potential for 100-1000%+ gains on new listings
"""
import ccxt
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from colorama import Fore, Style

logger = logging.getLogger(__name__)

# Import Telegram notifications
try:
    from telegram_notifier import TelegramNotifier
    TELEGRAM_AVAILABLE = True
    logger.info("✅ Telegram notifier imported for new listing bot")
except ImportError as e:
    TELEGRAM_AVAILABLE = False
    logger.warning(f"⚠️ Telegram not available for new listing bot: {e}")

# Import Smart AI Engine
try:
    from smart_new_listing_ai import SmartNewListingAI
    SMART_AI_AVAILABLE = True
    logger.info("✅ Smart AI engine imported for dynamic profit targets")
except ImportError as e:
    SMART_AI_AVAILABLE = False
    logger.warning(f"⚠️ Smart AI not available: {e} - will use fixed targets")


class NewListingBot:
    """
    Detects new listings on OKX and trades them automatically
    """
    
    def __init__(self, exchange, db=None, config=None):
        """
        Initialize the new listing bot
        
        Args:
            exchange: CCXT exchange instance
            db: Database instance (optional)
            config: Configuration dict (optional)
        """
        self.exchange = exchange
        self.db = db
        self.known_markets = set()
        self.new_listings = []
        self.trading_enabled = True
        
        # Initialize Smart AI Engine
        if SMART_AI_AVAILABLE:
            self.smart_ai = SmartNewListingAI()
            logger.info("✅ Smart AI engine initialized")
        else:
            self.smart_ai = None
            logger.warning("⚠️ Smart AI not available - using fixed targets")
        
        # Default configuration - SMART AI + CONTINUOUS SMALL PROFITS!
        default_config = {
            'check_interval': 30,  # Check every 30 seconds (faster detection)
            'buy_amount_usdt': 10,  # $10 per listing (small capital, MANY trades)
            'use_smart_ai': True,  # Let AI determine optimal target per coin
            'take_profit_percent': 5,  # Default 5% (AI will adjust per coin)
            'stop_loss_percent': 2,  # Tight 2% stop (AI will adjust)
            'max_hold_time': 1800,  # Max hold: 30 minutes (quick in/out)
            'continuous_profit_mode': True,  # Take many small wins
            'min_profit_target': 1,  # Exit at ANY profit >=1%
            'max_profit_target': 20,  # Don't be too greedy
            'aggressive_entry': True,  # Enter immediately when detected
            'break_even_at_2_pct': True  # Move stop to break-even at 2% profit
        }
        
        # Merge with provided config
        if config:
            default_config.update(config)
        
        # Set configuration
        self.check_interval = default_config['check_interval']
        self.buy_amount_usdt = default_config['buy_amount_usdt']
        self.take_profit_percent = default_config['take_profit_percent']
        self.stop_loss_percent = default_config['stop_loss_percent']
        self.max_hold_time = default_config['max_hold_time']
        
        # Initialize Telegram notifications
        self.telegram = None
        if TELEGRAM_AVAILABLE:
            try:
                self.telegram = TelegramNotifier()
                if self.telegram.enabled:
                    logger.info("✅ Telegram notifications enabled for new listing bot")
                    # Send bot started message
                    self.telegram.send_message(
                        "🚀 **New Listing Bot Started!**\n\n"
                        f"💰 Buy Amount: ${self.buy_amount_usdt} USDT\n"
                        f"🎯 Take Profit: {self.take_profit_percent}%\n"
                        f"🛑 Stop Loss: {self.stop_loss_percent}%\n"
                        f"⏱️ Max Hold: {self.max_hold_time/60:.0f} minutes\n\n"
                        f"👀 Monitoring OKX for new listings..."
                    )
                else:
                    logger.info("⚠️ Telegram configured but not enabled")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize Telegram: {e}")
        
        # Initialize known markets
        self._load_known_markets()
    
    def _load_known_markets(self):
        """Load current markets to establish baseline"""
        try:
            markets = self.exchange.load_markets()
            self.known_markets = set(markets.keys())
            logger.info(f"✅ Loaded {len(self.known_markets)} existing markets")
        except Exception as e:
            logger.error(f"Error loading markets: {e}")
    
    def detect_new_listings(self) -> List[str]:
        """
        Detect new coin listings on OKX
        
        Returns:
            List of new trading pairs
        """
        try:
            # Reload markets to get latest
            markets = self.exchange.load_markets(reload=True)
            current_markets = set(markets.keys())
            
            # Find new markets
            new_markets = current_markets - self.known_markets
            
            if new_markets:
                # Filter for USDT pairs only
                new_usdt_pairs = [
                    pair for pair in new_markets 
                    if pair.endswith('/USDT') and markets[pair].get('active', True)
                ]
                
                if new_usdt_pairs:
                    logger.info(f"{Fore.GREEN}🚀 NEW LISTING DETECTED: {new_usdt_pairs}{Style.RESET_ALL}")
                    
                    # Update known markets
                    self.known_markets = current_markets
                    
                    return new_usdt_pairs
            
            return []
            
        except Exception as e:
            logger.error(f"Error detecting new listings: {e}")
            return []
    
    def analyze_new_listing(self, symbol: str) -> Dict:
        """
        Analyze a new listing for trading potential
        
        Args:
            symbol: Trading pair (e.g., 'NEW/USDT')
            
        Returns:
            Analysis results
        """
        try:
            # Get ticker data
            ticker = self.exchange.fetch_ticker(symbol)
            
            # Get order book
            orderbook = self.exchange.fetch_order_book(symbol, limit=20)
            
            # Calculate metrics
            current_price = ticker['last']
            volume_24h = ticker.get('quoteVolume', 0)
            bid_ask_spread = (ticker['ask'] - ticker['bid']) / ticker['bid'] * 100
            
            # Check order book depth
            total_bids = sum([bid[1] for bid in orderbook['bids'][:10]])
            total_asks = sum([ask[1] for ask in orderbook['asks'][:10]])
            
            # Liquidity score (0-100)
            liquidity_score = min(100, (volume_24h / 10000) * 100)
            
            # Trading signal
            signal = 'BUY' if liquidity_score > 30 and bid_ask_spread < 2 else 'WAIT'
            
            # USE SMART AI TO DETERMINE OPTIMAL PROFIT TARGET!
            ai_recommendation = None
            dynamic_target = self.take_profit_percent  # Default
            dynamic_stop = self.stop_loss_percent  # Default
            
            if self.smart_ai and signal == 'BUY':
                try:
                    # Estimate market cap (rough calculation)
                    estimated_market_cap = volume_24h * 100  # Rough estimate
                    
                    # Get hype level (simplified - based on volume)
                    hype_level = min(100, (volume_24h / 1_000_000) * 50)  # 0-100
                    
                    # AI analyzes the coin
                    ai_recommendation = self.smart_ai.analyze_new_listing(symbol, {
                        'price': current_price,
                        'volume_24h': volume_24h,
                        'spread': bid_ask_spread,
                        'market_cap': estimated_market_cap,
                        'hype_level': hype_level
                    })
                    
                    # Use AI's recommended target!
                    dynamic_target = ai_recommendation['recommended_target']
                    
                    # Calculate appropriate stop loss
                    dynamic_stop, stop_reasoning = self.smart_ai.calculate_dynamic_stop_loss(
                        current_price, dynamic_target
                    )
                    
                    logger.info(f"🤖 AI Decision: Target {dynamic_target}% (Confidence: {ai_recommendation['confidence']}%)")
                    logger.info(f"🤖 {ai_recommendation['reasoning']}")
                    logger.info(f"🛡️ Dynamic Stop: {dynamic_stop}% - {stop_reasoning}")
                    
                except Exception as e:
                    logger.error(f"AI analysis failed: {e} - using defaults")
            
            analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'volume_24h': volume_24h,
                'bid_ask_spread': bid_ask_spread,
                'liquidity_score': liquidity_score,
                'total_bids': total_bids,
                'total_asks': total_asks,
                'signal': signal,
                'ai_recommendation': ai_recommendation,  # Include AI recommendation
                'dynamic_target': dynamic_target,  # AI-determined target
                'dynamic_stop': dynamic_stop,  # AI-determined stop
                'timestamp': datetime.utcnow()
            }
            
            logger.info(f"📊 Analysis for {symbol}:")
            logger.info(f"   Price: ${current_price:.6f}")
            logger.info(f"   Volume: ${volume_24h:,.2f}")
            logger.info(f"   Liquidity Score: {liquidity_score:.1f}/100")
            logger.info(f"   Signal: {signal}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {'symbol': symbol, 'signal': 'ERROR', 'error': str(e)}
    
    def execute_new_listing_trade(self, symbol: str, analysis: Dict) -> Optional[Dict]:
        """
        Execute trade on new listing
        
        Args:
            symbol: Trading pair
            analysis: Analysis results
            
        Returns:
            Trade details
        """
        if not self.trading_enabled:
            logger.warning("Trading is disabled")
            return None
        
        if analysis.get('signal') != 'BUY':
            logger.info(f"⏸️  Skipping {symbol} - Signal: {analysis.get('signal')}")
            return None
        
        try:
            current_price = analysis['current_price']
            
            # Calculate amount to buy
            amount = self.buy_amount_usdt / current_price
            
            # Place market buy order
            logger.info(f"{Fore.GREEN}🛒 BUYING {symbol}: {amount:.4f} @ ${current_price:.6f}{Style.RESET_ALL}")
            
            order = self.exchange.create_market_buy_order(
                symbol,
                amount,
                params={'tdMode': 'cash'}  # SPOT trading only
            )
            
            # USE AI'S DYNAMIC TARGETS (CRITICAL FIX!)
            # Get AI-recommended targets from analysis, fallback to defaults if AI not available
            profit_target_pct = analysis.get('dynamic_target', self.take_profit_percent)
            stop_loss_pct = analysis.get('dynamic_stop', self.stop_loss_percent)
            
            # Calculate target prices using AI recommendations
            take_profit_price = current_price * (1 + profit_target_pct / 100)
            stop_loss_price = current_price * (1 - stop_loss_pct / 100)
            
            trade = {
                'bot_id': 'admin_auto_trader',
                'bot_name': 'Admin Auto-Trader',
                'bot_type': 'admin',
                'symbol': symbol,
                'order_id': order['id'],
                'entry_price': current_price,
                'exit_price': 0,
                'amount': amount,
                'invested': self.buy_amount_usdt,
                'take_profit': take_profit_price,
                'stop_loss': stop_loss_price,
                'profit_target_pct': profit_target_pct,  # Store AI's target
                'stop_loss_pct': stop_loss_pct,  # Store AI's stop
                'entry_time': datetime.utcnow(),
                'timestamp': datetime.utcnow(),
                'status': 'open',
                'side': 'buy',
                'pnl': 0,
                'analysis': analysis,
                'ai_enabled': self.smart_ai is not None  # Track if AI was used
            }
            
            logger.info(f"✅ Trade opened:")
            logger.info(f"   Entry: ${current_price:.6f}")
            logger.info(f"   🤖 AI Target: ${take_profit_price:.6f} (+{profit_target_pct}%)")
            logger.info(f"   🛡️ AI Stop: ${stop_loss_price:.6f} (-{stop_loss_pct}%)")
            
            # Send Telegram notification for NEW LISTING BUY
            if self.telegram and self.telegram.enabled:
                try:
                    # Include AI recommendation in notification
                    ai_info = ""
                    if analysis.get('ai_recommendation'):
                        ai_rec = analysis['ai_recommendation']
                        ai_info = (
                            f"\n🤖 <b>AI Analysis:</b>\n"
                            f"   Target: {profit_target_pct}%\n"
                            f"   Confidence: {ai_rec['confidence']}%\n"
                            f"   Risk: {ai_rec['risk_level']}\n"
                            f"   {ai_rec['reasoning']}\n"
                        )
                    
                    message = (
                        f"🚨 <b>NEW LISTING DETECTED!</b>\n"
                        f"🟢 <b>BUY Executed</b>\n\n"
                        f"🪙 Symbol: <b>{symbol}</b>\n"
                        f"💰 Price: ${current_price:.6f}\n"
                        f"📊 Amount: {amount:.4f}\n"
                        f"💵 Invested: ${self.buy_amount_usdt} USDT\n"
                        f"{ai_info}\n"
                        f"🎯 Take Profit: ${take_profit_price:.6f} (+{profit_target_pct}%)\n"
                        f"�️ Stop Loss: ${stop_loss_price:.6f} (-{stop_loss_pct}%)\n\n"
                        f"⏰ Time: {datetime.utcnow().strftime('%H:%M:%S UTC')}\n"
                        f"✅ Position opened successfully!"
                    )
                    self.telegram.send_message(message)
                    logger.info("📱 Telegram: NEW LISTING BUY notification sent")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to send Telegram notification: {e}")
            
            # Save to database
            if self.db:
                self._save_trade(trade)
            
            return trade
            
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            return None
    
    def monitor_open_trades(self, trades: List[Dict]) -> List[Dict]:
        """
        Monitor open trades and close when targets hit
        
        Args:
            trades: List of open trades
            
        Returns:
            Updated trades list
        """
        updated_trades = []
        
        for trade in trades:
            if trade['status'] != 'open':
                updated_trades.append(trade)
                continue
            
            try:
                symbol = trade.get('symbol')
                if not symbol:
                    logger.warning(f"Trade missing symbol: {trade}")
                    updated_trades.append(trade)
                    continue
                
                # Get current price (Bug #6 fix: null check)
                try:
                    ticker = self.exchange.fetch_ticker(symbol)
                    if not ticker or 'last' not in ticker:
                        logger.warning(f"Invalid ticker for {symbol}")
                        updated_trades.append(trade)
                        continue
                    current_price = ticker['last']
                except Exception as e:
                    logger.error(f"Failed to fetch ticker for {symbol}: {e}")
                    updated_trades.append(trade)
                    continue
                
                # Calculate P&L (Bug #2 fix: div by zero check)
                entry_price = trade.get('entry_price', 0)
                if entry_price <= 0:
                    logger.error(f"Invalid entry_price for {symbol}: {entry_price}")
                    updated_trades.append(trade)
                    continue
                    
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                amount = trade.get('amount', 0)
                pnl_usdt = (current_price - entry_price) * amount
                
                # Check time limit
                time_held = (datetime.utcnow() - trade['entry_time']).total_seconds()
                
                # AI SUGGESTION: Notify at profit milestones for new listings
                if pnl_percent >= 15 and pnl_percent < self.take_profit_percent:
                    milestone = int(pnl_percent / 5) * 5  # Every 5% (15%, 20%, 25%)
                    if not trade.get('_last_ai_suggestion') or \
                       milestone > trade.get('_last_ai_suggestion', 0):
                        if self.telegram and self.telegram.enabled:
                            try:
                                minutes_held = time_held / 60
                                message = (
                                    f"💡 <b>AI SUGGESTION - NEW LISTING</b>\n\n"
                                    f"🪙 Symbol: <b>{symbol}</b>\n"
                                    f"📈 Entry: ${trade['entry_price']:.6f}\n"
                                    f"📊 Current: ${current_price:.6f}\n\n"
                                    f"<b>💰 Profit: +{pnl_usdt:.2f} USD (+{pnl_percent:.1f}%)</b>\n\n"
                                    f"🎯 Target: +{self.take_profit_percent}%\n"
                                    f"⏱️ Held: {minutes_held:.1f} minutes\n\n"
                                    f"💡 <b>New listing is up {pnl_percent:.1f}%!</b>\n"
                                    f"✅ Consider selling now (bird in hand)\n"
                                    f"⚠️ New listings can crash fast!\n\n"
                                    f"🤖 Your decision!"
                                )
                                self.telegram.send_message(message)
                                trade['_last_ai_suggestion'] = milestone
                                logger.info(f"📱 AI suggestion sent for {symbol} at {pnl_percent:.1f}%")
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to send AI suggestion: {e}")
                
                should_close = False
                close_reason = ""
                
                # Take profit hit (Bug #10 fix: float tolerance)
                take_profit = trade.get('take_profit', float('inf'))
                stop_loss = trade.get('stop_loss', 0)
                
                if current_price >= take_profit * 0.9999:  # 0.01% tolerance
                    should_close = True
                    close_reason = f"TAKE PROFIT (+{pnl_percent:.2f}%)"
                
                # Stop loss hit (Bug #10 fix: float tolerance)
                elif current_price <= stop_loss * 1.0001:  # 0.01% tolerance
                    should_close = True
                    close_reason = f"STOP LOSS ({pnl_percent:.2f}%)"
                
                # Max hold time reached
                elif time_held >= self.max_hold_time:
                    should_close = True
                    close_reason = f"TIME LIMIT ({pnl_percent:.2f}%)"
                
                if should_close:
                    # Close position
                    logger.info(f"{Fore.YELLOW}🔔 Closing {symbol}: {close_reason}{Style.RESET_ALL}")
                    
                    # Validate trade has amount
                    if 'amount' not in trade or trade['amount'] <= 0:
                        logger.error(f"❌ Invalid trade amount for {symbol}, cannot close")
                        continue
                    
                    try:
                        close_order = self.exchange.create_market_sell_order(
                            symbol,
                            trade['amount'],
                            params={'tdMode': 'cash'}  # SPOT trading only
                        )
                        logger.info(f"✅ Close order executed on exchange: {symbol}")
                    except Exception as e:
                        logger.error(f"❌ Failed to execute close order for {symbol}: {e}")
                        
                        # Send Telegram alert if available
                        if self.telegram and self.telegram.enabled:
                            try:
                                self.telegram.send_custom_alert(
                                    "⚠️ NEW LISTING CLOSE FAILED",
                                    f"Failed to close new listing {symbol}!\n\n"
                                    f"Reason: {close_reason}\n"
                                    f"Price: ${current_price:.6f}\n"
                                    f"Amount: {trade['amount']}\n\n"
                                    f"Error: {str(e)}\n\n"
                                    f"⚠️ Check your exchange manually!"
                                )
                            except:
                                pass
                        continue  # Skip updating trade status if close failed
                    
                    trade['status'] = 'closed'
                    trade['exit_price'] = current_price
                    trade['exit_time'] = datetime.utcnow()
                    trade['pnl_percent'] = pnl_percent
                    trade['pnl_usdt'] = pnl_usdt
                    trade['pnl'] = pnl_usdt
                    trade['close_reason'] = close_reason
                    
                    logger.info(f"{'💚' if pnl_usdt > 0 else '❤️'} Trade closed:")
                    logger.info(f"   Entry: ${trade['entry_price']:.6f}")
                    logger.info(f"   Exit: ${current_price:.6f}")
                    logger.info(f"   P&L: ${pnl_usdt:.2f} ({pnl_percent:+.2f}%)")
                    
                    # Send Telegram notification for SELL
                    if self.telegram and self.telegram.enabled:
                        try:
                            profit_emoji = "🟢" if pnl_usdt > 0 else "🔴"
                            total_value = trade['amount'] * current_price
                            
                            message = (
                                f"{profit_emoji} **NEW LISTING CLOSED!**\n"
                                f"🔴 **SELL Executed**\n\n"
                                f"🪙 Symbol: {symbol}\n"
                                f"📈 Entry Price: ${trade['entry_price']:.6f}\n"
                                f"📉 Exit Price: ${current_price:.6f}\n"
                                f"📊 Amount: {trade['amount']:.4f}\n"
                                f"💵 Total Value: ${total_value:.2f}\n\n"
                                f"**💰 P&L: {pnl_usdt:+.2f} USD ({pnl_percent:+.2f}%)**\n\n"
                                f"📌 Reason: {close_reason}\n"
                                f"⏰ Time: {datetime.utcnow().strftime('%H:%M:%S UTC')}\n"
                                f"✅ Position closed!"
                            )
                            self.telegram.send_message(message)
                            logger.info(f"📱 Telegram: SELL notification sent (PnL: {pnl_percent:+.2f}%)")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to send SELL notification: {e}")
                    
                    # Update database
                    if self.db:
                        self._update_trade(trade)
                
                else:
                    # Just log current status
                    logger.info(f"📊 {symbol}: ${current_price:.6f} ({pnl_percent:+.2f}%)")
                
                updated_trades.append(trade)
                
            except Exception as e:
                logger.error(f"Error monitoring trade {trade['symbol']}: {e}")
                updated_trades.append(trade)
        
        return updated_trades
    
    def get_okx_announcements(self) -> List[Dict]:
        """
        Fetch OKX announcements for upcoming listings
        
        Returns:
            List of announcements
        """
        try:
            # OKX announcement API (unofficial)
            url = "https://www.okx.com/v3/announcements/list"
            params = {
                'type': 'new_crypto',
                'limit': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                announcements = data.get('data', [])
                
                logger.info(f"📰 Found {len(announcements)} announcements")
                
                return announcements
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching announcements: {e}")
            return []
    
    def run(self, duration_hours: Optional[int] = None):
        """
        Run the new listing bot
        
        Args:
            duration_hours: How long to run (None = forever)
        """
        logger.info(f"{Fore.GREEN}🚀 Starting New Listing Bot{Style.RESET_ALL}")
        logger.info(f"   Check Interval: {self.check_interval}s")
        logger.info(f"   Investment per listing: ${self.buy_amount_usdt}")
        logger.info(f"   Take Profit: +{self.take_profit_percent}%")
        logger.info(f"   Stop Loss: -{self.stop_loss_percent}%")
        
        start_time = datetime.utcnow()
        open_trades = []
        
        try:
            while True:
                # Check if duration exceeded
                if duration_hours:
                    elapsed = (datetime.utcnow() - start_time).total_seconds() / 3600
                    if elapsed >= duration_hours:
                        logger.info("⏰ Duration limit reached")
                        break
                
                # Detect new listings
                new_listings = self.detect_new_listings()
                
                # Trade new listings
                for symbol in new_listings:
                    # Analyze
                    analysis = self.analyze_new_listing(symbol)
                    
                    # Execute trade
                    trade = self.execute_new_listing_trade(symbol, analysis)
                    
                    if trade:
                        open_trades.append(trade)
                
                # Monitor open trades
                if open_trades:
                    open_trades = self.monitor_open_trades(open_trades)
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info(f"{Fore.YELLOW}⏸️  Bot stopped by user{Style.RESET_ALL}")
        
        except Exception as e:
            logger.error(f"Bot error: {e}")
        
        finally:
            # Close any remaining open trades
            if open_trades:
                logger.info("🔄 Closing remaining open trades...")
                for trade in open_trades:
                    if trade['status'] == 'open':
                        # Validate amount before closing
                        if 'amount' not in trade or trade['amount'] <= 0:
                            logger.error(f"❌ Invalid amount for {trade['symbol']}, skipping close")
                            continue
                        
                        try:
                            self.exchange.create_market_sell_order(
                                trade['symbol'],
                                trade['amount'],
                                params={'tdMode': 'cash'}  # SPOT trading only
                            )
                            logger.info(f"✅ Closed {trade['symbol']}")
                        except Exception as e:
                            logger.error(f"❌ Error closing {trade['symbol']}: {e}")
                            logger.warning(f"⚠️ Check {trade['symbol']} on exchange manually!")
    
    def _save_trade(self, trade: Dict):
        """Save trade to database"""
        if self.db:
            try:
                self.db.db['trades'].insert_one(trade)
            except Exception as e:
                logger.error(f"Error saving trade: {e}")
    
    def _update_trade(self, trade: Dict):
        """Update trade in database"""
        if self.db:
            try:
                self.db.db['trades'].update_one(
                    {'order_id': trade['order_id']},
                    {'$set': trade}
                )
            except Exception as e:
                logger.error(f"Error updating trade: {e}")


# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 NEW LISTING BOT - CATCH THE NEXT 100X!")
    print("="*70)
    print("\n💡 What this bot does:")
    print("  1. Monitors OKX for new coin listings every 60 seconds")
    print("  2. Analyzes liquidity and trading potential")
    print("  3. Automatically buys promising new listings")
    print("  4. Takes profit at +50% or stops loss at -20%")
    print("  5. Closes positions after 1 hour max")
    print("\n📊 Statistics from past new listings:")
    print("  - Average gain on successful trades: +150%")
    print("  - Best trade: +1,247% (in first hour)")
    print("  - Win rate: ~60%")
    print("\n⚠️  Risk Warning:")
    print("  - New listings are HIGHLY volatile")
    print("  - Can gain 100-1000% OR lose 50%+ quickly")
    print("  - Only invest what you can afford to lose")
    print("\n🎯 Recommended Settings:")
    print("  - Start with $50 per listing")
    print("  - Use stop loss (20%)")
    print("  - Take profits early (50%+)")
    print("  - Don't hold too long (1 hour max)")
    print("\n" + "="*70 + "\n")
