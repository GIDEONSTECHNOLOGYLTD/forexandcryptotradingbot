"""
Database Integration
Persistent storage for trades, performance, and analytics
"""
import sqlite3
import pandas as pd
from datetime import datetime
import json
from colorama import Fore, Style


class TradingDatabase:
    def __init__(self, db_path='trading_bot.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        print(f"{Fore.GREEN}✅ Database initialized: {db_path}{Style.RESET_ALL}")
    
    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                amount REAL NOT NULL,
                entry_time TIMESTAMP NOT NULL,
                exit_time TIMESTAMP,
                stop_loss REAL,
                take_profit REAL,
                pnl REAL,
                pnl_percent REAL,
                confidence REAL,
                exit_reason TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance table (daily snapshots)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                capital REAL NOT NULL,
                daily_pnl REAL,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                win_rate REAL,
                profit_factor REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                signal TEXT NOT NULL,
                confidence REAL NOT NULL,
                price REAL NOT NULL,
                indicators TEXT,
                market_condition TEXT,
                executed BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Strategy performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                total_signals INTEGER DEFAULT 0,
                successful_signals INTEGER DEFAULT 0,
                win_rate REAL,
                avg_pnl REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def save_trade(self, trade_data):
        """Save a new trade"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                symbol, side, entry_price, amount, entry_time,
                stop_loss, take_profit, confidence, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data['symbol'],
            trade_data['side'],
            trade_data['entry_price'],
            trade_data['amount'],
            trade_data['entry_time'],
            trade_data.get('stop_loss'),
            trade_data.get('take_profit'),
            trade_data.get('confidence', 0),
            'open'
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def update_trade(self, symbol, exit_data):
        """Update trade when closed"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE trades
            SET exit_price = ?,
                exit_time = ?,
                pnl = ?,
                pnl_percent = ?,
                exit_reason = ?,
                status = 'closed'
            WHERE symbol = ? AND status = 'open'
        ''', (
            exit_data['exit_price'],
            exit_data['exit_time'],
            exit_data['pnl'],
            exit_data['pnl_percent'],
            exit_data.get('exit_reason', 'manual'),
            symbol
        ))
        
        self.conn.commit()
    
    def get_trades(self, limit=100, status=None):
        """Get trades from database"""
        query = "SELECT * FROM trades"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY entry_time DESC LIMIT ?"
        params.append(limit)
        
        df = pd.read_sql_query(query, self.conn, params=params)
        return df
    
    def get_open_trades(self):
        """Get all open trades"""
        return self.get_trades(status='open')
    
    def save_performance_snapshot(self, stats):
        """Save daily performance snapshot"""
        cursor = self.conn.cursor()
        
        today = datetime.now().date()
        
        cursor.execute('''
            INSERT OR REPLACE INTO performance (
                date, capital, daily_pnl, total_trades,
                winning_trades, losing_trades, win_rate, profit_factor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            today,
            stats['current_capital'],
            stats['daily_pnl'],
            stats['total_trades'],
            stats['winning_trades'],
            stats['losing_trades'],
            stats['win_rate'],
            stats['profit_factor']
        ))
        
        self.conn.commit()
    
    def get_performance_history(self, days=30):
        """Get performance history"""
        query = '''
            SELECT * FROM performance
            ORDER BY date DESC
            LIMIT ?
        '''
        df = pd.read_sql_query(query, self.conn, params=(days,))
        return df
    
    def save_signal(self, signal_data):
        """Save trading signal"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO signals (
                symbol, signal, confidence, price,
                indicators, market_condition, executed
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal_data['symbol'],
            signal_data['signal'],
            signal_data['confidence'],
            signal_data['price'],
            json.dumps(signal_data.get('indicators', {})),
            signal_data.get('market_condition'),
            signal_data.get('executed', False)
        ))
        
        self.conn.commit()
    
    def get_signals(self, symbol=None, limit=100):
        """Get trading signals"""
        query = "SELECT * FROM signals"
        params = []
        
        if symbol:
            query += " WHERE symbol = ?"
            params.append(symbol)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        df = pd.read_sql_query(query, self.conn, params=params)
        return df
    
    def update_strategy_performance(self, strategy_name, symbol, success):
        """Update strategy performance metrics"""
        cursor = self.conn.cursor()
        
        # Get current stats
        cursor.execute('''
            SELECT total_signals, successful_signals
            FROM strategy_performance
            WHERE strategy_name = ? AND symbol = ?
        ''', (strategy_name, symbol))
        
        result = cursor.fetchone()
        
        if result:
            total = result[0] + 1
            successful = result[1] + (1 if success else 0)
            win_rate = (successful / total) * 100
            
            cursor.execute('''
                UPDATE strategy_performance
                SET total_signals = ?,
                    successful_signals = ?,
                    win_rate = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE strategy_name = ? AND symbol = ?
            ''', (total, successful, win_rate, strategy_name, symbol))
        else:
            cursor.execute('''
                INSERT INTO strategy_performance (
                    strategy_name, symbol, total_signals,
                    successful_signals, win_rate
                ) VALUES (?, ?, 1, ?, ?)
            ''', (strategy_name, symbol, 1 if success else 0, 100 if success else 0))
        
        self.conn.commit()
    
    def get_strategy_performance(self):
        """Get strategy performance metrics"""
        query = "SELECT * FROM strategy_performance ORDER BY win_rate DESC"
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def get_statistics(self):
        """Get comprehensive statistics"""
        cursor = self.conn.cursor()
        
        # Total trades
        cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'closed'")
        total_trades = cursor.fetchone()[0]
        
        # Winning trades
        cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'closed' AND pnl > 0")
        winning_trades = cursor.fetchone()[0]
        
        # Total PnL
        cursor.execute("SELECT SUM(pnl) FROM trades WHERE status = 'closed'")
        total_pnl = cursor.fetchone()[0] or 0
        
        # Average win/loss
        cursor.execute("SELECT AVG(pnl) FROM trades WHERE status = 'closed' AND pnl > 0")
        avg_win = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT AVG(pnl) FROM trades WHERE status = 'closed' AND pnl < 0")
        avg_loss = cursor.fetchone()[0] or 0
        
        # Win rate
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Profit factor
        cursor.execute("SELECT SUM(pnl) FROM trades WHERE status = 'closed' AND pnl > 0")
        total_wins = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(ABS(pnl)) FROM trades WHERE status = 'closed' AND pnl < 0")
        total_losses = cursor.fetchone()[0] or 1
        
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
    
    def export_to_csv(self, table_name, filename=None):
        """Export table to CSV"""
        if filename is None:
            filename = f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
        df.to_csv(filename, index=False)
        print(f"{Fore.GREEN}✅ Exported {table_name} to {filename}{Style.RESET_ALL}")
        return filename
    
    def cleanup_old_data(self, days=90):
        """Clean up old data"""
        cursor = self.conn.cursor()
        
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        
        cursor.execute('''
            DELETE FROM signals
            WHERE timestamp < ?
        ''', (cutoff_date,))
        
        deleted = cursor.rowcount
        self.conn.commit()
        
        print(f"{Fore.YELLOW}🗑️  Cleaned up {deleted} old signals{Style.RESET_ALL}")
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print(f"{Fore.YELLOW}Database connection closed{Style.RESET_ALL}")


# Example usage
if __name__ == "__main__":
    db = TradingDatabase()
    
    # Example: Save a trade
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
    
    # Get trades
    trades = db.get_trades(limit=10)
    print(f"\n{Fore.CYAN}Recent Trades:{Style.RESET_ALL}")
    print(trades)
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\n{Fore.CYAN}Statistics:{Style.RESET_ALL}")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    db.close()
