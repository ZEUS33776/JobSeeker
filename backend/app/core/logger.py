import logging
import sys
from datetime import datetime

def setup_logging(level=logging.INFO):
    """
    Setup logging configuration for the application
    
    Args:
        level: Logging level (default: INFO)
    """
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log', mode='a')
        ]
    )
    
    # Create logs directory if it doesn't exist
    import os
    os.makedirs('logs', exist_ok=True)

# Create service logger for services
service_logger = logging.getLogger('app.services')
service_logger.setLevel(logging.INFO)

# Create handler if not already set
if not service_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    service_logger.addHandler(handler)
