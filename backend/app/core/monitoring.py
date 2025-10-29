import time
import logging
from functools import wraps
from typing import Callable, Any
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import psutil
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and logging."""
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Get request info
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(f"Request: {method} {url} from {client_ip}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} for {method} {url} "
                f"in {process_time:.3f}s"
            )
            
            # Add performance headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Server-Info"] = "Clinic-Billing-System"
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Error: {str(e)} for {method} {url} "
                f"in {process_time:.3f}s"
            )
            raise

def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        function_name = f"{func.__module__}.{func.__name__}"
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function {function_name} completed in {execution_time:.3f}s"
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function {function_name} failed after {execution_time:.3f}s: {str(e)}"
            )
            raise
    
    return wrapper

class SystemMonitor:
    """System resource monitoring."""
    
    @staticmethod
    def get_system_info() -> dict:
        """Get current system resource information."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Process info
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'process_memory_mb': round(process_memory, 2),
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system info: {str(e)}")
            return {
                'error': str(e),
                'timestamp': time.time()
            }
    
    @staticmethod
    def log_system_status():
        """Log current system status."""
        info = SystemMonitor.get_system_info()
        
        if 'error' in info:
            logger.error(f"System monitoring error: {info['error']}")
        else:
            logger.info(
                f"System Status - CPU: {info['cpu_percent']}%, "
                f"Memory: {info['memory_percent']}%, "
                f"Disk: {info['disk_percent']:.1f}%, "
                f"Process Memory: {info['process_memory_mb']}MB"
            )

class DatabaseMonitor:
    """Database performance monitoring."""
    
    @staticmethod
    def log_database_operation(operation: str, table: str, duration: float):
        """Log database operation performance."""
        logger.info(
            f"Database {operation} on {table} took {duration:.3f}s"
        )
    
    @staticmethod
    def monitor_query_performance(query_name: str, duration: float):
        """Monitor specific query performance."""
        if duration > 1.0:  # Log slow queries
            logger.warning(
                f"Slow query detected: {query_name} took {duration:.3f}s"
            )
        else:
            logger.debug(f"Query {query_name} completed in {duration:.3f}s")

class APIMonitor:
    """API endpoint monitoring."""
    
    @staticmethod
    def log_endpoint_performance(endpoint: str, method: str, duration: float, status_code: int):
        """Log API endpoint performance."""
        level = logging.WARNING if duration > 2.0 else logging.INFO
        
        logger.log(
            level,
            f"API {method} {endpoint} - {status_code} in {duration:.3f}s"
        )
    
    @staticmethod
    def track_endpoint_usage(endpoint: str, method: str):
        """Track endpoint usage for analytics."""
        logger.info(f"Endpoint accessed: {method} {endpoint}")

# Health check endpoint data
def get_health_status() -> dict:
    """Get comprehensive health status."""
    system_info = SystemMonitor.get_system_info()
    
    return {
        'status': 'healthy' if system_info.get('cpu_percent', 0) < 90 else 'degraded',
        'system': system_info,
        'timestamp': time.time()
    }
