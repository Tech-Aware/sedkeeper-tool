import logging
from log_config import get_logger, SUCCESS, setup_logging
logger = get_logger(__name__)


class ViewError(Exception):
    """Base exception class for View-related errors."""
    def __init__(self, message):
        super().__init__(message)  # Appelle le constructeur de Exception avec le message
        logger.error("An error occurred in View", exc_info=True)


class FrameError(ViewError):
    """Exception raised for errors in frame operations."""
    def __init__(self, message="Error in frame operation"):
        super().__init__(message)  # Appelle le constructeur de ViewError avec le message


class SecretFrameCreationError(FrameError):
    """Exception raised for errors in the secret frame creation process."""
    def __init__(self, message="Error in secret frame creation"):
        super().__init__(message)


class WelcomeFrameCreationError(FrameError):
    """Exception raised for errors in the welcome frame creation process."""

    def __init__(self, message="Error in welcome frame creation"):
        super().__init__(message)


class UIElementError(ViewError):
    """Exception raised for errors in creating or manipulating UI elements."""
    def __init__(self, message="Error in UI element"):
        super().__init__(message)


class InitializationError(ViewError):
    """Exception raised when View initialization fails."""
    def __init__(self, message="Error in view initialization"):
        super().__init__(message)


class ButtonCreationError(ViewError):
    """Exception raised when there's an error creating a button."""
    def __init__(self, message="Error in button creation"):
        super().__init__(message)


class MainMenuError(ViewError):
    """Exception raised for errors in the main menu creation or manipulation."""
    def __init__(self, message="Error in main menu"):
        super().__init__(message)


class SeedkeeperError(Exception):
    """Base exception class for Seedkeeper Tool."""
    pass


class CardError(SeedkeeperError):
    """Exception raised for errors related to card operations."""
    pass


class ControllerError(SeedkeeperError):
    """Base exception class for Controller-related errors."""
    pass
