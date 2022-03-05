import logging


def get_logger(fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
    logger = logging.getLogger()
    format_str = logging.Formatter(fmt)  # 设置日志格式
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    sh.setFormatter(format_str)
    fh = logging.FileHandler('log.txt', encoding='utf-8')
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger

logger = get_logger()