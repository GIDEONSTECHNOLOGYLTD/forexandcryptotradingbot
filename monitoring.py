"""
Monitoring and Observability System
Includes metrics, logging, health checks, and alerting
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from datetime import datetime
import time
import logging
from functools import wraps
from typing import Callable
import psutil
import os
from colorama import Fore, Style

# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# Trading metrics
trades_total = Counter('trading_bot_trades_total', 'Total number of trades', ['symbol', 'side', 'status'])
trade_pnl = Histogram('trading_bot_trade_pnl', 'Trade profit/loss in dollars', buckets=[-1000, -500, -100, 0, 100, 500, 1000, 5000])
active_positions = Gauge('trading_bot_active_positions', 'Number of active positions')
account_balance = Gauge('trading_bot_account_balance', 'Current account balance in dollars')

# API metrics
api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['endpoint'])
api_errors_total = Counter('api_errors_total', 'Total API errors', ['endpoint', 'error_type'])

# System metrics
system_cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
system_memory_usage = Gauge('system_memory_usage_percent', 'Memory usage percentage')
system_disk_usage = Gauge('system_disk_usage_percent', 'Disk usage percentage')

# Database metrics
db_queries_total = Counter('db_queries_total', 'Total database queries', ['operation'])
db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration', ['operation'])
db_errors_total = Counter('db_errors_total', 'Total database errors', ['operation'])

# User metrics
users_total = Gauge('users_total', 'Total number of users')
active_users = Gauge('active_users', 'Number of active users')
subscriptions_total = Gauge('subscriptions_total', 'Total subscriptions', ['plan'])


# ============================================================================
# MONITORING DECORATORS
# ============================================================================

def monitor_trade(func: Callable) -> Callable:
    """Decorator to monitor trade executions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Extract trade details
        if result and isinstance(result, dict):
            symbol = result.get('symbol', 'unknown')
            side = result.get('side', 'unknown')
            status = result.get('status', 'unknown')
            pnl = result.get('pnl', 0)
            
            # Update metrics
            trades_total.labels(symbol=symbol, side=side, status=status).inc()
            if pnl != 0:
                trade_pnl.observe(pnl)
                
        return result
    return wrapper


def monitor_api_call(endpoint: str):
    """Decorator to monitor API calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                status = 'success'
                return result
            except Exception as e:
                status = 'error'
                api_errors_total.labels(endpoint=endpoint, error_type=type(e).__name__).inc()
                raise
            finally:
                duration = time.time() - start_time
                api_request_duration.labels(endpoint=endpoint).observe(duration)
                api_requests_total.labels(method='GET', endpoint=endpoint, status=status).inc()
                
        return wrapper
    return decorator


def monitor_db_query(operation: str):
    """Decorator to monitor database queries"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                db_queries_total.labels(operation=operation).inc()
                return result
            except Exception as e:
                db_errors_total.labels(operation=operation).inc()
                raise
            finally:
                duration = time.time() - start_time
                db_query_duration.labels(operation=operation).observe(duration)
                
        return wrapper
    return decorator


# ============================================================================
# SYSTEM MONITORING
# ============================================================================

class SystemMonitor:
    """Monitor system resources"""
    
    @staticmethod
    def update_system_metrics():
        """Update system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            system_disk_usage.set(disk.percent)
            
        except Exception as e:
            logging.error(f"Error updating system metrics: {e}")
            
    @staticmethod
    def check_system_health() -> dict:
        """Check system health"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health = {
            'status': 'healthy',
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'warnings': []
        }
        
        # Check for issues
        if cpu_percent > 80:
            health['warnings'].append('High CPU usage')
            health['status'] = 'degraded'
            
        if memory.percent > 85:
            health['warnings'].append('High memory usage')
            health['status'] = 'degraded'
            
        if disk.percent > 90:
            health['warnings'].append('High disk usage')
            health['status'] = 'degraded'
            
        return health


# ============================================================================
# HEALTH CHECKS
# ============================================================================

class HealthChecker:
    """Application health checks"""
    
    @staticmethod
    def check_database(db) -> bool:
        """Check database connection"""
        try:
            # Try a simple query
            db.db.command('ping')
            return True
        except Exception as e:
            logging.error(f"Database health check failed: {e}")
            return False
            
    @staticmethod
    def check_exchange(exchange) -> bool:
        """Check exchange connection"""
        try:
            # Try to fetch server time
            exchange.fetch_time()
            return True
        except Exception as e:
            logging.error(f"Exchange health check failed: {e}")
            return False
            
    @staticmethod
    def check_redis(redis_client) -> bool:
        """Check Redis connection"""
        try:
            redis_client.ping()
            return True
        except Exception as e:
            logging.error(f"Redis health check failed: {e}")
            return False
            
    @staticmethod
    def get_health_status(db=None, exchange=None, redis_client=None) -> dict:
        """Get complete health status"""
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Check components
        if db:
            db_healthy = HealthChecker.check_database(db)
            health['checks']['database'] = 'ok' if db_healthy else 'error'
            if not db_healthy:
                health['status'] = 'unhealthy'
                
        if exchange:
            exchange_healthy = HealthChecker.check_exchange(exchange)
            health['checks']['exchange'] = 'ok' if exchange_healthy else 'error'
            if not exchange_healthy:
                health['status'] = 'degraded'
                
        if redis_client:
            redis_healthy = HealthChecker.check_redis(redis_client)
            health['checks']['redis'] = 'ok' if redis_healthy else 'error'
            if not redis_healthy:
                health['status'] = 'degraded'
                
        # System health
        system_health = SystemMonitor.check_system_health()
        health['checks']['system'] = system_health['status']
        health['system_metrics'] = {
            'cpu_percent': system_health['cpu_percent'],
            'memory_percent': system_health['memory_percent'],
            'disk_percent': system_health['disk_percent']
        }
        
        if system_health['status'] != 'healthy':
            health['status'] = 'degraded'
            health['warnings'] = system_health['warnings']
            
        return health


# ============================================================================
# ALERTING
# ============================================================================

class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self, telegram_notifier=None):
        self.telegram = telegram_notifier
        self.alert_history = []
        
    def send_alert(self, level: str, message: str, details: dict = None):
        """Send an alert"""
        alert = {
            'level': level,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.alert_history.append(alert)
        
        # Log alert
        if level == 'critical':
            logging.critical(f"ALERT: {message}")
        elif level == 'error':
            logging.error(f"ALERT: {message}")
        elif level == 'warning':
            logging.warning(f"ALERT: {message}")
        else:
            logging.info(f"ALERT: {message}")
            
        # Send to Telegram if available
        if self.telegram and level in ['critical', 'error']:
            try:
                emoji = '🚨' if level == 'critical' else '⚠️'
                self.telegram.send_message(f"{emoji} {level.upper()}: {message}")
            except Exception as e:
                logging.error(f"Failed to send Telegram alert: {e}")
                
    def check_thresholds(self):
        """Check various thresholds and send alerts"""
        # System resources
        system_health = SystemMonitor.check_system_health()
        
        if system_health['cpu_percent'] > 90:
            self.send_alert('critical', 'CPU usage above 90%', 
                          {'cpu_percent': system_health['cpu_percent']})
                          
        if system_health['memory_percent'] > 95:
            self.send_alert('critical', 'Memory usage above 95%',
                          {'memory_percent': system_health['memory_percent']})
                          
        if system_health['disk_percent'] > 95:
            self.send_alert('critical', 'Disk usage above 95%',
                          {'disk_percent': system_health['disk_percent']})


# ============================================================================
# METRICS ENDPOINT
# ============================================================================

def get_prometheus_metrics():
    """Get Prometheus metrics in exposition format"""
    return generate_latest(REGISTRY)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📊 Monitoring System")
    print("="*70)
    
    # Update system metrics
    SystemMonitor.update_system_metrics()
    
    # Check health
    health = SystemMonitor.check_system_health()
    
    print(f"\n🏥 System Health: {health['status'].upper()}")
    print(f"   CPU: {health['cpu_percent']:.1f}%")
    print(f"   Memory: {health['memory_percent']:.1f}%")
    print(f"   Disk: {health['disk_percent']:.1f}%")
    
    if health['warnings']:
        print(f"\n⚠️  Warnings:")
        for warning in health['warnings']:
            print(f"   - {warning}")
            
    print("\n📈 Metrics available at: /metrics endpoint")
    print("\n" + "="*70 + "\n")
