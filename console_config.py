import logging
import colorlog

def setup_console(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('discord.client').setLevel(logging.WARNING)
    logging.getLogger('discord.gateway').setLevel(logging.ERROR)
    logging.getLogger('discord.http').setLevel(logging.ERROR)
    logging.getLogger('discord.state').setLevel(logging.ERROR)
    logging.getLogger('discord.webhook.async_').setLevel(logging.ERROR)

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
