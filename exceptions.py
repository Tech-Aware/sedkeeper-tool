import logging
from log_config import get_logger, SUCCESS, setup_logging
logger = get_logger(__name__)

# EXCEPTIONS IN VIEW
class ViewError(Exception):
    """Base exception class for View-related errors."""
    def __init__(self, message):
        super().__init__(message)  # Appelle le constructeur de Exception avec le message
        logger.error("An error occurred in View", exc_info=True)


class AttributeInitializationError(ViewError):
    """Exception raised when there's an error initializing attributes."""
    def __init__(self, message="Error in attribute initialization"):
        super().__init__(message)


class ApplicationRestartError(ViewError):
    """Exception raised when there's an error restarting the application."""
    def __init__(self, message="Error in application restart"):
        super().__init__(message)


class FrameClearingError(ViewError):
    """Exception raised when there's an error clearing a frame."""
    def __init__(self, message="Error in frame clearing"):
        super().__init__(message)


class MenuDeletionError(ViewError):
    """Exception raised when there's an error deleting a menu."""
    def __init__(self, message="Error in menu deletion"):
        super().__init__(message)


class UIElementError(ViewError):
    """Exception raised for errors in creating or manipulating UI elements."""
    def __init__(self, message="Error in UI element"):
        super().__init__(message)


# EXCEPTIONS IN UI ELEMENT
class WindowSetupError(UIElementError):
    """Exception raised when there's an error setting up the main window."""
    def __init__(self, message="Error in window setup"):
        super().__init__(message)


class FrameCreationError(UIElementError):
    """Exception raised when there's an error creating or placing a frame."""
    def __init__(self, message="Error in frame creation"):
        super().__init__(message)


class MenuCreationError(UIElementError):
    """Exception raised when there's an error creating a menu."""
    def __init__(self, message="Error in menu creation"):
        super().__init__(message)



class CanvasCreationError(UIElementError):
    """Exception raised when there's an error creating a canvas."""
    def __init__(self, message="Error in canvas creation"):
        super().__init__(message)


class BackgroundPhotoError(UIElementError):
    """Exception raised when there's an error creating a background photo."""
    def __init__(self, message="Error in background photo creation"):
        super().__init__(message)


class LabelCreationError(UIElementError):
    """Exception raised when there's an error creating a label."""
    def __init__(self, message="Error in label creation"):
        super().__init__(message)


class EntryCreationError(UIElementError):
    """Exception raised when there's an error creating an entry."""
    def __init__(self, message="Error in entry creation"):
        super().__init__(message)


class HeaderCreationError(UIElementError):
    """Exception raised when there's an error creating a header."""
    def __init__(self, message="Error in header creation"):
        super().__init__(message)

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
