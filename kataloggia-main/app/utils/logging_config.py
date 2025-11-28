"""
Logging Configuration
Structured logging setup
"""
import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# Try to import structlog
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("[INFO] structlog yüklü değil, standart logging kullanılacak")

def setup_logging(app):
    """Setup logging configuration"""
    
    # Create logs directory
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Configure logging level
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    if STRUCTLOG_AVAILABLE:
        # Structured logging with structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        logger = structlog.get_logger()
    else:
        # Standard logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=10),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logger = logging.getLogger('kataloggia')
    
    app.logger = logger
    return logger

def get_logger(name='kataloggia'):
    """Get logger instance"""
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)

