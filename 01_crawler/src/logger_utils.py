import os
import logging
import config


def setup_logger():
    """
    Set up logger for writing logs.
    
    Returns:
        logging.Logger object
    """
    # Tạo logger
    logger = logging.getLogger('ThanhNienCrawler')
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Tránh duplicate handlers
    if logger.handlers:
        return logger
    
    # Tạo formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)
    
    file_handler = logging.FileHandler(
        os.path.join(config.OUTPUT_DIR, config.LOG_FILE),
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
