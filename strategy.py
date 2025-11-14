"""
Trading Strategy Module
Implements multiple trading strategies with technical indicators
"""
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator
import config


class TradingStrategy:
    def __init__(self, name="Multi-Strategy"):
        self.name = name
        
    def add_indicators(self, df):
        """Add technical indicators to dataframe"""
        # Moving Averages
        df['sma_fast'] = SMAIndicator(close=df['close'], window=config.SMA_FAST).sma_indicator()
        df['sma_slow'] = SMAIndicator(close=df['close'], window=config.SMA_SLOW).sma_indicator()
        df['ema_fast'] = EMAIndicator(close=df['close'], window=config.EMA_FAST).ema_indicator()
        df['ema_slow'] = EMAIndicator(close=df['close'], window=config.EMA_SLOW).ema_indicator()
        
        # RSI
        df['rsi'] = RSIIndicator(close=df['close'], window=config.RSI_PERIOD).rsi()
        
        # MACD
        macd = MACD(close=df['close'], 
                    window_slow=config.MACD_SLOW,
                    window_fast=config.MACD_FAST,
                    window_sign=config.MACD_SIGNAL)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # Bollinger Bands
        bb = BollingerBands(close=df['close'], window=config.BB_PERIOD, window_dev=config.BB_STD)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = bb.bollinger_wband()
        
        # On Balance Volume
        df['obv'] = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
        
        # Price momentum
        df['momentum'] = df['close'].pct_change(periods=10) * 100
        
        return df
    
    def generate_signal(self, df):
        """
        Generate trading signal based on multiple strategies
        Returns: 'buy', 'sell', or None
        """
        if len(df) < config.SMA_SLOW + 10:
            return None, 0
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        buy_signals = 0
        sell_signals = 0
        
        # Strategy 1: Moving Average Crossover
        if self._ma_crossover_signal(df) == 'buy':
            buy_signals += 2
        elif self._ma_crossover_signal(df) == 'sell':
            sell_signals += 2
        
        # Strategy 2: RSI Oversold/Overbought
        if self._rsi_signal(latest) == 'buy':
            buy_signals += 1
        elif self._rsi_signal(latest) == 'sell':
            sell_signals += 1
        
        # Strategy 3: MACD Crossover
        if self._macd_signal(latest, prev) == 'buy':
            buy_signals += 2
        elif self._macd_signal(latest, prev) == 'sell':
            sell_signals += 2
        
        # Strategy 4: Bollinger Bands
        if self._bollinger_signal(latest) == 'buy':
            buy_signals += 1
        elif self._bollinger_signal(latest) == 'sell':
            sell_signals += 1
        
        # Strategy 5: Momentum
        if self._momentum_signal(latest) == 'buy':
            buy_signals += 1
        elif self._momentum_signal(latest) == 'sell':
            sell_signals += 1
        
        # Calculate confidence score
        total_signals = buy_signals + sell_signals
        if total_signals == 0:
            return None, 0
        
        # Determine signal based on vote count
        # FORCE BUY ONLY - no sell signals for spot trading!
        if buy_signals >= sell_signals and buy_signals > 0:  # Buy if equal or more
            confidence = (buy_signals / total_signals) * 100
            if confidence >= 50:  # Lowered from 60% to 50% for more opportunities
                return 'buy', confidence
        
        # Skip sell signals - we need USDT to buy first!
        # elif sell_signals > buy_signals:
        #     confidence = (sell_signals / total_signals) * 100
        #     if confidence >= 60:
        #         return 'sell', confidence
        
        return 'hold', 0  # Changed from None to 'hold'
    
    def _ma_crossover_signal(self, df):
        """Moving Average Crossover Strategy"""
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Golden Cross (bullish)
        if prev['sma_fast'] <= prev['sma_slow'] and latest['sma_fast'] > latest['sma_slow']:
            return 'buy'
        
        # Death Cross (bearish)
        if prev['sma_fast'] >= prev['sma_slow'] and latest['sma_fast'] < latest['sma_slow']:
            return 'sell'
        
        return None
    
    def _rsi_signal(self, latest):
        """RSI Strategy"""
        rsi = latest['rsi']
        
        if rsi < config.RSI_OVERSOLD:
            return 'buy'
        elif rsi > config.RSI_OVERBOUGHT:
            return 'sell'
        
        return None
    
    def _macd_signal(self, latest, prev):
        """MACD Crossover Strategy"""
        # Bullish crossover
        if prev['macd'] <= prev['macd_signal'] and latest['macd'] > latest['macd_signal']:
            return 'buy'
        
        # Bearish crossover
        if prev['macd'] >= prev['macd_signal'] and latest['macd'] < latest['macd_signal']:
            return 'sell'
        
        return None
    
    def _bollinger_signal(self, latest):
        """Bollinger Bands Strategy"""
        price = latest['close']
        
        # Price touches lower band (oversold)
        if price <= latest['bb_lower']:
            return 'buy'
        
        # Price touches upper band (overbought)
        if price >= latest['bb_upper']:
            return 'sell'
        
        return None
    
    def _momentum_signal(self, latest):
        """Momentum Strategy"""
        momentum = latest['momentum']
        
        if momentum > 3:  # Strong positive momentum
            return 'buy'
        elif momentum < -3:  # Strong negative momentum
            return 'sell'
        
        return None
    
    def analyze_market_condition(self, df):
        """
        Analyze overall market condition
        Returns: 'trending_up', 'trending_down', 'ranging', 'volatile'
        """
        if len(df) < 50:
            return 'unknown'
        
        latest = df.iloc[-1]
        
        # Check trend
        if latest['sma_fast'] > latest['sma_slow'] and latest['close'] > latest['sma_fast']:
            trend = 'trending_up'
        elif latest['sma_fast'] < latest['sma_slow'] and latest['close'] < latest['sma_fast']:
            trend = 'trending_down'
        else:
            trend = 'ranging'
        
        # Check volatility using Bollinger Band width
        bb_width = latest['bb_width']
        if bb_width > 0.1:  # High volatility
            return 'volatile'
        
        return trend
