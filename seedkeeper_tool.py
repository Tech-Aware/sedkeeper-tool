import sys
import os
import logging
from log_config import setup_logging, get_logger, SUCCESS
from exceptions import SeedkeeperError, CardError, ControllerError

from view import View

logger = get_logger(__name__)


def main() -> None:
    setup_logging()
    logger.info("Starting Seedkeeper Tool")

    try:
        logger.info("Initializing View")
        view = View()
        logger.info("View initialized successfully")

        logger.info("Setting window properties")
        view.resizable(False, False)
        view.title("Seedkeeper Tool")

        logger.info("Displaying welcome screen")
        view.welcome()

        logger.info("Starting main event loop")
        view.mainloop()
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()