import logging
import colorlog
logger = logging.getLogger("test")
console_handler = logging.StreamHandler()
log_colors_config = {
    'DEBUG': 'white',
    'INFO': 'blue',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}
logger.setLevel("DEBUG")
console_formatter = colorlog.ColoredFormatter(
    fmt='%(log_color)s %(asctime)s  %(funcName)s - line:%(lineno)d %(levelname)s %(message)s',
    datefmt='%Y-%m-%d  %H:%M:%S',
    log_colors=log_colors_config
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
console_handler.close()
