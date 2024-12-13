import logging
import colorlog

def setup_console(name):
    logger = logging.getLogger(name)
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s[%(levelname)s]%(reset)s %(asctime)s - %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
            'COMMANDS': 'blue',
        }))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
