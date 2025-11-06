"""
Pytest configuration and shared fixtures
"""
import pytest
import os
import sys
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config


@pytest.fixture
def mock_exchange():
    """Mock CCXT exchange object"""
    exchange = Mock()
    exchange.fetch_ohlcv = Mock(return_value=[
        [1609459200000, 29000, 29500, 28800, 29200, 1000],  # timestamp, open, high, low, close, volume
        [1609462800000, 29200, 29800, 29100, 29500, 1200],
        [1609466400000, 29500, 30000, 29300, 29800, 1500],
    ])
    exchange.fetch_ticker = Mock(return_value={
        'symbol': 'BTC/USDT',
        'last': 29800,
        'bid': 29750,
        'ask': 29850,
        'volume': 10000,
        'quoteVolume': 298000000
    })
    exchange.fetch_balance = Mock(return_value={
        'USDT': {'free': 10000, 'used': 0, 'total': 10000}
    })
    exchange.create_order = Mock(return_value={
        'id': '12345',
        'symbol': 'BTC/USDT',
        'type': 'market',
        'side': 'buy',
        'price': 29800,
        'amount': 0.1,
        'filled': 0.1,
        'status': 'closed'
    })
    return exchange


@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    return {
        'symbol': 'BTC/USDT',
        'price': 29800,
        'volume': 298000000,
        'price_change_24h': 2.5,
        'high_24h': 30000,
        'low_24h': 28800
    }


@pytest.fixture
def mock_database():
    """Mock database object"""
    db = Mock()
    db.add_trade = Mock(return_value=True)
    db.get_open_positions = Mock(return_value=[])
    db.update_position = Mock(return_value=True)
    db.get_daily_pnl = Mock(return_value=0)
    return db


@pytest.fixture
def test_config():
    """Test configuration"""
    return {
        'initial_capital': 10000,
        'max_position_size': 2.0,
        'stop_loss_percent': 2.0,
        'take_profit_percent': 4.0,
        'max_open_positions': 3,
        'paper_trading': True
    }


@pytest.fixture
def mock_telegram():
    """Mock Telegram notifier"""
    telegram = Mock()
    telegram.send_message = Mock(return_value=True)
    telegram.send_trade_notification = Mock(return_value=True)
    return telegram


@pytest.fixture(autouse=True)
def set_test_env():
    """Set test environment variables"""
    os.environ['PAPER_TRADING'] = 'True'
    os.environ['OKX_API_KEY'] = 'test_key'
    os.environ['OKX_SECRET_KEY'] = 'test_secret'
    os.environ['OKX_PASSPHRASE'] = 'test_passphrase'
    yield
    # Cleanup
    for key in ['PAPER_TRADING', 'OKX_API_KEY', 'OKX_SECRET_KEY', 'OKX_PASSPHRASE']:
        os.environ.pop(key, None)
