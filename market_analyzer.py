"""
Advanced Market Analysis Module
Real-time market condition analysis, volatility clustering, and regime detection
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class MarketAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.market_regimes = {}
        self.volatility_clusters = {}
        
    def analyze_market_sentiment(self, symbol):
        """Comprehensive market sentiment analysis"""
        try:
            sentiment_scores = {
                'news_sentiment': self._get_news_sentiment(symbol),
                'social_sentiment': self._get_social_sentiment(symbol),
                'fear_greed_index': self._get_fear_greed_index(),
                'market_momentum': self._calculate_market_momentum(symbol)
            }
            
            # Weighted composite sentiment
            weights = {
                'news_sentiment': 0.3,
                'social_sentiment': 0.2,
                'fear_greed_index': 0.3,
                'market_momentum': 0.2
            }
            
            composite_sentiment = sum(
                sentiment_scores[key] * weights[key] 
                for key in sentiment_scores if sentiment_scores[key] is not None
            )
            
            return {
                'composite_sentiment': composite_sentiment,
                'individual_scores': sentiment_scores,
                'sentiment_strength': self._classify_sentiment_strength(composite_sentiment)
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment for {symbol}: {e}")
            return {'composite_sentiment': 0.5, 'sentiment_strength': 'neutral'}
    
    def _get_news_sentiment(self, symbol):
        """Get sentiment from financial news"""
        try:
            # Simulate news sentiment analysis
            # In production, integrate with NewsAPI, Alpha Vantage, or similar
            base_symbol = symbol.split('/')[0].lower()
            
            # Simulate news headlines analysis
            sample_headlines = [
                f"{base_symbol} shows strong technical breakout",
                f"Institutional adoption of {base_symbol} increasing",
                f"Market volatility affects {base_symbol} trading",
                f"{base_symbol} reaches new support level"
            ]
            
            sentiments = []
            for headline in sample_headlines:
                blob = TextBlob(headline)
                sentiment = blob.sentiment.polarity
                sentiments.append(sentiment)
            
            # Convert to 0-1 scale
            avg_sentiment = np.mean(sentiments)
            normalized_sentiment = (avg_sentiment + 1) / 2
            
            return normalized_sentiment
            
        except Exception as e:
            print(f"Error getting news sentiment: {e}")
            return 0.5
    
    def _get_social_sentiment(self, symbol):
        """Get sentiment from social media"""
        try:
            # Simulate social media sentiment
            # In production, integrate with Twitter API, Reddit API, etc.
            base_symbol = symbol.split('/')[0].lower()
            
            # Simulate social posts
            sample_posts = [
                f"Bullish on {base_symbol} long term",
                f"{base_symbol} looking strong today",
                f"Uncertain about {base_symbol} short term",
                f"{base_symbol} technical analysis looks good"
            ]
            
            sentiments = []
            for post in sample_posts:
                scores = self.sentiment_analyzer.polarity_scores(post)
                compound_score = scores['compound']
                sentiments.append(compound_score)
            
            # Convert to 0-1 scale
            avg_sentiment = np.mean(sentiments)
            normalized_sentiment = (avg_sentiment + 1) / 2
            
            return normalized_sentiment
            
        except Exception as e:
            print(f"Error getting social sentiment: {e}")
            return 0.5
    
    def _get_fear_greed_index(self):
        """Get market fear & greed index"""
        try:
            # Simulate fear & greed index
            # In production, use CNN Fear & Greed Index API or similar
            
            # Generate realistic fear/greed based on time patterns
            current_hour = datetime.now().hour
            
            # Market hours tend to be more optimistic
            if 9 <= current_hour <= 16:  # Market hours
                base_index = np.random.normal(55, 15)  # Slightly bullish
            else:
                base_index = np.random.normal(45, 20)  # More volatile
            
            # Clamp to 0-100 range and normalize to 0-1
            fear_greed_index = max(0, min(100, base_index)) / 100
            
            return fear_greed_index
            
        except Exception as e:
            print(f"Error getting fear & greed index: {e}")
            return 0.5
    
    def _calculate_market_momentum(self, symbol):
        """Calculate market momentum indicator"""
        try:
            # Use price momentum as proxy for market sentiment
            # In production, could use more sophisticated momentum indicators
            
            # Simulate momentum calculation
            # Positive momentum = bullish sentiment
            momentum_score = np.random.normal(0.02, 0.05)  # 2% average with 5% volatility
            
            # Convert to 0-1 scale
            # Assume momentum range of -20% to +20%
            normalized_momentum = (momentum_score + 0.2) / 0.4
            normalized_momentum = max(0, min(1, normalized_momentum))
            
            return normalized_momentum
            
        except Exception as e:
            print(f"Error calculating market momentum: {e}")
            return 0.5
    
    def _classify_sentiment_strength(self, sentiment):
        """Classify sentiment strength"""
        if sentiment >= 0.7:
            return 'very_bullish'
        elif sentiment >= 0.6:
            return 'bullish'
        elif sentiment >= 0.4:
            return 'neutral'
        elif sentiment >= 0.3:
            return 'bearish'
        else:
            return 'very_bearish'
    
    def detect_market_regime(self, df, symbol):
        """Detect current market regime using advanced analysis"""
        try:
            if len(df) < 50:
                return 'insufficient_data'
            
            # Calculate regime indicators
            returns = df['close'].pct_change().dropna()
            volatility = returns.rolling(20).std()
            
            # Trend indicators
            sma_20 = df['close'].rolling(20).mean()
            sma_50 = df['close'].rolling(50).mean()
            
            latest = df.iloc[-1]
            
            # Volatility regime
            current_vol = volatility.iloc[-1]
            avg_vol = volatility.mean()
            
            if current_vol > avg_vol * 1.5:
                vol_regime = 'high_volatility'
            elif current_vol < avg_vol * 0.7:
                vol_regime = 'low_volatility'
            else:
                vol_regime = 'normal_volatility'
            
            # Trend regime
            if latest['close'] > sma_20.iloc[-1] > sma_50.iloc[-1]:
                trend_regime = 'strong_uptrend'
            elif latest['close'] < sma_20.iloc[-1] < sma_50.iloc[-1]:
                trend_regime = 'strong_downtrend'
            elif abs(latest['close'] - sma_20.iloc[-1]) / latest['close'] < 0.02:
                trend_regime = 'ranging'
            else:
                trend_regime = 'weak_trend'
            
            # Market structure
            highs = df['high'].rolling(10).max()
            lows = df['low'].rolling(10).min()
            
            if latest['high'] >= highs.iloc[-2]:
                structure = 'breaking_resistance'
            elif latest['low'] <= lows.iloc[-2]:
                structure = 'breaking_support'
            else:
                structure = 'within_range'
            
            regime = f"{trend_regime}_{vol_regime}_{structure}"
            
            # Store regime for future reference
            self.market_regimes[symbol] = {
                'regime': regime,
                'trend': trend_regime,
                'volatility': vol_regime,
                'structure': structure,
                'timestamp': datetime.now()
            }
            
            return regime
            
        except Exception as e:
            print(f"Error detecting market regime for {symbol}: {e}")
            return 'unknown'
    
    def analyze_volatility_clustering(self, df, symbol):
        """Analyze volatility clustering patterns"""
        try:
            if len(df) < 100:
                return {'cluster': 'insufficient_data', 'forecast': 0.02}
            
            # Calculate returns and volatility
            returns = df['close'].pct_change().dropna()
            squared_returns = returns ** 2
            
            # Create features for clustering
            features = []
            window_sizes = [5, 10, 20]
            
            for window in window_sizes:
                vol_ma = squared_returns.rolling(window).mean()
                features.append(vol_ma.iloc[-1])
            
            # Add current volatility
            current_vol = returns.rolling(20).std().iloc[-1]
            features.append(current_vol)
            
            # Perform clustering (simplified)
            if symbol not in self.volatility_clusters:
                # Initialize clusters for this symbol
                self.volatility_clusters[symbol] = {
                    'low_vol': 0.01,
                    'medium_vol': 0.03,
                    'high_vol': 0.06
                }
            
            clusters = self.volatility_clusters[symbol]
            
            # Classify current volatility
            if current_vol <= clusters['low_vol']:
                vol_cluster = 'low_volatility'
                forecast_vol = clusters['low_vol'] * 1.2  # Expect slight increase
            elif current_vol <= clusters['medium_vol']:
                vol_cluster = 'medium_volatility'
                forecast_vol = current_vol * 0.95  # Expect mean reversion
            else:
                vol_cluster = 'high_volatility'
                forecast_vol = current_vol * 0.8  # Expect volatility to decrease
            
            return {
                'cluster': vol_cluster,
                'current_volatility': current_vol,
                'forecast': forecast_vol,
                'persistence': self._calculate_volatility_persistence(squared_returns)
            }
            
        except Exception as e:
            print(f"Error analyzing volatility clustering for {symbol}: {e}")
            return {'cluster': 'unknown', 'forecast': 0.02}
    
    def _calculate_volatility_persistence(self, squared_returns):
        """Calculate volatility persistence (GARCH-like effect)"""
        try:
            # Simple volatility persistence measure
            if len(squared_returns) < 20:
                return 0.5
            
            # Calculate autocorrelation of squared returns
            recent_vol = squared_returns.tail(10).mean()
            historical_vol = squared_returns.tail(50).mean()
            
            persistence = min(recent_vol / historical_vol, 2.0) / 2.0
            return persistence
            
        except Exception as e:
            return 0.5
    
    def calculate_market_microstructure(self, df, symbol):
        """Analyze market microstructure indicators"""
        try:
            if len(df) < 50:
                return {'liquidity': 'unknown', 'efficiency': 0.5}
            
            # Price impact analysis
            returns = df['close'].pct_change().dropna()
            volumes = df['volume']
            
            # Volume-weighted average price deviation
            vwap = (df['close'] * df['volume']).rolling(20).sum() / df['volume'].rolling(20).sum()
            price_deviation = abs(df['close'] - vwap) / df['close']
            
            # Liquidity proxy (inverse of price impact)
            avg_deviation = price_deviation.tail(20).mean()
            
            if avg_deviation < 0.001:  # Less than 0.1% deviation
                liquidity = 'high_liquidity'
            elif avg_deviation < 0.005:  # Less than 0.5% deviation
                liquidity = 'medium_liquidity'
            else:
                liquidity = 'low_liquidity'
            
            # Market efficiency (randomness of returns)
            # More random = more efficient
            autocorr = returns.tail(50).autocorr(lag=1)
            efficiency = 1 - abs(autocorr) if not np.isnan(autocorr) else 0.5
            
            return {
                'liquidity': liquidity,
                'efficiency': efficiency,
                'price_impact': avg_deviation,
                'volume_trend': self._analyze_volume_trend(volumes)
            }
            
        except Exception as e:
            print(f"Error calculating microstructure for {symbol}: {e}")
            return {'liquidity': 'unknown', 'efficiency': 0.5}
    
    def _analyze_volume_trend(self, volumes):
        """Analyze volume trend"""
        try:
            if len(volumes) < 20:
                return 'insufficient_data'
            
            recent_volume = volumes.tail(10).mean()
            historical_volume = volumes.tail(50).mean()
            
            ratio = recent_volume / historical_volume
            
            if ratio > 1.5:
                return 'increasing_volume'
            elif ratio < 0.7:
                return 'decreasing_volume'
            else:
                return 'stable_volume'
                
        except Exception as e:
            return 'unknown'
    
    def generate_market_report(self, df, symbol):
        """Generate comprehensive market analysis report"""
        try:
            # Perform all analyses
            sentiment = self.analyze_market_sentiment(symbol)
            regime = self.detect_market_regime(df, symbol)
            volatility = self.analyze_volatility_clustering(df, symbol)
            microstructure = self.calculate_market_microstructure(df, symbol)
            
            # Generate overall market score
            market_score = self._calculate_market_score(sentiment, regime, volatility, microstructure)
            
            report = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'sentiment_analysis': sentiment,
                'market_regime': regime,
                'volatility_analysis': volatility,
                'microstructure': microstructure,
                'overall_score': market_score,
                'recommendation': self._generate_recommendation(market_score, sentiment, regime)
            }
            
            return report
            
        except Exception as e:
            print(f"Error generating market report for {symbol}: {e}")
            return None
    
    def _calculate_market_score(self, sentiment, regime, volatility, microstructure):
        """Calculate overall market attractiveness score"""
        try:
            score = 0
            
            # Sentiment component (30%)
            sentiment_score = sentiment.get('composite_sentiment', 0.5)
            score += sentiment_score * 0.3
            
            # Regime component (25%)
            regime_scores = {
                'strong_uptrend': 0.8,
                'weak_trend': 0.6,
                'ranging': 0.5,
                'strong_downtrend': 0.2
            }
            
            regime_key = regime.split('_')[0] if isinstance(regime, str) else 'ranging'
            regime_score = regime_scores.get(regime_key, 0.5)
            score += regime_score * 0.25
            
            # Volatility component (25%)
            vol_cluster = volatility.get('cluster', 'medium_volatility')
            vol_scores = {
                'low_volatility': 0.7,  # Stable but less opportunity
                'medium_volatility': 0.8,  # Optimal
                'high_volatility': 0.4  # Risky
            }
            vol_score = vol_scores.get(vol_cluster, 0.5)
            score += vol_score * 0.25
            
            # Microstructure component (20%)
            liquidity = microstructure.get('liquidity', 'medium_liquidity')
            efficiency = microstructure.get('efficiency', 0.5)
            
            liquidity_scores = {
                'high_liquidity': 0.8,
                'medium_liquidity': 0.6,
                'low_liquidity': 0.3
            }
            
            micro_score = (liquidity_scores.get(liquidity, 0.5) + efficiency) / 2
            score += micro_score * 0.2
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            return 0.5
    
    def _generate_recommendation(self, market_score, sentiment, regime):
        """Generate trading recommendation"""
        try:
            if market_score >= 0.75:
                if sentiment.get('composite_sentiment', 0.5) > 0.6:
                    return 'strong_buy'
                else:
                    return 'buy'
            elif market_score >= 0.6:
                return 'moderate_buy'
            elif market_score >= 0.4:
                return 'hold'
            elif market_score >= 0.25:
                return 'moderate_sell'
            else:
                return 'strong_sell'
                
        except Exception as e:
            return 'hold'
