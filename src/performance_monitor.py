import time
import logging
import os
import psutil
from functools import wraps
from typing import Callable, Any

# Configure logging
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'performance.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('PerformanceMonitor')

def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function performance metrics.
    
    This decorator measures:
    - Execution time
    - Memory usage
    - CPU utilization
    
    Args:
        func (Callable): The function to be monitored
    
    Returns:
        Callable: The wrapped function with performance monitoring
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        process = psutil.Process(os.getpid())
        
        # Pre-execution measurements
        start_time = time.perf_counter()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Post-execution measurements
        end_time = time.perf_counter()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = process.cpu_percent()
        
        # Calculate metrics
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        cpu_usage = (end_cpu + start_cpu) / 2
        
        # Log performance metrics
        logger.info(
            f"Function: {func.__name__}\n"
            f"Execution Time: {execution_time:.6f} seconds\n"
            f"Memory Usage: {memory_used:.2f} MB\n"
            f"CPU Usage: {cpu_usage:.2f}%\n"
            f"-" * 50
        )
        
        return result
    
    return wrapper