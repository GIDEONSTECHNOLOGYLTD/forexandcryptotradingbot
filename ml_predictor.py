"""
Machine Learning Predictor for Trading Bot
Uses multiple ML models to predict price movements
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MLPredictor:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boost': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = []
        
    def prepare_features(self, df):
        """Prepare features for ML model"""
        features = pd.DataFrame()
        
        # Price features
        features['returns'] = df['close'].pct_change()
        features['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Volatility features
        features['volatility'] = df['close'].rolling(window=20).std()
        features['volatility_ratio'] = features['volatility'] / features['volatility'].rolling(window=50).mean()
        
        # Momentum features
        features['momentum_5'] = df['close'] / df['close'].shift(5) - 1
        features['momentum_10'] = df['close'] / df['close'].shift(10) - 1
        features['momentum_20'] = df['close'] / df['close'].shift(20) - 1
        
        # Moving averages
        features['sma_5'] = df['close'].rolling(window=5).mean()
        features['sma_20'] = df['close'].rolling(window=20).mean()
        features['sma_50'] = df['close'].rolling(window=50).mean()
        features['sma_ratio_5_20'] = features['sma_5'] / features['sma_20']
        features['sma_ratio_20_50'] = features['sma_20'] / features['sma_50']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        features['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        features['macd'] = exp1 - exp2
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
        features['macd_diff'] = features['macd'] - features['macd_signal']
        
        # Bollinger Bands
        features['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        features['bb_upper'] = features['bb_middle'] + (bb_std * 2)
        features['bb_lower'] = features['bb_middle'] - (bb_std * 2)
        features['bb_position'] = (df['close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
        
        # Volume features (if available)
        if 'volume' in df.columns:
            features['volume_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
            features['volume_momentum'] = df['volume'] / df['volume'].shift(5)
        
        # Time features
        if isinstance(df.index, pd.DatetimeIndex):
            features['hour'] = df.index.hour
            features['day_of_week'] = df.index.dayofweek
            features['day_of_month'] = df.index.day
        
        # Drop NaN values
        features = features.fillna(method='ffill').fillna(0)
        
        return features
    
    def create_labels(self, df, forward_periods=5, threshold=0.02):
        """Create labels for training (1 = buy, 0 = hold, -1 = sell)"""
        future_returns = df['close'].shift(-forward_periods) / df['close'] - 1
        
        labels = np.where(future_returns > threshold, 1,
                         np.where(future_returns < -threshold, -1, 0))
        
        return labels
    
    def train(self, historical_data, symbol):
        """Train ML models on historical data"""
        try:
            logger.info(f"Training ML models for {symbol}...")
            
            # Prepare features and labels
            features = self.prepare_features(historical_data)
            labels = self.create_labels(historical_data)
            
            # Remove last few rows (no future data for labels)
            features = features[:-5]
            labels = labels[:-5]
            
            # Store feature columns
            self.feature_columns = features.columns.tolist()
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, shuffle=False
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train each model
            scores = {}
            for name, model in self.models.items():
                model.fit(X_train_scaled, y_train)
                score = model.score(X_test_scaled, y_test)
                scores[name] = score
                logger.info(f"{name} accuracy: {score:.4f}")
            
            self.is_trained = True
            
            # Save models
            self.save_models(symbol)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error training ML models: {e}")
            return {}
    
    def predict(self, current_data):
        """Predict next move using ensemble of models"""
        if not self.is_trained:
            return None, 0.0
        
        try:
            # Prepare features
            features = self.prepare_features(current_data)
            
            # Get last row
            X = features.iloc[-1:][self.feature_columns]
            X_scaled = self.scaler.transform(X)
            
            # Get predictions from all models
            predictions = []
            probabilities = []
            
            for name, model in self.models.items():
                pred = model.predict(X_scaled)[0]
                predictions.append(pred)
                
                # Get probability if available
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(X_scaled)[0]
                    probabilities.append(proba)
            
            # Ensemble prediction (majority vote)
            ensemble_pred = np.sign(np.mean(predictions))
            
            # Average confidence
            if probabilities:
                avg_proba = np.mean(probabilities, axis=0)
                confidence = np.max(avg_proba)
            else:
                confidence = 0.6
            
            # Convert to signal
            if ensemble_pred > 0:
                signal = 'buy'
            elif ensemble_pred < 0:
                signal = 'sell'
            else:
                signal = 'hold'
            
            return signal, confidence
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return None, 0.0
    
    def get_feature_importance(self):
        """Get feature importance from Random Forest"""
        if not self.is_trained:
            return {}
        
        rf_model = self.models['random_forest']
        importance = dict(zip(self.feature_columns, rf_model.feature_importances_))
        
        # Sort by importance
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        
        return importance
    
    def save_models(self, symbol):
        """Save trained models to disk"""
        try:
            joblib.dump(self.models, f'models/ml_models_{symbol}.pkl')
            joblib.dump(self.scaler, f'models/scaler_{symbol}.pkl')
            joblib.dump(self.feature_columns, f'models/features_{symbol}.pkl')
            logger.info(f"Models saved for {symbol}")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self, symbol):
        """Load trained models from disk"""
        try:
            self.models = joblib.load(f'models/ml_models_{symbol}.pkl')
            self.scaler = joblib.load(f'models/scaler_{symbol}.pkl')
            self.feature_columns = joblib.load(f'models/features_{symbol}.pkl')
            self.is_trained = True
            logger.info(f"Models loaded for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False


class SentimentAnalyzer:
    """Analyze market sentiment from news and social media"""
    
    def __init__(self):
        self.sentiment_sources = []
        
    def analyze_news_sentiment(self, symbol):
        """Analyze news sentiment for a symbol"""
        # Placeholder for news API integration
        # Can integrate with: NewsAPI, CryptoPanic, etc.
        return 0.0  # Neutral
    
    def analyze_social_sentiment(self, symbol):
        """Analyze social media sentiment"""
        # Placeholder for Twitter/Reddit API integration
        return 0.0  # Neutral
    
    def get_overall_sentiment(self, symbol):
        """Get combined sentiment score"""
        news_sentiment = self.analyze_news_sentiment(symbol)
        social_sentiment = self.analyze_social_sentiment(symbol)
        
        # Weighted average
        overall = (news_sentiment * 0.6) + (social_sentiment * 0.4)
        
        return overall


class MarketRegimeDetector:
    """Detect current market regime (trending, ranging, volatile)"""
    
    def __init__(self):
        self.regimes = ['trending_up', 'trending_down', 'ranging', 'volatile']
    
    def detect_regime(self, df):
        """Detect current market regime"""
        # Calculate indicators
        returns = df['close'].pct_change()
        volatility = returns.rolling(window=20).std()
        
        # Trend strength (ADX-like)
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        
        # Moving averages
        sma_20 = df['close'].rolling(window=20).mean()
        sma_50 = df['close'].rolling(window=50).mean()
        
        # Current values
        current_price = df['close'].iloc[-1]
        current_vol = volatility.iloc[-1]
        avg_vol = volatility.mean()
        
        # Detect regime
        if current_vol > avg_vol * 1.5:
            regime = 'volatile'
        elif current_price > sma_20.iloc[-1] > sma_50.iloc[-1]:
            regime = 'trending_up'
        elif current_price < sma_20.iloc[-1] < sma_50.iloc[-1]:
            regime = 'trending_down'
        else:
            regime = 'ranging'
        
        return regime
    
    def get_regime_strategy(self, regime):
        """Get recommended strategy for current regime"""
        strategies = {
            'trending_up': 'momentum',
            'trending_down': 'mean_reversion',
            'ranging': 'mean_reversion',
            'volatile': 'breakout'
        }
        
        return strategies.get(regime, 'momentum')
