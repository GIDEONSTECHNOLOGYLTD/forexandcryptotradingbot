import os
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TradingBot:
    def __init__(self, exchange_id='binance', symbol='BTC/USDT', timeframe='1h', test_mode=True):
        """
        Initialize the trading bot with exchange and trading pair
        
        Args:
            exchange_id (str): Exchange ID (e.g., 'binance', 'ftx')
            symbol (str): Trading pair (e.g., 'BTC/USDT')
            timeframe (str): Timeframe for candles (e.g., '1h', '4h', '1d')
            test_mode (bool): Whether to use testnet/sandbox mode
        """
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.timeframe = timeframe
        self.test_mode = test_mode
        
        # Initialize exchange
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'apiKey': os.getenv(f'{exchange_id.upper()}_API_KEY'),
            'secret': os.getenv(f'{exchange_id.upper()}_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # or 'spot'
            },
        })
        
        if test_mode:
            self.exchange.set_sandbox_mode(True)
            print(f"Running in TEST MODE on {exchange_id}")
        
        # Load markets
        self.markets = self.exchange.load_markets()
        
    def fetch_ohlcv(self, limit=100):
        """Fetch OHLCV (Open, High, Low, Close, Volume) data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching OHLCV data: {e}")
            return None
    
    def calculate_indicators(self, df):
        """Calculate technical indicators"""
        # Simple Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # Relative Strength Index (RSI)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = self.bollinger_bands(df['close'])
        
        return df
    
    @staticmethod
    def bollinger_bands(price, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        rolling_mean = price.rolling(window=window).mean()
        rolling_std = price.rolling(window=window).std()
        
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        
        return upper_band, rolling_mean, lower_band
    
    def check_conditions(self, df):
        """Check trading conditions based on indicators"""
        if len(df) < 50:  # Not enough data
            return None
            
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Example strategy: Golden Cross (SMA 20 crosses above SMA 50)
        if (prev['sma_20'] <= prev['sma_50']) and (latest['sma_20'] > latest['sma_50']):
            return 'buy'
            
        # Example strategy: Death Cross (SMA 20 crosses below SMA 50)
        elif (prev['sma_20'] >= prev['sma_50']) and (latest['sma_20'] < latest['sma_50']):
            return 'sell'
            
        return None
    
    def execute_trade(self, signal):
        """Execute a trade based on the signal"""
        if self.test_mode:
            print(f"[TEST MODE] Would execute {signal} order for {self.symbol}")
            return True
            
        try:
            if signal == 'buy':
                # Place buy order (example with market order)
                order = self.exchange.create_market_buy_order(
                    symbol=self.symbol,
                    amount=0.001  # Adjust based on your risk management
                )
                print(f"Buy order executed: {order}")
                return order
                
            elif signal == 'sell':
                # Place sell order (example with market order)
                order = self.exchange.create_market_sell_order(
                    symbol=self.symbol,
                    amount=0.001  # Adjust based on your position size
                )
                print(f"Sell order executed: {order}")
                return order
                
        except Exception as e:
            print(f"Error executing {signal} order: {e}")
            return None
    
    def run(self):
        """Main trading loop"""
        print(f"Starting trading bot for {self.symbol} on {self.exchange_id}")
        
        while True:
            try:
                # Fetch market data
                df = self.fetch_ohlcv(limit=100)
                if df is None:
                    time.sleep(60)  # Wait before retrying
                    continue
                
                # Calculate indicators
                df = self.calculate_indicators(df)
                
                # Check trading conditions
                signal = self.check_conditions(df)
                
                if signal:
                    print(f"{datetime.now()} - Signal detected: {signal.upper()} for {self.symbol}")
                    self.execute_trade(signal)
                
                # Wait before next iteration (adjust based on your timeframe)
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\nStopping trading bot...")
                break
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    # Initialize and run the bot
    bot = TradingBot(
        exchange_id='binance',
        symbol='BTC/USDT',
        timeframe='1h',
        test_mode=True  # Set to False for real trading
    )
    
    bot.run()
