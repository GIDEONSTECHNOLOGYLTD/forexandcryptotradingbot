"""
API Service for Third-Party Integration
Allows external developers to integrate with the trading bot
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class APIKeyManager:
    """
    Manage API keys for third-party access
    """
    
    def __init__(self, db):
        """
        Initialize API key manager
        
        Args:
            db: Database instance
        """
        self.db = db
        self.api_keys_collection = db.db['api_keys']
    
    def generate_api_key(self, user_id: str, name: str, permissions: list = None) -> Dict:
        """
        Generate new API key for user
        
        Args:
            user_id: User ID
            name: API key name/description
            permissions: List of allowed permissions
            
        Returns:
            API key details
        """
        try:
            # Generate secure API key
            api_key = f"sk_{secrets.token_urlsafe(32)}"
            
            # Generate API secret
            api_secret = secrets.token_urlsafe(48)
            
            # Hash the secret for storage
            secret_hash = hashlib.sha256(api_secret.encode()).hexdigest()
            
            # Default permissions if none provided
            if permissions is None:
                permissions = ['read:bots', 'read:trades', 'write:bots']
            
            # Store API key
            key_data = {
                'api_key': api_key,
                'secret_hash': secret_hash,
                'user_id': user_id,
                'name': name,
                'permissions': permissions,
                'created_at': datetime.utcnow(),
                'last_used': None,
                'is_active': True,
                'rate_limit': 1000,  # requests per hour
                'usage_count': 0
            }
            
            self.api_keys_collection.insert_one(key_data)
            
            logger.info(f"✅ API key generated for user {user_id}")
            
            # Return key and secret (only time secret is shown)
            return {
                'api_key': api_key,
                'api_secret': api_secret,  # Show once, never stored
                'name': name,
                'permissions': permissions,
                'created_at': key_data['created_at'],
                'rate_limit': key_data['rate_limit']
            }
            
        except Exception as e:
            logger.error(f"Error generating API key: {e}")
            raise
    
    def validate_api_key(self, api_key: str, api_secret: str) -> Optional[Dict]:
        """
        Validate API key and secret
        
        Args:
            api_key: API key
            api_secret: API secret
            
        Returns:
            Key data if valid, None otherwise
        """
        try:
            # Find API key
            key_data = self.api_keys_collection.find_one({
                'api_key': api_key,
                'is_active': True
            })
            
            if not key_data:
                logger.warning(f"Invalid API key: {api_key[:10]}...")
                return None
            
            # Verify secret
            secret_hash = hashlib.sha256(api_secret.encode()).hexdigest()
            
            if secret_hash != key_data['secret_hash']:
                logger.warning(f"Invalid API secret for key: {api_key[:10]}...")
                return None
            
            # Update last used
            self.api_keys_collection.update_one(
                {'api_key': api_key},
                {
                    '$set': {'last_used': datetime.utcnow()},
                    '$inc': {'usage_count': 1}
                }
            )
            
            return key_data
            
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None
    
    def check_rate_limit(self, api_key: str) -> bool:
        """
        Check if API key has exceeded rate limit
        
        Args:
            api_key: API key
            
        Returns:
            True if within limit, False if exceeded
        """
        try:
            key_data = self.api_keys_collection.find_one({'api_key': api_key})
            
            if not key_data:
                return False
            
            # Check usage in last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            # Count recent requests (simplified - in production use Redis)
            recent_usage = key_data.get('usage_count', 0)
            rate_limit = key_data.get('rate_limit', 1000)
            
            return recent_usage < rate_limit
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False
    
    def revoke_api_key(self, api_key: str, user_id: str) -> bool:
        """
        Revoke an API key
        
        Args:
            api_key: API key to revoke
            user_id: User ID (for authorization)
            
        Returns:
            Success status
        """
        try:
            result = self.api_keys_collection.update_one(
                {'api_key': api_key, 'user_id': user_id},
                {'$set': {'is_active': False, 'revoked_at': datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ API key revoked: {api_key[:10]}...")
                return True
            else:
                logger.warning(f"API key not found or unauthorized: {api_key[:10]}...")
                return False
                
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            return False
    
    def list_user_api_keys(self, user_id: str) -> list:
        """
        List all API keys for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of API keys (without secrets)
        """
        try:
            keys = list(self.api_keys_collection.find({'user_id': user_id}))
            
            # Remove sensitive data
            for key in keys:
                key['_id'] = str(key['_id'])
                key.pop('secret_hash', None)
                # Mask API key
                key['api_key_masked'] = key['api_key'][:10] + '...' + key['api_key'][-4:]
                key.pop('api_key', None)
            
            return keys
            
        except Exception as e:
            logger.error(f"Error listing API keys: {e}")
            return []
    
    def check_permission(self, api_key: str, required_permission: str) -> bool:
        """
        Check if API key has required permission
        
        Args:
            api_key: API key
            required_permission: Permission to check (e.g., 'write:bots')
            
        Returns:
            True if has permission, False otherwise
        """
        try:
            key_data = self.api_keys_collection.find_one({'api_key': api_key})
            
            if not key_data or not key_data.get('is_active'):
                return False
            
            permissions = key_data.get('permissions', [])
            
            # Check for wildcard permission
            if '*' in permissions or 'admin' in permissions:
                return True
            
            # Check for specific permission
            if required_permission in permissions:
                return True
            
            # Check for category permission (e.g., 'read:*')
            category = required_permission.split(':')[0]
            if f"{category}:*" in permissions:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False


class APIRateLimiter:
    """
    Rate limiting for API requests
    """
    
    def __init__(self):
        """Initialize rate limiter"""
        self.request_counts = {}  # In production, use Redis
    
    def check_rate_limit(self, api_key: str, limit: int = 1000, window: int = 3600) -> Dict:
        """
        Check rate limit for API key
        
        Args:
            api_key: API key
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            Rate limit status
        """
        current_time = datetime.utcnow()
        
        if api_key not in self.request_counts:
            self.request_counts[api_key] = []
        
        # Remove old requests outside window
        cutoff_time = current_time - timedelta(seconds=window)
        self.request_counts[api_key] = [
            req_time for req_time in self.request_counts[api_key]
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        current_count = len(self.request_counts[api_key])
        
        if current_count >= limit:
            return {
                'allowed': False,
                'limit': limit,
                'remaining': 0,
                'reset_at': (current_time + timedelta(seconds=window)).isoformat()
            }
        
        # Add current request
        self.request_counts[api_key].append(current_time)
        
        return {
            'allowed': True,
            'limit': limit,
            'remaining': limit - current_count - 1,
            'reset_at': (current_time + timedelta(seconds=window)).isoformat()
        }


# Available API permissions
API_PERMISSIONS = {
    'read:bots': 'View bot configurations and status',
    'write:bots': 'Create, update, and delete bots',
    'read:trades': 'View trade history and analytics',
    'write:trades': 'Execute trades manually',
    'read:account': 'View account information',
    'write:account': 'Update account settings',
    'read:market': 'Access market data',
    'admin': 'Full administrative access'
}


# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔑 API Service for Third-Party Integration")
    print("="*70)
    print("\n📋 Available Permissions:")
    for perm, desc in API_PERMISSIONS.items():
        print(f"  - {perm}: {desc}")
    
    print("\n💡 Usage:")
    print("  from api_service import APIKeyManager")
    print("  api_manager = APIKeyManager(db)")
    print("  key = api_manager.generate_api_key(user_id, 'My App', ['read:bots', 'write:bots'])")
    
    print("\n🔒 Security Features:")
    print("  - Secure key generation (cryptographically random)")
    print("  - Secret hashing (SHA-256)")
    print("  - Rate limiting (1000 requests/hour default)")
    print("  - Permission-based access control")
    print("  - Usage tracking and analytics")
    
    print("\n📚 API Documentation:")
    print("  - POST /api/v1/bots - Create bot")
    print("  - GET /api/v1/bots - List bots")
    print("  - GET /api/v1/bots/{id} - Get bot details")
    print("  - PUT /api/v1/bots/{id} - Update bot")
    print("  - DELETE /api/v1/bots/{id} - Delete bot")
    print("  - GET /api/v1/trades - Get trade history")
    print("  - GET /api/v1/account - Get account info")
    
    print("\n" + "="*70 + "\n")
