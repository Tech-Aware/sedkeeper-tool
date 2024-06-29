class SeedkeeperError(Exception):
    """Base exception class for Seedkeeper Tool."""
    pass


class CardError(SeedkeeperError):
    """Exception raised for errors related to card operations."""
    pass


class ControllerError(SeedkeeperError):
    """Base exception class for Controller-related errors."""
    pass


class ViewError(SeedkeeperError):
    """Base exception class for View-related errors."""
    pass


class FrameError(ViewError):
    """Exception raised for errors in frame operations."""
    pass


class UIElementError(ViewError):
    """Exception raised for errors in creating or manipulating UI elements."""
    pass


class InitializationError(ViewError):
    """Exception raised when View initialization fails."""
    pass


class ButtonCreationError(ViewError):
    """Exception raised when there's an error creating a button."""
    pass


class MainMenuError(ViewError):
    """Exception raised for errors in the main menu creation or manipulation."""
    pass