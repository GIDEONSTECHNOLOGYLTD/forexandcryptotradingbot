"""
Smart New Listing AI - Dynamic Profit Target System
Studies each new listing's behavior and determines optimal exit point
Takes CONTINUOUS SMALL PROFITS instead of waiting for big gains
"""
import logging
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class SmartNewListingAI:
    """
    Analyzes new listing patterns and suggests optimal profit targets
    Uses machine learning-like heuristics to maximize win rate
    """
    
    def __init__(self):
        self.historical_data = {}
        
    def analyze_new_listing(self, symbol: str, initial_data: Dict) -> Dict:
        """
        Analyze new listing characteristics and determine optimal strategy
        
        Args:
            symbol: Trading pair
            initial_data: {
                'price': current price,
                'volume_24h': 24h volume,
                'spread': bid/ask spread,
                'market_cap': estimated market cap,
                'hype_level': social media hype (0-100)
            }
        
        Returns:
            dict: {
                'recommended_target': optimal profit % (1-50%),
                'confidence': confidence in recommendation (0-100),
                'reasoning': why this target,
                'risk_level': LOW/MEDIUM/HIGH
            }
        """
        try:
            volume = initial_data.get('volume_24h', 0)
            spread = initial_data.get('spread', 0)
            market_cap = initial_data.get('market_cap', 0)
            hype = initial_data.get('hype_level', 50)
            
            # ANALYSIS FACTORS
            
            # 1. Volume Analysis (higher volume = more stable = higher target safe)
            if volume > 10_000_000:  # $10M+ volume
                volume_score = 10  # Very liquid - can target higher
            elif volume > 5_000_000:  # $5M+ volume
                volume_score = 8
            elif volume > 1_000_000:  # $1M+ volume
                volume_score = 6
            elif volume > 500_000:  # $500K+ volume
                volume_score = 4
            else:
                volume_score = 2  # Low volume - quick exit needed
            
            # 2. Spread Analysis (tighter spread = more efficient = can hold longer)
            if spread < 0.5:  # 0.5% spread - very tight
                spread_score = 10
            elif spread < 1.0:  # 1% spread - good
                spread_score = 8
            elif spread < 2.0:  # 2% spread - acceptable
                spread_score = 6
            elif spread < 5.0:  # 5% spread - wide
                spread_score = 4
            else:
                spread_score = 2  # Very wide - dangerous
            
            # 3. Market Cap Analysis (reasonable cap = more legitimate)
            if market_cap > 100_000_000:  # $100M+
                cap_score = 10  # Large cap - safer
            elif market_cap > 50_000_000:  # $50M+
                cap_score = 8
            elif market_cap > 10_000_000:  # $10M+
                cap_score = 6
            elif market_cap > 1_000_000:  # $1M+
                cap_score = 4
            else:
                cap_score = 2  # Micro cap - very risky
            
            # 4. Hype Level (social media buzz)
            if hype > 80:  # Extreme hype
                hype_score = 6  # Dangerous - likely to crash soon
            elif hype > 60:  # High hype
                hype_score = 8  # Good momentum
            elif hype > 40:  # Medium hype
                hype_score = 10  # Balanced - best
            elif hype > 20:  # Low hype
                hype_score = 6  # May not pump much
            else:
                hype_score = 4  # Very low - dead listing
            
            # CALCULATE OVERALL SCORE
            total_score = (volume_score + spread_score + cap_score + hype_score) / 4
            
            # DETERMINE OPTIMAL TARGET BASED ON SCORE
            if total_score >= 9:  # Excellent conditions
                recommended_target = 15  # Can aim for 15%
                risk_level = "LOW"
                reasoning = "High liquidity + tight spread + good fundamentals = 15% target safe"
            elif total_score >= 7.5:  # Good conditions
                recommended_target = 10  # Safe 10% target
                risk_level = "LOW"
                reasoning = "Good liquidity + decent spread = 10% target optimal"
            elif total_score >= 6:  # Medium conditions
                recommended_target = 5  # Quick 5% scalp
                risk_level = "MEDIUM"
                reasoning = "Medium liquidity - take 5% quickly and exit"
            elif total_score >= 4.5:  # Below average
                recommended_target = 3  # Very quick 3%
                risk_level = "MEDIUM"
                reasoning = "Weak fundamentals - grab 3% fast"
            elif total_score >= 3:  # Poor conditions
                recommended_target = 2  # Ultra quick 2%
                risk_level = "HIGH"
                reasoning = "Poor liquidity - take 2% immediately"
            else:  # Very poor
                recommended_target = 1  # Any profit is good
                risk_level = "HIGH"
                reasoning = "Very risky - exit at ANY profit (1%+)"
            
            # ADJUST FOR EXTREME CASES
            
            # If spread is too wide (>5%), lower target significantly
            if spread > 5:
                recommended_target = min(recommended_target, 3)
                reasoning += " | Wide spread detected - lowered target"
            
            # If volume is too low (<$100K), ultra conservative
            if volume < 100_000:
                recommended_target = min(recommended_target, 2)
                reasoning += " | Low volume - extreme caution"
                risk_level = "HIGH"
            
            # If hype is extreme (>90), it's a bubble - quick exit
            if hype > 90:
                recommended_target = min(recommended_target, 5)
                reasoning += " | Extreme hype bubble - quick exit"
            
            # CONFIDENCE CALCULATION
            confidence = int(total_score * 10)  # 0-100
            
            result = {
                'recommended_target': recommended_target,
                'confidence': confidence,
                'reasoning': reasoning,
                'risk_level': risk_level,
                'volume_score': volume_score,
                'spread_score': spread_score,
                'cap_score': cap_score,
                'hype_score': hype_score,
                'total_score': total_score
            }
            
            logger.info(f"AI Analysis for {symbol}: Target {recommended_target}% (Confidence: {confidence}%)")
            logger.info(f"  Reasoning: {reasoning}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            # Safe fallback
            return {
                'recommended_target': 5,
                'confidence': 50,
                'reasoning': 'Analysis failed - using safe 5% default',
                'risk_level': 'MEDIUM'
            }
    
    def analyze_price_action(self, symbol: str, price_history: list) -> Dict:
        """
        Analyze real-time price movement to adjust target dynamically
        
        Args:
            symbol: Trading pair
            price_history: List of prices over time [(timestamp, price), ...]
        
        Returns:
            dict: {
                'momentum': 'STRONG_UP'/'UP'/'SIDEWAYS'/'DOWN'/'STRONG_DOWN',
                'volatility': 0-100,
                'recommendation': 'HOLD'/'TAKE_PROFIT'/'EXIT_NOW',
                'adjusted_target': new target if different
            }
        """
        try:
            if len(price_history) < 5:
                return {
                    'momentum': 'UNKNOWN',
                    'volatility': 50,
                    'recommendation': 'HOLD',
                    'adjusted_target': None
                }
            
            prices = [p[1] for p in price_history[-20:]]  # Last 20 data points
            
            # Calculate momentum
            recent_trend = (prices[-1] - prices[-5]) / prices[-5] * 100  # Last 5 candles
            
            if recent_trend > 5:
                momentum = 'STRONG_UP'
            elif recent_trend > 2:
                momentum = 'UP'
            elif recent_trend > -2:
                momentum = 'SIDEWAYS'
            elif recent_trend > -5:
                momentum = 'DOWN'
            else:
                momentum = 'STRONG_DOWN'
            
            # Calculate volatility (standard deviation)
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            volatility = np.std(returns) * 100
            
            # DECISION LOGIC
            
            # If price is dropping fast - EXIT NOW
            if momentum == 'STRONG_DOWN':
                recommendation = 'EXIT_NOW'
                adjusted_target = None  # Exit at market
            
            # If sideways after pump - TAKE PROFIT
            elif momentum == 'SIDEWAYS' and max(prices) > prices[-1] * 1.05:
                recommendation = 'TAKE_PROFIT'
                adjusted_target = None
            
            # If strong momentum up - HOLD (may go higher)
            elif momentum == 'STRONG_UP':
                recommendation = 'HOLD'
                adjusted_target = None
            
            # If moderate momentum - HOLD but watch
            elif momentum == 'UP':
                recommendation = 'HOLD'
                adjusted_target = None
            
            # If down but not crashing - reduce target
            elif momentum == 'DOWN':
                recommendation = 'TAKE_PROFIT'
                adjusted_target = 3  # Lower target to 3%
            
            else:
                recommendation = 'HOLD'
                adjusted_target = None
            
            return {
                'momentum': momentum,
                'volatility': volatility,
                'recommendation': recommendation,
                'adjusted_target': adjusted_target,
                'recent_trend': recent_trend
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price action: {e}")
            return {
                'momentum': 'UNKNOWN',
                'volatility': 50,
                'recommendation': 'HOLD',
                'adjusted_target': None
            }
    
    def calculate_dynamic_stop_loss(self, entry_price: float, target_pct: float) -> Tuple[float, str]:
        """
        Calculate appropriate stop loss based on target
        
        Lower targets need tighter stops
        Higher targets can have wider stops
        
        Args:
            entry_price: Entry price
            target_pct: Target profit percentage
        
        Returns:
            tuple: (stop_loss_pct, reasoning)
        """
        # RULE: Stop loss should be 1/3 to 1/2 of target
        # But minimum 1%, maximum 5%
        
        if target_pct <= 2:
            # Ultra low target = ultra tight stop
            stop_pct = 1  # 1% stop
            reasoning = "Low 2% target needs 1% tight stop"
        elif target_pct <= 5:
            # Low target = tight stop
            stop_pct = 2  # 2% stop
            reasoning = "5% target uses 2% stop (2.5:1 ratio)"
        elif target_pct <= 10:
            # Medium target = medium stop
            stop_pct = 3  # 3% stop
            reasoning = "10% target uses 3% stop (3.3:1 ratio)"
        elif target_pct <= 15:
            # Higher target = wider stop
            stop_pct = 4  # 4% stop
            reasoning = "15% target uses 4% stop (3.75:1 ratio)"
        else:
            # Very high target = widest stop
            stop_pct = 5  # 5% stop (max)
            reasoning = "High target uses 5% stop (minimum 3:1 ratio)"
        
        stop_price = entry_price * (1 - stop_pct / 100)
        
        return stop_pct, reasoning
    
    def suggest_position_size(self, balance: float, confidence: int, risk_level: str) -> float:
        """
        Suggest position size based on confidence and risk
        
        Args:
            balance: Available balance
            confidence: AI confidence (0-100)
            risk_level: LOW/MEDIUM/HIGH
        
        Returns:
            float: Suggested position size in USD
        """
        # BASE SIZE: 10% of balance (conservative)
        base_size = balance * 0.10
        
        # ADJUST FOR CONFIDENCE
        if confidence >= 80:
            confidence_multiplier = 1.5  # High confidence = bigger position
        elif confidence >= 60:
            confidence_multiplier = 1.0  # Normal
        else:
            confidence_multiplier = 0.5  # Low confidence = smaller
        
        # ADJUST FOR RISK LEVEL
        if risk_level == 'LOW':
            risk_multiplier = 1.2
        elif risk_level == 'MEDIUM':
            risk_multiplier = 1.0
        else:  # HIGH
            risk_multiplier = 0.6  # Reduce size for high risk
        
        suggested_size = base_size * confidence_multiplier * risk_multiplier
        
        # LIMITS
        suggested_size = max(5, suggested_size)  # Minimum $5
        suggested_size = min(balance * 0.20, suggested_size)  # Maximum 20% of balance
        
        return round(suggested_size, 2)


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🤖 SMART NEW LISTING AI - DYNAMIC PROFIT TARGETS")
    print("="*70 + "\n")
    
    ai = SmartNewListingAI()
    
    # Test Case 1: High quality listing
    print("📊 Test 1: High Quality Listing (BTC-like)")
    result1 = ai.analyze_new_listing('QUALITY/USDT', {
        'price': 1.00,
        'volume_24h': 15_000_000,  # $15M volume
        'spread': 0.3,  # 0.3% spread
        'market_cap': 150_000_000,  # $150M cap
        'hype_level': 50  # Medium hype
    })
    print(f"  Target: {result1['recommended_target']}%")
    print(f"  Confidence: {result1['confidence']}%")
    print(f"  Risk: {result1['risk_level']}")
    print(f"  Reasoning: {result1['reasoning']}\n")
    
    # Test Case 2: Low quality listing
    print("📊 Test 2: Low Quality Listing (Risky)")
    result2 = ai.analyze_new_listing('RISKY/USDT', {
        'price': 0.001,
        'volume_24h': 50_000,  # Only $50K volume
        'spread': 8.0,  # 8% spread - very wide
        'market_cap': 500_000,  # $500K cap
        'hype_level': 90  # Extreme hype (bubble)
    })
    print(f"  Target: {result2['recommended_target']}%")
    print(f"  Confidence: {result2['confidence']}%")
    print(f"  Risk: {result2['risk_level']}")
    print(f"  Reasoning: {result2['reasoning']}\n")
    
    # Test Case 3: Medium quality
    print("📊 Test 3: Medium Quality Listing")
    result3 = ai.analyze_new_listing('MEDIUM/USDT', {
        'price': 0.50,
        'volume_24h': 2_000_000,  # $2M volume
        'spread': 1.5,  # 1.5% spread
        'market_cap': 20_000_000,  # $20M cap
        'hype_level': 60  # Good hype
    })
    print(f"  Target: {result3['recommended_target']}%")
    print(f"  Confidence: {result3['confidence']}%")
    print(f"  Risk: {result3['risk_level']}")
    print(f"  Reasoning: {result3['reasoning']}\n")
    
    # Test position sizing
    print("💰 Position Size Recommendations (Balance: $100)")
    print(f"  High Confidence (80%) + LOW Risk: ${ai.suggest_position_size(100, 80, 'LOW')}")
    print(f"  Medium Confidence (60%) + MEDIUM Risk: ${ai.suggest_position_size(100, 60, 'MEDIUM')}")
    print(f"  Low Confidence (40%) + HIGH Risk: ${ai.suggest_position_size(100, 40, 'HIGH')}")
    
    print("\n" + "="*70)
    print("✅ Smart AI analyzes each listing and suggests optimal targets!")
    print("="*70 + "\n")
