"""
Complete OKX Crypto Payment Handler
Handles subscription payments using admin OKX account
"""
import ccxt
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import config
from mongodb_database import MongoTradingDatabase

class OKXPaymentHandler:
    """Handle crypto payments through admin OKX account"""
    
    def __init__(self):
        self.db = MongoTradingDatabase()
        self.exchange = ccxt.okx({
            'apiKey': config.OKX_API_KEY,
            'secret': config.OKX_SECRET_KEY,
            'password': config.OKX_PASSPHRASE,
            'enableRateLimit': True
        })
        
        # Plan prices in USD
        self.plan_prices = {
            'pro': 29,
            'enterprise': 99
        }
        
        # Supported cryptocurrencies
        self.supported_cryptos = ['BTC', 'ETH', 'USDT', 'USDC', 'SOL', 'BNB']
    
    def generate_payment_id(self, user_id: str, plan: str) -> str:
        """Generate unique payment ID"""
        timestamp = str(int(time.time()))
        data = f"{user_id}_{plan}_{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get_crypto_price(self, crypto: str) -> float:
        """Get current crypto price in USD"""
        # Stablecoins are always $1
        if crypto in ['USDT', 'USDC', 'DAI', 'BUSD']:
            return 1.0
            
        try:
            ticker = self.exchange.fetch_ticker(f'{crypto}/USDT')
            return ticker['last']
        except Exception as e:
            print(f"Error fetching {crypto} price: {e}")
            # Fallback prices
            fallback_prices = {
                'BTC': 45000,
                'ETH': 3000,
                'SOL': 100,
                'BNB': 300,
            }
            return fallback_prices.get(crypto, 1)
    
    def calculate_crypto_amount(self, plan: str, crypto: str) -> float:
        """Calculate how much crypto user needs to send"""
        usd_amount = self.plan_prices[plan]
        crypto_price = self.get_crypto_price(crypto)
        crypto_amount = usd_amount / crypto_price
        
        # Add 1% buffer for price fluctuations
        crypto_amount = crypto_amount * 1.01
        
        return round(crypto_amount, 8)
    
    def get_all_usdt_networks(self) -> List[Dict]:
        """Get all supported USDT networks on OKX"""
        return [
            {'network': 'TRC20', 'name': 'Tron (TRC20)', 'fee': 'Low (~1 USDT)', 'okx_name': 'USDT-TRC20'},
            {'network': 'ERC20', 'name': 'Ethereum (ERC20)', 'fee': 'High (~5-20 USDT)', 'okx_name': 'USDT-ERC20'},
            {'network': 'BEP20', 'name': 'BSC (BEP20)', 'fee': 'Low (~0.5 USDT)', 'okx_name': 'USDT-BSC'},
            {'network': 'Polygon', 'name': 'Polygon (MATIC)', 'fee': 'Very Low (~0.1 USDT)', 'okx_name': 'USDT-Polygon'},
            {'network': 'Arbitrum', 'name': 'Arbitrum One', 'fee': 'Low (~1 USDT)', 'okx_name': 'USDT-Arbitrum One'},
            {'network': 'Optimism', 'name': 'Optimism', 'fee': 'Low (~1 USDT)', 'okx_name': 'USDT-Optimism'},
            {'network': 'Avalanche', 'name': 'Avalanche C-Chain', 'fee': 'Low (~0.5 USDT)', 'okx_name': 'USDT-Avalanche C-Chain'},
        ]
    
    def create_deposit_address(self, crypto: str, network: str = None) -> Dict:
        """Get deposit address for crypto from admin OKX account"""
        try:
            # OKX network mapping - EXACT names from OKX API
            # Note: OKX uses just the network name, NOT "USDT-NetworkName" format!
            okx_network_map = {
                'TRC20': 'TRC20',
                'ERC20': 'ERC20',
                'BEP20': 'BSC',  # OKX calls it just "BSC"!
                'Polygon': 'Polygon',
                'Arbitrum': 'Arbitrum One',
                'Optimism': 'Optimism',
                'Avalanche': 'Avalanche C-Chain',
                'BSC': 'BSC',
            }
            
            # Default networks for each crypto
            default_networks = {
                'BTC': 'Bitcoin',
                'ETH': 'ERC20',
                'USDT': 'TRC20',  # Default to TRC20 (lowest fees)
                'USDC': 'ERC20',
                'SOL': 'Solana',
                'BNB': 'BSC'
            }
            
            # Use provided network or default
            selected_network = network or default_networks.get(crypto, 'TRC20')
            
            # Map to OKX's actual network name if it's USDT
            if crypto == 'USDT' and selected_network in okx_network_map:
                okx_network_name = okx_network_map[selected_network]
            else:
                okx_network_name = selected_network
            
            print(f"🔍 Fetching deposit address: {crypto} on {okx_network_name}")
            
            # Fetch deposit address with network
            deposit_address = self.exchange.fetch_deposit_address(crypto, {'network': okx_network_name})
            
            return {
                'address': deposit_address['address'],
                'tag': deposit_address.get('tag'),
                'network': selected_network,
                'crypto': crypto
            }
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error creating deposit address for {crypto} on {network}: {error_msg}")
            
            # Check if it's a network name issue
            if 'network' in error_msg.lower() or 'chain' in error_msg.lower():
                return {
                    'address': 'ERROR_INVALID_NETWORK',
                    'tag': None,
                    'network': network,
                    'crypto': crypto,
                    'error': f'Network "{network}" not supported by OKX. Please try TRC20, ERC20, or Polygon.'
                }
            
            # Check if it's an API credentials issue
            if 'api' in error_msg.lower() or 'auth' in error_msg.lower() or 'key' in error_msg.lower():
                return {
                    'address': 'ERROR_API_SETUP',
                    'tag': None,
                    'network': network,
                    'crypto': crypto,
                    'error': 'OKX API not configured. Contact support: ceo@gideonstechnology.com'
                }
            
            # General error
            return {
                'address': 'ERROR_CONTACT_SUPPORT',
                'tag': None,
                'network': network,
                'crypto': crypto,
                'error': f'Unable to generate address. Error: {error_msg}. Contact support.'
            }
    
    def initialize_payment(self, user_id: str, plan: str, crypto: str, network: str = None) -> Dict:
        """Initialize a new crypto payment"""
        
        # Validate inputs
        if plan not in self.plan_prices:
            raise ValueError(f"Invalid plan: {plan}")
        
        if crypto not in self.supported_cryptos:
            raise ValueError(f"Unsupported cryptocurrency: {crypto}")
        
        # Generate payment ID
        payment_id = self.generate_payment_id(user_id, plan)
        
        # Calculate amount
        crypto_amount = self.calculate_crypto_amount(plan, crypto)
        usd_amount = self.plan_prices[plan]
        
        # Get deposit address with specified network
        deposit_info = self.create_deposit_address(crypto, network)
        
        # Create payment record
        payment_record = {
            'payment_id': payment_id,
            'user_id': user_id,
            'plan': plan,
            'amount_usd': usd_amount,
            'crypto_currency': crypto,
            'crypto_amount': crypto_amount,
            'deposit_address': deposit_info['address'],
            'deposit_tag': deposit_info['tag'],
            'network': deposit_info['network'],
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=2),  # 2 hour expiry
            'confirmed': False
        }
        
        # Save to database
        self.db.db['payments'].insert_one(payment_record)
        
        return {
            'payment_id': payment_id,
            'deposit_address': deposit_info['address'],
            'deposit_tag': deposit_info['tag'],
            'network': deposit_info['network'],
            'crypto_currency': crypto,
            'crypto_amount': crypto_amount,
            'amount_usd': usd_amount,
            'expires_in_seconds': 7200,
            'instructions': self._get_payment_instructions(crypto, deposit_info)
        }
    
    def _get_payment_instructions(self, crypto: str, deposit_info: Dict) -> str:
        """Get payment instructions for user"""
        instructions = f"""
        Payment Instructions:
        
        1. Send EXACTLY {crypto} to the address below
        2. Network: {deposit_info['network']}
        3. Address: {deposit_info['address']}
        """
        
        if deposit_info['tag']:
            instructions += f"\n4. IMPORTANT: Include Memo/Tag: {deposit_info['tag']}"
        
        instructions += """
        
        5. Payment will be confirmed automatically within 10-30 minutes
        6. Your subscription will activate immediately after confirmation
        
        ⚠️ WARNING: 
        - Send only {crypto} to this address
        - Use the correct network
        - Include the memo/tag if required
        - Payment expires in 2 hours
        """
        
        return instructions
    
    def check_payment_status(self, payment_id: str) -> Dict:
        """Check if payment has been received"""
        
        # Get payment record
        payment = self.db.db['payments'].find_one({'payment_id': payment_id})
        
        if not payment:
            return {'status': 'not_found'}
        
        if payment['status'] == 'completed':
            return {'status': 'completed', 'confirmed': True}
        
        if datetime.utcnow() > payment['expires_at']:
            # Payment expired
            self.db.db['payments'].update_one(
                {'payment_id': payment_id},
                {'$set': {'status': 'expired'}}
            )
            return {'status': 'expired'}
        
        # Check for deposits
        try:
            deposits = self.exchange.fetch_deposits(
                code=payment['crypto_currency'],
                since=int(payment['created_at'].timestamp() * 1000)
            )
            
            # Look for matching deposit
            for deposit in deposits:
                if self._is_matching_deposit(deposit, payment):
                    # Payment found!
                    return self._confirm_payment(payment_id, deposit)
            
            return {'status': 'pending', 'confirmed': False}
            
        except Exception as e:
            print(f"Error checking deposits: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _is_matching_deposit(self, deposit: Dict, payment: Dict) -> bool:
        """Check if deposit matches payment"""
        
        # Check address
        if deposit.get('address') != payment['deposit_address']:
            return False
        
        # Check tag/memo if required
        if payment['deposit_tag'] and deposit.get('tag') != payment['deposit_tag']:
            return False
        
        # Check amount (allow 2% variance for fees)
        expected_amount = payment['crypto_amount']
        received_amount = deposit['amount']
        
        if received_amount < expected_amount * 0.98:
            return False
        
        # Check status
        if deposit['status'] not in ['ok', 'confirmed']:
            return False
        
        return True
    
    def _confirm_payment(self, payment_id: str, deposit: Dict) -> Dict:
        """Confirm payment and activate subscription"""
        
        payment = self.db.db['payments'].find_one({'payment_id': payment_id})
        
        # Update payment status
        self.db.db['payments'].update_one(
            {'payment_id': payment_id},
            {'$set': {
                'status': 'completed',
                'confirmed': True,
                'confirmed_at': datetime.utcnow(),
                'tx_hash': deposit.get('txid'),
                'received_amount': deposit['amount']
            }}
        )
        
        # Activate user subscription
        self.db.db['users'].update_one(
            {'_id': payment['user_id']},
            {'$set': {
                'subscription': payment['plan'],
                'subscription_active': True,
                'subscription_start': datetime.utcnow(),
                'subscription_expires': datetime.utcnow() + timedelta(days=30),
                'last_payment_date': datetime.utcnow(),
                'last_payment_amount': payment['amount_usd']
            }}
        )
        
        return {
            'status': 'completed',
            'confirmed': True,
            'plan': payment['plan'],
            'tx_hash': deposit.get('txid')
        }
    
    def check_all_pending_payments(self):
        """Background job to check all pending payments"""
        
        pending_payments = self.db.db['payments'].find({
            'status': 'pending',
            'expires_at': {'$gt': datetime.utcnow()}
        })
        
        confirmed_count = 0
        
        for payment in pending_payments:
            result = self.check_payment_status(payment['payment_id'])
            if result['status'] == 'completed':
                confirmed_count += 1
                print(f"✅ Payment confirmed: {payment['payment_id']}")
        
        return confirmed_count
    
    def get_payment_history(self, user_id: str) -> list:
        """Get user's payment history"""
        
        payments = list(self.db.db['payments'].find(
            {'user_id': user_id},
            {'_id': 0}
        ).sort('created_at', -1))
        
        return payments
    
    def cancel_payment(self, payment_id: str) -> bool:
        """Cancel a pending payment"""
        
        result = self.db.db['payments'].update_one(
            {'payment_id': payment_id, 'status': 'pending'},
            {'$set': {'status': 'cancelled', 'cancelled_at': datetime.utcnow()}}
        )
        
        return result.modified_count > 0


# Singleton instance
payment_handler = OKXPaymentHandler()
