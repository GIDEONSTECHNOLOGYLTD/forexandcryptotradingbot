"""
P2P Copy Trading System
Allows users to copy trades from expert traders
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)


class CopyTradingSystem:
    """
    P2P Copy Trading Platform
    - Expert traders share their strategies
    - Regular users copy their trades automatically
    - Revenue sharing model
    """
    
    def __init__(self, db):
        self.db = db
        self.active_copies = {}  # {follower_id: {leader_id: copy_config}}
    
    def create_expert_profile(self, user_id: str, profile_data: dict) -> str:
        """Create expert trader profile"""
        try:
            expert_profile = {
                'user_id': user_id,
                'display_name': profile_data.get('display_name'),
                'bio': profile_data.get('bio'),
                'strategy_description': profile_data.get('strategy_description'),
                'subscription_fee': profile_data.get('subscription_fee', 0),  # Monthly fee
                'profit_share': profile_data.get('profit_share', 0),  # % of follower profits
                'min_copy_amount': profile_data.get('min_copy_amount', 100),
                'max_followers': profile_data.get('max_followers', 100),
                'is_verified': False,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'stats': {
                    'total_followers': 0,
                    'total_trades': 0,
                    'win_rate': 0,
                    'total_profit': 0,
                    'avg_profit_per_trade': 0
                }
            }
            
            result = self.db.expert_traders.insert_one(expert_profile)
            
            logger.info(f"Expert profile created for user {user_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating expert profile: {e}")
            raise
    
    def get_expert_leaderboard(self, limit: int = 50) -> List[dict]:
        """Get top expert traders"""
        try:
            experts = list(self.db.expert_traders.find(
                {'is_active': True},
                sort=[('stats.win_rate', -1), ('stats.total_profit', -1)]
            ).limit(limit))
            
            for expert in experts:
                expert['_id'] = str(expert['_id'])
                # Hide sensitive info
                expert.pop('user_id', None)
            
            return experts
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    def start_copying(self, follower_id: str, leader_id: str, copy_config: dict) -> dict:
        """Start copying an expert trader"""
        try:
            # Validate expert exists
            expert = self.db.expert_traders.find_one({'user_id': leader_id, 'is_active': True})
            if not expert:
                raise Exception("Expert trader not found")
            
            # Check follower limits
            if expert['stats']['total_followers'] >= expert['max_followers']:
                raise Exception("Expert has reached maximum followers")
            
            # Check minimum amount
            if copy_config.get('copy_amount', 0) < expert['min_copy_amount']:
                raise Exception(f"Minimum copy amount is ${expert['min_copy_amount']}")
            
            # Create copy relationship
            copy_relationship = {
                'follower_id': follower_id,
                'leader_id': leader_id,
                'copy_amount': copy_config.get('copy_amount'),
                'copy_ratio': copy_config.get('copy_ratio', 1.0),  # 1.0 = 100% of leader's trades
                'max_position_size': copy_config.get('max_position_size'),
                'stop_loss_multiplier': copy_config.get('stop_loss_multiplier', 1.0),
                'take_profit_multiplier': copy_config.get('take_profit_multiplier', 1.0),
                'copy_symbols': copy_config.get('copy_symbols', 'all'),  # 'all' or list of symbols
                'is_active': True,
                'started_at': datetime.utcnow(),
                'stats': {
                    'total_copied_trades': 0,
                    'total_profit': 0,
                    'win_rate': 0
                }
            }
            
            result = self.db.copy_relationships.insert_one(copy_relationship)
            
            # Update expert follower count
            self.db.expert_traders.update_one(
                {'user_id': leader_id},
                {'$inc': {'stats.total_followers': 1}}
            )
            
            # Add to active copies
            if follower_id not in self.active_copies:
                self.active_copies[follower_id] = {}
            self.active_copies[follower_id][leader_id] = copy_relationship
            
            logger.info(f"User {follower_id} started copying {leader_id}")
            
            return {
                'copy_id': str(result.inserted_id),
                'status': 'active',
                'message': 'Successfully started copying'
            }
            
        except Exception as e:
            logger.error(f"Error starting copy: {e}")
            raise
    
    def stop_copying(self, follower_id: str, leader_id: str):
        """Stop copying an expert trader"""
        try:
            # Deactivate copy relationship
            self.db.copy_relationships.update_one(
                {'follower_id': follower_id, 'leader_id': leader_id},
                {'$set': {
                    'is_active': False,
                    'stopped_at': datetime.utcnow()
                }}
            )
            
            # Update expert follower count
            self.db.expert_traders.update_one(
                {'user_id': leader_id},
                {'$inc': {'stats.total_followers': -1}}
            )
            
            # Remove from active copies
            if follower_id in self.active_copies:
                self.active_copies[follower_id].pop(leader_id, None)
            
            logger.info(f"User {follower_id} stopped copying {leader_id}")
            
        except Exception as e:
            logger.error(f"Error stopping copy: {e}")
            raise
    
    async def copy_trade(self, leader_trade: dict):
        """Copy a trade from leader to all followers"""
        try:
            leader_id = leader_trade['user_id']
            
            # Get all active followers
            followers = list(self.db.copy_relationships.find({
                'leader_id': leader_id,
                'is_active': True
            }))
            
            for follower_config in followers:
                try:
                    # Check if should copy this symbol
                    if follower_config['copy_symbols'] != 'all':
                        if leader_trade['symbol'] not in follower_config['copy_symbols']:
                            continue
                    
                    # Calculate follower's position size
                    follower_position_size = self._calculate_follower_position_size(
                        leader_trade,
                        follower_config
                    )
                    
                    # Create copied trade
                    copied_trade = {
                        'user_id': follower_config['follower_id'],
                        'leader_id': leader_id,
                        'leader_trade_id': leader_trade['_id'],
                        'symbol': leader_trade['symbol'],
                        'signal': leader_trade['signal'],
                        'entry_price': leader_trade['entry_price'],
                        'position_size': follower_position_size,
                        'stop_loss': leader_trade['stop_loss'] * follower_config['stop_loss_multiplier'],
                        'take_profit': leader_trade['take_profit'] * follower_config['take_profit_multiplier'],
                        'strategy': 'copy_trading',
                        'status': 'open',
                        'entry_time': datetime.utcnow(),
                        'is_copy_trade': True
                    }
                    
                    # Save copied trade
                    self.db.trades.insert_one(copied_trade)
                    
                    # Update stats
                    self.db.copy_relationships.update_one(
                        {'_id': follower_config['_id']},
                        {'$inc': {'stats.total_copied_trades': 1}}
                    )
                    
                    logger.info(f"Trade copied from {leader_id} to {follower_config['follower_id']}")
                    
                except Exception as e:
                    logger.error(f"Error copying trade to follower: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in copy_trade: {e}")
    
    def _calculate_follower_position_size(self, leader_trade: dict, follower_config: dict) -> float:
        """Calculate position size for follower based on copy ratio"""
        # Base calculation: follower's copy amount * copy ratio
        base_size = follower_config['copy_amount'] * follower_config['copy_ratio']
        
        # Apply max position size limit
        if follower_config['max_position_size']:
            base_size = min(base_size, follower_config['max_position_size'])
        
        # Calculate actual position size based on price
        position_size = base_size / leader_trade['entry_price']
        
        return position_size
    
    def get_follower_stats(self, follower_id: str) -> dict:
        """Get statistics for a follower"""
        try:
            # Get all copy relationships
            relationships = list(self.db.copy_relationships.find({'follower_id': follower_id}))
            
            # Get all copied trades
            copied_trades = list(self.db.trades.find({
                'user_id': follower_id,
                'is_copy_trade': True
            }))
            
            # Calculate stats
            total_trades = len(copied_trades)
            winning_trades = [t for t in copied_trades if t.get('pnl', 0) > 0]
            total_profit = sum(t.get('pnl', 0) for t in copied_trades)
            
            return {
                'total_leaders_following': len([r for r in relationships if r['is_active']]),
                'total_copied_trades': total_trades,
                'winning_trades': len(winning_trades),
                'win_rate': (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0,
                'total_profit': total_profit,
                'active_relationships': relationships
            }
            
        except Exception as e:
            logger.error(f"Error getting follower stats: {e}")
            return {}
    
    def get_leader_stats(self, leader_id: str) -> dict:
        """Get statistics for a leader"""
        try:
            expert = self.db.expert_traders.find_one({'user_id': leader_id})
            if not expert:
                return {}
            
            # Get all followers
            followers = list(self.db.copy_relationships.find({
                'leader_id': leader_id,
                'is_active': True
            }))
            
            # Calculate total AUM (Assets Under Management)
            total_aum = sum(f['copy_amount'] for f in followers)
            
            # Calculate revenue
            monthly_revenue = len(followers) * expert['subscription_fee']
            
            return {
                'total_followers': len(followers),
                'total_aum': total_aum,
                'monthly_revenue': monthly_revenue,
                'stats': expert['stats'],
                'subscription_fee': expert['subscription_fee'],
                'profit_share': expert['profit_share']
            }
            
        except Exception as e:
            logger.error(f"Error getting leader stats: {e}")
            return {}
    
    def calculate_profit_share(self, follower_id: str, leader_id: str, profit: float) -> dict:
        """Calculate profit sharing between follower and leader"""
        try:
            expert = self.db.expert_traders.find_one({'user_id': leader_id})
            if not expert:
                return {'follower_profit': profit, 'leader_share': 0}
            
            profit_share_percent = expert['profit_share']
            leader_share = profit * (profit_share_percent / 100)
            follower_profit = profit - leader_share
            
            # Record profit share
            self.db.profit_shares.insert_one({
                'follower_id': follower_id,
                'leader_id': leader_id,
                'total_profit': profit,
                'leader_share': leader_share,
                'follower_profit': follower_profit,
                'timestamp': datetime.utcnow()
            })
            
            return {
                'follower_profit': follower_profit,
                'leader_share': leader_share,
                'share_percent': profit_share_percent
            }
            
        except Exception as e:
            logger.error(f"Error calculating profit share: {e}")
            return {'follower_profit': profit, 'leader_share': 0}


class P2PMarketplace:
    """
    P2P Trading Marketplace
    Users can buy/sell strategies and signals
    """
    
    def __init__(self, db):
        self.db = db
    
    def list_strategy(self, seller_id: str, strategy_data: dict) -> str:
        """List a trading strategy for sale"""
        try:
            listing = {
                'seller_id': seller_id,
                'strategy_name': strategy_data['name'],
                'description': strategy_data['description'],
                'price': strategy_data['price'],
                'strategy_type': strategy_data.get('type', 'indicator'),
                'backtested_results': strategy_data.get('backtest'),
                'is_active': True,
                'total_sales': 0,
                'rating': 0,
                'reviews': [],
                'created_at': datetime.utcnow()
            }
            
            result = self.db.strategy_marketplace.insert_one(listing)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error listing strategy: {e}")
            raise
    
    def purchase_strategy(self, buyer_id: str, strategy_id: str) -> dict:
        """Purchase a strategy from marketplace"""
        try:
            strategy = self.db.strategy_marketplace.find_one({'_id': strategy_id})
            if not strategy:
                raise Exception("Strategy not found")
            
            # Create purchase record
            purchase = {
                'buyer_id': buyer_id,
                'seller_id': strategy['seller_id'],
                'strategy_id': strategy_id,
                'price': strategy['price'],
                'purchased_at': datetime.utcnow()
            }
            
            self.db.strategy_purchases.insert_one(purchase)
            
            # Update strategy sales count
            self.db.strategy_marketplace.update_one(
                {'_id': strategy_id},
                {'$inc': {'total_sales': 1}}
            )
            
            return {
                'purchase_id': str(purchase['_id']),
                'strategy': strategy,
                'message': 'Strategy purchased successfully'
            }
            
        except Exception as e:
            logger.error(f"Error purchasing strategy: {e}")
            raise
