"""
Advanced Strategy Engine with Multiple Strategies
Dynamically selects best strategy based on market conditions
"""
import numpy as np
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AdvancedStrategyEngine:
    """
    Multi-strategy trading engine that adapts to market conditions
    """
    
    def __init__(self):
        self.strategies = {
            'momentum': MomentumStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'breakout': BreakoutStrategy(),
            'scalping': ScalpingStrategy(),
            'swing': SwingStrategy()
        }
        self.strategy_performance = {name: {'wins': 0, 'losses': 0, 'total_pnl': 0} 
                                    for name in self.strategies.keys()}
        self.current_strategy = 'momentum'
        
    def select_best_strategy(self, market_data, regime):
        """Select best strategy based on market regime and performance"""
        
        # Strategy preferences by regime
        regime_strategies = {
            'trending_up': ['momentum', 'breakout', 'swing'],
            'trending_down': ['mean_reversion', 'swing'],
            'ranging': ['mean_reversion', 'scalping'],
            'volatile': ['breakout', 'scalping']
        }
        
        # Get suitable strategies for current regime
        suitable_strategies = regime_strategies.get(regime, ['momentum'])
        
        # Calculate performance scores
        scores = {}
        for strategy_name in suitable_strategies:
            perf = self.strategy_performance[strategy_name]
            total_trades = perf['wins'] + perf['losses']
            
            if total_trades > 0:
                win_rate = perf['wins'] / total_trades
                avg_pnl = perf['total_pnl'] / total_trades
                score = (win_rate * 0.6) + (avg_pnl * 0.4)
            else:
                score = 0.5  # Neutral score for untested strategies
            
            scores[strategy_name] = score
        
        # Select best performing strategy
        best_strategy = max(scores.items(), key=lambda x: x[1])[0]
        self.current_strategy = best_strategy
        
        logger.info(f"Selected strategy: {best_strategy} for regime: {regime}")
        return best_strategy
    
    def generate_signal(self, market_data, strategy_name=None):
        """Generate trading signal using specified or current strategy"""
        if strategy_name is None:
            strategy_name = self.current_strategy
        
        strategy = self.strategies.get(strategy_name)
        if not strategy:
            logger.error(f"Strategy {strategy_name} not found")
            return None
        
        signal = strategy.generate_signal(market_data)
        return signal
    
    def update_performance(self, strategy_name, trade_result):
        """Update strategy performance metrics"""
        perf = self.strategy_performance[strategy_name]
        
        if trade_result['pnl'] > 0:
            perf['wins'] += 1
        else:
            perf['losses'] += 1
        
        perf['total_pnl'] += trade_result['pnl']
    
    def get_strategy_stats(self):
        """Get performance statistics for all strategies"""
        stats = {}
        for name, perf in self.strategy_performance.items():
            total_trades = perf['wins'] + perf['losses']
            if total_trades > 0:
                stats[name] = {
                    'total_trades': total_trades,
                    'wins': perf['wins'],
                    'losses': perf['losses'],
                    'win_rate': perf['wins'] / total_trades * 100,
                    'total_pnl': perf['total_pnl'],
                    'avg_pnl': perf['total_pnl'] / total_trades
                }
            else:
                stats[name] = {
                    'total_trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'win_rate': 0,
                    'total_pnl': 0,
                    'avg_pnl': 0
                }
        
        return stats


class MomentumStrategy:
    """Momentum-based trading strategy"""
    
    def generate_signal(self, df):
        """Generate signal based on momentum indicators"""
        # Calculate momentum indicators
        returns_5 = df['close'].pct_change(5).iloc[-1]
        returns_10 = df['close'].pct_change(10).iloc[-1]
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9, adjust=False).mean()
        macd_diff = (macd - signal_line).iloc[-1]
        
        # Generate signal
        confidence = 0
        signal = None
        
        if returns_5 > 0.02 and returns_10 > 0.03 and current_rsi < 70 and macd_diff > 0:
            signal = 'buy'
            confidence = min(100, 60 + (returns_10 * 100))
        elif returns_5 < -0.02 and returns_10 < -0.03 and current_rsi > 30 and macd_diff < 0:
            signal = 'sell'
            confidence = min(100, 60 + (abs(returns_10) * 100))
        
        return {'signal': signal, 'confidence': confidence, 'strategy': 'momentum'}


class MeanReversionStrategy:
    """Mean reversion trading strategy"""
    
    def generate_signal(self, df):
        """Generate signal based on mean reversion"""
        # Bollinger Bands
        sma_20 = df['close'].rolling(window=20).mean()
        std_20 = df['close'].rolling(window=20).std()
        upper_band = sma_20 + (std_20 * 2)
        lower_band = sma_20 - (std_20 * 2)
        
        current_price = df['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_sma = sma_20.iloc[-1]
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Generate signal
        signal = None
        confidence = 0
        
        # Oversold - buy signal
        if current_price < current_lower and current_rsi < 30:
            signal = 'buy'
            distance_from_band = (current_lower - current_price) / current_price
            confidence = min(100, 60 + (distance_from_band * 200))
        
        # Overbought - sell signal
        elif current_price > current_upper and current_rsi > 70:
            signal = 'sell'
            distance_from_band = (current_price - current_upper) / current_price
            confidence = min(100, 60 + (distance_from_band * 200))
        
        return {'signal': signal, 'confidence': confidence, 'strategy': 'mean_reversion'}


class BreakoutStrategy:
    """Breakout trading strategy"""
    
    def generate_signal(self, df):
        """Generate signal based on breakouts"""
        # Calculate support and resistance
        lookback = 20
        recent_high = df['high'].rolling(window=lookback).max().iloc[-1]
        recent_low = df['low'].rolling(window=lookback).min().iloc[-1]
        
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        
        # Volume confirmation
        avg_volume = df['volume'].rolling(window=20).mean().iloc[-1] if 'volume' in df.columns else 1
        current_volume = df['volume'].iloc[-1] if 'volume' in df.columns else 1
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # ATR for volatility
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        
        signal = None
        confidence = 0
        
        # Bullish breakout
        if current_price > recent_high and prev_price <= recent_high:
            signal = 'buy'
            confidence = min(100, 50 + (volume_ratio * 20) + 10)
        
        # Bearish breakout
        elif current_price < recent_low and prev_price >= recent_low:
            signal = 'sell'
            confidence = min(100, 50 + (volume_ratio * 20) + 10)
        
        return {'signal': signal, 'confidence': confidence, 'strategy': 'breakout'}


class ScalpingStrategy:
    """Short-term scalping strategy"""
    
    def generate_signal(self, df):
        """Generate quick scalping signals"""
        # Fast moving averages
        ema_5 = df['close'].ewm(span=5, adjust=False).mean()
        ema_10 = df['close'].ewm(span=10, adjust=False).mean()
        
        current_price = df['close'].iloc[-1]
        current_ema5 = ema_5.iloc[-1]
        current_ema10 = ema_10.iloc[-1]
        prev_ema5 = ema_5.iloc[-2]
        prev_ema10 = ema_10.iloc[-2]
        
        # Stochastic oscillator
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        k = 100 * ((df['close'] - low_14) / (high_14 - low_14))
        d = k.rolling(window=3).mean()
        
        current_k = k.iloc[-1]
        current_d = d.iloc[-1]
        
        signal = None
        confidence = 0
        
        # Bullish crossover
        if current_ema5 > current_ema10 and prev_ema5 <= prev_ema10 and current_k < 80:
            signal = 'buy'
            confidence = 70
        
        # Bearish crossover
        elif current_ema5 < current_ema10 and prev_ema5 >= prev_ema10 and current_k > 20:
            signal = 'sell'
            confidence = 70
        
        return {'signal': signal, 'confidence': confidence, 'strategy': 'scalping'}


class SwingStrategy:
    """Swing trading strategy for longer-term positions"""
    
    def generate_signal(self, df):
        """Generate swing trading signals"""
        # Multiple timeframe analysis
        sma_50 = df['close'].rolling(window=50).mean()
        sma_200 = df['close'].rolling(window=200).mean()
        
        current_price = df['close'].iloc[-1]
        current_sma50 = sma_50.iloc[-1]
        current_sma200 = sma_200.iloc[-1]
        
        # Weekly trend (approximation using 5-day periods)
        weekly_returns = df['close'].pct_change(5).iloc[-1]
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9, adjust=False).mean()
        macd_histogram = macd - signal_line
        current_macd_hist = macd_histogram.iloc[-1]
        
        signal = None
        confidence = 0
        
        # Strong uptrend
        if (current_price > current_sma50 > current_sma200 and 
            weekly_returns > 0 and 
            current_rsi > 40 and current_rsi < 70 and
            current_macd_hist > 0):
            signal = 'buy'
            confidence = 75
        
        # Strong downtrend
        elif (current_price < current_sma50 < current_sma200 and 
              weekly_returns < 0 and 
              current_rsi < 60 and current_rsi > 30 and
              current_macd_hist < 0):
            signal = 'sell'
            confidence = 75
        
        return {'signal': signal, 'confidence': confidence, 'strategy': 'swing'}


class PortfolioOptimizer:
    """Optimize portfolio allocation across multiple assets"""
    
    def __init__(self):
        self.max_positions = 5
        self.max_allocation_per_asset = 0.3  # 30% max per asset
        
    def optimize_allocation(self, opportunities, total_capital):
        """Optimize capital allocation across opportunities"""
        if not opportunities:
            return {}
        
        # Sort by confidence score
        sorted_opps = sorted(opportunities, key=lambda x: x['confidence'], reverse=True)
        
        # Select top opportunities
        selected = sorted_opps[:self.max_positions]
        
        # Calculate allocation weights based on confidence
        total_confidence = sum(opp['confidence'] for opp in selected)
        
        allocations = {}
        for opp in selected:
            weight = opp['confidence'] / total_confidence
            # Cap at max allocation
            weight = min(weight, self.max_allocation_per_asset)
            
            allocations[opp['symbol']] = {
                'weight': weight,
                'capital': total_capital * weight,
                'confidence': opp['confidence'],
                'signal': opp['signal']
            }
        
        return allocations
    
    def rebalance_portfolio(self, current_positions, new_allocations, total_capital):
        """Rebalance portfolio to match target allocations"""
        actions = []
        
        # Close positions not in new allocations
        for symbol in current_positions:
            if symbol not in new_allocations:
                actions.append({
                    'action': 'close',
                    'symbol': symbol,
                    'reason': 'not_in_allocation'
                })
        
        # Adjust or open new positions
        for symbol, allocation in new_allocations.items():
            target_value = allocation['capital']
            
            if symbol in current_positions:
                current_value = current_positions[symbol]['value']
                diff = target_value - current_value
                
                if abs(diff) > total_capital * 0.05:  # 5% threshold
                    actions.append({
                        'action': 'adjust',
                        'symbol': symbol,
                        'target_value': target_value,
                        'current_value': current_value
                    })
            else:
                actions.append({
                    'action': 'open',
                    'symbol': symbol,
                    'value': target_value,
                    'signal': allocation['signal']
                })
        
        return actions
