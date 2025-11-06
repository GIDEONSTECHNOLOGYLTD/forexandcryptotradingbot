"""
PayStack Payment Integration
For African markets - Nigeria, Ghana, South Africa, Kenya, etc.
"""
import requests
import os
from typing import Optional, Dict
from datetime import datetime
from colorama import Fore, Style
import config

# PayStack Configuration
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY', '')
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY', '')
PAYSTACK_BASE_URL = 'https://api.paystack.co'

# Subscription Plans (in Kobo for NGN, cents for other currencies)
PAYSTACK_PLANS = {
    'pro_ngn': {
        'name': 'Pro Plan (Nigeria)',
        'amount': 1500000,  # ₦15,000 (NGN)
        'currency': 'NGN',
        'interval': 'monthly',
        'plan_code': os.getenv('PAYSTACK_PRO_NGN_CODE', '')
    },
    'pro_usd': {
        'name': 'Pro Plan (USD)',
        'amount': 2900,  # $29.00
        'currency': 'USD',
        'interval': 'monthly',
        'plan_code': os.getenv('PAYSTACK_PRO_USD_CODE', '')
    },
    'enterprise_ngn': {
        'name': 'Enterprise Plan (Nigeria)',
        'amount': 5000000,  # ₦50,000 (NGN)
        'currency': 'NGN',
        'interval': 'monthly',
        'plan_code': os.getenv('PAYSTACK_ENTERPRISE_NGN_CODE', '')
    },
    'enterprise_usd': {
        'name': 'Enterprise Plan (USD)',
        'amount': 9900,  # $99.00
        'currency': 'USD',
        'interval': 'monthly',
        'plan_code': os.getenv('PAYSTACK_ENTERPRISE_USD_CODE', '')
    }
}


class PayStackProcessor:
    """Handle PayStack payment operations"""
    
    def __init__(self):
        """Initialize PayStack processor"""
        self.secret_key = PAYSTACK_SECRET_KEY
        self.public_key = PAYSTACK_PUBLIC_KEY
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
    def initialize_transaction(
        self,
        email: str,
        amount: int,
        currency: str = 'NGN',
        metadata: Dict = None
    ) -> Optional[Dict]:
        """
        Initialize a transaction
        
        Args:
            email: Customer email
            amount: Amount in smallest currency unit (kobo for NGN)
            currency: Currency code (NGN, USD, GHS, ZAR, KES)
            metadata: Additional metadata
            
        Returns:
            Transaction details with authorization_url
        """
        url = f'{PAYSTACK_BASE_URL}/transaction/initialize'
        
        data = {
            'email': email,
            'amount': amount,
            'currency': currency,
            'metadata': metadata or {}
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            result = response.json()
            
            if result.get('status'):
                print(f"{Fore.GREEN}✅ Transaction initialized: {result['data']['reference']}{Style.RESET_ALL}")
                return {
                    'authorization_url': result['data']['authorization_url'],
                    'access_code': result['data']['access_code'],
                    'reference': result['data']['reference']
                }
            else:
                print(f"{Fore.RED}❌ PayStack error: {result.get('message')}{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            return None
            
    def verify_transaction(self, reference: str) -> Optional[Dict]:
        """
        Verify a transaction
        
        Args:
            reference: Transaction reference
            
        Returns:
            Transaction details
        """
        url = f'{PAYSTACK_BASE_URL}/transaction/verify/{reference}'
        
        try:
            response = requests.get(url, headers=self.headers)
            result = response.json()
            
            if result.get('status'):
                data = result['data']
                print(f"{Fore.GREEN}✅ Transaction verified: {data['status']}{Style.RESET_ALL}")
                return {
                    'status': data['status'],
                    'amount': data['amount'],
                    'currency': data['currency'],
                    'customer': data['customer'],
                    'paid_at': data.get('paid_at')
                }
            else:
                print(f"{Fore.RED}❌ Verification failed: {result.get('message')}{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            return None
            
    def create_subscription(
        self,
        customer_email: str,
        plan_code: str,
        authorization_code: str = None
    ) -> Optional[Dict]:
        """
        Create a subscription
        
        Args:
            customer_email: Customer email
            plan_code: PayStack plan code
            authorization_code: Payment authorization code (from previous transaction)
            
        Returns:
            Subscription details
        """
        url = f'{PAYSTACK_BASE_URL}/subscription'
        
        data = {
            'customer': customer_email,
            'plan': plan_code
        }
        
        if authorization_code:
            data['authorization'] = authorization_code
            
        try:
            response = requests.post(url, json=data, headers=self.headers)
            result = response.json()
            
            if result.get('status'):
                print(f"{Fore.GREEN}✅ Subscription created{Style.RESET_ALL}")
                return result['data']
            else:
                print(f"{Fore.RED}❌ Error: {result.get('message')}{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            return None
            
    def cancel_subscription(
        self,
        subscription_code: str,
        email_token: str
    ) -> bool:
        """
        Cancel a subscription
        
        Args:
            subscription_code: Subscription code
            email_token: Email token from subscription email
            
        Returns:
            Success status
        """
        url = f'{PAYSTACK_BASE_URL}/subscription/disable'
        
        data = {
            'code': subscription_code,
            'token': email_token
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            result = response.json()
            
            if result.get('status'):
                print(f"{Fore.GREEN}✅ Subscription cancelled{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Error: {result.get('message')}{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            return False
            
    def create_customer(
        self,
        email: str,
        first_name: str,
        last_name: str,
        phone: str = None
    ) -> Optional[str]:
        """
        Create a customer
        
        Returns:
            Customer code
        """
        url = f'{PAYSTACK_BASE_URL}/customer'
        
        data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name
        }
        
        if phone:
            data['phone'] = phone
            
        try:
            response = requests.post(url, json=data, headers=self.headers)
            result = response.json()
            
            if result.get('status'):
                print(f"{Fore.GREEN}✅ Customer created: {result['data']['customer_code']}{Style.RESET_ALL}")
                return result['data']['customer_code']
            else:
                print(f"{Fore.RED}❌ Error: {result.get('message')}{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            return None


# Example usage
if __name__ == "__main__":
    processor = PayStackProcessor()
    
    print("\n" + "="*70)
    print("💳 PayStack Integration - African Payments")
    print("="*70)
    print("\n📊 Available Plans:")
    
    for plan_id, plan in PAYSTACK_PLANS.items():
        amount_display = plan['amount'] / 100 if plan['currency'] == 'NGN' else plan['amount'] / 100
        symbol = '₦' if plan['currency'] == 'NGN' else '$'
        print(f"\n{plan['name']}")
        print(f"  Price: {symbol}{amount_display:,.2f}/{plan['interval']}")
        print(f"  Currency: {plan['currency']}")
    
    print("\n" + "="*70)
    print("⚙️  Setup Instructions:")
    print("="*70)
    print("\n1. Create PayStack account: https://dashboard.paystack.com/signup")
    print("2. Get API keys from: Settings > API Keys & Webhooks")
    print("3. Create subscription plans in Dashboard")
    print("4. Add to .env file:")
    print("   PAYSTACK_SECRET_KEY=sk_test_...")
    print("   PAYSTACK_PUBLIC_KEY=pk_test_...")
    print("   PAYSTACK_PRO_NGN_CODE=PLN_...")
    print("   PAYSTACK_ENTERPRISE_NGN_CODE=PLN_...")
    print("\n5. Supported countries: 🇳🇬 🇬🇭 🇿🇦 🇰🇪 and more")
    print("\n" + "="*70 + "\n")
