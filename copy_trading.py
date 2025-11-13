"""
Copy Trading System
Top traders share strategies, others copy their trades
Platform earns fees from successful copying
"""

from datetime import datetime
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)


class CopyTradingSystem:
    """
    Complete Copy Trading Implementation
    Leaders publish strategies
    Followers copy trades automatically
    Platform earns fees
    """
    
    def __init__(self, db):
        self.db = db
        self.published_strategies = db.db['published_strategies']
        self.copy_subscriptions = db.db['copy_subscriptions']
        self.copy_trades = db.db['copy_trades']
        logger.info("Copy Trading System initialized")
    
    def publish_strategy(self, trader_id, strategy_name, description, profit_share=10):
        """
        Trader publishes their strategy for others to copy
        """
        # Get trader's performance
        performance = self.get_trader_performance(trader_id)
        
        strategy = {
            'trader_id': str(trader_id),
            'name': strategy_name,
            'description': description,
            'win_rate': performance['win_rate'],
            'total_return': performance['total_return'],
            'monthly_return': performance['monthly_return'],
            'max_drawdown': performance['max_drawdown'],
            'total_trades': performance['total_trades'],
            'subscribers': 0,
            'subscription_fee': 0,  # Can add monthly fee later
            'profit_share': profit_share,  # % of follower profits
            'status': 'active',
            'created_at': datetime.utcnow(),
            'last_updated': datetime.utcnow()
        }
        
        result = self.published_strategies.insert_one(strategy)
        
        logger.info(f"Strategy published: {strategy_name} by {trader_id}")
        
        strategy['_id'] = str(result.inserted_id)
        return strategy
    
    def get_trader_performance(self, trader_id):
        """
        Calculate trader's performance metrics
        """
        # Get all trades by this trader
        trades = list(self.db.db['trades'].find({
            'user_id': str(trader_id),
            'status': 'closed'
        }).sort('timestamp', -1))
        
        if not trades:
            return {
                'win_rate': 0,
                'total_return': 0,
                'monthly_return': 0,
                'max_drawdown': 0,
                'total_trades': 0
            }
        
        # Calculate metrics
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0
        
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        initial_capital = trades[0].get('capital', 1000) if trades else 1000
        total_return = (total_pnl / initial_capital) * 100
        
        # Monthly return (approximate)
        if trades:
            first_trade = trades[-1]['timestamp']
            last_trade = trades[0]['timestamp']
            months = max((last_trade - first_trade).days / 30, 1)
            monthly_return = total_return / months
        else:
            monthly_return = 0
        
        # Max drawdown (simplified)
        max_drawdown = self.calculate_max_drawdown(trades)
        
        return {
            'win_rate': win_rate,
            'total_return': total_return,
            'monthly_return': monthly_return,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades)
        }
    
    def calculate_max_drawdown(self, trades):
        """
        Calculate maximum drawdown
        """
        if not trades:
            return 0
        
        cumulative_pnl = 0
        peak = 0
        max_dd = 0
        
        for trade in sorted(trades, key=lambda x: x['timestamp']):
            cumulative_pnl += trade.get('pnl', 0)
            peak = max(peak, cumulative_pnl)
            drawdown = peak - cumulative_pnl
            max_dd = max(max_dd, drawdown)
        
        initial_capital = trades[0].get('capital', 1000)
        return (max_dd / initial_capital) * 100 if initial_capital > 0 else 0
    
    def get_top_traders(self, limit=20):
        """
        Get top performing traders/strategies
        """
        strategies = list(self.published_strategies.find({
            'status': 'active'
        }).sort([
            ('win_rate', -1),
            ('monthly_return', -1)
        ]).limit(limit))
        
        # Convert ObjectId to string
        for strategy in strategies:
            strategy['_id'] = str(strategy['_id'])
            strategy['trader_id'] = str(strategy['trader_id'])
        
        return strategies
    
    def subscribe_to_strategy(self, follower_id, strategy_id, capital):
        """
        User subscribes to copy a strategy
        """
        # Check if strategy exists
        strategy = self.published_strategies.find_one({'_id': ObjectId(strategy_id)})
        
        if not strategy:
            raise Exception("Strategy not found")
        
        # Check if already subscribed
        existing = self.copy_subscriptions.find_one({
            'follower_id': str(follower_id),
            'strategy_id': strategy_id,
            'status': 'active'
        })
        
        if existing:
            raise Exception("Already subscribed to this strategy")
        
        subscription = {
            'follower_id': str(follower_id),
            'strategy_id': strategy_id,
            'leader_id': str(strategy['trader_id']),
            'capital': capital,
            'status': 'active',
            'started_at': datetime.utcnow(),
            'total_profit': 0,
            'total_trades': 0,
            'copied_trades': []
        }
        
        result = self.copy_subscriptions.insert_one(subscription)
        
        # Update subscriber count
        self.published_strategies.update_one(
            {'_id': ObjectId(strategy_id)},
            {'$inc': {'subscribers': 1}}
        )
        
        logger.info(f"User {follower_id} subscribed to strategy {strategy_id}")
        
        subscription['_id'] = str(result.inserted_id)
        return subscription
    
    def unsubscribe_from_strategy(self, follower_id, strategy_id):
        """
        Unsubscribe from a strategy
        """
        result = self.copy_subscriptions.update_one(
            {
                'follower_id': str(follower_id),
                'strategy_id': strategy_id,
                'status': 'active'
            },
            {
                '$set': {
                    'status': 'inactive',
                    'ended_at': datetime.utcnow()
                }
            }
        )
        
        # Update subscriber count
        self.published_strategies.update_one(
            {'_id': ObjectId(strategy_id)},
            {'$inc': {'subscribers': -1}}
        )
        
        logger.info(f"User {follower_id} unsubscribed from strategy {strategy_id}")
        
        return result.modified_count > 0
    
    def execute_copy_trade(self, leader_trade):
        """
        When leader makes a trade, automatically copy for all followers
        """
        leader_id = leader_trade['user_id']
        
        # Find all active subscriptions to this leader
        subscriptions = list(self.copy_subscriptions.find({
            'leader_id': str(leader_id),
            'status': 'active'
        }))
        
        logger.info(f"Copying trade for {len(subscriptions)} followers")
        
        copied_trades = []
        
        for subscription in subscriptions:
            try:
                # Calculate scaling factor based on capital
                leader_capital = self.get_trader_capital(leader_id)
                follower_capital = subscription['capital']
                
                scaling_factor = follower_capital / leader_capital if leader_capital > 0 else 0
                
                # Create follower trade
                follower_trade = {
                    'user_id': subscription['follower_id'],
                    'symbol': leader_trade['symbol'],
                    'side': leader_trade['side'],
                    'amount': leader_trade['amount'] * scaling_factor,
                    'price': leader_trade['price'],
                    'copied_from': str(leader_id),
                    'original_trade_id': str(leader_trade.get('_id')),
                    'subscription_id': str(subscription['_id']),
                    'is_copy': True,
                    'timestamp': datetime.utcnow(),
                    'status': 'open'
                }
                
                # Save copy trade
                result = self.copy_trades.insert_one(follower_trade)
                
                # Update subscription stats
                self.copy_subscriptions.update_one(
                    {'_id': subscription['_id']},
                    {
                        '$inc': {'total_trades': 1},
                        '$push': {'copied_trades': str(result.inserted_id)}
                    }
                )
                
                copied_trades.append(follower_trade)
                
                logger.info(f"Trade copied for user {subscription['follower_id']}")
                
            except Exception as e:
                logger.error(f"Error copying trade for {subscription['follower_id']}: {e}")
        
        return copied_trades
    
    def close_copy_trade(self, original_trade_id, exit_price):
        """
        When leader closes trade, close all copied trades
        """
        # Find all copy trades of this original trade
        copy_trades = list(self.copy_trades.find({
            'original_trade_id': str(original_trade_id),
            'status': 'open'
        }))
        
        logger.info(f"Closing {len(copy_trades)} copied trades")
        
        for copy_trade in copy_trades:
            try:
                # Calculate profit
                entry_price = copy_trade['price']
                amount = copy_trade['amount']
                side = copy_trade['side']
                
                if side == 'buy':
                    profit = (exit_price - entry_price) * amount
                else:
                    profit = (entry_price - exit_price) * amount
                
                # Update copy trade
                self.copy_trades.update_one(
                    {'_id': copy_trade['_id']},
                    {
                        '$set': {
                            'status': 'closed',
                            'exit_price': exit_price,
                            'profit': profit,
                            'closed_at': datetime.utcnow()
                        }
                    }
                )
                
                # Calculate profit share
                profit_share = self.calculate_profit_share(
                    copy_trade['subscription_id'],
                    profit
                )
                
                # Update subscription profit
                self.copy_subscriptions.update_one(
                    {'_id': ObjectId(copy_trade['subscription_id'])},
                    {'$inc': {'total_profit': profit_share['follower_keeps']}}
                )
                
                logger.info(f"Copy trade closed: {profit_share}")
                
            except Exception as e:
                logger.error(f"Error closing copy trade: {e}")
    
    def calculate_profit_share(self, subscription_id, profit):
        """
        Calculate platform, leader, and follower share of profits
        """
        subscription = self.copy_subscriptions.find_one({'_id': ObjectId(subscription_id)})
        strategy = self.published_strategies.find_one({'_id': ObjectId(subscription['strategy_id'])})
        
        if profit <= 0:
            # No profit sharing on losses
            return {
                'follower_keeps': profit,
                'leader_earns': 0,
                'platform_earns': 0
            }
        
        profit_share_percent = strategy['profit_share'] / 100
        
        leader_share = profit * profit_share_percent
        follower_keeps = profit * (1 - profit_share_percent)
        platform_fee = leader_share * 0.20  # Platform takes 20% of leader's share
        
        return {
            'follower_keeps': follower_keeps,
            'leader_earns': leader_share - platform_fee,
            'platform_earns': platform_fee
        }
    
    def get_trader_capital(self, trader_id):
        """
        Get trader's current capital
        """
        user = self.db.db['users'].find_one({'_id': ObjectId(trader_id)})
        
        if user:
            # Get balance from user or calculate from trades
            return user.get('balance', 1000)
        
        return 1000  # Default
    
    def get_follower_subscriptions(self, follower_id):
        """
        Get all subscriptions for a follower
        """
        subscriptions = list(self.copy_subscriptions.find({
            'follower_id': str(follower_id)
        }))
        
        # Enrich with strategy details
        for sub in subscriptions:
            sub['_id'] = str(sub['_id'])
            strategy = self.published_strategies.find_one({'_id': ObjectId(sub['strategy_id'])})
            if strategy:
                sub['strategy_name'] = strategy['name']
                sub['leader_win_rate'] = strategy['win_rate']
        
        return subscriptions
    
    def get_leader_earnings(self, leader_id):
        """
        Calculate total earnings for a leader from copy trading
        """
        # Find all subscriptions to this leader's strategies
        strategies = list(self.published_strategies.find({
            'trader_id': str(leader_id)
        }))
        
        total_earnings = 0
        
        for strategy in strategies:
            subscriptions = list(self.copy_subscriptions.find({
                'strategy_id': str(strategy['_id']),
                'status': 'active'
            }))
            
            for sub in subscriptions:
                # Calculate earnings from this subscription
                if sub['total_profit'] > 0:
                    profit_share = strategy['profit_share'] / 100
                    earnings = sub['total_profit'] * profit_share * 0.80  # After platform fee
                    total_earnings += earnings
        
        return total_earnings
