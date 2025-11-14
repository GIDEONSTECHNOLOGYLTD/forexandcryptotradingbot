"""
MongoDB Database Integration
Much easier than SQL - no complex queries needed!
Uses MongoDB Atlas (free cloud database) or local MongoDB
"""
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import os
from colorama import Fore, Style


class MongoTradingDatabase:
    def __init__(self, connection_string=None):
        """
        Initialize MongoDB connection
        
        Options:
        1. MongoDB Atlas (Free Cloud): Get connection string from mongodb.com/cloud/atlas
        2. Local MongoDB: mongodb://localhost:27017/
        
        Set in .env:
        MONGODB_URI=your_connection_string_here
        """
        # Get connection string from environment or parameter
        self.connection_string = connection_string or os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        
        try:
            # Connect to MongoDB
            self.client = MongoClient(self.connection_string)
            
            # Create/use database
            self.db = self.client['trading_bot']
            
            # Collections (like tables in SQL, but easier!)
            self.trades = self.db['trades']
            self.performance = self.db['performance']
            self.signals = self.db['signals']
            self.strategy_performance = self.db['strategy_performance']
            
            # Test connection
            self.client.server_info()
            
            # Create indexes for faster queries
            self._create_indexes()
            
            print(f"{Fore.GREEN}✅ MongoDB connected successfully!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ MongoDB connection failed: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Make sure MongoDB is running or check your connection string{Style.RESET_ALL}")
            raise
    
    def _create_indexes(self):
        """Create indexes for faster queries"""
        # Index on symbol for faster lookups
        self.trades.create_index('symbol')
        self.trades.create_index('status')
        self.trades.create_index('entry_time')
        
        self.signals.create_index('symbol')
        self.signals.create_index('timestamp')
        
        self.performance.create_index('date', unique=True)
    
    def save_trade(self, trade_data):
        """
        Save a new trade - Super easy with MongoDB!
        Just pass a dictionary, no SQL needed
        """
        try:
            # Add timestamp
            trade_data['created_at'] = datetime.now()
            trade_data['status'] = 'open'
            
            # Insert into MongoDB (that's it!)
            result = self.trades.insert_one(trade_data)
            
            print(f"{Fore.GREEN}✅ Trade saved: {result.inserted_id}{Style.RESET_ALL}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving trade: {e}{Style.RESET_ALL}")
            return None
    
    def update_trade(self, symbol, exit_data):
        """
        Update trade when closed - Easy!
        """
        try:
            # Find open trade for this symbol
            result = self.trades.update_one(
                {'symbol': symbol, 'status': 'open'},
                {
                    '$set': {
                        'exit_price': exit_data['exit_price'],
                        'exit_time': exit_data['exit_time'],
                        'pnl': exit_data['pnl'],
                        'pnl_percent': exit_data['pnl_percent'],
                        'exit_reason': exit_data.get('exit_reason', 'manual'),
                        'status': 'closed',
                        'updated_at': datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"{Fore.GREEN}✅ Trade updated for {symbol}{Style.RESET_ALL}")
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error updating trade: {e}{Style.RESET_ALL}")
            return False
    
    def get_trades(self, limit=100, status=None):
        """
        Get trades - Super simple!
        """
        try:
            # Build query
            query = {}
            if status:
                query['status'] = status
            
            # Get trades (sorted by newest first)
            trades = list(self.trades.find(query).sort('entry_time', -1).limit(limit))
            
            # Convert to DataFrame for easy viewing
            if trades:
                df = pd.DataFrame(trades)
                # Remove MongoDB _id for cleaner display
                if '_id' in df.columns:
                    df['_id'] = df['_id'].astype(str)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting trades: {e}{Style.RESET_ALL}")
            return pd.DataFrame()
    
    def get_open_trades(self):
        """Get all open trades"""
        return self.get_trades(status='open')
    
    def get_closed_trades(self, limit=100):
        """Get closed trades"""
        return self.get_trades(limit=limit, status='closed')
    
    def save_performance_snapshot(self, stats):
        """
        Save daily performance - Easy with MongoDB!
        """
        try:
            # MongoDB needs datetime, not date!
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Upsert (update if exists, insert if not)
            self.performance.update_one(
                {'date': today},
                {
                    '$set': {
                        'capital': stats['current_capital'],
                        'daily_pnl': stats['daily_pnl'],
                        'total_trades': stats['total_trades'],
                        'winning_trades': stats['winning_trades'],
                        'losing_trades': stats['losing_trades'],
                        'win_rate': stats['win_rate'],
                        'profit_factor': stats['profit_factor'],
                        'updated_at': datetime.now()
                    }
                },
                upsert=True
            )
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving performance: {e}{Style.RESET_ALL}")
    
    def get_performance_history(self, days=30):
        """Get performance history"""
        try:
            # Get last N days
            performances = list(
                self.performance.find()
                .sort('date', -1)
                .limit(days)
            )
            
            if performances:
                df = pd.DataFrame(performances)
                if '_id' in df.columns:
                    df['_id'] = df['_id'].astype(str)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting performance: {e}{Style.RESET_ALL}")
            return pd.DataFrame()
    
    def save_signal(self, signal_data):
        """
        Save trading signal - Just pass a dictionary!
        """
        try:
            signal_data['timestamp'] = datetime.now()
            result = self.signals.insert_one(signal_data)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving signal: {e}{Style.RESET_ALL}")
            return None
    
    def get_signals(self, symbol=None, limit=100):
        """Get trading signals"""
        try:
            query = {}
            if symbol:
                query['symbol'] = symbol
            
            signals = list(
                self.signals.find(query)
                .sort('timestamp', -1)
                .limit(limit)
            )
            
            if signals:
                df = pd.DataFrame(signals)
                if '_id' in df.columns:
                    df['_id'] = df['_id'].astype(str)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting signals: {e}{Style.RESET_ALL}")
            return pd.DataFrame()
    
    def update_strategy_performance(self, strategy_name, symbol, success):
        """Update strategy performance metrics"""
        try:
            # Find existing record
            existing = self.strategy_performance.find_one({
                'strategy_name': strategy_name,
                'symbol': symbol
            })
            
            if existing:
                # Update existing
                total = existing['total_signals'] + 1
                successful = existing['successful_signals'] + (1 if success else 0)
                win_rate = (successful / total) * 100
                
                self.strategy_performance.update_one(
                    {'strategy_name': strategy_name, 'symbol': symbol},
                    {
                        '$set': {
                            'total_signals': total,
                            'successful_signals': successful,
                            'win_rate': win_rate,
                            'last_updated': datetime.now()
                        }
                    }
                )
            else:
                # Create new
                self.strategy_performance.insert_one({
                    'strategy_name': strategy_name,
                    'symbol': symbol,
                    'total_signals': 1,
                    'successful_signals': 1 if success else 0,
                    'win_rate': 100 if success else 0,
                    'last_updated': datetime.now()
                })
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error updating strategy: {e}{Style.RESET_ALL}")
    
    def get_strategy_performance(self):
        """Get strategy performance metrics"""
        try:
            strategies = list(
                self.strategy_performance.find()
                .sort('win_rate', -1)
            )
            
            if strategies:
                df = pd.DataFrame(strategies)
                if '_id' in df.columns:
                    df['_id'] = df['_id'].astype(str)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting strategy performance: {e}{Style.RESET_ALL}")
            return pd.DataFrame()
    
    def get_statistics(self):
        """
        Get comprehensive statistics - MongoDB makes this easy!
        """
        try:
            # Use MongoDB aggregation (powerful but simple)
            pipeline = [
                {'$match': {'status': 'closed'}},
                {'$group': {
                    '_id': None,
                    'total_trades': {'$sum': 1},
                    'total_pnl': {'$sum': '$pnl'},
                    'winning_trades': {
                        '$sum': {'$cond': [{'$gt': ['$pnl', 0]}, 1, 0]}
                    },
                    'avg_win': {
                        '$avg': {'$cond': [{'$gt': ['$pnl', 0]}, '$pnl', None]}
                    },
                    'avg_loss': {
                        '$avg': {'$cond': [{'$lt': ['$pnl', 0]}, '$pnl', None]}
                    }
                }}
            ]
            
            result = list(self.trades.aggregate(pipeline))
            
            if result:
                stats = result[0]
                total_trades = stats['total_trades']
                winning_trades = stats['winning_trades']
                losing_trades = total_trades - winning_trades
                
                # Calculate profit factor
                wins = list(self.trades.find({'status': 'closed', 'pnl': {'$gt': 0}}))
                losses = list(self.trades.find({'status': 'closed', 'pnl': {'$lt': 0}}))
                
                total_wins = sum(t['pnl'] for t in wins) if wins else 0
                total_losses = abs(sum(t['pnl'] for t in losses)) if losses else 1
                
                return {
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                    'total_pnl': stats['total_pnl'],
                    'avg_win': stats['avg_win'] or 0,
                    'avg_loss': stats['avg_loss'] or 0,
                    'profit_factor': total_wins / total_losses if total_losses > 0 else 0
                }
            else:
                return {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0,
                    'total_pnl': 0,
                    'avg_win': 0,
                    'avg_loss': 0,
                    'profit_factor': 0
                }
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting statistics: {e}{Style.RESET_ALL}")
            return {}
    
    def export_to_csv(self, collection_name, filename=None):
        """Export collection to CSV"""
        try:
            if filename is None:
                filename = f"{collection_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Get collection
            collection = self.db[collection_name]
            data = list(collection.find())
            
            if data:
                df = pd.DataFrame(data)
                # Convert ObjectId to string
                if '_id' in df.columns:
                    df['_id'] = df['_id'].astype(str)
                
                df.to_csv(filename, index=False)
                print(f"{Fore.GREEN}✅ Exported {collection_name} to {filename}{Style.RESET_ALL}")
                return filename
            else:
                print(f"{Fore.YELLOW}⚠️  No data to export{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error exporting: {e}{Style.RESET_ALL}")
            return None
    
    def cleanup_old_data(self, days=90):
        """Clean up old signals"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            result = self.signals.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
            print(f"{Fore.YELLOW}🗑️  Cleaned up {result.deleted_count} old signals{Style.RESET_ALL}")
            return result.deleted_count
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error cleaning up: {e}{Style.RESET_ALL}")
            return 0
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        print(f"{Fore.YELLOW}MongoDB connection closed{Style.RESET_ALL}")


# Example usage and setup guide
if __name__ == "__main__":
    print(f"{Fore.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║              MONGODB DATABASE SETUP GUIDE                          ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Option 1: MongoDB Atlas (Free Cloud - Recommended){Style.RESET_ALL}")
    print("1. Go to: https://www.mongodb.com/cloud/atlas")
    print("2. Sign up for free account")
    print("3. Create a free cluster (M0 - Free tier)")
    print("4. Click 'Connect' → 'Connect your application'")
    print("5. Copy the connection string")
    print("6. Add to .env file:")
    print("   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/")
    
    print(f"\n{Fore.YELLOW}Option 2: Local MongoDB{Style.RESET_ALL}")
    print("1. Install MongoDB: https://www.mongodb.com/try/download/community")
    print("2. Start MongoDB service")
    print("3. Add to .env file:")
    print("   MONGODB_URI=mongodb://localhost:27017/")
    
    print(f"\n{Fore.GREEN}Testing MongoDB Connection...{Style.RESET_ALL}")
    
    try:
        # Try to connect
        db = MongoTradingDatabase()
        
        # Test save
        print(f"\n{Fore.CYAN}Testing save trade...{Style.RESET_ALL}")
        trade = {
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'entry_price': 43250.50,
            'amount': 0.0046,
            'entry_time': datetime.now(),
            'stop_loss': 42385.49,
            'take_profit': 44980.52,
            'confidence': 75.0
        }
        
        trade_id = db.save_trade(trade)
        print(f"{Fore.GREEN}✅ Trade saved with ID: {trade_id}{Style.RESET_ALL}")
        
        # Test get trades
        print(f"\n{Fore.CYAN}Getting trades...{Style.RESET_ALL}")
        trades = db.get_trades(limit=10)
        print(trades)
        
        # Test statistics
        print(f"\n{Fore.CYAN}Getting statistics...{Style.RESET_ALL}")
        stats = db.get_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        db.close()
        
        print(f"\n{Fore.GREEN}✅ MongoDB is working perfectly!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}You can now use MongoDB instead of SQLite{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ MongoDB setup needed{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Follow the setup guide above{Style.RESET_ALL}")
