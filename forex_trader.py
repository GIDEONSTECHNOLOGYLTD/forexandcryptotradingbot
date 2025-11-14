"""
Forex Trading Module
Supports major forex pairs on OKX
"""
import ccxt
import logging
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


class ForexTrader:
    """
    Forex trading functionality
    Supports major currency pairs
    """
    
    # Major forex pairs available on OKX
    FOREX_PAIRS = [
        'EUR/USD',  # Euro / US Dollar
        'GBP/USD',  # British Pound / US Dollar
        'USD/JPY',  # US Dollar / Japanese Yen
        'USD/CHF',  # US Dollar / Swiss Franc
        'AUD/USD',  # Australian Dollar / US Dollar
        'USD/CAD',  # US Dollar / Canadian Dollar
        'NZD/USD',  # New Zealand Dollar / US Dollar
        'EUR/GBP',  # Euro / British Pound
        'EUR/JPY',  # Euro / Japanese Yen
        'GBP/JPY',  # British Pound / Japanese Yen
    ]
    
    def __init__(self, exchange):
        self.exchange = exchange
        self.forex_enabled = self._check_forex_support()
    
    def _check_forex_support(self) -> bool:
        """Check if exchange supports forex trading"""
        try:
            markets = self.exchange.load_markets()
            # Check if any forex pairs are available
            for pair in self.FOREX_PAIRS:
                if pair in markets:
                    logger.info(f"Forex trading supported: {pair}")
                    return True
            
            logger.warning("Forex pairs not found on exchange")
            return False
        except Exception as e:
            logger.error(f"Error checking forex support: {e}")
            return False
    
    def get_available_pairs(self) -> list:
        """Get list of available forex pairs"""
        try:
            markets = self.exchange.load_markets()
            available = []
            
            for pair in self.FOREX_PAIRS:
                if pair in markets:
                    available.append({
                        'symbol': pair,
                        'base': pair.split('/')[0],
                        'quote': pair.split('/')[1],
                        'active': markets[pair].get('active', True)
                    })
            
            return available
        except Exception as e:
            logger.error(f"Error getting forex pairs: {e}")
            return []
    
    def get_forex_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """Get forex market data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Error fetching forex data for {symbol}: {e}")
            return pd.DataFrame()
    
    def analyze_forex_pair(self, symbol: str) -> dict:
        """Analyze a forex pair"""
        try:
            df = self.get_forex_data(symbol)
            
            if df.empty:
                return {'error': 'No data available'}
            
            # Calculate technical indicators
            # Moving averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Current values
            current_price = df['close'].iloc[-1]
            current_rsi = df['rsi'].iloc[-1]
            sma_20 = df['sma_20'].iloc[-1]
            sma_50 = df['sma_50'].iloc[-1]
            
            # Trend determination
            trend = 'neutral'
            if current_price > sma_20 > sma_50:
                trend = 'bullish'
            elif current_price < sma_20 < sma_50:
                trend = 'bearish'
            
            # Signal generation
            signal = 'hold'
            if current_rsi < 30 and trend != 'bearish':
                signal = 'buy'
            elif current_rsi > 70 and trend != 'bullish':
                signal = 'sell'
            
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                'trend': trend,
                'signal': signal,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {'error': str(e)}
    
    def execute_forex_trade(self, symbol: str, side: str, amount: float, paper_trading: bool = True) -> dict:
        """Execute a forex trade"""
        try:
            if paper_trading:
                # Simulate trade
                ticker = self.exchange.fetch_ticker(symbol)
                return {
                    'id': f"paper_{datetime.utcnow().timestamp()}",
                    'symbol': symbol,
                    'side': side,
                    'amount': amount,
                    'price': ticker['last'],
                    'status': 'closed',
                    'paper_trading': True
                }
            else:
                # Real trade - SPOT ONLY (no margin/leverage)
                order = self.exchange.create_market_order(
                    symbol, 
                    side, 
                    amount,
                    params={'tdMode': 'cash'}  # SPOT trading only - prevents debt
                )
                return order
                
        except Exception as e:
            logger.error(f"Error executing forex trade: {e}")
            raise
    
    def get_forex_market_overview(self) -> list:
        """Get overview of all forex markets"""
        overview = []
        
        for pair in self.get_available_pairs():
            try:
                analysis = self.analyze_forex_pair(pair['symbol'])
                if 'error' not in analysis:
                    overview.append(analysis)
            except Exception as e:
                logger.error(f"Error getting overview for {pair['symbol']}: {e}")
        
        return overview
    
    def calculate_pip_value(self, symbol: str, position_size: float) -> float:
        """Calculate pip value for forex pair"""
        try:
            # For most pairs, 1 pip = 0.0001
            # For JPY pairs, 1 pip = 0.01
            if 'JPY' in symbol:
                pip_size = 0.01
            else:
                pip_size = 0.0001
            
            # Pip value = pip size × position size
            pip_value = pip_size * position_size
            
            return pip_value
        except Exception as e:
            logger.error(f"Error calculating pip value: {e}")
            return 0.0001
    
    def calculate_forex_position_size(self, symbol: str, account_balance: float, risk_percent: float = 0.02) -> float:
        """Calculate position size for forex trade"""
        try:
            # Risk amount
            risk_amount = account_balance * risk_percent
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Calculate stop loss distance (2% of price)
            stop_loss_distance = current_price * 0.02
            
            # Calculate position size
            # Position size = Risk amount / Stop loss distance
            position_size = risk_amount / stop_loss_distance
            
            return position_size
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0


class ForexStrategy:
    """
    Forex-specific trading strategies
    """
    
    @staticmethod
    def trend_following(df: pd.DataFrame) -> dict:
        """Trend following strategy for forex"""
        # Calculate indicators
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema_12'] - df['ema_26']
        df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        current_macd = df['macd'].iloc[-1]
        current_signal = df['signal_line'].iloc[-1]
        prev_macd = df['macd'].iloc[-2]
        prev_signal = df['signal_line'].iloc[-2]
        
        signal = None
        confidence = 0
        
        # Bullish crossover
        if current_macd > current_signal and prev_macd <= prev_signal:
            signal = 'buy'
            confidence = 70
        # Bearish crossover
        elif current_macd < current_signal and prev_macd >= prev_signal:
            signal = 'sell'
            confidence = 70
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strategy': 'forex_trend_following'
        }
    
    @staticmethod
    def range_trading(df: pd.DataFrame) -> dict:
        """Range trading strategy for forex"""
        # Calculate Bollinger Bands
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['std_20'] = df['close'].rolling(window=20).std()
        df['upper_band'] = df['sma_20'] + (df['std_20'] * 2)
        df['lower_band'] = df['sma_20'] - (df['std_20'] * 2)
        
        current_price = df['close'].iloc[-1]
        upper_band = df['upper_band'].iloc[-1]
        lower_band = df['lower_band'].iloc[-1]
        sma = df['sma_20'].iloc[-1]
        
        signal = None
        confidence = 0
        
        # Price near lower band - buy
        if current_price <= lower_band:
            signal = 'buy'
            distance = (lower_band - current_price) / current_price
            confidence = min(80, 60 + (distance * 200))
        
        # Price near upper band - sell
        elif current_price >= upper_band:
            signal = 'sell'
            distance = (current_price - upper_band) / current_price
            confidence = min(80, 60 + (distance * 200))
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strategy': 'forex_range_trading'
        }
    
    @staticmethod
    def breakout_strategy(df: pd.DataFrame) -> dict:
        """Breakout strategy for forex"""
        lookback = 20
        
        recent_high = df['high'].rolling(window=lookback).max().iloc[-1]
        recent_low = df['low'].rolling(window=lookback).min().iloc[-1]
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        
        signal = None
        confidence = 0
        
        # Bullish breakout
        if current_price > recent_high and prev_price <= recent_high:
            signal = 'buy'
            confidence = 75
        
        # Bearish breakout
        elif current_price < recent_low and prev_price >= recent_low:
            signal = 'sell'
            confidence = 75
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strategy': 'forex_breakout'
        }
