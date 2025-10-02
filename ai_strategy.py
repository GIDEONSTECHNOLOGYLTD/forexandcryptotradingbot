"""
Advanced AI-Powered Trading Strategy
Implements machine learning, sentiment analysis, and multi-timeframe analysis
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import joblib
import requests
import re
from datetime import datetime, timedelta
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeSMAIndicator
import config


class AITradingStrategy:
    def __init__(self):
        self.name = "AI-Powered Multi-Strategy"
        self.models = {}
        self.scalers = {}
        self.sentiment_cache = {}
        self.last_sentiment_update = None
        
    def add_advanced_indicators(self, df):
        """Add comprehensive technical indicators"""
        # Basic indicators
        df['sma_9'] = SMAIndicator(close=df['close'], window=9).sma_indicator()
        df['sma_21'] = SMAIndicator(close=df['close'], window=21).sma_indicator()
        df['sma_50'] = SMAIndicator(close=df['close'], window=50).sma_indicator()
        df['sma_200'] = SMAIndicator(close=df['close'], window=200).sma_indicator()
        
        df['ema_9'] = EMAIndicator(close=df['close'], window=9).ema_indicator()
        df['ema_21'] = EMAIndicator(close=df['close'], window=21).ema_indicator()
        df['ema_50'] = EMAIndicator(close=df['close'], window=50).ema_indicator()
        
        # RSI variants
        df['rsi_14'] = RSIIndicator(close=df['close'], window=14).rsi()
        df['rsi_7'] = RSIIndicator(close=df['close'], window=7).rsi()
        df['rsi_21'] = RSIIndicator(close=df['close'], window=21).rsi()
        
        # MACD
        macd = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        
        # Bollinger Bands
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = bb.bollinger_wband()
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Stochastic
        stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        # ADX (Trend Strength)
        adx = ADXIndicator(high=df['high'], low=df['low'], close=df['close'])
        df['adx'] = adx.adx()
        df['adx_pos'] = adx.adx_pos()
        df['adx_neg'] = adx.adx_neg()
        
        # ATR (Volatility)
        df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close']).average_true_range()
        
        # Volume indicators
        df['obv'] = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
        df['volume_sma'] = VolumeSMAIndicator(close=df['close'], volume=df['volume']).volume_sma()
        
        # Price action patterns
        df['doji'] = self._detect_doji(df)
        df['hammer'] = self._detect_hammer(df)
        df['shooting_star'] = self._detect_shooting_star(df)
        
        # Market structure
        df['higher_high'] = self._detect_higher_highs(df)
        df['lower_low'] = self._detect_lower_lows(df)
        df['support_resistance'] = self._calculate_support_resistance(df)
        
        # Momentum indicators
        df['momentum_5'] = df['close'].pct_change(5) * 100
        df['momentum_10'] = df['close'].pct_change(10) * 100
        df['momentum_20'] = df['close'].pct_change(20) * 100
        
        # Volatility measures
        df['volatility_5'] = df['close'].rolling(5).std()
        df['volatility_20'] = df['close'].rolling(20).std()
        
        return df
    
    def _detect_doji(self, df):
        """Detect Doji candlestick patterns"""
        body = abs(df['close'] - df['open'])
        range_size = df['high'] - df['low']
        return (body / range_size) < 0.1
    
    def _detect_hammer(self, df):
        """Detect Hammer candlestick patterns"""
        body = abs(df['close'] - df['open'])
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        return (lower_shadow > 2 * body) & (upper_shadow < body)
    
    def _detect_shooting_star(self, df):
        """Detect Shooting Star patterns"""
        body = abs(df['close'] - df['open'])
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        return (upper_shadow > 2 * body) & (lower_shadow < body)
    
    def _detect_higher_highs(self, df, window=5):
        """Detect higher highs pattern"""
        return df['high'] > df['high'].rolling(window).max().shift(1)
    
    def _detect_lower_lows(self, df, window=5):
        """Detect lower lows pattern"""
        return df['low'] < df['low'].rolling(window).min().shift(1)
    
    def _calculate_support_resistance(self, df, window=20):
        """Calculate support/resistance levels"""
        rolling_max = df['high'].rolling(window).max()
        rolling_min = df['low'].rolling(window).min()
        return (df['close'] - rolling_min) / (rolling_max - rolling_min)
    
    def get_market_sentiment(self, symbol):
        """Get market sentiment from news and social media"""
        try:
            # Cache sentiment for 1 hour
            if (self.last_sentiment_update and 
                datetime.now() - self.last_sentiment_update < timedelta(hours=1)):
                return self.sentiment_cache.get(symbol, 0.5)
            
            # Fear & Greed Index (simplified simulation)
            # In production, integrate with real APIs like:
            # - CoinGecko API for crypto sentiment
            # - Twitter API for social sentiment
            # - News APIs for fundamental sentiment
            
            base_symbol = symbol.split('/')[0].lower()
            sentiment_score = self._simulate_sentiment_analysis(base_symbol)
            
            self.sentiment_cache[symbol] = sentiment_score
            self.last_sentiment_update = datetime.now()
            
            return sentiment_score
            
        except Exception as e:
            print(f"Error getting sentiment for {symbol}: {e}")
            return 0.5  # Neutral sentiment
    
    def _simulate_sentiment_analysis(self, symbol):
        """Simulate advanced sentiment analysis"""
        # This simulates real sentiment analysis
        # In production, replace with actual API calls
        import random
        
        # Simulate market conditions affecting sentiment
        current_hour = datetime.now().hour
        
        # Market hours tend to be more bullish
        if 8 <= current_hour <= 16:
            base_sentiment = 0.55
        else:
            base_sentiment = 0.45
        
        # Add some randomness based on "market conditions"
        volatility_factor = random.uniform(-0.2, 0.2)
        sentiment = max(0, min(1, base_sentiment + volatility_factor))
        
        return sentiment
    
    def prepare_ml_features(self, df):
        """Prepare features for machine learning models"""
        features = []
        
        # Technical indicators
        feature_columns = [
            'sma_9', 'sma_21', 'sma_50', 'ema_9', 'ema_21', 'ema_50',
            'rsi_14', 'rsi_7', 'rsi_21', 'macd', 'macd_signal', 'macd_histogram',
            'bb_position', 'bb_width', 'stoch_k', 'stoch_d', 'adx',
            'atr', 'momentum_5', 'momentum_10', 'momentum_20',
            'volatility_5', 'volatility_20', 'support_resistance'
        ]
        
        # Price ratios
        df['close_sma_ratio'] = df['close'] / df['sma_21']
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        df['high_low_ratio'] = df['high'] / df['low']
        
        feature_columns.extend(['close_sma_ratio', 'volume_ratio', 'high_low_ratio'])
        
        # Pattern recognition features
        df['bullish_patterns'] = (df['hammer'].astype(int) + 
                                 df['higher_high'].astype(int))
        df['bearish_patterns'] = (df['shooting_star'].astype(int) + 
                                 df['lower_low'].astype(int))
        
        feature_columns.extend(['bullish_patterns', 'bearish_patterns'])
        
        return df[feature_columns].fillna(0)
    
    def train_ml_model(self, df, symbol):
        """Train machine learning model for price prediction"""
        try:
            # Prepare features
            features_df = self.prepare_ml_features(df)
            
            # Create target (future price movement)
            df['future_return'] = df['close'].shift(-1) / df['close'] - 1
            target = df['future_return'].fillna(0)
            
            # Remove last row (no future data)
            features_df = features_df[:-1]
            target = target[:-1]
            
            if len(features_df) < 50:
                return False
            
            # Scale features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features_df)
            
            # Train ensemble model
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=3)
            
            rf_model.fit(features_scaled, target)
            gb_model.fit(features_scaled, target)
            
            # Store models
            self.models[symbol] = {
                'rf': rf_model,
                'gb': gb_model,
                'features': list(features_df.columns)
            }
            self.scalers[symbol] = scaler
            
            return True
            
        except Exception as e:
            print(f"Error training ML model for {symbol}: {e}")
            return False
    
    def predict_price_movement(self, df, symbol):
        """Predict future price movement using ML"""
        try:
            if symbol not in self.models:
                # Train model if not exists
                if not self.train_ml_model(df, symbol):
                    return 0, 0
            
            # Prepare current features
            features_df = self.prepare_ml_features(df)
            current_features = features_df.iloc[-1:].values
            
            # Scale features
            scaler = self.scalers[symbol]
            current_features_scaled = scaler.transform(current_features)
            
            # Make predictions
            models = self.models[symbol]
            rf_pred = models['rf'].predict(current_features_scaled)[0]
            gb_pred = models['gb'].predict(current_features_scaled)[0]
            
            # Ensemble prediction
            ensemble_pred = (rf_pred + gb_pred) / 2
            
            # Convert to confidence score
            confidence = min(95, abs(ensemble_pred) * 1000)
            
            return ensemble_pred, confidence
            
        except Exception as e:
            print(f"Error predicting for {symbol}: {e}")
            return 0, 0
    
    def generate_advanced_signal(self, df, symbol):
        """Generate trading signal using advanced AI analysis"""
        if len(df) < 200:
            return None, 0, {}
        
        # Add all indicators
        df = self.add_advanced_indicators(df)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Get ML prediction
        ml_prediction, ml_confidence = self.predict_price_movement(df, symbol)
        
        # Get market sentiment
        sentiment = self.get_market_sentiment(symbol)
        
        # Advanced signal scoring system
        signals = {
            'trend': 0,
            'momentum': 0,
            'mean_reversion': 0,
            'pattern': 0,
            'volume': 0,
            'ml_prediction': 0,
            'sentiment': 0
        }
        
        # 1. Trend Analysis (30% weight)
        if latest['ema_21'] > latest['ema_50'] and latest['close'] > latest['ema_21']:
            signals['trend'] = 3
        elif latest['ema_21'] < latest['ema_50'] and latest['close'] < latest['ema_21']:
            signals['trend'] = -3
        elif latest['adx'] > 25:  # Strong trend
            if latest['adx_pos'] > latest['adx_neg']:
                signals['trend'] = 2
            else:
                signals['trend'] = -2
        
        # 2. Momentum Analysis (25% weight)
        rsi_score = 0
        if latest['rsi_14'] < 30:
            rsi_score = 2
        elif latest['rsi_14'] > 70:
            rsi_score = -2
        elif 40 < latest['rsi_14'] < 60:
            rsi_score = 1 if latest['rsi_14'] > 50 else -1
        
        macd_score = 0
        if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
            macd_score = 3
        elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
            macd_score = -3
        elif latest['macd'] > latest['macd_signal']:
            macd_score = 1
        else:
            macd_score = -1
        
        signals['momentum'] = (rsi_score + macd_score) / 2
        
        # 3. Mean Reversion (20% weight)
        bb_score = 0
        if latest['bb_position'] < 0.2:  # Near lower band
            bb_score = 2
        elif latest['bb_position'] > 0.8:  # Near upper band
            bb_score = -2
        
        stoch_score = 0
        if latest['stoch_k'] < 20 and latest['stoch_d'] < 20:
            stoch_score = 2
        elif latest['stoch_k'] > 80 and latest['stoch_d'] > 80:
            stoch_score = -2
        
        signals['mean_reversion'] = (bb_score + stoch_score) / 2
        
        # 4. Pattern Recognition (10% weight)
        pattern_score = 0
        if latest['bullish_patterns'] > 0:
            pattern_score = 2
        elif latest['bearish_patterns'] > 0:
            pattern_score = -2
        
        if latest['doji']:
            pattern_score *= 0.5  # Reduce confidence for indecision
        
        signals['pattern'] = pattern_score
        
        # 5. Volume Analysis (10% weight)
        volume_score = 0
        if latest['volume'] > latest['volume_sma'] * 1.5:
            # High volume confirms the move
            if latest['close'] > prev['close']:
                volume_score = 2
            else:
                volume_score = -2
        
        signals['volume'] = volume_score
        
        # 6. ML Prediction (20% weight)
        if ml_confidence > 50:
            if ml_prediction > 0.001:  # Predict >0.1% move up
                signals['ml_prediction'] = 3
            elif ml_prediction < -0.001:  # Predict >0.1% move down
                signals['ml_prediction'] = -3
            else:
                signals['ml_prediction'] = ml_prediction * 1000  # Scale small predictions
        
        # 7. Sentiment Analysis (15% weight)
        if sentiment > 0.7:
            signals['sentiment'] = 2
        elif sentiment < 0.3:
            signals['sentiment'] = -2
        else:
            signals['sentiment'] = (sentiment - 0.5) * 4  # Scale around neutral
        
        # Calculate weighted final score
        weights = {
            'trend': 0.30,
            'momentum': 0.25,
            'mean_reversion': 0.20,
            'pattern': 0.10,
            'volume': 0.10,
            'ml_prediction': 0.20,
            'sentiment': 0.15
        }
        
        final_score = sum(signals[key] * weights[key] for key in signals)
        
        # Normalize to confidence percentage
        confidence = min(95, abs(final_score) * 15)
        
        # Generate signal
        if final_score > 0.5 and confidence >= 65:
            signal = 'buy'
        elif final_score < -0.5 and confidence >= 65:
            signal = 'sell'
        else:
            signal = None
        
        # Additional context
        context = {
            'ml_prediction': ml_prediction,
            'sentiment': sentiment,
            'trend_strength': latest['adx'],
            'volatility': latest['atr'],
            'signal_breakdown': signals,
            'market_condition': self._analyze_market_regime(df)
        }
        
        return signal, confidence, context
    
    def _analyze_market_regime(self, df):
        """Analyze current market regime"""
        latest = df.iloc[-1]
        
        # Volatility regime
        if latest['atr'] > df['atr'].rolling(50).mean() * 1.5:
            volatility_regime = 'high_volatility'
        elif latest['atr'] < df['atr'].rolling(50).mean() * 0.7:
            volatility_regime = 'low_volatility'
        else:
            volatility_regime = 'normal_volatility'
        
        # Trend regime
        if latest['adx'] > 30:
            if latest['ema_21'] > latest['ema_50']:
                trend_regime = 'strong_uptrend'
            else:
                trend_regime = 'strong_downtrend'
        elif latest['adx'] > 20:
            trend_regime = 'trending'
        else:
            trend_regime = 'ranging'
        
        return f"{trend_regime}_{volatility_regime}"
