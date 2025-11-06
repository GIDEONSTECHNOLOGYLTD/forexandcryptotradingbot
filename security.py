"""
Enhanced Security Module
Includes rate limiting, email verification, 2FA, and security middleware
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional, Dict
import re
import secrets
import hashlib
import pyotp
from collections import defaultdict
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from colorama import Fore, Style


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """Rate limiting to prevent API abuse"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.rpm = requests_per_minute
        self.rph = requests_per_hour
        self.requests = defaultdict(list)
        
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Clean old requests
        self.requests[identifier] = [
            timestamp for timestamp in self.requests[identifier]
            if now - timestamp < 3600  # Keep last hour
        ]
        
        # Check limits
        minute_ago = now - 60
        hour_ago = now - 3600
        
        recent_minute = sum(1 for t in self.requests[identifier] if t > minute_ago)
        recent_hour = sum(1 for t in self.requests[identifier] if t > hour_ago)
        
        if recent_minute >= self.rpm:
            return False
        if recent_hour >= self.rph:
            return False
            
        # Add current request
        self.requests[identifier].append(now)
        return True
        
    def get_retry_after(self, identifier: str) -> int:
        """Get seconds until next request allowed"""
        if not self.requests[identifier]:
            return 0
            
        now = time.time()
        minute_ago = now - 60
        
        recent_minute = [t for t in self.requests[identifier] if t > minute_ago]
        
        if len(recent_minute) >= self.rpm:
            oldest_request = min(recent_minute)
            return int(60 - (now - oldest_request)) + 1
            
        return 0


# Global rate limiter
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Get client identifier (IP or user ID)
    client_ip = request.client.host
    user_id = request.state.user_id if hasattr(request.state, 'user_id') else None
    identifier = user_id or client_ip
    
    # Check rate limit
    if not rate_limiter.is_allowed(identifier):
        retry_after = rate_limiter.get_retry_after(identifier)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )
        
    response = await call_next(request)
    return response


# ============================================================================
# EMAIL VERIFICATION
# ============================================================================

class EmailVerification:
    """Email verification system"""
    
    def __init__(self, smtp_host: str = None, smtp_port: int = 587,
                 smtp_user: str = None, smtp_password: str = None):
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user or os.getenv('SMTP_USER')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        self.verification_codes = {}  # In production, use Redis
        
    def generate_verification_code(self, email: str) -> str:
        """Generate a 6-digit verification code"""
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Store with expiry (10 minutes)
        self.verification_codes[email] = {
            'code': code,
            'expires_at': datetime.now() + timedelta(minutes=10),
            'attempts': 0
        }
        
        return code
        
    def verify_code(self, email: str, code: str) -> bool:
        """Verify the code"""
        if email not in self.verification_codes:
            return False
            
        stored = self.verification_codes[email]
        
        # Check expiry
        if datetime.now() > stored['expires_at']:
            del self.verification_codes[email]
            return False
            
        # Check attempts
        if stored['attempts'] >= 3:
            del self.verification_codes[email]
            return False
            
        # Verify code
        if stored['code'] == code:
            del self.verification_codes[email]
            return True
        else:
            stored['attempts'] += 1
            return False
            
    def send_verification_email(self, email: str, code: str) -> bool:
        """Send verification email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Trading Bot - Email Verification'
            msg['From'] = self.smtp_user
            msg['To'] = email
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Email Verification</h2>
                    <p>Your verification code is:</p>
                    <h1 style="color: #667eea; font-size: 36px; letter-spacing: 5px;">{code}</h1>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                
            print(f"{Fore.GREEN}✅ Verification email sent to {email}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to send email: {e}{Style.RESET_ALL}")
            return False


# ============================================================================
# TWO-FACTOR AUTHENTICATION (2FA)
# ============================================================================

class TwoFactorAuth:
    """Two-factor authentication using TOTP"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new 2FA secret"""
        return pyotp.random_base32()
        
    @staticmethod
    def generate_qr_code_url(email: str, secret: str, issuer: str = "Trading Bot") -> str:
        """Generate QR code URL for authenticator apps"""
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name=issuer
        )
        
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verify a 2FA token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
        
    @staticmethod
    def generate_backup_codes(count: int = 10) -> list:
        """Generate backup codes"""
        codes = []
        for _ in range(count):
            code = '-'.join([
                ''.join([str(secrets.randbelow(10)) for _ in range(4)])
                for _ in range(2)
            ])
            codes.append(code)
        return codes


# ============================================================================
# PASSWORD SECURITY
# ============================================================================

class PasswordValidator:
    """Validate password strength"""
    
    @staticmethod
    def validate(password: str) -> tuple[bool, list]:
        """
        Validate password strength
        Returns: (is_valid, errors)
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
            
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
            
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
            
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one number")
            
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character")
            
        # Check common passwords
        common_passwords = ['password', '12345678', 'qwerty', 'abc123']
        if password.lower() in common_passwords:
            errors.append("Password is too common")
            
        return len(errors) == 0, errors
        
    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """Generate a strong random password"""
        import string
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(chars) for _ in range(length))


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

class SessionManager:
    """Manage user sessions"""
    
    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions = {}  # In production, use Redis
        self.timeout = timedelta(minutes=session_timeout_minutes)
        
    def create_session(self, user_id: str) -> str:
        """Create a new session"""
        session_id = secrets.token_urlsafe(32)
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        
        return session_id
        
    def validate_session(self, session_id: str) -> Optional[str]:
        """Validate and refresh session"""
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        
        # Check timeout
        if datetime.now() - session['last_activity'] > self.timeout:
            del self.sessions[session_id]
            return None
            
        # Update last activity
        session['last_activity'] = datetime.now()
        return session['user_id']
        
    def destroy_session(self, session_id: str):
        """Destroy a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]


# ============================================================================
# IP WHITELISTING
# ============================================================================

class IPWhitelist:
    """IP address whitelisting"""
    
    def __init__(self):
        self.whitelist = set()
        
    def add_ip(self, ip: str):
        """Add IP to whitelist"""
        self.whitelist.add(ip)
        
    def remove_ip(self, ip: str):
        """Remove IP from whitelist"""
        self.whitelist.discard(ip)
        
    def is_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        return ip in self.whitelist
        
    def check_middleware(self, request: Request):
        """Middleware to check IP whitelist"""
        if self.whitelist:  # Only check if whitelist is not empty
            client_ip = request.client.host
            if client_ip not in self.whitelist:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="IP address not whitelisted"
                )


# ============================================================================
# SECURITY HEADERS
# ============================================================================

async def security_headers_middleware(request: Request, call_next):
    """Add security headers to response"""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response


# ============================================================================
# AUDIT LOGGING
# ============================================================================

class AuditLogger:
    """Log security-relevant events"""
    
    def __init__(self, db=None):
        self.db = db
        self.logs = []
        
    def log_event(self, event_type: str, user_id: str = None,
                  ip_address: str = None, details: dict = None):
        """Log a security event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {}
        }
        
        self.logs.append(event)
        
        # Store in database if available
        if self.db:
            try:
                self.db.db['audit_logs'].insert_one(event)
            except Exception as e:
                print(f"{Fore.RED}❌ Failed to store audit log: {e}{Style.RESET_ALL}")
                
        # Log to file
        import logging
        logging.info(f"AUDIT: {event_type} - User: {user_id} - IP: {ip_address}")


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔐 Security System")
    print("="*70)
    
    # Test password validation
    print("\n🔑 Password Validation:")
    password = "MySecure123!"
    is_valid, errors = PasswordValidator.validate(password)
    print(f"   Password: {password}")
    print(f"   Valid: {is_valid}")
    if errors:
        print(f"   Errors: {', '.join(errors)}")
        
    # Test 2FA
    print("\n📱 Two-Factor Authentication:")
    secret = TwoFactorAuth.generate_secret()
    print(f"   Secret: {secret}")
    qr_url = TwoFactorAuth.generate_qr_code_url("user@example.com", secret)
    print(f"   QR URL: {qr_url[:50]}...")
    
    # Test rate limiting
    print("\n⏱️  Rate Limiting:")
    limiter = RateLimiter(requests_per_minute=5)
    for i in range(7):
        allowed = limiter.is_allowed("test_user")
        print(f"   Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'}")
        
    print("\n" + "="*70 + "\n")
