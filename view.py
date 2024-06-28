from typing import Optional
from functools import wraps

import customtkinter
from PIL import Image, ImageTk

from log_config import get_logger, SUCCESS, setup_logging

logger = get_logger(__name__)

BG_MAIN_MENU = "#202738"
BG_BUTTON = "#e1e1e0"
BG_HOVER_BUTTON = "grey"
TEXT_COLOR = "black"
ICON_PATH = "./pictures_db/icon_"

APP_VERSION = "0.0.0"


def log_method(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Entering {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__}")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise
    return wrapper


class InitializationError(Exception):
    pass


class View(customtkinter.CTk):
    @log_method
    def __init__(self):
        try:
            super().__init__()
            self._initialize_attributes()
            self._setup_main_window()
            self._declare_widgets()
            self._set_close_protocol()
            logger.log(SUCCESS, "View initialization completed successfully")
        except Exception as e:
            logger.critical("Failed to initialize View", exc_info=True)
            raise InitializationError(f"Failed to initialize View: {e}") from e

    def _initialize_attributes(self):
        self.card_type: Optional[str] = None
        self.setup_done: Optional[bool] = None
        self.is_seeded: Optional[bool] = None
        self.needs2FA: Optional[bool] = None
        self.card_version: Optional[str] = None
        self.card_present: Optional[bool] = None
        self.card_label: Optional[str] = None
        self.app_open: bool = True
        self.welcome_in_display: bool = True
        self.spot_if_unlock: bool = False
        self.pin_left: Optional[int] = None

    @log_method
    def _setup_main_window(self):
        self.title("SEEDKEEPER TOOL")
        window_width = 1000
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        self.main_frame = customtkinter.CTkFrame(self, width=750, height=600, bg_color="whitesmoke",
                                                 fg_color="whitesmoke")
        self.main_frame.place(relx=0.25, rely=0.5, anchor="e")

    @log_method
    def _declare_widgets(self):
        self.current_frame: Optional[customtkinter.CTkFrame] = None
        self.canvas: Optional[customtkinter.Canvas] = None
        self.background_photo: Optional[ImageTk.PhotoImage] = None
        self.create_background_photo: Optional[callable] = None
        self.header: Optional[customtkinter.CTkLabel] = None
        self.text_box: Optional[customtkinter.CTkTextbox] = None
        self.button: Optional[customtkinter.CTkButton] = None
        self.finish_button: Optional[customtkinter.CTkButton] = None
        self.menu: Optional[customtkinter.CTkFrame] = None
        self.counter: Optional[int] = None
        self.display_menu: bool = False

    def _set_close_protocol(self):
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        logger.debug("WM_DELETE_WINDOW protocol set successfully")

    @log_method
    def on_close(self):
        logger.info("Closing App")
        self.app_open = False
        self.destroy()
        # Assuming self.controller.cc.card_disconnect() exists
        # self.controller.cc.card_disconnect()

    @log_method
    def welcome(self):
        # This method should be implemented to launch the welcome view
        pass


# Example usage of different log levels
if __name__ == "__main__":
    setup_logging()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.log(SUCCESS, "This is a success message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")