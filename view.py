import logging
import sys
import tkinter
from typing import Optional
import os
import time
import _tkinter
import customtkinter
from customtkinter import CTkImage
import webbrowser
from PIL import Image, ImageTk


if (len(sys.argv) >= 2) and (sys.argv[1] in ['-v', '--verbose']):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(name)s - %(funcName)s() - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
else:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(name)s - %(funcName)s() - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

MAIN_MENU_COLOR = "#202738"
BUTTON_COLOR = "#e1e1e0"
HOVER_COLOR = "grey"
TEXT_COLOR = "black"

ICON_PATH = "./pictures_db/icon_"


class InitializationError(Exception):
    pass

class View(customtkinter.CTk):
    def __init__(self, loglevel: int = logging.INFO):
        try:
            logger.info("Starting View.__init__()")
            super().__init__()
            self._setup_logging(loglevel)
            self._initialize_attributes()
            #self._initialize_controller(loglevel)
            self._setup_main_window()
            self._declare_widgets()
            #self._launch_welcome_view()
            self._set_close_protocol()
            logger.info("Initialization of View.__init__() completed successfully")
        except Exception as e:
            logger.critical(f"An unexpected error occurred in __init__: {e}", exc_info=True)
            raise InitializationError(f"Failed to initialize View: {e}") from e

    def _setup_logging(self, loglevel: int) -> None:
        logger.setLevel(loglevel)
        logger.debug(f"Log level set to {logging.getLevelName(loglevel)}")

    def _initialize_attributes(self) -> None:
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

    def _initialize_controller(self, loglevel: int) -> None:
        try:
            logger.info("Initializing controller")
            self.controller = Controller(None, self, loglevel=loglevel)
            logger.info("Controller initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize the controller: {e}", exc_info=True)
            raise InitializationError(f"Failed to initialize the controller: {e}") from e

    def _setup_main_window(self) -> None:
        try:
            logger.debug("Initializing main window")
            self.main_window()
            logger.debug("Main window initialized successfully")

            logger.debug("Creating main frame")
            self.main_frame = customtkinter.CTkFrame(self, width=750, height=600, bg_color="whitesmoke",
                                                     fg_color="whitesmoke")
            self.main_frame.place(relx=0.25, rely=0.5, anchor="e")
            logger.debug("Main frame created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize the main window or create the main frame: {e}", exc_info=True)
            raise InitializationError(f"Failed to setup main window: {e}") from e

    def _declare_widgets(self) -> None:
        try:
            logger.debug("Declaring widgets")
            self.current_frame: Optional[customtkinter.CTkFrame] = None
            self.canvas: Optional[tkinter.Canvas] = None
            self.background_photo: Optional[tkinter.PhotoImage] = None
            self.create_background_photo: Optional[callable] = None
            self.header: Optional[customtkinter.CTkLabel] = None
            self.text_box: Optional[customtkinter.CTkTextbox] = None
            self.button: Optional[customtkinter.CTkButton] = None
            self.finish_button: Optional[customtkinter.CTkButton] = None
            self.menu: Optional[customtkinter.CTkFrame] = None
            self.counter: Optional[int] = None
            self.display_menu: bool = False
            logger.debug("Widgets declared successfully")
        except Exception as e:
            logger.error(f"Failed to declare widgets: {e}", exc_info=True)
            raise InitializationError(f"Failed to declare widgets: {e}") from e

    def _launch_welcome_view(self) -> None:
        try:
            logger.debug("Launching welcome view")
            self.welcome()
            logger.debug("Welcome view launched successfully")
        except Exception as e:
            logger.error(f"Failed to launch welcome view: {e}", exc_info=True)
            raise InitializationError(f"Failed to launch welcome view: {e}") from e

    def _set_close_protocol(self) -> None:
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        logger.debug("WM_DELETE_WINDOW protocol set successfully")

    def main_window(self, width: Optional[int] = None, height: Optional[int] = None) -> None:
        logger.debug("IN View.main_window")
        try:
            self.title("SEEDKEEPER TOOL")
            logger.debug("Window title set to 'SATOCHIP UTILS'")

            window_width = width or 1000
            window_height = height or 600
            logger.debug(f"Window dimensions set to width: {window_width}, height: {window_height}")

            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            logger.debug(f"Screen dimensions obtained: width: {screen_width}, height: {screen_height}")

            center_x = int((screen_width - window_width) / 2)
            center_y = int((screen_height - window_height) / 2)
            logger.debug(f"Window position calculated: center_x: {center_x}, center_y: {center_y}")

            self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
            logger.debug("Window geometry set successfully")
        except Exception as e:
            logger.critical(f"An unexpected error occurred in main_window: {e}", exc_info=True)
            raise InitializationError(f"Failed to setup main window: {e}") from e
        logger.debug("OUT View.main_window")

    def on_close(self) -> None:
        logger.info("IN View.on_close : Closing App")
        try:
            self.app_open = False
            logger.debug("app_open set to False")

            self.destroy()
            logger.debug("Main window destroyed")

            self.controller.cc.card_disconnect()
            logger.debug("Card disconnected successfully")
        except Exception as e:
            logger.error(f"An unexpected error occurred in on_close: {e}", exc_info=True)
        finally:
            logger.debug("OUT View.on_close")

    def welcome(self) -> None:
        # Cette méthode doit être implémentée pour lancer la vue de bienvenue
        pass