import sys
import os
import logging
from log_config import setup_logging, get_logger, SUCCESS

from view import View

def get_application_path() -> str:
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def check_cert_directory(app_path: str, logger: logging.Logger) -> None:
    cert_dir = os.path.join(app_path, 'pysatochip', 'cert')
    logger.info(f"Cert directory: {cert_dir}")

    if not os.path.exists(cert_dir):
        logger.error(f"Cert directory not found: {cert_dir}")
        return

    logger.log(SUCCESS, "Cert directory found")
    for cert_file in os.listdir(cert_dir):
        cert_path = os.path.join(cert_dir, cert_file)
        if os.path.isfile(cert_path):
            logger.info(f"Cert file found: {cert_path}")
        else:
            logger.warning(f"Expected cert file not found: {cert_path}")

def main() -> None:
    setup_logging()
    logger = get_logger(__name__)
    logger.info(f"Log level: {logging.getLevelName(logger.getEffectiveLevel())}")

    app_path = get_application_path()
    logger.info(f"Application path: {app_path}")
    os.chdir(app_path)

    check_cert_directory(app_path, logger)

    try:
        view = View()
        view.resizable(False, False)
        view.mainloop()
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()