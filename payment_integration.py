"""
Payment Integration with Stripe
Handles subscriptions, invoices, and webhooks
"""
import stripe
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from colorama import Fore, Style
import config

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')

# Subscription Plans
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'max_bots': 1,
        'features': ['Paper trading', 'Basic strategies', 'Email support']
    },
    'pro': {
        'name': 'Pro',
        'price': 29,
        'price_id': os.getenv('STRIPE_PRO_PRICE_ID', ''),  # From Stripe Dashboard
        'max_bots': 3,
        'features': ['Live trading', 'All strategies', 'Telegram alerts', 'Priority support']
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 99,
        'price_id': os.getenv('STRIPE_ENTERPRISE_PRICE_ID', ''),  # From Stripe Dashboard
        'max_bots': -1,  # Unlimited
        'features': ['Everything in Pro', 'Unlimited bots', 'Custom strategies', 'API access', 'White-label', '24/7 support']
    }
}


class PaymentProcessor:
    """Handles all payment operations"""
    
    def __init__(self):
        """Initialize payment processor"""
        self.stripe_key = stripe.api_key
        
    def create_customer(self, email: str, name: str, metadata: Dict = None) -> Optional[str]:
        """
        Create a Stripe customer
        
        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata
            
        Returns:
            Customer ID or None
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            print(f"{Fore.GREEN}✅ Created Stripe customer: {customer.id}{Style.RESET_ALL}")
            return customer.id
        except stripe.error.StripeError as e:
            print(f"{Fore.RED}❌ Stripe error: {e}{Style.RESET_ALL}")
            return None
            
    def create_subscription(
        self,
        customer_id: str,
        plan: str,
        trial_days: int = 7
    ) -> Optional[Dict]:
        """
        Create a subscription for a customer
        
        Args:
            customer_id: Stripe customer ID
            plan: Plan name ('pro' or 'enterprise')
            trial_days: Free trial days (default: 7)
            
        Returns:
            Subscription details or None
        """
        if plan not in ['pro', 'enterprise']:
            print(f"{Fore.RED}❌ Invalid plan: {plan}{Style.RESET_ALL}")
            return None
            
        price_id = SUBSCRIPTION_PLANS[plan]['price_id']
        
        if not price_id:
            print(f"{Fore.RED}❌ Stripe Price ID not configured for {plan}{Style.RESET_ALL}")
            return None
            
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                trial_period_days=trial_days,
                metadata={
                    'plan': plan,
                    'plan_name': SUBSCRIPTION_PLANS[plan]['name']
                }
            )
            
            print(f"{Fore.GREEN}✅ Created subscription: {subscription.id}{Style.RESET_ALL}")
            
            return {
                'subscription_id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'trial_end': subscription.trial_end,
                'plan': plan
            }
        except stripe.error.StripeError as e:
            print(f"{Fore.RED}❌ Stripe error: {e}{Style.RESET_ALL}")
            return None
            
    def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Success status
        """
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            print(f"{Fore.GREEN}✅ Cancelled subscription: {subscription_id}{Style.RESET_ALL}")
            return True
        except stripe.error.StripeError as e:
            print(f"{Fore.RED}❌ Stripe error: {e}{Style.RESET_ALL}")
            return False
            
    def update_subscription(
        self,
        subscription_id: str,
        new_plan: str
    ) -> Optional[Dict]:
        """
        Update subscription to a different plan
        
        Args:
            subscription_id: Stripe subscription ID
            new_plan: New plan name
            
        Returns:
            Updated subscription details or None
        """
        if new_plan not in ['pro', 'enterprise']:
            print(f"{Fore.RED}❌ Invalid plan: {new_plan}{Style.RESET_ALL}")
            return None
            
        price_id = SUBSCRIPTION_PLANS[new_plan]['price_id']
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': price_id,
                }],
                metadata={
                    'plan': new_plan,
                    'plan_name': SUBSCRIPTION_PLANS[new_plan]['name']
                }
            )
            
            print(f"{Fore.GREEN}✅ Updated subscription to {new_plan}{Style.RESET_ALL}")
            
            return {
                'subscription_id': updated_subscription.id,
                'status': updated_subscription.status,
                'plan': new_plan
            }
        except stripe.error.StripeError as e:
            print(f"{Fore.RED}❌ Stripe error: {e}{Style.RESET_ALL}")
            return None
            
    def create_payment_intent(
        self,
        amount: int,
        currency: str = 'usd',
        customer_id: Optional[str] = None,
        description: str = ''
    ) -> Optional[Dict]:
        """
        Create a one-time payment intent
        
        Args:
            amount: Amount in cents (e.g., 2900 for $29.00)
            currency: Currency code
            customer_id: Stripe customer ID (optional)
            description: Payment description
            
        Returns:
            Payment intent details or None
        """
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                description=description,
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'amount': amount,
                'currency': currency
            }
        except stripe.error.StripeError as e:
            print(f"{Fore.RED}❌ Stripe error: {e}{Style.RESET_ALL}")
            return None
            
    def get_subscription_status(self, subscription_id: str) -> Optional[Dict]:
        """
        Get subscription status
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Subscription details or None
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'plan': subscription.metadata.get('plan', 'unknown')
            }
        except stripe.error.StripeError as e:
            print(f"{Fore.RED}❌ Stripe error: {e}{Style.RESET_ALL}")
            return None
            
    def create_invoice(
        self,
        customer_id: str,
        description: str,
        amount: int
    ) -> Optional[str]:
        """
        Create and finalize an invoice
        
        Args:
            customer_id: Stripe customer ID
            description: Invoice description
            amount: Amount in cents
            
        Returns:
            Invoice ID or None
        """
        try:
            # Create invoice item
            stripe.InvoiceItem.create(
                customer=customer_id,
                amount=amount,
                currency='usd',
                description=description
            )
            
            # Create invoice
            invoice = stripe.Invoice.create(
                customer=customer_id,
                auto_advance=True  # Auto-finalize
            )
            
            # Finalize and pay
            invoice = stripe.Invoice.finalize_invoice(invoice.id)
            
            print(f"{Fore.GREEN}✅ Created invoice: {invoice.id}{Style.RESET_ALL}")
            return invoice.id
        except stripe.error.StripeError as e:
            print(f"{Fore.RED}❌ Stripe error: {e}{Style.RESET_ALL}")
            return None
            
    def handle_webhook(self, payload: bytes, sig_header: str) -> Optional[Dict]:
        """
        Handle Stripe webhook events
        
        Args:
            payload: Request body
            sig_header: Stripe signature header
            
        Returns:
            Event details or None
        """
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            
            event_type = event['type']
            data = event['data']['object']
            
            print(f"{Fore.CYAN}📧 Webhook: {event_type}{Style.RESET_ALL}")
            
            # Handle different event types
            handlers = {
                'customer.subscription.created': self._handle_subscription_created,
                'customer.subscription.updated': self._handle_subscription_updated,
                'customer.subscription.deleted': self._handle_subscription_deleted,
                'invoice.paid': self._handle_invoice_paid,
                'invoice.payment_failed': self._handle_payment_failed,
                'payment_intent.succeeded': self._handle_payment_succeeded,
            }
            
            handler = handlers.get(event_type)
            if handler:
                return handler(data)
                
            return {'status': 'unhandled', 'type': event_type}
            
        except ValueError as e:
            print(f"{Fore.RED}❌ Invalid payload: {e}{Style.RESET_ALL}")
            return None
        except stripe.error.SignatureVerificationError as e:
            print(f"{Fore.RED}❌ Invalid signature: {e}{Style.RESET_ALL}")
            return None
            
    def _handle_subscription_created(self, subscription):
        """Handle subscription created event"""
        print(f"{Fore.GREEN}✅ New subscription: {subscription['id']}{Style.RESET_ALL}")
        return {
            'status': 'success',
            'action': 'subscription_created',
            'subscription_id': subscription['id']
        }
        
    def _handle_subscription_updated(self, subscription):
        """Handle subscription updated event"""
        print(f"{Fore.YELLOW}🔄 Subscription updated: {subscription['id']}{Style.RESET_ALL}")
        return {
            'status': 'success',
            'action': 'subscription_updated',
            'subscription_id': subscription['id']
        }
        
    def _handle_subscription_deleted(self, subscription):
        """Handle subscription deleted event"""
        print(f"{Fore.RED}❌ Subscription cancelled: {subscription['id']}{Style.RESET_ALL}")
        return {
            'status': 'success',
            'action': 'subscription_cancelled',
            'subscription_id': subscription['id']
        }
        
    def _handle_invoice_paid(self, invoice):
        """Handle invoice paid event"""
        print(f"{Fore.GREEN}💰 Invoice paid: {invoice['id']}{Style.RESET_ALL}")
        return {
            'status': 'success',
            'action': 'payment_received',
            'invoice_id': invoice['id'],
            'amount': invoice['amount_paid']
        }
        
    def _handle_payment_failed(self, invoice):
        """Handle payment failed event"""
        print(f"{Fore.RED}❌ Payment failed: {invoice['id']}{Style.RESET_ALL}")
        return {
            'status': 'failed',
            'action': 'payment_failed',
            'invoice_id': invoice['id']
        }
        
    def _handle_payment_succeeded(self, payment_intent):
        """Handle payment succeeded event"""
        print(f"{Fore.GREEN}✅ Payment succeeded: {payment_intent['id']}{Style.RESET_ALL}")
        return {
            'status': 'success',
            'action': 'payment_succeeded',
            'payment_intent_id': payment_intent['id'],
            'amount': payment_intent['amount']
        }


# Example usage
if __name__ == "__main__":
    processor = PaymentProcessor()
    
    print("\n" + "="*70)
    print("💳 Payment Integration System")
    print("="*70)
    print("\n📊 Available Plans:")
    
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        print(f"\n{plan['name']} - ${plan['price']}/month")
        print(f"  Max Bots: {plan['max_bots'] if plan['max_bots'] != -1 else 'Unlimited'}")
        print(f"  Features: {', '.join(plan['features'])}")
    
    print("\n" + "="*70)
    print("⚙️  Setup Instructions:")
    print("="*70)
    print("\n1. Get Stripe API keys from: https://dashboard.stripe.com/apikeys")
    print("2. Create products and prices in Stripe Dashboard")
    print("3. Add to .env file:")
    print("   STRIPE_SECRET_KEY=sk_test_...")
    print("   STRIPE_PRO_PRICE_ID=price_...")
    print("   STRIPE_ENTERPRISE_PRICE_ID=price_...")
    print("   STRIPE_WEBHOOK_SECRET=whsec_...")
    print("\n4. Test with: python payment_integration.py")
    print("\n" + "="*70 + "\n")
