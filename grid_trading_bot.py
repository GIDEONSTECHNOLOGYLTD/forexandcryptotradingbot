"""
Grid Trading Bot - Buy Low, Sell High Automatically
One of the most profitable strategies in ranging markets
"""
import logging
from typing import List, Dict
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class GridTradingBot:
    """
    Grid Trading Strategy
    - Creates buy and sell orders at regular intervals
    - Profits from price oscillations
    - Perfect for ranging/sideways markets
    """
    
    def __init__(self, exchange, config: dict):
        self.exchange = exchange
        self.symbol = config['symbol']
        self.lower_price = config['lower_price']
        self.upper_price = config['upper_price']
        self.grid_count = config['grid_count']
        self.investment = config['investment']
        self.profit_per_grid = config.get('profit_per_grid', 0.01)  # 1% profit per grid
        
        self.grids = []
        self.active_orders = {}
        self.completed_trades = []
        
        self._calculate_grids()
    
    def _calculate_grids(self):
        """Calculate grid levels"""
        price_range = self.upper_price - self.lower_price
        grid_size = price_range / (self.grid_count - 1)
        
        for i in range(self.grid_count):
            price = self.lower_price + (i * grid_size)
            self.grids.append({
                'level': i,
                'buy_price': price,
                'sell_price': price * (1 + self.profit_per_grid),
                'quantity': self.investment / self.grid_count / price,
                'status': 'pending'
            })
        
        logger.info(f"Created {self.grid_count} grids from ${self.lower_price} to ${self.upper_price}")
    
    def start(self):
        """Start grid trading"""
        logger.info(f"Starting grid trading for {self.symbol}")
        
        # Place initial buy orders at all grid levels
        for grid in self.grids:
            try:
                order = self.exchange.create_limit_buy_order(
                    self.symbol,
                    grid['quantity'],
                    grid['buy_price']
                )
                
                self.active_orders[grid['level']] = {
                    'buy_order': order,
                    'sell_order': None,
                    'grid': grid
                }
                
                logger.info(f"Placed buy order at ${grid['buy_price']:.2f}")
                
            except Exception as e:
                logger.error(f"Error placing buy order: {e}")
    
    def check_orders(self):
        """Check and manage grid orders"""
        for level, order_pair in list(self.active_orders.items()):
            try:
                grid = order_pair['grid']
                
                # Check if buy order is filled
                if order_pair['buy_order'] and not order_pair['sell_order']:
                    buy_order = self.exchange.fetch_order(
                        order_pair['buy_order']['id'],
                        self.symbol
                    )
                    
                    if buy_order['status'] == 'closed':
                        # Buy order filled, place sell order
                        sell_order = self.exchange.create_limit_sell_order(
                            self.symbol,
                            grid['quantity'],
                            grid['sell_price']
                        )
                        
                        order_pair['sell_order'] = sell_order
                        logger.info(f"Buy filled at ${grid['buy_price']:.2f}, placed sell at ${grid['sell_price']:.2f}")
                
                # Check if sell order is filled
                elif order_pair['sell_order']:
                    sell_order = self.exchange.fetch_order(
                        order_pair['sell_order']['id'],
                        self.symbol
                    )
                    
                    if sell_order['status'] == 'closed':
                        # Sell order filled, record profit and place new buy order
                        profit = (grid['sell_price'] - grid['buy_price']) * grid['quantity']
                        
                        self.completed_trades.append({
                            'level': level,
                            'buy_price': grid['buy_price'],
                            'sell_price': grid['sell_price'],
                            'quantity': grid['quantity'],
                            'profit': profit,
                            'timestamp': datetime.utcnow()
                        })
                        
                        # Place new buy order at same grid level
                        new_buy_order = self.exchange.create_limit_buy_order(
                            self.symbol,
                            grid['quantity'],
                            grid['buy_price']
                        )
                        
                        order_pair['buy_order'] = new_buy_order
                        order_pair['sell_order'] = None
                        
                        logger.info(f"Grid {level} completed! Profit: ${profit:.2f}")
                
            except Exception as e:
                logger.error(f"Error checking orders for grid {level}: {e}")
    
    def stop(self):
        """Stop grid trading and cancel all orders"""
        logger.info("Stopping grid trading...")
        
        for level, order_pair in self.active_orders.items():
            try:
                if order_pair['buy_order']:
                    self.exchange.cancel_order(order_pair['buy_order']['id'], self.symbol)
                if order_pair['sell_order']:
                    self.exchange.cancel_order(order_pair['sell_order']['id'], self.symbol)
            except Exception as e:
                logger.error(f"Error canceling orders: {e}")
        
        self.active_orders.clear()
    
    def get_statistics(self) -> dict:
        """Get grid trading statistics"""
        total_profit = sum(trade['profit'] for trade in self.completed_trades)
        total_trades = len(self.completed_trades)
        
        return {
            'total_profit': total_profit,
            'total_trades': total_trades,
            'avg_profit_per_trade': total_profit / total_trades if total_trades > 0 else 0,
            'active_grids': len(self.active_orders),
            'completed_grids': total_trades,
            'roi': (total_profit / self.investment * 100) if self.investment > 0 else 0
        }


class DCABot:
    """
    Dollar Cost Averaging Bot
    - Buys dips automatically
    - Averages down cost basis
    - Takes profit at target
    """
    
    def __init__(self, exchange, config: dict):
        self.exchange = exchange
        self.symbol = config['symbol']
        self.base_order_size = config['base_order_size']
        self.safety_order_size = config['safety_order_size']
        self.max_safety_orders = config['max_safety_orders']
        self.price_deviation = config['price_deviation']  # % price must drop to trigger safety order
        self.take_profit = config['take_profit']  # % profit target
        
        self.entry_price = None
        self.total_invested = 0
        self.total_quantity = 0
        self.safety_orders_used = 0
        self.active = False
    
    def start(self):
        """Start DCA bot with base order"""
        try:
            # Place base order
            ticker = self.exchange.fetch_ticker(self.symbol)
            current_price = ticker['last']
            
            quantity = self.base_order_size / current_price
            
            order = self.exchange.create_market_buy_order(self.symbol, quantity)
            
            self.entry_price = current_price
            self.total_invested = self.base_order_size
            self.total_quantity = quantity
            self.active = True
            
            logger.info(f"DCA Bot started - Base order: {quantity} @ ${current_price:.2f}")
            
        except Exception as e:
            logger.error(f"Error starting DCA bot: {e}")
            raise
    
    def check_and_execute(self):
        """Check if safety order or take profit should be triggered"""
        if not self.active:
            return
        
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            current_price = ticker['last']
            
            avg_price = self.total_invested / self.total_quantity
            price_change = (current_price - avg_price) / avg_price * 100
            
            # Check for take profit
            if price_change >= self.take_profit:
                self._take_profit(current_price)
                return
            
            # Check for safety order
            if self.safety_orders_used < self.max_safety_orders:
                price_drop = (avg_price - current_price) / avg_price * 100
                
                if price_drop >= self.price_deviation * (self.safety_orders_used + 1):
                    self._place_safety_order(current_price)
        
        except Exception as e:
            logger.error(f"Error in DCA check: {e}")
    
    def _place_safety_order(self, current_price: float):
        """Place a safety order"""
        try:
            # Safety orders can be larger than base order (martingale)
            multiplier = 1.5 ** self.safety_orders_used  # Increase size exponentially
            order_size = self.safety_order_size * multiplier
            
            quantity = order_size / current_price
            
            order = self.exchange.create_market_buy_order(self.symbol, quantity)
            
            self.total_invested += order_size
            self.total_quantity += quantity
            self.safety_orders_used += 1
            
            new_avg = self.total_invested / self.total_quantity
            
            logger.info(f"Safety order #{self.safety_orders_used}: {quantity} @ ${current_price:.2f}")
            logger.info(f"New average price: ${new_avg:.2f}")
            
        except Exception as e:
            logger.error(f"Error placing safety order: {e}")
    
    def _take_profit(self, current_price: float):
        """Take profit and close position"""
        try:
            # Sell entire position
            order = self.exchange.create_market_sell_order(self.symbol, self.total_quantity)
            
            revenue = self.total_quantity * current_price
            profit = revenue - self.total_invested
            roi = (profit / self.total_invested) * 100
            
            logger.info(f"Take profit triggered!")
            logger.info(f"Sold {self.total_quantity} @ ${current_price:.2f}")
            logger.info(f"Profit: ${profit:.2f} ({roi:.2f}% ROI)")
            
            # Reset bot
            self.active = False
            self.entry_price = None
            self.total_invested = 0
            self.total_quantity = 0
            self.safety_orders_used = 0
            
        except Exception as e:
            logger.error(f"Error taking profit: {e}")
    
    def stop(self):
        """Stop DCA bot and close position"""
        if self.active and self.total_quantity > 0:
            try:
                order = self.exchange.create_market_sell_order(self.symbol, self.total_quantity)
                logger.info(f"DCA Bot stopped - Position closed")
                self.active = False
            except Exception as e:
                logger.error(f"Error stopping DCA bot: {e}")
    
    def get_status(self) -> dict:
        """Get current DCA bot status"""
        if not self.active:
            return {'status': 'inactive'}
        
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            current_price = ticker['last']
            
            avg_price = self.total_invested / self.total_quantity
            current_value = self.total_quantity * current_price
            unrealized_pnl = current_value - self.total_invested
            unrealized_pnl_pct = (unrealized_pnl / self.total_invested) * 100
            
            return {
                'status': 'active',
                'entry_price': self.entry_price,
                'avg_price': avg_price,
                'current_price': current_price,
                'total_invested': self.total_invested,
                'total_quantity': self.total_quantity,
                'current_value': current_value,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_pct': unrealized_pnl_pct,
                'safety_orders_used': self.safety_orders_used,
                'safety_orders_remaining': self.max_safety_orders - self.safety_orders_used
            }
        except Exception as e:
            logger.error(f"Error getting DCA status: {e}")
            return {'status': 'error', 'error': str(e)}


class ArbitrageBot:
    """
    Arbitrage Bot - Profit from price differences
    """
    
    def __init__(self, exchange1, exchange2, symbol: str, min_profit: float = 0.5):
        self.exchange1 = exchange1
        self.exchange2 = exchange2
        self.symbol = symbol
        self.min_profit = min_profit  # Minimum profit percentage
        
    def find_arbitrage_opportunity(self) -> dict:
        """Find arbitrage opportunities between exchanges"""
        try:
            # Get prices from both exchanges
            ticker1 = self.exchange1.fetch_ticker(self.symbol)
            ticker2 = self.exchange2.fetch_ticker(self.symbol)
            
            price1 = ticker1['last']
            price2 = ticker2['last']
            
            # Calculate profit potential
            if price1 < price2:
                profit_pct = ((price2 - price1) / price1) * 100
                if profit_pct >= self.min_profit:
                    return {
                        'opportunity': True,
                        'buy_exchange': 'exchange1',
                        'sell_exchange': 'exchange2',
                        'buy_price': price1,
                        'sell_price': price2,
                        'profit_pct': profit_pct
                    }
            elif price2 < price1:
                profit_pct = ((price1 - price2) / price2) * 100
                if profit_pct >= self.min_profit:
                    return {
                        'opportunity': True,
                        'buy_exchange': 'exchange2',
                        'sell_exchange': 'exchange1',
                        'buy_price': price2,
                        'sell_price': price1,
                        'profit_pct': profit_pct
                    }
            
            return {'opportunity': False}
            
        except Exception as e:
            logger.error(f"Error finding arbitrage: {e}")
            return {'opportunity': False, 'error': str(e)}
    
    def execute_arbitrage(self, opportunity: dict, amount: float):
        """Execute arbitrage trade"""
        try:
            buy_exchange = self.exchange1 if opportunity['buy_exchange'] == 'exchange1' else self.exchange2
            sell_exchange = self.exchange2 if opportunity['sell_exchange'] == 'exchange2' else self.exchange1
            
            # Buy on cheaper exchange
            buy_order = buy_exchange.create_market_buy_order(self.symbol, amount)
            
            # Sell on expensive exchange
            sell_order = sell_exchange.create_market_sell_order(self.symbol, amount)
            
            profit = (opportunity['sell_price'] - opportunity['buy_price']) * amount
            
            logger.info(f"Arbitrage executed! Profit: ${profit:.2f}")
            
            return {
                'success': True,
                'profit': profit,
                'buy_order': buy_order,
                'sell_order': sell_order
            }
            
        except Exception as e:
            logger.error(f"Error executing arbitrage: {e}")
            return {'success': False, 'error': str(e)}
