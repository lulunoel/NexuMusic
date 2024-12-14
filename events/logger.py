import logging
import colorlog

def setup_console(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs

    # Create colorlog StreamHandler
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s] (%(name)s) %(message)s',
        datefmt='%m/%d/%y %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        reset=True,
        style='%'
    ))
    logger.addHandler(console_handler)
    return logger
