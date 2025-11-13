"""
User Bot Manager - Manages individual trading bots for each user
Each user can have multiple bots trading independently
"""
import asyncio
import ccxt
from datetime import datetime
import logging
from typing import Dict, Optional
from cryptography.fernet import Fernet
import config
from advanced_strategy_engine import AdvancedStrategyEngine
from smart_risk_manager import SmartRiskManager
from ml_predictor import MLPredictor, MarketRegimeDetector

logger = logging.getLogger(__name__)


class UserTradingBot:
    """Individual trading bot instance for a user"""
    
    def __init__(self, user_id: str, bot_config: dict, db):
        self.user_id = user_id
        self.bot_id = bot_config['bot_id']
        self.db = db
        
        # Bot configuration
        self.config = bot_config
        self.paper_trading = bot_config.get('paper_trading', True)
        self.initial_capital = bot_config.get('initial_capital', 10000)
        self.strategy = bot_config.get('strategy', 'momentum')
        self.symbols = bot_config.get('symbols', ['BTC/USDT'])
        
        # Trading components
        self.strategy_engine = AdvancedStrategyEngine()
        self.risk_manager = SmartRiskManager(self.initial_capital)
        self.ml_predictor = MLPredictor()
        self.regime_detector = MarketRegimeDetector()
        
        # Bot state
        self.is_running = False
        self.exchange = None
        self.positions = {}
        
        # Initialize exchange
        self._init_exchange()
        
    def _init_exchange(self):
        """Initialize exchange connection with user's API keys"""
        try:
            if self.paper_trading:
                # Use system keys for paper trading
                self.exchange = ccxt.okx({
                    'apiKey': config.OKX_API_KEY,
                    'secret': config.OKX_SECRET_KEY,
                    'password': config.OKX_PASSPHRASE,
                    'enableRateLimit': True
                })
            else:
                # Decrypt and use user's API keys
                user = self.db.users.find_one({'_id': self.user_id})
                if not user or not user.get('okx_api_key'):
                    raise Exception("User API keys not found")
                
                # Decrypt keys
                fernet = Fernet(config.ENCRYPTION_KEY.encode())
                api_key = fernet.decrypt(user['okx_api_key'].encode()).decode()
                secret = fernet.decrypt(user['okx_secret_key'].encode()).decode()
                passphrase = fernet.decrypt(user['okx_passphrase'].encode()).decode()
                
                self.exchange = ccxt.okx({
                    'apiKey': api_key,
                    'secret': secret,
                    'password': passphrase,
                    'enableRateLimit': True
                })
            
            logger.info(f"Exchange initialized for bot {self.bot_id}")
            
        except Exception as e:
            logger.error(f"Error initializing exchange: {e}")
            raise
    
    async def start(self):
        """Start the trading bot"""
        if self.is_running:
            logger.warning(f"Bot {self.bot_id} is already running")
            return
        
        self.is_running = True
        logger.info(f"Starting bot {self.bot_id} for user {self.user_id}")
        
        # Update bot status in database
        self.db.bot_instances.update_one(
            {'_id': self.bot_id},
            {'$set': {
                'status': 'running',
                'started_at': datetime.utcnow()
            }}
        )
        
        # Start trading loop
        asyncio.create_task(self._trading_loop())
    
    async def stop(self):
        """Stop the trading bot"""
        self.is_running = False
        logger.info(f"Stopping bot {self.bot_id}")
        
        # Close all positions
        await self._close_all_positions()
        
        # Update bot status
        self.db.bot_instances.update_one(
            {'_id': self.bot_id},
            {'$set': {
                'status': 'stopped',
                'stopped_at': datetime.utcnow()
            }}
        )
    
    async def _trading_loop(self):
        """Main trading loop"""
        while self.is_running:
            try:
                for symbol in self.symbols:
                    await self._analyze_and_trade(symbol)
                
                # Check existing positions
                await self._manage_positions()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # 1 minute
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_and_trade(self, symbol: str):
        """Analyze market and execute trades"""
        try:
            # Get market data
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=100)
            
            # Detect market regime
            import pandas as pd
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            regime = self.regime_detector.detect_regime(df)
            
            # Select best strategy
            best_strategy = self.strategy_engine.select_best_strategy(df, regime)
            
            # Generate signal
            signal = self.strategy_engine.generate_signal(df, best_strategy)
            
            if signal and signal['signal'] in ['buy', 'sell']:
                # Check if should take trade
                current_price = df['close'].iloc[-1]
                
                if self.risk_manager.should_take_trade(
                    symbol, 
                    signal['confidence'], 
                    {'volatility': df['close'].pct_change().std()}
                ):
                    await self._execute_trade(symbol, signal, current_price)
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
    
    async def _execute_trade(self, symbol: str, signal: dict, current_price: float):
        """Execute a trade"""
        try:
            # Calculate position size
            atr = self._calculate_atr(symbol)
            stop_loss = self.risk_manager.calculate_stop_loss(
                current_price, 
                signal['signal'], 
                atr
            )
            
            position_size = self.risk_manager.calculate_position_size(
                symbol,
                current_price,
                stop_loss,
                signal['confidence'],
                0.02  # volatility
            )
            
            if position_size <= 0:
                return
            
            # Execute order
            if self.paper_trading:
                # Simulate order
                order = {
                    'id': f"paper_{datetime.utcnow().timestamp()}",
                    'symbol': symbol,
                    'side': signal['signal'],
                    'amount': position_size,
                    'price': current_price,
                    'status': 'closed'
                }
            else:
                # Real order
                order = self.exchange.create_market_order(
                    symbol,
                    signal['signal'],
                    position_size
                )
            
            # Calculate take profit
            take_profit = self.risk_manager.calculate_take_profit(
                current_price,
                stop_loss,
                signal['signal']
            )
            
            # Add position to risk manager
            self.risk_manager.add_position(
                symbol,
                signal['signal'],
                current_price,
                position_size,
                stop_loss,
                take_profit
            )
            
            # Save trade to database
            trade_record = {
                'user_id': self.user_id,
                'bot_id': self.bot_id,
                'bot_name': self.config.get('bot_type', 'Trading Bot'),
                'bot_type': 'user',
                'symbol': symbol,
                'signal': signal['signal'],
                'entry_price': current_price,
                'position_size': position_size,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': signal.get('strategy', 'unknown'),
                'confidence': signal['confidence'],
                'status': 'open',
                'entry_time': datetime.utcnow(),
                'timestamp': datetime.utcnow(),
                'paper_trading': self.paper_trading
            }
            
            self.db.trades.insert_one(trade_record)
            
            logger.info(f"Trade executed: {symbol} {signal['signal']} @ {current_price}")
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    async def _manage_positions(self):
        """Manage open positions"""
        for symbol in list(self.risk_manager.open_positions.keys()):
            try:
                # Get current price
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Update position
                self.risk_manager.update_position(symbol, current_price)
                
                # Check exit conditions
                exit_reason = self.risk_manager.check_exit_conditions(symbol, current_price)
                
                if exit_reason:
                    await self._close_position(symbol, current_price, exit_reason)
                    
            except Exception as e:
                logger.error(f"Error managing position {symbol}: {e}")
    
    async def _close_position(self, symbol: str, exit_price: float, reason: str):
        """Close a position"""
        try:
            position = self.risk_manager.open_positions.get(symbol)
            if not position:
                return
            
            # Execute close order
            if not self.paper_trading:
                side = 'sell' if position['signal'] == 'buy' else 'buy'
                self.exchange.create_market_order(
                    symbol,
                    side,
                    position['position_size']
                )
            
            # Close position in risk manager
            self.risk_manager.close_position(symbol, exit_price, reason)
            
            # Update trade in database
            self.db.trades.update_one(
                {
                    'user_id': self.user_id,
                    'bot_id': self.bot_id,
                    'symbol': symbol,
                    'status': 'open'
                },
                {'$set': {
                    'exit_price': exit_price,
                    'exit_time': datetime.utcnow(),
                    'exit_reason': reason,
                    'status': 'closed',
                    'pnl': position['unrealized_pnl']
                }}
            )
            
            logger.info(f"Position closed: {symbol} @ {exit_price} ({reason})")
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    async def _close_all_positions(self):
        """Close all open positions"""
        for symbol in list(self.risk_manager.open_positions.keys()):
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                await self._close_position(symbol, current_price, 'bot_stopped')
            except Exception as e:
                logger.error(f"Error closing position {symbol}: {e}")
    
    def _calculate_atr(self, symbol: str) -> float:
        """Calculate Average True Range"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=14)
            import pandas as pd
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]
            
            return atr
        except:
            return 0.02 * self.exchange.fetch_ticker(symbol)['last']
    
    def get_status(self) -> dict:
        """Get bot status"""
        return {
            'bot_id': self.bot_id,
            'user_id': self.user_id,
            'is_running': self.is_running,
            'paper_trading': self.paper_trading,
            'strategy': self.strategy,
            'symbols': self.symbols,
            'open_positions': len(self.risk_manager.open_positions),
            'current_capital': self.risk_manager.current_capital,
            'total_pnl': self.risk_manager.current_capital - self.initial_capital,
            'metrics': self.risk_manager.get_risk_metrics()
        }


class BotManager:
    """Manages all user bots"""
    
    def __init__(self, db):
        self.db = db
        self.active_bots: Dict[str, UserTradingBot] = {}
    
    async def create_bot(self, user_id: str, bot_config: dict) -> str:
        """Create a new bot for user"""
        bot_id = str(self.db.bot_instances.insert_one({
            'user_id': user_id,
            'config': bot_config,
            'status': 'stopped',
            'created_at': datetime.utcnow()
        }).inserted_id)
        
        bot_config['bot_id'] = bot_id
        
        return bot_id
    
    async def start_bot(self, user_id: str, bot_id: str):
        """Start a user's bot"""
        # Get bot config from database
        bot_doc = self.db.bot_instances.find_one({'_id': bot_id, 'user_id': user_id})
        if not bot_doc:
            raise Exception("Bot not found")
        
        # Create bot instance
        bot = UserTradingBot(user_id, bot_doc, self.db)
        self.active_bots[bot_id] = bot
        
        # Start bot
        await bot.start()
        
        return bot.get_status()
    
    async def stop_bot(self, user_id: str, bot_id: str):
        """Stop a user's bot"""
        bot = self.active_bots.get(bot_id)
        if bot:
            await bot.stop()
            del self.active_bots[bot_id]
    
    def get_bot_status(self, bot_id: str) -> Optional[dict]:
        """Get bot status"""
        bot = self.active_bots.get(bot_id)
        if bot:
            return bot.get_status()
        return None
    
    def get_user_bots(self, user_id: str) -> list:
        """Get all bots for a user"""
        return [
            bot.get_status() 
            for bot in self.active_bots.values() 
            if bot.user_id == user_id
        ]
