"""
Performance Optimization Module
Hyperparameter tuning, strategy optimization, and performance enhancement
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import itertools
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')


class PerformanceOptimizer:
    def __init__(self):
        self.optimization_results = {}
        self.best_parameters = {}
        
    def optimize_strategy_parameters(self, df, symbol, strategy_class, param_grid):
        """Optimize strategy parameters using grid search"""
        print(f"\n🔧 Optimizing strategy parameters for {symbol}")
        print("="*60)
        
        try:
            # Prepare data
            if len(df) < 200:
                print("❌ Insufficient data for optimization")
                return None
            
            # Split data for optimization
            train_size = int(len(df) * 0.7)
            train_data = df.iloc[:train_size]
            test_data = df.iloc[train_size:]
            
            best_score = -np.inf
            best_params = None
            results = []
            
            # Generate parameter combinations
            param_combinations = list(itertools.product(*param_grid.values()))
            param_names = list(param_grid.keys())
            
            print(f"Testing {len(param_combinations)} parameter combinations...")
            
            for i, param_values in enumerate(param_combinations):
                params = dict(zip(param_names, param_values))
                
                # Test parameters
                score = self._test_strategy_parameters(train_data, test_data, strategy_class, params)
                
                results.append({
                    'parameters': params.copy(),
                    'score': score,
                    'rank': 0  # Will be filled later
                })
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                
                if (i + 1) % 10 == 0:
                    print(f"Progress: {i+1}/{len(param_combinations)} combinations tested")
            
            # Rank results
            results.sort(key=lambda x: x['score'], reverse=True)
            for i, result in enumerate(results):
                result['rank'] = i + 1
            
            # Store results
            self.optimization_results[symbol] = {
                'best_parameters': best_params,
                'best_score': best_score,
                'all_results': results[:20],  # Top 20 results
                'optimization_date': datetime.now()
            }
            
            self._display_optimization_results(symbol, best_params, best_score, results[:5])
            
            return best_params
            
        except Exception as e:
            print(f"Error optimizing parameters for {symbol}: {e}")
            return None
    
    def _test_strategy_parameters(self, train_data, test_data, strategy_class, params):
        """Test strategy with given parameters"""
        try:
            # Initialize strategy with parameters
            strategy = strategy_class(**params)
            
            # Add indicators to training data
            train_data_with_indicators = strategy.add_indicators(train_data.copy())
            
            # Simulate trading on test data
            capital = 10000
            trades = []
            
            for i in range(50, len(test_data)):  # Start after indicators stabilize
                current_data = test_data.iloc[:i+1]
                current_data_with_indicators = strategy.add_indicators(current_data.copy())
                
                signal, confidence = strategy.generate_signal(current_data_with_indicators)
                
                if signal and confidence >= 60:
                    # Simulate trade
                    entry_price = test_data.iloc[i]['close']
                    
                    # Look for exit in next 10 periods
                    exit_found = False
                    for j in range(i+1, min(i+11, len(test_data))):
                        exit_price = test_data.iloc[j]['close']
                        
                        if signal == 'buy':
                            pnl_percent = (exit_price - entry_price) / entry_price
                        else:
                            pnl_percent = (entry_price - exit_price) / entry_price
                        
                        # Exit conditions
                        if pnl_percent > 0.02 or pnl_percent < -0.01:  # 2% profit or 1% loss
                            trades.append(pnl_percent)
                            exit_found = True
                            break
                    
                    if not exit_found and i+10 < len(test_data):
                        # Force exit after 10 periods
                        exit_price = test_data.iloc[i+10]['close']
                        if signal == 'buy':
                            pnl_percent = (exit_price - entry_price) / entry_price
                        else:
                            pnl_percent = (entry_price - exit_price) / entry_price
                        trades.append(pnl_percent)
            
            # Calculate performance score
            if not trades:
                return -1
            
            total_return = sum(trades)
            win_rate = len([t for t in trades if t > 0]) / len(trades)
            avg_win = np.mean([t for t in trades if t > 0]) if any(t > 0 for t in trades) else 0
            avg_loss = np.mean([t for t in trades if t <= 0]) if any(t <= 0 for t in trades) else 0
            
            # Composite score
            score = (
                total_return * 100 +  # Total return weight
                win_rate * 50 +      # Win rate weight
                len(trades) * 0.1    # Number of trades (more is slightly better)
            )
            
            # Penalty for high losses
            if avg_loss < -0.05:  # More than 5% average loss
                score *= 0.5
            
            return score
            
        except Exception as e:
            return -1
    
    def _display_optimization_results(self, symbol, best_params, best_score, top_results):
        """Display optimization results"""
        print(f"\n✅ Optimization Results for {symbol}")
        print("-" * 50)
        print(f"Best Score: {best_score:.2f}")
        print(f"Best Parameters: {best_params}")
        
        print(f"\nTop 5 Parameter Combinations:")
        for i, result in enumerate(top_results):
            print(f"{i+1}. Score: {result['score']:.2f} | Params: {result['parameters']}")
    
    def optimize_ml_model(self, df, symbol, target_column='future_return'):
        """Optimize machine learning model hyperparameters"""
        print(f"\n🤖 Optimizing ML model for {symbol}")
        print("="*50)
        
        try:
            # Prepare features and target
            from ai_strategy import AITradingStrategy
            strategy = AITradingStrategy()
            
            # Add indicators
            df_with_indicators = strategy.add_advanced_indicators(df.copy())
            features_df = strategy.prepare_ml_features(df_with_indicators)
            
            # Create target variable
            df_with_indicators['future_return'] = df_with_indicators['close'].shift(-1) / df_with_indicators['close'] - 1
            target = df_with_indicators['future_return'].fillna(0)[:-1]
            features_df = features_df[:-1]
            
            if len(features_df) < 100:
                print("❌ Insufficient data for ML optimization")
                return None
            
            # Split data
            train_size = int(len(features_df) * 0.8)
            X_train = features_df.iloc[:train_size]
            y_train = target.iloc[:train_size]
            X_test = features_df.iloc[train_size:]
            y_test = target.iloc[train_size:]
            
            # Define parameter grid for Random Forest
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'max_features': ['sqrt', 'log2', None]
            }
            
            # Perform randomized search
            rf = RandomForestRegressor(random_state=42)
            random_search = RandomizedSearchCV(
                rf, param_grid, n_iter=20, cv=3, 
                scoring='neg_mean_squared_error', random_state=42
            )
            
            print("Running randomized search...")
            random_search.fit(X_train, y_train)
            
            # Get best model
            best_model = random_search.best_estimator_
            
            # Evaluate on test set
            train_score = best_model.score(X_train, y_train)
            test_score = best_model.score(X_test, y_test)
            
            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': X_train.columns,
                'importance': best_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Store results
            self.best_parameters[f"{symbol}_ml"] = {
                'best_params': random_search.best_params_,
                'train_score': train_score,
                'test_score': test_score,
                'feature_importance': feature_importance.head(10).to_dict(),
                'model_path': f"models/{symbol}_optimized_model.joblib"
            }
            
            # Save model
            import os
            os.makedirs('models', exist_ok=True)
            joblib.dump(best_model, f"models/{symbol}_optimized_model.joblib")
            
            print(f"✅ ML Model Optimization Complete")
            print(f"Best Parameters: {random_search.best_params_}")
            print(f"Train Score: {train_score:.4f}")
            print(f"Test Score: {test_score:.4f}")
            print(f"Top Features: {feature_importance.head(5)['feature'].tolist()}")
            
            return random_search.best_params_
            
        except Exception as e:
            print(f"Error optimizing ML model for {symbol}: {e}")
            return None
    
    def optimize_risk_parameters(self, historical_trades):
        """Optimize risk management parameters based on historical performance"""
        print(f"\n⚖️ Optimizing Risk Management Parameters")
        print("="*50)
        
        try:
            if len(historical_trades) < 50:
                print("❌ Insufficient trade history for risk optimization")
                return None
            
            # Convert trades to DataFrame
            trades_df = pd.DataFrame(historical_trades)
            
            # Define parameter ranges to test
            stop_loss_range = [0.01, 0.015, 0.02, 0.025, 0.03]
            take_profit_range = [0.02, 0.03, 0.04, 0.05, 0.06]
            position_size_range = [0.01, 0.015, 0.02, 0.025, 0.03]
            
            best_score = -np.inf
            best_params = None
            results = []
            
            for stop_loss in stop_loss_range:
                for take_profit in take_profit_range:
                    for position_size in position_size_range:
                        # Simulate trades with these parameters
                        score = self._simulate_risk_parameters(
                            trades_df, stop_loss, take_profit, position_size
                        )
                        
                        params = {
                            'stop_loss_percent': stop_loss * 100,
                            'take_profit_percent': take_profit * 100,
                            'position_size_percent': position_size * 100
                        }
                        
                        results.append({
                            'parameters': params,
                            'score': score
                        })
                        
                        if score > best_score:
                            best_score = score
                            best_params = params
            
            # Sort results
            results.sort(key=lambda x: x['score'], reverse=True)
            
            print(f"✅ Risk Optimization Complete")
            print(f"Best Score: {best_score:.2f}")
            print(f"Best Parameters: {best_params}")
            print(f"\nTop 3 Parameter Combinations:")
            for i, result in enumerate(results[:3]):
                print(f"{i+1}. Score: {result['score']:.2f} | Params: {result['parameters']}")
            
            return best_params
            
        except Exception as e:
            print(f"Error optimizing risk parameters: {e}")
            return None
    
    def _simulate_risk_parameters(self, trades_df, stop_loss, take_profit, position_size):
        """Simulate trading with given risk parameters"""
        try:
            total_return = 0
            max_drawdown = 0
            peak_capital = 10000
            current_capital = 10000
            
            for _, trade in trades_df.iterrows():
                # Apply position sizing
                trade_return = trade.get('pnl_percent', 0) / 100
                
                # Apply stop loss and take profit
                if trade_return < -stop_loss:
                    trade_return = -stop_loss
                elif trade_return > take_profit:
                    trade_return = take_profit
                
                # Apply position sizing
                position_return = trade_return * position_size
                current_capital += current_capital * position_return
                
                # Track drawdown
                if current_capital > peak_capital:
                    peak_capital = current_capital
                
                drawdown = (peak_capital - current_capital) / peak_capital
                max_drawdown = max(max_drawdown, drawdown)
            
            # Calculate score
            total_return = (current_capital - 10000) / 10000
            
            # Penalize high drawdown
            if max_drawdown > 0.2:  # More than 20% drawdown
                score = total_return - (max_drawdown * 2)
            else:
                score = total_return - max_drawdown
            
            return score
            
        except Exception as e:
            return -1
    
    def run_comprehensive_optimization(self, df, symbol):
        """Run comprehensive optimization across all components"""
        print(f"\n🚀 Running Comprehensive Optimization for {symbol}")
        print("="*70)
        
        optimization_results = {}
        
        # 1. Strategy Parameter Optimization
        print("\n1️⃣ Strategy Parameter Optimization")
        strategy_param_grid = {
            'rsi_period': [10, 14, 18, 21],
            'rsi_oversold': [25, 30, 35],
            'rsi_overbought': [65, 70, 75],
            'sma_fast': [15, 20, 25],
            'sma_slow': [45, 50, 55],
            'confidence_threshold': [60, 65, 70, 75]
        }
        
        # Note: This would require refactoring the strategy class to accept parameters
        # For now, we'll simulate the optimization
        print("Strategy optimization completed (simulated)")
        optimization_results['strategy'] = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'confidence_threshold': 65
        }
        
        # 2. ML Model Optimization
        print("\n2️⃣ Machine Learning Model Optimization")
        ml_params = self.optimize_ml_model(df, symbol)
        optimization_results['ml_model'] = ml_params
        
        # 3. Risk Parameter Optimization (simulated with sample data)
        print("\n3️⃣ Risk Management Optimization")
        # Generate sample trades for demonstration
        sample_trades = []
        for i in range(100):
            pnl_percent = np.random.normal(0.5, 3.0)  # 0.5% average return, 3% volatility
            sample_trades.append({'pnl_percent': pnl_percent})
        
        risk_params = self.optimize_risk_parameters(sample_trades)
        optimization_results['risk_management'] = risk_params
        
        # 4. Generate Optimization Report
        self._generate_optimization_report(symbol, optimization_results)
        
        return optimization_results
    
    def _generate_optimization_report(self, symbol, results):
        """Generate comprehensive optimization report"""
        print(f"\n📊 OPTIMIZATION REPORT FOR {symbol}")
        print("="*70)
        
        print(f"🎯 Strategy Parameters:")
        if results.get('strategy'):
            for param, value in results['strategy'].items():
                print(f"   • {param}: {value}")
        
        print(f"\n🤖 ML Model Parameters:")
        if results.get('ml_model'):
            for param, value in results['ml_model'].items():
                print(f"   • {param}: {value}")
        
        print(f"\n⚖️ Risk Management Parameters:")
        if results.get('risk_management'):
            for param, value in results['risk_management'].items():
                print(f"   • {param}: {value}")
        
        print(f"\n✅ Optimization completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save results
        import json
        with open(f'optimization_results_{symbol.replace("/", "_")}.json', 'w') as f:
            # Convert numpy types to native Python types for JSON serialization
            json_results = self._convert_to_json_serializable(results)
            json.dump(json_results, f, indent=2, default=str)
        
        print(f"📁 Results saved to optimization_results_{symbol.replace('/', '_')}.json")
    
    def _convert_to_json_serializable(self, obj):
        """Convert numpy types to JSON serializable types"""
        if isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    def load_optimized_parameters(self, symbol):
        """Load previously optimized parameters"""
        try:
            import json
            filename = f'optimization_results_{symbol.replace("/", "_")}.json'
            
            with open(filename, 'r') as f:
                results = json.load(f)
            
            print(f"✅ Loaded optimized parameters for {symbol}")
            return results
            
        except FileNotFoundError:
            print(f"⚠️ No optimization results found for {symbol}")
            return None
        except Exception as e:
            print(f"❌ Error loading optimization results: {e}")
            return None
    
    def continuous_optimization(self, symbols, optimization_interval_days=7):
        """Run continuous optimization for multiple symbols"""
        print(f"\n🔄 Starting Continuous Optimization")
        print(f"Symbols: {symbols}")
        print(f"Optimization Interval: {optimization_interval_days} days")
        print("="*60)
        
        last_optimization = {}
        
        while True:
            try:
                current_time = datetime.now()
                
                for symbol in symbols:
                    # Check if optimization is needed
                    if symbol not in last_optimization:
                        needs_optimization = True
                    else:
                        time_since_last = current_time - last_optimization[symbol]
                        needs_optimization = time_since_last.days >= optimization_interval_days
                    
                    if needs_optimization:
                        print(f"\n🔧 Optimizing {symbol}...")
                        
                        # Fetch fresh data (simulated)
                        # In production, fetch real market data
                        df = self._generate_sample_data(symbol)
                        
                        # Run optimization
                        results = self.run_comprehensive_optimization(df, symbol)
                        
                        if results:
                            last_optimization[symbol] = current_time
                            print(f"✅ {symbol} optimization completed")
                        else:
                            print(f"❌ {symbol} optimization failed")
                
                # Wait before next check (1 hour)
                print(f"\n⏳ Waiting 1 hour before next optimization check...")
                time.sleep(3600)
                
            except KeyboardInterrupt:
                print(f"\n🛑 Continuous optimization stopped")
                break
            except Exception as e:
                print(f"❌ Error in continuous optimization: {e}")
                time.sleep(300)  # Wait 5 minutes before retry
    
    def _generate_sample_data(self, symbol, days=365):
        """Generate sample market data for testing"""
        # This is the same as in advanced_backtester.py
        np.random.seed(42)
        
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                             end=datetime.now(), freq='1H')
        
        base_price = 100.0
        returns = np.random.normal(0.0001, 0.02, len(dates))
        
        prices = [base_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        df = pd.DataFrame(index=dates)
        df['close'] = prices
        df['open'] = df['close'].shift(1).fillna(df['close'].iloc[0])
        
        volatility = np.random.uniform(0.005, 0.02, len(df))
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + volatility)
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - volatility)
        df['volume'] = np.random.uniform(1000000, 10000000, len(df))
        
        return df
