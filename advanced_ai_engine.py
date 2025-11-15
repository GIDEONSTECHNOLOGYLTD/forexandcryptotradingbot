"""
Advanced AI Trading Engine
Implements real AI features based on top trading bots
"""
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class AdvancedAIEngine:
    """
    Advanced AI engine for smarter trading decisions
    Based on analysis of: 3Commas, Cryptohopper, TradeSanta, Pionex, Bitsgap
    """
    
    def __init__(self, exchange):
        self.exchange = exchange
        
    def analyze_multi_timeframe(self, symbol: str) -> Dict:
        """
        Analyze trend across multiple timeframes (like 3Commas)
        
        Returns:
            dict: {
                'trend': 'BULL'/'BEAR'/'NEUTRAL',
                'confidence': 0-100,
                'timeframes': {'15m': 'BULL', '1h': 'BULL', '4h': 'NEUTRAL'}
            }
        """
        try:
            timeframes = ['15m', '1h', '4h']
            trends = {}
            
            for tf in timeframes:
                # Fetch OHLCV data
                ohlcv = self.exchange.fetch_ohlcv(symbol, tf, limit=50)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # Calculate trend indicators
                df['SMA_20'] = df['close'].rolling(window=20).mean()
                df['SMA_50'] = df['close'].rolling(window=50).mean() if len(df) >= 50 else df['close'].rolling(window=20).mean()
                
                current_price = df['close'].iloc[-1]
                sma_20 = df['SMA_20'].iloc[-1]
                sma_50 = df['SMA_50'].iloc[-1]
                
                # Determine trend
                if current_price > sma_20 and sma_20 > sma_50:
                    trends[tf] = 'BULL'
                elif current_price < sma_20 and sma_20 < sma_50:
                    trends[tf] = 'BEAR'
                else:
                    trends[tf] = 'NEUTRAL'
            
            # Calculate overall confidence
            bull_count = sum([1 for t in trends.values() if t == 'BULL'])
            bear_count = sum([1 for t in trends.values() if t == 'BEAR'])
            
            if bull_count == 3:
                overall_trend = 'BULL'
                confidence = 95  # All timeframes agree
            elif bull_count == 2:
                overall_trend = 'BULL'
                confidence = 75  # Majority agree
            elif bear_count == 3:
                overall_trend = 'BEAR'
                confidence = 95
            elif bear_count == 2:
                overall_trend = 'BEAR'
                confidence = 75
            else:
                overall_trend = 'NEUTRAL'
                confidence = 50
            
            return {
                'trend': overall_trend,
                'confidence': confidence,
                'timeframes': trends
            }
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe analysis: {e}")
            return {
                'trend': 'NEUTRAL',
                'confidence': 50,
                'timeframes': {}
            }
    
    def calculate_smart_position_size(self, balance: float, confidence: int, 
                                     volatility: float, max_risk_pct: float = 0.02) -> float:
        """
        Calculate position size based on multiple factors (like Bitsgap)
        
        Args:
            balance: Current account balance
            confidence: Signal confidence (0-100)
            volatility: Market volatility (0-1)
            max_risk_pct: Maximum risk per trade (default 2%)
        
        Returns:
            float: Position size in USD
        """
        try:
            # Base position size (% of balance)
            base_pct = 0.10  # 10% of balance
            
            # Adjust for confidence
            confidence_multiplier = confidence / 100
            
            # Adjust for volatility (higher volatility = smaller position)
            if volatility > 0.05:  # 5%+ volatility
                volatility_multiplier = 0.5  # Cut in half
            elif volatility > 0.03:  # 3%+ volatility
                volatility_multiplier = 0.75
            else:
                volatility_multiplier = 1.0
            
            # Calculate position size
            position_size = balance * base_pct * confidence_multiplier * volatility_multiplier
            
            # Apply maximum risk limit
            max_position = balance * max_risk_pct * 10  # Max 20% of balance
            position_size = min(position_size, max_position)
            
            # Minimum position size ($5 for most exchanges)
            position_size = max(position_size, 5.0)
            
            logger.info(f"Smart position sizing: ${position_size:.2f} (confidence: {confidence}%, volatility: {volatility:.3f})")
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating smart position size: {e}")
            return balance * 0.05  # Fallback: 5% of balance
    
    def calculate_dynamic_stop_loss(self, entry_price: float, side: str, 
                                   volatility: float, confidence: int) -> Tuple[float, float]:
        """
        Calculate dynamic stop loss based on volatility (like TradeSanta)
        
        Args:
            entry_price: Entry price
            side: 'buy' or 'sell'
            volatility: Market volatility
            confidence: Signal confidence
        
        Returns:
            tuple: (stop_loss_price, stop_loss_percent)
        """
        try:
            # Base stop loss: 2% for high confidence, 5% for low confidence
            if confidence >= 80:
                base_stop_pct = 0.01  # 1% - very tight
            elif confidence >= 60:
                base_stop_pct = 0.02  # 2% - normal
            else:
                base_stop_pct = 0.03  # 3% - wider for uncertainty
            
            # Adjust for volatility
            if volatility > 0.05:
                # High volatility - wider stop to avoid getting stopped out
                stop_pct = base_stop_pct * 2
            elif volatility > 0.03:
                stop_pct = base_stop_pct * 1.5
            else:
                stop_pct = base_stop_pct
            
            # Cap at 5% maximum
            stop_pct = min(stop_pct, 0.05)
            
            # Calculate stop loss price
            if side.lower() in ['buy', 'long']:
                stop_loss_price = entry_price * (1 - stop_pct)
            else:
                stop_loss_price = entry_price * (1 + stop_pct)
            
            logger.info(f"Dynamic stop loss: {stop_pct*100:.1f}% @ ${stop_loss_price:.2f}")
            
            return stop_loss_price, stop_pct
            
        except Exception as e:
            logger.error(f"Error calculating dynamic stop loss: {e}")
            return entry_price * 0.98, 0.02  # Fallback: 2%
    
    def calculate_dynamic_take_profit(self, entry_price: float, stop_loss_price: float,
                                     side: str, risk_reward_ratio: float = 3.0) -> Tuple[float, float]:
        """
        Calculate dynamic take profit based on risk-reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            side: 'buy' or 'sell'
            risk_reward_ratio: Desired risk-reward ratio (default 3:1)
        
        Returns:
            tuple: (take_profit_price, take_profit_percent)
        """
        try:
            # Calculate risk amount
            risk = abs(entry_price - stop_loss_price)
            
            # Calculate reward (risk * ratio)
            reward = risk * risk_reward_ratio
            
            # Calculate take profit price
            if side.lower() in ['buy', 'long']:
                take_profit_price = entry_price + reward
            else:
                take_profit_price = entry_price - reward
            
            take_profit_pct = abs(take_profit_price - entry_price) / entry_price
            
            logger.info(f"Dynamic take profit: {take_profit_pct*100:.1f}% @ ${take_profit_price:.2f} (R:R = {risk_reward_ratio}:1)")
            
            return take_profit_price, take_profit_pct
            
        except Exception as e:
            logger.error(f"Error calculating dynamic take profit: {e}")
            return entry_price * 1.05, 0.05  # Fallback: 5%
    
    def calculate_volatility(self, symbol: str, timeframe: str = '1h', periods: int = 24) -> float:
        """
        Calculate recent volatility (standard deviation of returns)
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe for analysis
            periods: Number of periods to analyze
        
        Returns:
            float: Volatility as decimal (e.g., 0.03 = 3%)
        """
        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=periods + 1)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Calculate returns
            df['returns'] = df['close'].pct_change()
            
            # Calculate standard deviation (volatility)
            volatility = df['returns'].std()
            
            logger.info(f"Volatility for {symbol}: {volatility*100:.2f}%")
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.02  # Fallback: 2% volatility
    
    def update_smart_trailing_stop(self, position: Dict, current_price: float) -> Dict:
        """
        Update trailing stop dynamically based on profit level (like 3Commas)
        
        Args:
            position: Position dict
            current_price: Current market price
        
        Returns:
            dict: Updated position with new stop loss
        """
        try:
            entry_price = position['entry_price']
            signal = position['signal']
            
            # Calculate current profit
            if signal in ['buy', 'long']:
                profit_pct = (current_price - entry_price) / entry_price * 100
            else:
                profit_pct = (entry_price - current_price) / entry_price * 100
            
            # Dynamic trailing distance based on profit level
            if profit_pct >= 30:
                trail_pct = 0.02  # 2% trail (very tight)
            elif profit_pct >= 20:
                trail_pct = 0.03  # 3% trail
            elif profit_pct >= 10:
                trail_pct = 0.05  # 5% trail
            elif profit_pct >= 5:
                trail_pct = 0.07  # 7% trail
            else:
                # Below 5% profit - no trailing yet
                return position
            
            # Calculate new stop loss
            if signal in ['buy', 'long']:
                new_stop = current_price * (1 - trail_pct)
                # Only move stop up, never down
                if new_stop > position['stop_loss']:
                    position['stop_loss'] = new_stop
                    logger.info(f"🛡️ Trailing stop updated: ${new_stop:.2f} (trail: {trail_pct*100:.0f}%)")
            else:
                new_stop = current_price * (1 + trail_pct)
                # Only move stop down, never up
                if new_stop < position['stop_loss']:
                    position['stop_loss'] = new_stop
                    logger.info(f"🛡️ Trailing stop updated: ${new_stop:.2f} (trail: {trail_pct*100:.0f}%)")
            
            return position
            
        except Exception as e:
            logger.error(f"Error updating smart trailing stop: {e}")
            return position
    
    def analyze_risk_score(self, symbol: str, confidence: int, volatility: float) -> Dict:
        """
        Calculate comprehensive risk score (like Bitsgap)
        
        Args:
            symbol: Trading pair
            confidence: Signal confidence
            volatility: Market volatility
        
        Returns:
            dict: {
                'risk_score': 0-1 (0=low risk, 1=high risk),
                'recommendation': 'SAFE'/'MODERATE'/'RISKY'/'DANGEROUS',
                'factors': {factor: value}
            }
        """
        try:
            factors = {}
            
            # 1. Volatility risk (0-1)
            if volatility > 0.10:
                volatility_risk = 1.0  # Very risky
            elif volatility > 0.05:
                volatility_risk = 0.7
            elif volatility > 0.03:
                volatility_risk = 0.4
            else:
                volatility_risk = 0.2  # Low risk
            factors['volatility'] = volatility_risk
            
            # 2. Confidence risk (0-1, inverted - low confidence = high risk)
            confidence_risk = 1 - (confidence / 100)
            factors['confidence'] = confidence_risk
            
            # 3. Liquidity risk (check volume)
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                volume_24h = ticker.get('quoteVolume', 0)
                
                if volume_24h > 10_000_000:
                    liquidity_risk = 0.1  # Very liquid
                elif volume_24h > 1_000_000:
                    liquidity_risk = 0.3
                elif volume_24h > 100_000:
                    liquidity_risk = 0.5
                else:
                    liquidity_risk = 0.9  # Low liquidity = risky
                factors['liquidity'] = liquidity_risk
            except:
                liquidity_risk = 0.5
                factors['liquidity'] = 0.5
            
            # Calculate overall risk score (weighted average)
            risk_score = (
                volatility_risk * 0.4 +
                confidence_risk * 0.4 +
                liquidity_risk * 0.2
            )
            
            # Determine recommendation
            if risk_score <= 0.3:
                recommendation = 'SAFE'
            elif risk_score <= 0.5:
                recommendation = 'MODERATE'
            elif risk_score <= 0.7:
                recommendation = 'RISKY'
            else:
                recommendation = 'DANGEROUS'
            
            logger.info(f"Risk analysis for {symbol}: {risk_score:.2f} ({recommendation})")
            
            return {
                'risk_score': risk_score,
                'recommendation': recommendation,
                'factors': factors
            }
            
        except Exception as e:
            logger.error(f"Error analyzing risk score: {e}")
            return {
                'risk_score': 0.5,
                'recommendation': 'MODERATE',
                'factors': {}
            }
    
    def should_enter_trade(self, symbol: str, signal: str, confidence: int) -> Dict:
        """
        Comprehensive analysis to determine if trade should be entered
        
        Returns:
            dict: {
                'should_enter': True/False,
                'reason': str,
                'confidence_adjusted': int,
                'analysis': {various factors}
            }
        """
        try:
            # Multi-timeframe analysis
            mtf = self.analyze_multi_timeframe(symbol)
            
            # Calculate volatility
            volatility = self.calculate_volatility(symbol)
            
            # Risk score
            risk = self.analyze_risk_score(symbol, confidence, volatility)
            
            # Decision logic
            should_enter = True
            reasons = []
            
            # Check if risk is too high
            if risk['risk_score'] > 0.7:
                should_enter = False
                reasons.append(f"Risk too high ({risk['recommendation']})")
            
            # Check if multi-timeframe contradicts signal
            if signal.lower() == 'buy' and mtf['trend'] == 'BEAR' and mtf['confidence'] >= 75:
                should_enter = False
                reasons.append(f"Contradicts multi-timeframe trend (BEAR)")
            
            # Check if volatility is extreme
            if volatility > 0.15:  # 15%+ volatility
                should_enter = False
                reasons.append(f"Extreme volatility ({volatility*100:.1f}%)")
            
            # Adjust confidence based on analysis
            confidence_adjusted = confidence
            if mtf['trend'] == signal.upper() and mtf['confidence'] >= 75:
                confidence_adjusted = min(100, confidence + 10)  # Boost confidence
                reasons.append("Multi-timeframe confirms signal")
            
            if should_enter:
                reason = "All checks passed - Safe to trade"
            else:
                reason = " | ".join(reasons)
            
            return {
                'should_enter': should_enter,
                'reason': reason,
                'confidence_adjusted': confidence_adjusted,
                'analysis': {
                    'multi_timeframe': mtf,
                    'volatility': volatility,
                    'risk': risk
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {
                'should_enter': True,
                'reason': "Analysis failed - using original signal",
                'confidence_adjusted': confidence,
                'analysis': {}
            }


# Example usage
if __name__ == "__main__":
    import ccxt
    
    # Initialize exchange
    exchange = ccxt.okx()
    
    # Initialize AI engine
    ai = AdvancedAIEngine(exchange)
    
    print("\n" + "="*70)
    print("🤖 ADVANCED AI ENGINE - DEMONSTRATION")
    print("="*70 + "\n")
    
    symbol = "BTC/USDT"
    
    # 1. Multi-timeframe analysis
    print("📊 Multi-Timeframe Analysis:")
    mtf = ai.analyze_multi_timeframe(symbol)
    print(f"   Overall Trend: {mtf['trend']}")
    print(f"   Confidence: {mtf['confidence']}%")
    print(f"   Timeframes: {mtf['timeframes']}")
    print()
    
    # 2. Volatility calculation
    print("📈 Volatility Analysis:")
    volatility = ai.calculate_volatility(symbol)
    print(f"   Volatility: {volatility*100:.2f}%")
    print()
    
    # 3. Risk score
    print("⚠️ Risk Assessment:")
    risk = ai.analyze_risk_score(symbol, confidence=75, volatility=volatility)
    print(f"   Risk Score: {risk['risk_score']:.2f}")
    print(f"   Recommendation: {risk['recommendation']}")
    print(f"   Factors: {risk['factors']}")
    print()
    
    # 4. Smart position sizing
    print("💰 Smart Position Sizing:")
    balance = 1000
    position_size = ai.calculate_smart_position_size(balance, confidence=75, volatility=volatility)
    print(f"   Balance: ${balance}")
    print(f"   Position Size: ${position_size:.2f}")
    print()
    
    # 5. Comprehensive trade decision
    print("🎯 Trade Decision:")
    decision = ai.should_enter_trade(symbol, 'buy', confidence=75)
    print(f"   Should Enter: {decision['should_enter']}")
    print(f"   Reason: {decision['reason']}")
    print(f"   Adjusted Confidence: {decision['confidence_adjusted']}%")
    print()
    
    print("="*70)
    print("✅ AI Engine demonstration complete")
    print("="*70 + "\n")
