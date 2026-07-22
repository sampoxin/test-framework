import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# 日志级别通过环境变量 LOG_LEVEL 控制，默认 INFO
# 可选值: DEBUG / INFO / WARNING / ERROR
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

def setup_logger(name=None):
    logger = logging.getLogger(name or __name__)
    if not logger.handlers:
        logger.setLevel(getattr(logging, _LOG_LEVEL, logging.INFO))
        formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")

        log_dir = os.path.join(os.path.dirname(__file__), '..', 'log')
        os.makedirs(log_dir, exist_ok=True)

        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'{date_str}.log')

        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='D',
            interval=1,
            backupCount=30,
            encoding='utf-8',
            delay=False
        )
        file_handler.setFormatter(formatter)
        file_handler.suffix = '%Y-%m-%d.log'
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.propagate = False
    return logger

logger = setup_logger()