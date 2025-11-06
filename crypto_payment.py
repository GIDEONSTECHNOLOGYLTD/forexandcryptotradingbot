"""
Cryptocurrency Payment Integration
Accept Bitcoin, Ethereum, USDT, and other cryptocurrencies
Using CoinGate, NOWPayments, or direct wallet integration
"""
import requests
import os
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import hashlib
import hmac
from colorama import Fore, Style

# CoinGate Configuration (Popular crypto payment gateway)
COINGATE_API_KEY = os.getenv('COINGATE_API_KEY', '')
COINGATE_BASE_URL = 'https://api.coingate.com/v2'

# NOWPayments Configuration (Alternative)
NOWPAYMENTS_API_KEY = os.getenv('NOWPAYMENTS_API_KEY', '')
NOWPAYMENTS_BASE_URL = 'https://api.nowpayments.io/v1'

# Supported Cryptocurrencies
SUPPORTED_CRYPTOS = {
    'BTC': {'name': 'Bitcoin', 'symbol': '₿', 'decimals': 8},
    'ETH': {'name': 'Ethereum', 'symbol': 'Ξ', 'decimals': 18},
    'USDT': {'name': 'Tether', 'symbol': 'USDT', 'decimals': 6},
    'USDC': {'name': 'USD Coin', 'symbol': 'USDC', 'decimals': 6},
    'BNB': {'name': 'Binance Coin', 'symbol': 'BNB', 'decimals': 18},
    'LTC': {'name': 'Litecoin', 'symbol': 'Ł', 'decimals': 8},
}

# Subscription Plans (in USD)
CRYPTO_PLANS = {
    'pro': {
        'name': 'Pro Plan',
        'price_usd': 29,
        'interval': 'monthly'
    },
    'enterprise': {
        'name': 'Enterprise Plan',
        'price_usd': 99,
        'interval': 'monthly'
    }
}


class CryptoPaymentProcessor:
    """Handle cryptocurrency payments using multiple gateways"""
    
    def __init__(self, gateway: str = 'coingate'):
        """
        Initialize crypto payment processor
        
        Args:
            gateway: 'coingate' or 'nowpayments'
        """
        self.gateway = gateway
        
        if gateway == 'coingate':
            self.api_key = COINGATE_API_KEY
            self.base_url = COINGATE_BASE_URL
        elif gateway == 'nowpayments':
            self.api_key = NOWPAYMENTS_API_KEY
            self.base_url = NOWPAYMENTS_BASE_URL
        else:
            raise ValueError(f"Unsupported gateway: {gateway}")
            
        self.headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json'
        }
        
    def create_payment(
        self,
        amount_usd: float,
        currency: str,
        order_id: str,
        callback_url: str = None,
        success_url: str = None,
        cancel_url: str = None
    ) -> Optional[Dict]:
        """
        Create a cryptocurrency payment
        
        Args:
            amount_usd: Amount in USD
            currency: Crypto currency (BTC, ETH, USDT, etc.)
            order_id: Unique order identifier
            callback_url: IPN callback URL
            success_url: Success redirect URL
            cancel_url: Cancel redirect URL
            
        Returns:
            Payment details with payment URL
        """
        if self.gateway == 'coingate':
            return self._create_coingate_payment(
                amount_usd, currency, order_id,
                callback_url, success_url, cancel_url
            )
        elif self.gateway == 'nowpayments':
            return self._create_nowpayments_payment(
                amount_usd, currency, order_id, callback_url
            )
            
    def _create_coingate_payment(
        self,
        amount_usd: float,
        currency: str,
        order_id: str,
        callback_url: str,
        success_url: str,
        cancel_url: str
    ) -> Optional[Dict]:
        """Create CoinGate payment"""
        url = f'{self.base_url}/orders'
        
        data = {
            'order_id': order_id,
            'price_amount': amount_usd,
            'price_currency': 'USD',
            'receive_currency': currency,
            'callback_url': callback_url,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'title': 'Trading Bot Subscription',
            'description': f'Payment for trading bot subscription'
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}✅ Payment created: {result['id']}{Style.RESET_ALL}")
                return {
                    'payment_id': result['id'],
                    'payment_url': result['payment_url'],
                    'status': result['status'],
                    'amount': result['price_amount'],
                    'currency': result['price_currency'],
                    'receive_currency': result['receive_currency'],
                    'created_at': result['created_at']
                }
            else:
                print(f"{Fore.RED}❌ Error: {result.get('message')}{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            return None
            
    def _create_nowpayments_payment(
        self,
        amount_usd: float,
        currency: str,
        order_id: str,
        callback_url: str
    ) -> Optional[Dict]:
        """Create NOWPayments payment"""
        url = f'{self.base_url}/payment'
        
        data = {
            'price_amount': amount_usd,
            'price_currency': 'usd',
            'pay_currency': currency.lower(),
            'order_id': order_id,
            'ipn_callback_url': callback_url,
            'order_description': 'Trading Bot Subscription'
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            result = response.json()
            
            if 'payment_id' in result:
                print(f"{Fore.GREEN}✅ Payment created: {result['payment_id']}{Style.RESET_ALL}")
                return {
                    'payment_id': result['payment_id'],
                    'payment_url': result['invoice_url'],
                    'status': result['payment_status'],
                    'amount': result['pay_amount'],
                    'currency': result['pay_currency'].upper(),
                    'address': result['pay_address']
                }
            else:
                print(f"{Fore.RED}❌ Error: {result.get('message')}{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            return None
            
    def verify_payment(self, payment_id: str) -> Optional[Dict]:
        """
        Verify payment status
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment status details
        """
        if self.gateway == 'coingate':
            url = f'{self.base_url}/orders/{payment_id}'
        elif self.gateway == 'nowpayments':
            url = f'{self.base_url}/payment/{payment_id}'
            
        try:
            response = requests.get(url, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200:
                status = result.get('status') or result.get('payment_status')
                print(f"{Fore.GREEN}✅ Payment status: {status}{Style.RESET_ALL}")
                return result
            else:
                print(f"{Fore.RED}❌ Error verifying payment{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            return None
            
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Get exchange rate between currencies
        
        Args:
            from_currency: Source currency (e.g., 'USD')
            to_currency: Target currency (e.g., 'BTC')
            
        Returns:
            Exchange rate
        """
        if self.gateway == 'coingate':
            url = f'{self.base_url}/rates/merchant/{from_currency}/{to_currency}'
        else:
            url = f'{self.base_url}/estimate?amount=1&currency_from={from_currency}&currency_to={to_currency}'
            
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                if self.gateway == 'coingate':
                    return float(response.text.strip('"'))
                else:
                    result = response.json()
                    return float(result['estimated_amount'])
            else:
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            return None
            
    def calculate_crypto_amount(self, usd_amount: float, crypto_currency: str) -> Optional[float]:
        """
        Calculate crypto amount for USD price
        
        Args:
            usd_amount: Amount in USD
            crypto_currency: Cryptocurrency code
            
        Returns:
            Amount in cryptocurrency
        """
        rate = self.get_exchange_rate('USD', crypto_currency)
        if rate:
            return usd_amount * rate
        return None


# Direct Wallet Integration (for advanced users)
class DirectWalletPayment:
    """Direct wallet-to-wallet payments"""
    
    def __init__(self):
        """Initialize direct wallet payments"""
        self.wallets = {
            'BTC': os.getenv('BTC_WALLET_ADDRESS', ''),
            'ETH': os.getenv('ETH_WALLET_ADDRESS', ''),
            'USDT_ERC20': os.getenv('USDT_ERC20_ADDRESS', ''),
            'USDT_TRC20': os.getenv('USDT_TRC20_ADDRESS', ''),
        }
        
    def generate_payment_request(
        self,
        amount_usd: float,
        crypto_currency: str,
        order_id: str
    ) -> Optional[Dict]:
        """
        Generate payment request with wallet address
        
        Returns:
            Payment details with wallet address and amount
        """
        wallet_address = self.wallets.get(crypto_currency)
        
        if not wallet_address:
            print(f"{Fore.RED}❌ No wallet configured for {crypto_currency}{Style.RESET_ALL}")
            return None
            
        # Get current exchange rate
        processor = CryptoPaymentProcessor()
        crypto_amount = processor.calculate_crypto_amount(amount_usd, crypto_currency)
        
        if not crypto_amount:
            return None
            
        return {
            'order_id': order_id,
            'wallet_address': wallet_address,
            'amount_usd': amount_usd,
            'amount_crypto': crypto_amount,
            'currency': crypto_currency,
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat(),
            'instructions': f'Send {crypto_amount} {crypto_currency} to {wallet_address}'
        }


# Example usage
if __name__ == "__main__":
    processor = CryptoPaymentProcessor(gateway='coingate')
    
    print("\n" + "="*70)
    print("₿ Cryptocurrency Payment Integration")
    print("="*70)
    print("\n💰 Supported Cryptocurrencies:")
    
    for code, info in SUPPORTED_CRYPTOS.items():
        print(f"  {info['symbol']} {code} - {info['name']}")
    
    print("\n📊 Subscription Plans:")
    for plan_id, plan in CRYPTO_PLANS.items():
        print(f"\n{plan['name']}")
        print(f"  Price: ${plan['price_usd']}/{plan['interval']}")
        print(f"  Pay with: BTC, ETH, USDT, or any supported crypto")
    
    print("\n" + "="*70)
    print("⚙️  Setup Instructions:")
    print("="*70)
    print("\n📍 Option 1: CoinGate (Recommended)")
    print("1. Create account: https://coingate.com/")
    print("2. Get API credentials from Dashboard")
    print("3. Add to .env: COINGATE_API_KEY=your_api_key")
    
    print("\n📍 Option 2: NOWPayments")
    print("1. Create account: https://nowpayments.io/")
    print("2. Get API key from Settings")
    print("3. Add to .env: NOWPAYMENTS_API_KEY=your_api_key")
    
    print("\n📍 Option 3: Direct Wallet (Advanced)")
    print("1. Create crypto wallets (BTC, ETH, USDT)")
    print("2. Add addresses to .env:")
    print("   BTC_WALLET_ADDRESS=your_btc_address")
    print("   ETH_WALLET_ADDRESS=your_eth_address")
    
    print("\n✨ Benefits:")
    print("  • Global payments (no country restrictions)")
    print("  • Low fees (1-3% vs 2.9% + $0.30)")
    print("  • Fast settlements (crypto transfers)")
    print("  • Anonymous payments (privacy)")
    print("  • Perfect for crypto traders!")
    
    print("\n" + "="*70 + "\n")
