import logging

def setup_logger(name=None):
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format = "%(asctime)s - [%(levelname)s] - %(message)s",
    #     handlers=[
    #         logging.FileHandler("test_run.log", encoding="utf-8"),
    #         logging.StreamHandler()
    #     ]
    # )
    logger = logging.getLogger(name or __name__)
    # 避免重复添加 handler
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")

        # 文件 handler
        fh = logging.FileHandler("test_run.log", encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # 控制台 handler
        # sh = logging.StreamHandler()
        # sh.setFormatter(formatter)
        # logger.addHandler(sh)
    return logger