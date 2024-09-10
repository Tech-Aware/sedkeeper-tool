import sys
import os
from typing import NoReturn
from log_config import setup_logging, get_logger, SUCCESS
from exceptions import InitializationError
from view import View
from pysatochip import cert

logger = get_logger(__name__)


def get_application_path() -> str:
    """Determine and return the application path."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def check_cert_directory(app_path: str) -> bool:
    """
    Check if the cert directory and files exist.
    Return True if the directory is found, False otherwise.
    """
    cert_dir = os.path.join(app_path, 'pysatochip', 'cert')
    logger.debug(f"Cert directory: {cert_dir}")

    if not os.path.exists(cert_dir):
        logger.warning(f"Cert directory not found: {cert_dir}")
        return False

    logger.debug("Cert directory found")
    for cert_file in os.listdir(cert_dir):
        cert_path = os.path.join(cert_dir, cert_file)
        if os.path.isfile(cert_path):
            logger.log(SUCCESS, f"Cert file found: {cert_path}")
        else:
            logger.warning(f"Expected cert file not found: {cert_path}")

    return True


def initialize_view() -> View:
    """Initialize and return the View object."""
    logger.info("Initializing View")
    try:
        view = View()
        logger.log(SUCCESS, "View initialized successfully")
        return view
    except Exception as e:
        logger.error(f"Failed to initialize View: {e}")
        raise InitializationError(f"Failed to initialize View: {e}") from e


def configure_view(view: View) -> None:
    """Configure the view properties."""
    logger.info("Setting window properties")
    view.resizable(False, False)
    view.title("Seedkeeper Tool")

    # Add these lines to set the window icon
    icon_path = os.path.join(get_application_path(), "satochip_utils.ico")
    if os.path.exists(icon_path):
        view.iconbitmap(icon_path)
    else:
        logger.warning(f"Icon file not found: {icon_path}")


def main() -> NoReturn:
    """Main function to run the Seedkeeper Tool."""
    verbose_mode = setup_logging()
    logger = get_logger(__name__)

    logger.debug("Starting Seedkeeper Tool in verbose mode" if verbose_mode else "Starting Seedkeeper Tool")
    logger.info("Starting Seedkeeper Tool")

    try:
        app_path = get_application_path()
        os.chdir(app_path)

        cert_dir_exists = check_cert_directory(app_path)
        if not cert_dir_exists:
            logger.warning("Continuing execution without cert directory. Some features may be limited.")

        view = initialize_view()
        configure_view(view)

        logger.info("Displaying welcome screen")
        view.view_welcome()  # Removed cert_dir_missing argument

        logger.info("Starting main event loop")
        view.mainloop()
    except InitializationError as e:
        logger.critical(f"Initialization error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()


