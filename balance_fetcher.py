"""
Real-time balance fetcher for OKX accounts
Shows admin balance and user balances
"""
import ccxt
from cryptography.fernet import Fernet
import config
from mongodb_database import MongoTradingDatabase

class BalanceFetcher:
    """Fetch real-time balances from OKX"""
    
    def __init__(self):
        self.db = MongoTradingDatabase()
        self.encryption_key = config.ENCRYPTION_KEY.encode()
        self.fernet = Fernet(self.encryption_key)
    
    def get_admin_balance(self):
        """Get admin OKX account balance"""
        try:
            exchange = ccxt.okx({
                'apiKey': config.OKX_API_KEY,
                'secret': config.OKX_SECRET_KEY,
                'password': config.OKX_PASSPHRASE,
                'enableRateLimit': True
            })
            
            balance = exchange.fetch_balance()
            
            # Get total balance in USDT
            total_usdt = balance['total'].get('USDT', 0)
            
            # Get all non-zero balances
            assets = {}
            for currency, amount in balance['total'].items():
                if amount > 0:
                    assets[currency] = {
                        'total': amount,
                        'free': balance['free'].get(currency, 0),
                        'used': balance['used'].get(currency, 0)
                    }
            
            return {
                'success': True,
                'total_usdt': total_usdt,
                'assets': assets,
                'account_type': 'admin'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'account_type': 'admin'
            }
    
    def get_user_balance(self, user_id: str):
        """Get user's OKX account balance"""
        try:
            # Get user from database
            user = self.db.db['users'].find_one({'_id': user_id})
            
            if not user or not user.get('exchange_connected'):
                return {
                    'success': False,
                    'error': 'Exchange not connected',
                    'account_type': 'user'
                }
            
            # Decrypt user's API keys
            api_key = self.fernet.decrypt(user['okx_api_key'].encode()).decode()
            secret_key = self.fernet.decrypt(user['okx_secret_key'].encode()).decode()
            passphrase = self.fernet.decrypt(user['okx_passphrase'].encode()).decode()
            
            # Connect to user's OKX account
            exchange = ccxt.okx({
                'apiKey': api_key,
                'secret': secret_key,
                'password': passphrase,
                'enableRateLimit': True
            })
            
            balance = exchange.fetch_balance()
            
            # Get total balance in USDT
            total_usdt = balance['total'].get('USDT', 0)
            
            # Get all non-zero balances
            assets = {}
            for currency, amount in balance['total'].items():
                if amount > 0:
                    assets[currency] = {
                        'total': amount,
                        'free': balance['free'].get(currency, 0),
                        'used': balance['used'].get(currency, 0)
                    }
            
            return {
                'success': True,
                'total_usdt': total_usdt,
                'assets': assets,
                'account_type': 'user',
                'paper_trading': user.get('paper_trading', True)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'account_type': 'user'
            }

# Singleton instance
balance_fetcher = BalanceFetcher()
