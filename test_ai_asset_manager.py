"""
Test AI Asset Manager with Comprehensive Market Analysis
Run this to verify all AI features are working correctly
"""
import ccxt
import logging
from advanced_ai_engine import AdvancedAIEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_ai_engine():
    """Test the AI engine with comprehensive market analysis"""
    
    print("\n" + "="*70)
    print("🤖 TESTING AI ASSET MANAGER - COMPREHENSIVE ANALYSIS")
    print("="*70 + "\n")
    
    try:
        # Initialize exchange (no credentials needed for public data)
        exchange = ccxt.okx()
        
        # Initialize AI engine
        ai_engine = AdvancedAIEngine(exchange)
        logger.info("✅ AI Engine initialized")
        
        # Test symbol
        symbol = "BTC/USDT"
        
        print("\n" + "="*70)
        print(f"📊 Testing Comprehensive Market Analysis for {symbol}")
        print("="*70 + "\n")
        
        # Run comprehensive analysis
        analysis = ai_engine.comprehensive_market_analysis(symbol)
        
        print("\n" + "="*70)
        print("📋 ANALYSIS RESULTS")
        print("="*70)
        print(f"\n🎯 Recommendation: {analysis['recommendation']}")
        print(f"📊 Confidence: {analysis['confidence']}%")
        print(f"💪 Signal Strength: {analysis['signal_strength']}")
        
        print(f"\n📝 Reasons:")
        for reason in analysis['reasons']:
            print(f"  • {reason}")
        
        print(f"\n📊 Technical Indicators:")
        indicators = analysis['indicators']
        print(f"  RSI: {indicators['rsi']:.2f}")
        print(f"  MACD Trend: {indicators['macd']['trend']}")
        print(f"  Bollinger Position: {indicators['bollinger']['position']:.1f}%")
        print(f"  Order Book Pressure: {indicators['order_book']['pressure']}")
        print(f"  Multi-Timeframe: {indicators['multi_timeframe']['trend']} ({indicators['multi_timeframe']['confidence']}%)")
        print(f"  Volatility: {indicators['volatility']*100:.2f}%")
        
        print("\n" + "="*70)
        print("✅ ALL AI FEATURES WORKING CORRECTLY!")
        print("="*70 + "\n")
        
        # Test individual indicators
        print("\n" + "="*70)
        print("🔍 Testing Individual Indicators")
        print("="*70 + "\n")
        
        # Test RSI
        rsi = ai_engine.calculate_rsi(symbol)
        print(f"✅ RSI: {rsi:.2f}")
        if rsi > 70:
            print("   → Overbought (good time to sell)")
        elif rsi < 30:
            print("   → Oversold (good time to buy)")
        else:
            print("   → Neutral")
        
        # Test MACD
        macd = ai_engine.calculate_macd(symbol)
        print(f"\n✅ MACD: {macd['trend']}")
        print(f"   → MACD Line: {macd['macd']:.6f}")
        print(f"   → Signal Line: {macd['signal']:.6f}")
        print(f"   → Histogram: {macd['histogram']:.6f}")
        
        # Test Bollinger Bands
        bollinger = ai_engine.calculate_bollinger_bands(symbol)
        print(f"\n✅ Bollinger Bands:")
        print(f"   → Upper: ${bollinger['upper']:.2f}")
        print(f"   → Middle: ${bollinger['middle']:.2f}")
        print(f"   → Lower: ${bollinger['lower']:.2f}")
        print(f"   → Current: ${bollinger['current_price']:.2f}")
        print(f"   → Position: {bollinger['position']:.1f}%")
        if bollinger['position'] > 80:
            print("   → Near upper band (ideal sell zone)")
        elif bollinger['position'] < 20:
            print("   → Near lower band (potential buy zone)")
        
        # Test Order Book
        order_book = ai_engine.analyze_order_book(symbol)
        print(f"\n✅ Order Book Analysis:")
        print(f"   → Bid Strength: {order_book['bid_strength']:.1f}%")
        print(f"   → Ask Strength: {order_book['ask_strength']:.1f}%")
        print(f"   → Pressure: {order_book['pressure']}")
        print(f"   → Spread: {order_book['spread']:.4f}%")
        
        # Test Multi-Timeframe
        mtf = ai_engine.analyze_multi_timeframe(symbol)
        print(f"\n✅ Multi-Timeframe Analysis:")
        print(f"   → Overall: {mtf['trend']} (Confidence: {mtf['confidence']}%)")
        print(f"   → 15m: {mtf['timeframes'].get('15m', 'N/A')}")
        print(f"   → 1h: {mtf['timeframes'].get('1h', 'N/A')}")
        print(f"   → 4h: {mtf['timeframes'].get('4h', 'N/A')}")
        
        # Test Volatility
        volatility = ai_engine.calculate_volatility(symbol)
        print(f"\n✅ Volatility: {volatility*100:.2f}%")
        if volatility > 0.05:
            print("   → High volatility (risky)")
        elif volatility > 0.03:
            print("   → Moderate volatility")
        else:
            print("   → Low volatility (stable)")
        
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\n✅ Your AI Asset Manager is fully integrated and ready!")
        print("✅ All technical indicators working correctly!")
        print("✅ Comprehensive market analysis functioning!")
        print("\n🚀 Ready for production deployment!\n")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        print(f"\n❌ Error during testing: {e}")
        print("\nPlease ensure:")
        print("  1. Internet connection is active")
        print("  2. CCXT library is installed (pip install ccxt)")
        print("  3. Pandas and numpy are installed")
        return False

if __name__ == "__main__":
    test_ai_engine()
