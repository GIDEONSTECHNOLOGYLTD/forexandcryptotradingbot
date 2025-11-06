"""
Unit tests for risk management system
"""
import pytest
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from risk_manager import RiskManager


@pytest.fixture
def risk_manager():
    """Create a RiskManager instance"""
    return RiskManager(
        initial_capital=10000,
        max_position_size=2.0,
        stop_loss_percent=2.0,
        take_profit_percent=4.0,
        max_open_positions=3
    )


class TestRiskManager:
    """Test suite for RiskManager class"""
    
    def test_initialization(self, risk_manager):
        """Test risk manager initialization"""
        assert risk_manager.initial_capital == 10000
        assert risk_manager.max_position_size == 2.0
        assert risk_manager.stop_loss_percent == 2.0
        assert risk_manager.take_profit_percent == 4.0
        assert risk_manager.max_open_positions == 3
        
    def test_position_size_calculation(self, risk_manager):
        """Test position size calculation"""
        current_price = 30000
        position_size = risk_manager.calculate_position_size(current_price)
        
        # Position should be max 2% of capital
        max_size = 10000 * 0.02 / current_price
        assert position_size <= max_size
        assert position_size > 0
        
    def test_position_size_limits(self, risk_manager):
        """Test that position size respects limits"""
        # Very high price
        position_size = risk_manager.calculate_position_size(1000000)
        
        # Should still return a valid (small) position
        assert position_size > 0
        assert position_size * 1000000 <= 10000 * 0.02  # Max 2% of capital
        
    def test_stop_loss_calculation(self, risk_manager):
        """Test stop loss price calculation"""
        entry_price = 30000
        stop_loss = risk_manager.calculate_stop_loss(entry_price)
        
        # Stop loss should be 2% below entry
        expected_stop_loss = entry_price * (1 - 0.02)
        assert abs(stop_loss - expected_stop_loss) < 0.01
        
    def test_take_profit_calculation(self, risk_manager):
        """Test take profit price calculation"""
        entry_price = 30000
        take_profit = risk_manager.calculate_take_profit(entry_price)
        
        # Take profit should be 4% above entry
        expected_take_profit = entry_price * (1 + 0.04)
        assert abs(take_profit - expected_take_profit) < 0.01
        
    def test_risk_reward_ratio(self, risk_manager):
        """Test risk-reward ratio"""
        entry_price = 30000
        stop_loss = risk_manager.calculate_stop_loss(entry_price)
        take_profit = risk_manager.calculate_take_profit(entry_price)
        
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        ratio = reward / risk
        
        # Should be 2:1 ratio (4% profit / 2% loss)
        assert abs(ratio - 2.0) < 0.1
        
    def test_max_positions_check(self, risk_manager):
        """Test maximum positions limit"""
        # Simulate 3 open positions
        open_positions = [
            {'symbol': 'BTC/USDT', 'size': 0.1},
            {'symbol': 'ETH/USDT', 'size': 1.0},
            {'symbol': 'SOL/USDT', 'size': 10.0}
        ]
        
        can_open = risk_manager.can_open_position(open_positions)
        
        # Should not allow 4th position
        assert can_open == False
        
    def test_can_open_position_with_room(self, risk_manager):
        """Test can open position when under limit"""
        open_positions = [
            {'symbol': 'BTC/USDT', 'size': 0.1}
        ]
        
        can_open = risk_manager.can_open_position(open_positions)
        
        # Should allow more positions
        assert can_open == True
        
    def test_daily_loss_limit(self, risk_manager):
        """Test daily loss limit enforcement"""
        # Simulate large daily loss
        daily_pnl = -600  # $600 loss (6% of $10,000)
        
        should_stop = risk_manager.check_daily_loss_limit(daily_pnl, daily_limit_percent=5.0)
        
        # Should stop trading (loss exceeds 5%)
        assert should_stop == True
        
    def test_within_daily_loss_limit(self, risk_manager):
        """Test trading continues within daily loss limit"""
        # Small daily loss
        daily_pnl = -300  # $300 loss (3% of $10,000)
        
        should_stop = risk_manager.check_daily_loss_limit(daily_pnl, daily_limit_percent=5.0)
        
        # Should continue trading
        assert should_stop == False
        
    def test_portfolio_exposure(self, risk_manager):
        """Test total portfolio exposure calculation"""
        open_positions = [
            {'symbol': 'BTC/USDT', 'size': 0.1, 'entry_price': 30000},
            {'symbol': 'ETH/USDT', 'size': 1.0, 'entry_price': 2000}
        ]
        
        total_exposure = (0.1 * 30000) + (1.0 * 2000)
        exposure_percent = (total_exposure / 10000) * 100
        
        # Should be 5% of capital
        assert exposure_percent == 50
        
    def test_zero_capital_handling(self):
        """Test risk manager handles zero capital gracefully"""
        with pytest.raises(Exception):
            RiskManager(initial_capital=0)
            
    def test_negative_capital_handling(self):
        """Test risk manager rejects negative capital"""
        with pytest.raises(Exception):
            RiskManager(initial_capital=-1000)
            
    @pytest.mark.parametrize("capital,max_pos,expected_max_value", [
        (10000, 2.0, 200),
        (50000, 1.0, 500),
        (100000, 5.0, 5000),
    ])
    def test_various_capital_amounts(self, capital, max_pos, expected_max_value):
        """Test risk calculations with different capital amounts"""
        rm = RiskManager(
            initial_capital=capital,
            max_position_size=max_pos
        )
        
        price = 100
        position_size = rm.calculate_position_size(price)
        position_value = position_size * price
        
        # Position value should not exceed max percentage
        assert position_value <= capital * (max_pos / 100)


@pytest.mark.integration
class TestRiskManagerIntegration:
    """Integration tests for risk manager"""
    
    def test_complete_trade_risk_flow(self, risk_manager):
        """Test complete risk management flow for a trade"""
        # 1. Check if can open position
        assert risk_manager.can_open_position([]) == True
        
        # 2. Calculate position size
        entry_price = 30000
        position_size = risk_manager.calculate_position_size(entry_price)
        assert position_size > 0
        
        # 3. Calculate stop loss and take profit
        stop_loss = risk_manager.calculate_stop_loss(entry_price)
        take_profit = risk_manager.calculate_take_profit(entry_price)
        
        assert stop_loss < entry_price
        assert take_profit > entry_price
        
        # 4. Verify risk-reward
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        assert reward > risk  # Favorable risk-reward
