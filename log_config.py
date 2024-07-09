import logging
import sys
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Add a new logging level
SUCCESS = 25  # between WARNING and INFO
logging.addLevelName(SUCCESS, 'SUCCESS')


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kwargs)


logging.Logger.success = success


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.WHITE,
        'INFO': Fore.BLUE,
        'SUCCESS': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.BLACK
    }

    SPECIAL_LOGS = [
        "Logging card status",
        "Card presence: True",
        "Applet major version: 0",
        "Needs 2FA: False",
        "Is seeded: True",
        "Setup done: True",
        "Card type: SeedKeeper",
        "Card label: None",
        "Tries remaining: 5"
    ]

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        if any(special_log in record.msg for special_log in self.SPECIAL_LOGS):
            log_color = Fore.MAGENTA
        log_fmt = f'{log_color}%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(name)s - %(funcName)s() - %(message)s{Style.RESET_ALL}'
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def setup_logging():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if '-v' in sys.argv or '--verbose' in sys.argv else logging.INFO)
    root_logger.addHandler(console_handler)


def get_logger(name):
    return logging.getLogger(name)
