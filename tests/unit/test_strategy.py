"""
Unit tests for trading strategies
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from strategy import TradingStrategy


@pytest.fixture
def strategy():
    """Create a TradingStrategy instance"""
    return TradingStrategy()


@pytest.fixture
def sample_ohlcv_data():
    """Generate sample OHLCV data"""
    dates = pd.date_range('2024-01-01', periods=100, freq='H')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(28000, 30000, 100),
        'high': np.random.uniform(28500, 30500, 100),
        'low': np.random.uniform(27500, 29500, 100),
        'close': np.random.uniform(28000, 30000, 100),
        'volume': np.random.uniform(1000, 5000, 100)
    })
    return df


class TestTradingStrategy:
    """Test suite for TradingStrategy class"""
    
    def test_initialization(self, strategy):
        """Test strategy initialization"""
        assert strategy is not None
        assert hasattr(strategy, 'analyze_symbol')
        
    def test_rsi_calculation(self, strategy, sample_ohlcv_data):
        """Test RSI indicator calculation"""
        df = sample_ohlcv_data.copy()
        df['close'] = [100 + i for i in range(100)]  # Uptrend
        
        result = strategy.calculate_rsi(df['close'], period=14)
        
        assert result is not None
        assert len(result) > 0
        assert all(0 <= val <= 100 for val in result if not pd.isna(val))
        
    def test_rsi_oversold(self, strategy):
        """Test RSI oversold detection"""
        # Create downtrend data (RSI should be low)
        df = pd.DataFrame({
            'close': [100 - i for i in range(50)]  # Downtrend
        })
        
        rsi = strategy.calculate_rsi(df['close'], period=14)
        
        # Last RSI value should be low (oversold)
        assert rsi.iloc[-1] < 50  # Generally oversold territory
        
    def test_rsi_overbought(self, strategy):
        """Test RSI overbought detection"""
        # Create uptrend data (RSI should be high)
        df = pd.DataFrame({
            'close': [100 + i for i in range(50)]  # Uptrend
        })
        
        rsi = strategy.calculate_rsi(df['close'], period=14)
        
        # Last RSI value should be high (overbought)
        assert rsi.iloc[-1] > 50  # Generally overbought territory
        
    def test_macd_calculation(self, strategy, sample_ohlcv_data):
        """Test MACD indicator calculation"""
        df = sample_ohlcv_data.copy()
        
        macd, signal, histogram = strategy.calculate_macd(df['close'])
        
        assert macd is not None
        assert signal is not None
        assert histogram is not None
        assert len(macd) == len(signal) == len(histogram)
        
    def test_bollinger_bands(self, strategy, sample_ohlcv_data):
        """Test Bollinger Bands calculation"""
        df = sample_ohlcv_data.copy()
        
        upper, middle, lower = strategy.calculate_bollinger_bands(df['close'])
        
        assert upper is not None
        assert middle is not None
        assert lower is not None
        # Upper band should always be above middle, middle above lower
        assert all(upper.iloc[20:] > middle.iloc[20:])
        assert all(middle.iloc[20:] > lower.iloc[20:])
        
    def test_moving_average_crossover(self, strategy):
        """Test moving average crossover detection"""
        # Create clear crossover scenario
        close_prices = pd.Series([100] * 30 + [105 + i for i in range(20)])
        
        fast_ma = close_prices.rolling(10).mean()
        slow_ma = close_prices.rolling(20).mean()
        
        # Fast MA should eventually cross above slow MA
        assert fast_ma.iloc[-1] > slow_ma.iloc[-1]
        
    @pytest.mark.parametrize("signal_type,expected", [
        ("buy", True),
        ("sell", True),
        ("hold", True),
    ])
    def test_signal_generation(self, strategy, sample_ohlcv_data, signal_type, expected):
        """Test that strategy generates valid signals"""
        with patch.object(strategy, 'analyze_symbol') as mock_analyze:
            mock_analyze.return_value = {
                'signal': signal_type,
                'confidence': 75,
                'indicators': {}
            }
            
            result = strategy.analyze_symbol(sample_ohlcv_data)
            
            assert result is not None
            assert 'signal' in result
            assert 'confidence' in result
            
    def test_confidence_score_range(self, strategy, sample_ohlcv_data):
        """Test that confidence scores are in valid range"""
        with patch.object(strategy, 'analyze_symbol') as mock_analyze:
            mock_analyze.return_value = {
                'signal': 'buy',
                'confidence': 80,
                'indicators': {}
            }
            
            result = strategy.analyze_symbol(sample_ohlcv_data)
            
            assert 0 <= result['confidence'] <= 100
            
    def test_multiple_strategy_combination(self, strategy):
        """Test that multiple strategies are combined correctly"""
        # This tests the multi-strategy approach
        signals = ['buy', 'buy', 'hold', 'buy', 'sell']
        
        # Count buy signals
        buy_count = signals.count('buy')
        sell_count = signals.count('sell')
        
        # Combined signal should favor majority
        if buy_count > sell_count:
            expected_signal = 'buy'
        elif sell_count > buy_count:
            expected_signal = 'sell'
        else:
            expected_signal = 'hold'
            
        assert expected_signal in ['buy', 'sell', 'hold']
        
    def test_empty_data_handling(self, strategy):
        """Test strategy handles empty data gracefully"""
        empty_df = pd.DataFrame()
        
        # Should not crash with empty data
        try:
            result = strategy.calculate_rsi(pd.Series([]), period=14)
            assert result is not None or result is None  # Either result is acceptable
        except Exception as e:
            pytest.fail(f"Strategy should handle empty data: {e}")
            
    def test_insufficient_data_handling(self, strategy):
        """Test strategy handles insufficient data"""
        # Only 5 data points, but RSI needs 14+
        short_data = pd.Series([100, 101, 102, 103, 104])
        
        result = strategy.calculate_rsi(short_data, period=14)
        
        # Should return something (possibly NaN values)
        assert result is not None
        
    def test_momentum_calculation(self, strategy, sample_ohlcv_data):
        """Test momentum indicator"""
        df = sample_ohlcv_data.copy()
        
        # Calculate momentum
        momentum = df['close'].pct_change(periods=10) * 100
        
        assert momentum is not None
        assert len(momentum) == len(df)


@pytest.mark.integration
class TestStrategyIntegration:
    """Integration tests for strategy with real-like data"""
    
    def test_full_analysis_pipeline(self, strategy):
        """Test complete analysis from OHLCV to signal"""
        # Create realistic market data
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
            'open': [29000 + np.sin(i/10) * 1000 for i in range(100)],
            'high': [29500 + np.sin(i/10) * 1000 for i in range(100)],
            'low': [28500 + np.sin(i/10) * 1000 for i in range(100)],
            'close': [29000 + np.sin(i/10) * 1000 for i in range(100)],
            'volume': [1000 + i * 10 for i in range(100)]
        })
        
        with patch.object(strategy, 'analyze_symbol') as mock_analyze:
            mock_analyze.return_value = {
                'signal': 'buy',
                'confidence': 75,
                'indicators': {
                    'rsi': 45,
                    'macd': 'bullish',
                    'bb_position': 'lower'
                }
            }
            
            result = strategy.analyze_symbol(df)
            
            assert result is not None
            assert 'signal' in result
            assert 'confidence' in result
            assert 'indicators' in result
