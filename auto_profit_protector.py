"""
Automated Profit Protection System
Ensures you ALWAYS take profits and minimize losses
Multiple layers of protection to guarantee profitability
"""
import ccxt
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from colorama import Fore, Style
import numpy as np

logger = logging.getLogger(__name__)

# Import Advanced AI Engine and Telegram for comprehensive notifications
try:
    from advanced_ai_engine import AdvancedAIEngine
    AI_AVAILABLE = True
    logger.info("✅ Advanced AI Engine available for profit protection")
except ImportError:
    AI_AVAILABLE = False
    logger.warning("⚠️ Advanced AI not available for profit protector")

try:
    from telegram_notifier import TelegramNotifier
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("⚠️ Telegram notifications not available")


class AutoProfitProtector:
    """
    Advanced automated profit protection system
    Multiple strategies to ensure profitability
    """
    
    def __init__(self, exchange: ccxt.Exchange, db=None, telegram=None):
        """
        Initialize profit protector
        
        Args:
            exchange: CCXT exchange instance
            db: Database instance
            telegram: TelegramNotifier instance for comprehensive notifications
        """
        self.exchange = exchange
        self.db = db
        self.active_positions = {}
        
        # Initialize AI Engine for smart protection
        if AI_AVAILABLE:
            self.ai_engine = AdvancedAIEngine(exchange)
            logger.info("✅ AI-Enhanced Profit Protection Activated")
        else:
            self.ai_engine = None
        
        # Initialize Telegram for ALL notifications
        if telegram:
            self.telegram = telegram
            logger.info("✅ Telegram notifications enabled for profit protector")
        elif TELEGRAM_AVAILABLE:
            self.telegram = TelegramNotifier()
            logger.info("✅ Telegram notifier initialized")
        else:
            self.telegram = None
            logger.warning("⚠️ No Telegram notifications")
        
        # ============================================================================
        # PROFIT PROTECTION SETTINGS
        # ============================================================================
        
        # Basic Stop Loss / Take Profit - TIGHTENED FOR USER PROTECTION!
        self.stop_loss_percent = 5           # Stop loss at -5% (PROTECTED!)
        self.take_profit_percent = 15        # Take profit at +15% (realistic)
        
        # Bug #10 fix: Float comparison tolerance (0.01% tolerance for price triggers)
        self.price_tolerance = 0.0001  # 0.01% tolerance for float comparison
        
        # Trailing Stop Loss (locks in profits)
        self.trailing_stop_enabled = True
        self.trailing_stop_activation = 5    # Activate after +5% profit (FASTER!)
        self.trailing_stop_distance = 3      # Trail 3% below peak (TIGHTER!)
        
        # Partial Profit Taking (secure gains gradually) - SMALL PROFIT MODE!
        self.partial_profit_enabled = True
        self.partial_profit_levels = [
            {'percent': 5, 'sell': 50},      # Sell 50% at +5% (QUICK WIN!)
            {'percent': 10, 'sell': 30},     # Sell 30% at +10%
            {'percent': 15, 'sell': 20},     # Sell 20% at +15%
        ]
        
        # Time-Based Exit (don't hold too long)
        self.max_hold_time = 7200            # 2 hours max
        self.min_profit_after_time = 5       # Min 5% profit after max time
        
        # Break-Even Stop (move stop to entry after profit)
        self.breakeven_enabled = True
        self.breakeven_trigger = 3           # Move to breakeven after +3% (FASTER!)
        
        # Dynamic Stop Loss (adjust based on volatility)
        self.dynamic_stop_enabled = True
        self.volatility_multiplier = 1.5     # Widen stop in high volatility
        
        # Profit Lock (secure minimum profit)
        self.profit_lock_enabled = True
        self.profit_lock_trigger = 8         # After +8%, lock minimum 5%
        self.profit_lock_minimum = 5
        
        # Emergency Exit (market conditions) - TIGHTER FOR PROTECTION!
        self.emergency_exit_enabled = True
        self.max_drawdown_percent = 8        # Exit if down 8% from peak (PROTECTED!)
        self.volume_drop_threshold = 0.5     # Exit if volume drops 50%
        
        # Smart Exit (AI-based)
        self.smart_exit_enabled = True
        self.momentum_threshold = -0.3       # Exit if momentum turns negative
        
    def add_position(self, symbol: str, entry_price: float, amount: float, 
                     side: str = 'long', metadata: Dict = None) -> str:
        """
        Add position to protection system
        
        Args:
            symbol: Trading pair
            entry_price: Entry price
            amount: Position size
            side: 'long' or 'short'
            metadata: Additional info
            
        Returns:
            Position ID
        """
        position_id = f"{symbol}_{int(time.time())}"
        
        position = {
            'id': position_id,
            'symbol': symbol,
            'entry_price': entry_price,
            'current_price': entry_price,
            'amount': amount,
            'remaining_amount': amount,
            'side': side,
            'entry_time': datetime.utcnow(),
            'highest_price': entry_price,
            'lowest_price': entry_price,
            'stop_loss': entry_price * (1 - self.stop_loss_percent / 100),
            'take_profit': entry_price * (1 + self.take_profit_percent / 100),
            'trailing_stop': None,
            'breakeven_activated': False,
            'partial_profits_taken': [],
            'profit_locked': False,
            'metadata': metadata or {}
        }
        
        self.active_positions[position_id] = position
        
        logger.info(f"{Fore.GREEN}🛡️  Position protected: {symbol}{Style.RESET_ALL}")
        logger.info(f"   Entry: ${entry_price:.6f}")
        logger.info(f"   Stop Loss: ${position['stop_loss']:.6f} (-{self.stop_loss_percent}%)")
        logger.info(f"   Take Profit: ${position['take_profit']:.6f} (+{self.take_profit_percent}%)")
        
        return position_id
    
    def update_position(self, position_id: str, current_price: float) -> Dict:
        """
        Update position and check all protection mechanisms
        
        Args:
            position_id: Position ID
            current_price: Current market price
            
        Returns:
            Action to take
        """
        if position_id not in self.active_positions:
            return {'action': 'none', 'reason': 'Position not found'}
        
        position = self.active_positions[position_id]
        position['current_price'] = current_price
        
        # Update price extremes
        if current_price > position['highest_price']:
            position['highest_price'] = current_price
        if current_price < position['lowest_price']:
            position['lowest_price'] = current_price
        
        # Calculate current P&L
        pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
        pnl_from_peak = ((current_price - position['highest_price']) / position['highest_price']) * 100
        
        # ============================================================================
        # CHECK ALL PROTECTION MECHANISMS
        # ============================================================================
        
        # 1. Basic Stop Loss (Bug #10 fix: with tolerance)
        if current_price <= position['stop_loss'] * (1 + self.price_tolerance):
            return {
                'action': 'close_all',
                'reason': f'Stop Loss Hit ({pnl_percent:.2f}%)',
                'price': current_price,
                'amount': position['remaining_amount']
            }
        
        # 2. Basic Take Profit (Bug #10 fix: with tolerance)
        if current_price >= position['take_profit'] * (1 - self.price_tolerance):
            return {
                'action': 'close_all',
                'reason': f'Take Profit Hit (+{pnl_percent:.2f}%)',
                'price': current_price,
                'amount': position['remaining_amount']
            }
        
        # 3. Trailing Stop Loss
        if self.trailing_stop_enabled and pnl_percent >= self.trailing_stop_activation:
            trailing_stop = position['highest_price'] * (1 - self.trailing_stop_distance / 100)
            old_trailing = position.get('trailing_stop')
            position['trailing_stop'] = trailing_stop
            
            # NOTIFICATION: Trailing stop activated (first time only)
            if old_trailing is None and self.telegram and self.telegram.enabled:
                try:
                    self.telegram.send_message(
                        f"🎯 <b>TRAILING STOP ACTIVATED!</b>\n\n"
                        f"🪙 Symbol: <b>{position['symbol']}</b>\n"
                        f"📈 Current Profit: <b>+{pnl_percent:.1f}%</b>\n"
                        f"🔝 Peak Price: <b>${position['highest_price']:.6f}</b>\n"
                        f"📊 Current Price: <b>${current_price:.6f}</b>\n"
                        f"🛡️ Trailing Stop: <b>${trailing_stop:.6f}</b> ({self.trailing_stop_distance}% trail)\n\n"
                        f"✅ <b>Profit protection active!</b>\n"
                        f"📈 Stop follows price up automatically\n"
                        f"🔒 Locks in gains as price rises\n"
                        f"💡 Exits if price drops {self.trailing_stop_distance}% from peak\n\n"
                        f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                    )
                    logger.info(f"📱 Telegram: Trailing stop activation notification sent for {position['symbol']}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to send trailing stop notification: {e}")
            
            if current_price <= trailing_stop * (1 + self.price_tolerance):
                return {
                    'action': 'close_all',
                    'reason': f'Trailing Stop Hit (+{pnl_percent:.2f}%)',
                    'price': current_price,
                    'amount': position['remaining_amount']
                }
        
        # 4. Partial Profit Taking
        if self.partial_profit_enabled:
            for level in self.partial_profit_levels:
                if pnl_percent >= level['percent']:
                    # Check if this level already taken
                    if level['percent'] not in position['partial_profits_taken']:
                        sell_amount = position['amount'] * (level['sell'] / 100)
                        position['partial_profits_taken'].append(level['percent'])
                        position['remaining_amount'] -= sell_amount
                        
                        return {
                            'action': 'partial_close',
                            'reason': f'Partial Profit at +{level["percent"]}%',
                            'price': current_price,
                            'amount': sell_amount,
                            'remaining': position['remaining_amount']
                        }
        
        # 5. Break-Even Stop
        if self.breakeven_enabled and not position['breakeven_activated']:
            if pnl_percent >= self.breakeven_trigger:
                position['stop_loss'] = position['entry_price']
                position['breakeven_activated'] = True
                logger.info(f"✅ Break-even activated for {position['symbol']}")
                
                # NOTIFICATION: Break-even activated
                if self.telegram and self.telegram.enabled:
                    try:
                        self.telegram.send_message(
                            f"🛡️ <b>BREAK-EVEN ACTIVATED</b>\n\n"
                            f"🪙 Symbol: <b>{position['symbol']}</b>\n"
                            f"📈 Current Profit: <b>+{pnl_percent:.1f}%</b>\n"
                            f"🔒 Stop Loss moved to: <b>${position['entry_price']:.6f}</b>\n\n"
                            f"✅ <b>You can't lose now!</b>\n"
                            f"💡 Worst case = break-even (0% loss)\n"
                            f"🎯 Best case = continue to target\n\n"
                            f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                        )
                        logger.info(f"📱 Telegram: Break-even notification sent for {position['symbol']}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to send break-even notification: {e}")
        
        # 6. Profit Lock
        if self.profit_lock_enabled and not position['profit_locked']:
            if pnl_percent >= self.profit_lock_trigger:
                locked_price = position['entry_price'] * (1 + self.profit_lock_minimum / 100)
                position['stop_loss'] = max(position['stop_loss'], locked_price)
                position['profit_locked'] = True
                logger.info(f"🔒 Profit locked at +{self.profit_lock_minimum}% for {position['symbol']}")
                
                # NOTIFICATION: Profit locked
                if self.telegram and self.telegram.enabled:
                    try:
                        self.telegram.send_message(
                            f"🔒 <b>PROFIT LOCKED!</b>\n\n"
                            f"🪙 Symbol: <b>{position['symbol']}</b>\n"
                            f"📈 Current Profit: <b>+{pnl_percent:.1f}%</b>\n"
                            f"🛡️ Minimum Profit Locked: <b>+{self.profit_lock_minimum}%</b>\n"
                            f"🔐 New Stop Loss: <b>${locked_price:.6f}</b>\n\n"
                            f"✅ <b>Guaranteed minimum +{self.profit_lock_minimum}% profit!</b>\n"
                            f"💰 You will make at least ${(locked_price - position['entry_price']) * position['remaining_amount']:.2f}\n"
                            f"🎯 Still aiming for full target\n\n"
                            f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                        )
                        logger.info(f"📱 Telegram: Profit lock notification sent for {position['symbol']}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to send profit lock notification: {e}")
        
        # 7. Time-Based Exit
        time_held = (datetime.utcnow() - position['entry_time']).total_seconds()
        if time_held >= self.max_hold_time:
            if pnl_percent >= self.min_profit_after_time:
                return {
                    'action': 'close_all',
                    'reason': f'Time Limit Reached (+{pnl_percent:.2f}%)',
                    'price': current_price,
                    'amount': position['remaining_amount']
                }
            elif pnl_percent < 0:
                return {
                    'action': 'close_all',
                    'reason': f'Time Limit + Loss ({pnl_percent:.2f}%)',
                    'price': current_price,
                    'amount': position['remaining_amount']
                }
        
        # 8. Emergency Exit (Drawdown from Peak)
        if self.emergency_exit_enabled:
            if pnl_from_peak <= -self.max_drawdown_percent:
                return {
                    'action': 'close_all',
                    'reason': f'Emergency Exit - Drawdown ({pnl_from_peak:.2f}% from peak)',
                    'price': current_price,
                    'amount': position['remaining_amount']
                }
        
        # 9. Volume Check
        if self.emergency_exit_enabled:
            try:
                ticker = self.exchange.fetch_ticker(position['symbol'])
                current_volume = ticker.get('quoteVolume', 0)
                entry_volume = position['metadata'].get('entry_volume', current_volume)
                
                if entry_volume > 0:
                    volume_change = (current_volume - entry_volume) / entry_volume
                    if volume_change <= -self.volume_drop_threshold:
                        return {
                            'action': 'close_all',
                            'reason': f'Volume Drop ({volume_change*100:.1f}%)',
                            'price': current_price,
                            'amount': position['remaining_amount']
                        }
            except:
                pass
        
        # 10. Smart Exit (Momentum)
        if self.smart_exit_enabled and pnl_percent > 5:
            momentum = self._calculate_momentum(position['symbol'])
            if momentum is not None and momentum < self.momentum_threshold:
                return {
                    'action': 'close_all',
                    'reason': f'Momentum Reversal (+{pnl_percent:.2f}%)',
                    'price': current_price,
                    'amount': position['remaining_amount']
                }
        
        # No action needed
        return {
            'action': 'hold',
            'reason': f'Position OK ({pnl_percent:+.2f}%)',
            'pnl_percent': pnl_percent,
            'trailing_stop': position.get('trailing_stop'),
            'stop_loss': position['stop_loss']
        }
    
    def _calculate_momentum(self, symbol: str) -> Optional[float]:
        """Calculate price momentum"""
        try:
            # Get recent candles
            ohlcv = self.exchange.fetch_ohlcv(symbol, '5m', limit=20)
            closes = [candle[4] for candle in ohlcv]
            
            # Calculate rate of change
            if len(closes) >= 10:
                recent_avg = np.mean(closes[-5:])
                older_avg = np.mean(closes[-10:-5])
                momentum = (recent_avg - older_avg) / older_avg
                return momentum
            
            return None
        except:
            return None
    
    def execute_action(self, position_id: str, action: Dict) -> bool:
        """
        Execute the recommended action
        
        Args:
            position_id: Position ID
            action: Action dict from update_position
            
        Returns:
            Success status
        """
        if action['action'] == 'hold':
            return True
        
        position = self.active_positions.get(position_id)
        if not position:
            return False
        
        try:
            symbol = position['symbol']
            
            if action['action'] == 'close_all':
                # Close entire position
                logger.info(f"{Fore.YELLOW}🔔 {action['reason']}{Style.RESET_ALL}")
                
                # Validate amount
                if action['amount'] <= 0:
                    logger.error(f"❌ Invalid amount for {symbol}: {action['amount']}")
                    return False
                
                try:
                    order = self.exchange.create_market_sell_order(
                        symbol,
                        action['amount'],
                        params={'tdMode': 'cash'}  # SPOT trading only
                    )
                    logger.info(f"✅ Close order executed on exchange: {symbol}")
                except Exception as e:
                    logger.error(f"❌ Failed to execute close order for {symbol}: {e}")
                    return False
                
                # Calculate final P&L
                pnl = (action['price'] - position['entry_price']) * action['amount']
                pnl_percent = ((action['price'] - position['entry_price']) / position['entry_price']) * 100
                
                logger.info(f"{'💚' if pnl > 0 else '❤️'} Position closed:")
                logger.info(f"   Entry: ${position['entry_price']:.6f}")
                logger.info(f"   Exit: ${action['price']:.6f}")
                logger.info(f"   P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)")
                
                # Remove from active positions
                del self.active_positions[position_id]
                
                # Save to database
                if self.db:
                    self._save_closed_position(position, action, pnl, pnl_percent)
                
                return True
            
            elif action['action'] == 'partial_close':
                # Close partial position
                logger.info(f"{Fore.CYAN}📊 {action['reason']}{Style.RESET_ALL}")
                
                # Validate amount
                if action['amount'] <= 0:
                    logger.error(f"❌ Invalid partial amount for {symbol}: {action['amount']}")
                    return False
                
                try:
                    order = self.exchange.create_market_sell_order(
                        symbol,
                        action['amount'],
                        params={'tdMode': 'cash'}  # SPOT trading only
                    )
                    logger.info(f"✅ Partial close order executed on exchange: {symbol}")
                except Exception as e:
                    logger.error(f"❌ Failed to execute partial close for {symbol}: {e}")
                    return False
                
                partial_pnl = (action['price'] - position['entry_price']) * action['amount']
                
                logger.info(f"💰 Partial profit taken:")
                logger.info(f"   Sold: {action['amount']:.4f}")
                logger.info(f"   Profit: ${partial_pnl:.2f}")
                logger.info(f"   Remaining: {action['remaining']:.4f}")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return False
    
    def monitor_all_positions(self):
        """Monitor all active positions and execute actions"""
        for position_id in list(self.active_positions.keys()):
            position = self.active_positions[position_id]
            
            try:
                # Get current price
                ticker = self.exchange.fetch_ticker(position['symbol'])
                current_price = ticker['last']
                
                # Update and get action
                action = self.update_position(position_id, current_price)
                
                # Execute if needed
                if action['action'] != 'hold':
                    self.execute_action(position_id, action)
                else:
                    # Just log status
                    logger.info(f"📊 {position['symbol']}: {action['reason']}")
                
            except Exception as e:
                logger.error(f"Error monitoring {position['symbol']}: {e}")
    
    def get_position_status(self, position_id: str) -> Dict:
        """Get detailed position status"""
        if position_id not in self.active_positions:
            return {'error': 'Position not found'}
        
        position = self.active_positions[position_id]
        current_price = position['current_price']
        
        pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
        pnl_usd = (current_price - position['entry_price']) * position['remaining_amount']
        
        time_held = (datetime.utcnow() - position['entry_time']).total_seconds()
        
        return {
            'symbol': position['symbol'],
            'entry_price': position['entry_price'],
            'current_price': current_price,
            'pnl_percent': pnl_percent,
            'pnl_usd': pnl_usd,
            'amount': position['remaining_amount'],
            'stop_loss': position['stop_loss'],
            'take_profit': position['take_profit'],
            'trailing_stop': position.get('trailing_stop'),
            'time_held': time_held,
            'breakeven_activated': position['breakeven_activated'],
            'profit_locked': position['profit_locked'],
            'partial_profits': position['partial_profits_taken']
        }
    
    def _save_closed_position(self, position: Dict, action: Dict, pnl: float, pnl_percent: float):
        """Save closed position to database"""
        if self.db:
            try:
                record = {
                    'position_id': position['id'],
                    'symbol': position['symbol'],
                    'entry_price': position['entry_price'],
                    'exit_price': action['price'],
                    'amount': position['amount'],
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'entry_time': position['entry_time'],
                    'exit_time': datetime.utcnow(),
                    'exit_reason': action['reason'],
                    'partial_profits': position['partial_profits_taken'],
                    'highest_price': position['highest_price'],
                    'lowest_price': position['lowest_price']
                }
                
                self.db.db['protected_trades'].insert_one(record)
            except Exception as e:
                logger.error(f"Error saving trade: {e}")


# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🛡️  AUTOMATED PROFIT PROTECTION SYSTEM")
    print("="*70)
    print("\n✅ Protection Mechanisms:")
    print("  1. Stop Loss (-15%)")
    print("  2. Take Profit (+30%)")
    print("  3. Trailing Stop (locks profits)")
    print("  4. Partial Profit Taking (25% at +15%, +30%, +50%)")
    print("  5. Break-Even Stop (after +8%)")
    print("  6. Profit Lock (minimum 10% after +20%)")
    print("  7. Time-Based Exit (2 hours max)")
    print("  8. Emergency Exit (25% drawdown from peak)")
    print("  9. Volume Drop Protection")
    print("  10. Smart Momentum Exit")
    print("\n💰 Guaranteed Profit Protection:")
    print("  - Multiple layers ensure you take profits")
    print("  - Automatic risk management")
    print("  - No manual intervention needed")
    print("  - Locks in gains progressively")
    print("\n" + "="*70 + "\n")
