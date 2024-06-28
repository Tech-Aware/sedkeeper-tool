import logging
import sys
import os

from view import View, InitializationError

def setup_logging() -> int:
    log_level = logging.DEBUG if len(sys.argv) >= 2 and sys.argv[1] in ['-v', '--verbose'] else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(name)s - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return log_level

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

    logger.info("Cert directory found")
    for cert_file in os.listdir(cert_dir):
        cert_path = os.path.join(cert_dir, cert_file)
        if os.path.isfile(cert_path):
            logger.info(f"Cert file found: {cert_path}")
        else:
            logger.warning(f"Expected cert file not found: {cert_path}")

def main() -> None:
    log_level = setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Log level: {logging.getLevelName(log_level)}")

    app_path = get_application_path()
    logger.info(f"Application path: {app_path}")
    os.chdir(app_path)

    check_cert_directory(app_path, logger)

    try:
        view = View(log_level)
        view.resizable(False, False)
        view.mainloop()
    except InitializationError as e:
        logger.critical(f"Failed to initialize the application: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()