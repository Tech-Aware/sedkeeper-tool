import logging
import sys
import os
from typing import Optional, Dict, List, Callable, Any
from functools import wraps
import gc
import webbrowser

import customtkinter
import tkinter
from PIL import Image, ImageTk

from controller import Controller

from log_config import get_logger, SUCCESS, setup_logging
from exceptions import (ViewError, FrameError, UIElementError, InitializationError, ButtonCreationError, MainMenuError,
                        SecretFrameCreationError)

from pysatochip.version import PYSATOCHIP_VERSION
from pysatochip.CardConnector import CardError

logger = get_logger(__name__)

# Constants
BG_MAIN_MENU = "#21283b"
BG_BUTTON = "#e1e1e0"
BG_HOVER_BUTTON = "grey"
TEXT_COLOR = "black"
BUTTON_TEXT_COLOR = "white"
DEFAULT_BG_COLOR = "whitesmoke"
ICON_PATH = "./pictures_db/"
APP_VERSION = "0.1.0"
HIGHLIGHT_COLOR = "#D3D3D3"


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


class View(customtkinter.CTk):
    @log_method
    def __init__(self, loglevel=logging.INFO):
        try:
            logger.info("Initializing View")
            super().__init__()
            self._initialize_attributes()
            logger.debug("Attributes initialized")

            self._setup_main_window()
            logger.debug("Main window set up")

            self._declare_widgets()
            logger.debug("Widgets declared")

            self._set_close_protocol()
            logger.debug("Close protocol set")

            self.controller = Controller(None, self, loglevel=loglevel)
            logger.debug("Controller initialized")

            logger.log(SUCCESS, "View initialization completed successfully")
        except Exception as e:
            logger.critical("Failed to initialize View", exc_info=True)
            raise InitializationError(f"Failed to initialize View: {e}") from e

    #######################################################################################################
    """ UTILS """

    #######################################################################################################

    # FOR INITIALIZATION
    @log_method
    def _initialize_attributes(self):
        try:
            logger.debug("Initializing attributes")
            self.menu = None
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
            self.is_seedkeeper_v1: Optional[bool] = None
            logger.debug("All attributes initialized to their default values")
        except Exception as e:
            logger.error(f"Error in _initialize_attributes: {e}", exc_info=True)
            raise InitializationError(f"Failed to initialize attributes: {e}") from e

    #############################################################
    # FOR MAIN WINDOW
    @log_method
    def _setup_main_window(self):
        try:
            logger.info("Setting up main window")
            self.title("SEEDKEEPER TOOL")
            logger.debug("Window title set")

            window_width = 1000
            window_height = 600
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            center_x = int((screen_width - window_width) / 2)
            center_y = int((screen_height - window_height) / 2)
            self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
            logger.debug(f"Window geometry set to {window_width}x{window_height}, centered on screen")

            self.main_frame = customtkinter.CTkFrame(self, width=1000, height=600, bg_color='black',
                                                     fg_color='black')
            self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
            logger.debug("Main frame created and placed")

            logger.log(SUCCESS, "Main window setup completed successfully")
        except Exception as e:
            logger.error(f"Error in _setup_main_window: {e}", exc_info=True)
            raise UIElementError(f"Failed to set up main window: {e}") from e

    @log_method
    def _declare_widgets(self):
        try:
            logger.info("Declaring widgets")
            self.current_frame: Optional[customtkinter.CTkFrame] = None
            self.canvas: Optional[customtkinter.CTkCanvas] = None
            self.background_photo: Optional[ImageTk.PhotoImage] = None
            self.create_background_photo: Optional[callable] = None
            self.header: Optional[customtkinter.CTkLabel] = None
            self.text_box: Optional[customtkinter.CTkTextbox] = None
            self.button: Optional[customtkinter.CTkButton] = None
            self.finish_button: Optional[customtkinter.CTkButton] = None
            self.menu: Optional[customtkinter.CTkFrame] = None
            self.counter: Optional[int] = None
            self.display_menu: bool = False
            logger.debug("All widget attributes initialized to None or default values")

            logger.log(SUCCESS, "Widgets declared successfully")
        except Exception as e:
            logger.error(f"Error in _declare_widgets: {e}", exc_info=True)
            raise UIElementError(f"Failed to declare widgets: {e}") from e

    @log_method
    def _set_close_protocol(self):
        try:
            logger.info("Setting close protocol")
            self.protocol("WM_DELETE_WINDOW", self._on_close_app)
            logger.log(SUCCESS, "Close protocol set successfully")
        except Exception as e:
            logger.error(f"Error in _set_close_protocol: {e}", exc_info=True)
            raise UIElementError(f"Failed to set close protocol: {e}") from e

    @log_method
    def _on_close_app(self):
        try:
            logger.info("Closing application")
            self.app_open = False
            self.destroy()
            logger.log(SUCCESS, "Application closed successfully")
        except Exception as e:
            logger.error(f"Error while closing application: {e}", exc_info=True)
            # Even if there's an error, we should try to force close the application
            self.quit()

    @log_method
    def _restart_app(self):
        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    #############################################################
    # FOR UI MANAGEMENT
    @log_method
    def _create_label(self, text, bg_fg_color: str = None, frame=None) -> customtkinter.CTkLabel:
        try:
            logger.debug("Entering create_label method")
            label = None

            try:
                if bg_fg_color is not None:
                    try:
                        logger.debug(f"Creating label with background color: {bg_fg_color}")
                        label = customtkinter.CTkLabel(self.current_frame, text=text, bg_color=bg_fg_color,
                                                       fg_color=bg_fg_color,
                                                       font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                                  weight="normal"))
                    except Exception as e:
                        logger.warning(f"An error occurred while creating label with background color: {e}",
                                       exc_info=True)
                else:
                    try:
                        logger.debug(f"Creating label with background color: whitesmoke")
                        label = customtkinter.CTkLabel(self.main_frame, text=text, bg_color="whitesmoke",
                                                       fg_color="whitesmoke",
                                                       font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                                  weight="normal"))
                    except Exception as e:
                        logger.warning(f"An error occurred while creating label with background color: {e}",
                                       exc_info=True)

                if label is None:
                    try:
                        logger.debug("Creating default label with transparent background")
                        label = customtkinter.CTkLabel(self.current_frame, text=text, bg_color="transparent",
                                                       fg_color="transparent",
                                                       font=customtkinter.CTkFont(family="Outfit", size=16,
                                                                                  weight="normal"))
                    except Exception as e:
                        logger.error(f"An error occurred while creating default label: {e}", exc_info=True)

                logger.debug("Label created successfully")
            except Exception as e:
                logger.warning(f"An error occurred while creating the label: {e}", exc_info=True)
                try:
                    label = customtkinter.CTkLabel(self.current_frame, text=text, bg_color="transparent",
                                                   fg_color="transparent",
                                                   font=customtkinter.CTkFont(family="Outfit", size=20,
                                                                              weight="normal"))
                    logger.debug("Default label created due to previous error")
                except Exception as e:
                    logger.error(f"An error occurred while creating the default label after a previous error: {e}",
                                 exc_info=True)
                    raise

            logger.debug("Exiting create_label method successfully")
            return label
        except Exception as e:
            logger.error(f"An unexpected error occurred in create_label: {e}", exc_info=True)
            return None

    def _create_entry(self, show_option: str = None) -> customtkinter.CTkEntry:
        try:
            logger.debug("Entering create_entry method")
            entry = None

            try:
                if show_option is not None:
                    logger.debug("Creating entry with secure write")
                    entry = customtkinter.CTkEntry(self.current_frame, width=555, height=37, corner_radius=10,
                                                   bg_color='white',
                                                   fg_color=BG_BUTTON, border_color=BG_BUTTON,
                                                   show=f"{show_option}", text_color='grey')
                    logger.debug(f"Entry created with secure write option: {show_option}")
                else:
                    logger.debug("Creating entry without secure write")
                    entry = customtkinter.CTkEntry(self.current_frame, width=555, height=37, corner_radius=10,
                                                   bg_color='white',
                                                   fg_color=BG_BUTTON, border_color=BG_BUTTON, text_color='grey')
                    logger.debug("Entry created without secure write option")

                logger.debug("Exiting create_entry method successfully")
                return entry
            except Exception as e:
                logger.error(f"An error occurred while creating the entry: {e}", exc_info=True)
                raise
        except Exception as e:
            logger.error(f"An unexpected error occurred in create_entry: {e}", exc_info=True)
            return None

    @log_method
    def _create_button(self, text: str = None, command=None, frame=None) -> customtkinter.CTkButton:
        try:
            logger.debug("UTILS: VIew.create_button() | creating button")
            button = None

            try:
                if command is None:
                    try:
                        logger.debug("Creating button without command")
                        button = customtkinter.CTkButton(self.current_frame, text=text, corner_radius=100,
                                                         font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                                    weight="normal"),
                                                         bg_color='white', fg_color=BG_MAIN_MENU,
                                                         hover_color=BG_HOVER_BUTTON, cursor="hand2", width=120, height=35)
                    except Exception as e:
                        logger.error(f"Error creating button without command: {e}", exc_info=True)
                        raise
                else:
                    try:
                        logger.debug("Creating button with command")
                        button = customtkinter.CTkButton(self.current_frame, text=text, corner_radius=100,
                                                         font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                                    weight="normal"),
                                                         bg_color='white', fg_color=BG_MAIN_MENU,
                                                         hover_color=BG_HOVER_BUTTON, cursor="hand2", width=120, height=35,
                                                         command=command)
                    except Exception as e:
                        logger.error(f"Error creating button with command: {e}", exc_info=True)
                        raise
                logger.debug("Exiting create_button method successfully")
            except Exception as e:
                logger.error(f"An error occurred while creating the button: {e}", exc_info=True)
                raise

            logger.debug("Button created successfully")
            return button
        except Exception as e:
            logger.error(f"Unexpected error in create_button: {e}", exc_info=True)
            return None

    @log_method
    def _create_an_header(self, title_text: str = None, icon_name: str = None):
        try:
            logger.info(f"Creating header with title: {title_text} and icon: {icon_name}")

            header_frame = customtkinter.CTkFrame(self.current_frame, fg_color="whitesmoke", bg_color="whitesmoke", width=750,
                                                  height=40)
            logger.debug("Header frame created")

            if title_text and icon_name:
                icon_path = f"{ICON_PATH}{icon_name}"
                image = Image.open(icon_path)
                photo_image = customtkinter.CTkImage(image, size=(40, 40))
                logger.debug("Icon loaded and resized")

                button = customtkinter.CTkButton(header_frame, text=f"   {title_text}", image=photo_image,
                                                 font=customtkinter.CTkFont(family="Outfit", size=25, weight="bold"),
                                                 bg_color="whitesmoke", fg_color="whitesmoke", text_color="black",
                                                 hover_color="whitesmoke", compound="left")
                button.image = photo_image
                button.place(rely=0.5, relx=0, anchor="w")
                logger.debug("Header button created and placed")

            logger.log(SUCCESS, "Header created successfully")
            return header_frame
        except FileNotFoundError as e:
            logger.error(f"Icon file not found: {e}", exc_info=True)
            raise UIElementError(f"Failed to load icon: {e}") from e
        except Exception as e:
            logger.error(f"Error in create_an_header: {e}", exc_info=True)
            raise UIElementError(f"Failed to create header: {e}") from e

    @log_method
    def _create_frame(self):
        self._clear_current_frame()
        self.current_frame = customtkinter.CTkFrame(self.main_frame, width=750, height=600,
                                                    fg_color=DEFAULT_BG_COLOR,
                                                    bg_color=DEFAULT_BG_COLOR)
        self.current_frame.place(relx=0.250, rely=0.5, anchor='w')

    @log_method
    def _clear_current_frame(self):
        logger.debug("Clearing current frame")
        if hasattr(self, 'current_frame') and self.current_frame:
            for widget in self.current_frame.winfo_children():
                widget.destroy()
            self.current_frame.destroy()
            self.current_frame = None

        # Nettoyage des attributs spécifiques
        attributes_to_clear = ['header', 'canvas', 'background_photo', 'text_box', 'button', 'finish_button', 'menu']
        for attr in attributes_to_clear:
            if hasattr(self, attr):
                attr_value = getattr(self, attr)
                if attr_value:
                    if isinstance(attr_value, (customtkinter.CTkBaseClass, tkinter.BaseWidget)):
                        attr_value.destroy()
                    elif isinstance(attr_value, ImageTk.PhotoImage):
                        del attr_value
                setattr(self, attr, None)

        # Réinitialisation des variables d'état si nécessaire
        self.display_menu = False
        self.counter = None

        # Forcer le garbage collector
        gc.collect()

        logger.debug("Current frame and associated objects cleared")

    @log_method
    def _clear_welcome_frame(self):
        if hasattr(self, 'welcome_frame'):
            try:
                logger.info("Clearing welcome frame")
                self.welcome_frame.destroy()
                logger.log(SUCCESS, "Welcome frame cleared successfully")
            except Exception as e:
                logger.error(f"Error while clearing welcome frame: {e}", exc_info=True)
                raise FrameError(f"Failed to clear welcome frame: {e}") from e
        else:
            logger.debug("No welcome frame to clear")

    @staticmethod
    def _create_background_photo(self, picture_path):
        logger.info("UTILS: View.create_background_photo() | creating background photo")
        try:
            logger.info(f"Entering create_background_photo method with path: {picture_path}")

            try:
                if getattr(sys, 'frozen', False):
                    application_path = sys._MEIPASS
                    logger.info(f"Running in a bundled application, application path: {application_path}")
                else:
                    application_path = os.path.dirname(os.path.abspath(__file__))
                    logger.info(f"Running in a regular script, application path: {application_path}")
            except Exception as e:
                logger.error(f"An error occurred while determining application path: {e}", exc_info=True)
                return None

            try:
                pictures_path = os.path.join(application_path, picture_path)
                logger.debug(f"Full path to background photo: {pictures_path}")
            except Exception as e:
                logger.error(f"An error occurred while constructing the full path: {e}", exc_info=True)
                return None

            try:
                background_image = Image.open(pictures_path)
                logger.info("Background image opened successfully")
            except FileNotFoundError as e:
                logger.error(f"File not found: {pictures_path}, {e}", exc_info=True)
                return None
            except Exception as e:
                logger.error(f"An error occurred while opening the background image: {e}", exc_info=True)
                return None

            try:
                photo_image = ImageTk.PhotoImage(background_image)
                logger.info("Background photo converted to PhotoImage successfully")
            except Exception as e:
                logger.error(f"An error occurred while converting the background image to PhotoImage: {e}",
                             exc_info=True)
                return None

            logger.info("Background photo created successfully")
            return photo_image
        except Exception as e:
            logger.error(f"An unexpected error occurred in create_background_photo: {e}", exc_info=True)
            return None

    @log_method
    def _create_canvas(self, frame=None) -> customtkinter.CTkCanvas:
        try:
            logger.debug("UTILS: View.create_canvas() | creating canvas")
            try:
                canvas = customtkinter.CTkCanvas(self.current_frame, bg="whitesmoke", width=1000, height=600)
                logger.debug("Canvas created successfully")
            except Exception as e:
                logger.error(f"An error occurred while creating the canvas: {e}", exc_info=True)
                raise
            logger.debug("Exiting create_canvas method successfully")
            logger.debug("canvas create successfully")
            return canvas
        except Exception as e:
            logger.error(f"An unexpected error occurred in create_canvas: {e}", exc_info=True)
            return None

    ####################################################################################################################
    """ MAIN MENUS """

    ####################################################################################################################
    @log_method
    def _create_button_for_main_menu_item(
            self,
            frame: customtkinter.CTkFrame,
            button_label: str,
            icon_name: str,
            rel_y: float,
            rel_x: float,
            state: str,
            command: Optional[Callable] = None,
            text_color: str = 'white',
    ) -> Optional[customtkinter.CTkButton]:
        try:
            icon_path = f"{ICON_PATH}{icon_name}"
            image = Image.open(icon_path)
            image = image.resize((25, 25), Image.LANCZOS)
            photo_image = customtkinter.CTkImage(image)

            button = customtkinter.CTkButton(
                frame,
                text=button_label,
                text_color=text_color if text_color is not "white" else "white",
                font=customtkinter.CTkFont(family="Outfit", weight="normal", size=18),
                image=photo_image,
                bg_color=BG_MAIN_MENU,
                fg_color=BG_MAIN_MENU,
                hover_color=BG_MAIN_MENU,
                compound="left",
                cursor="hand2",
                command=command,
                state=state
            )
            button.image = photo_image  # keep a reference!
            button.place(rely=rel_y, relx=rel_x, anchor="e")

            return button

        except FileNotFoundError as e:
            logger.error(f"Icon file not found: {ICON_PATH}")
            raise ButtonCreationError(f"Failed to load icon: {e}") from e

        except (IOError, OSError) as e:
            logger.error(f"Error processing icon: {e}")
            raise ButtonCreationError(f"Failed to process icon: {e}") from e

        except Exception as e:
            logger.error(f"Unexpected error creating button: {e}")
            raise ButtonCreationError(f"Failed to create button: {e}") from e

    #############################################################
    # FOR SEEDKEEPER
    @log_method
    def create_seedkeeper_menu(self):
        self.menu = self._seedkeeper_lateral_menu()
        self.menu.place(relx=0.250, rely=0.5, anchor="e")
        logger.debug("Seedkeeper menu created")

    @log_method
    def _seedkeeper_lateral_menu(self, state=None, frame=None):
        if self.menu:
            self.menu.destroy()
        try:
            logger.info("Creating main menu")
            if state is None:
                state = "normal" if self.controller.cc.card_present else "disabled"
                logger.info(f"Card {'detected' if state == 'normal' else 'undetected'}, setting state to {state}")

            menu_frame = customtkinter.CTkFrame(self.main_frame, width=250, height=600,
                                                bg_color=BG_MAIN_MENU,
                                                fg_color=BG_MAIN_MENU, corner_radius=0, border_color="black",
                                                border_width=0)
            logger.debug("Main menu frame created")

            # Logo section
            image_frame = customtkinter.CTkFrame(menu_frame, bg_color=BG_MAIN_MENU, fg_color=BG_MAIN_MENU,
                                                 width=284, height=126)
            image_frame.place(rely=0, relx=0.5, anchor="n")
            logo_image = Image.open("./pictures_db/logo.png")
            logo_photo = ImageTk.PhotoImage(logo_image)
            canvas = customtkinter.CTkCanvas(image_frame, width=284, height=127, bg=BG_MAIN_MENU,
                                             highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(142, 63, image=logo_photo, anchor="center")
            canvas.image = logo_photo  # conserver une référence
            logger.debug("Logo section created")

            if self.controller.cc.card_present:
                logger.log(SUCCESS, "Card Present")
            else:
                logger.error(f"Card not present")

            # Menu items
            self._create_button_for_main_menu_item(menu_frame,
                                                   "My secrets" if self.controller.cc.card_present else "Insert card",
                                                   "secrets_icon.png" if self.controller.cc.card_present else "insert_card_icon.jpg",
                                                   0.26, 0.585 if self.controller.cc.card_present else 0.578,
                                                   state=state,
                                                   command=self.show_secrets if self.controller.cc.card_present else None)
            self._create_button_for_main_menu_item(menu_frame, "Generate",
                                                   "generate_icon.png" if self.controller.cc.card_present else "generate_locked_icon.png",
                                                   0.33, 0.56, state=state,
                                                   command=self.show_generate_secret if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self._create_button_for_main_menu_item(menu_frame, "Import",
                                                   "import_icon.png" if self.controller.cc.card_present else "import_locked_icon.png",
                                                   0.40, 0.51, state=state,
                                                   command=self.show_import_secret if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self._create_button_for_main_menu_item(menu_frame, "Settings",
                                                   "settings_icon.png" if self.controller.cc.card_present else "settings_locked_icon.png",
                                                   0.74, 0.546, state=state,
                                                   command=self.show_settings if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self._create_button_for_main_menu_item(menu_frame, "Help", "help_icon.png", 0.81, 0.49, state='normal',
                                                   command=self.show_help, text_color="white")
            self._create_button_for_main_menu_item(menu_frame, "Go to the webshop", "webshop_icon.png", 0.95, 0.82,
                                                   state='normal',
                                                   command=lambda: webbrowser.open("https://satochip.io/shop/", new=2))
            logger.debug("Menu items created")
            logger.log(SUCCESS, "Main menu created successfully")
            return menu_frame

        except Exception as e:
            error_message = f"An error occurred in main_menu: {e}"
            logger.error(error_message, exc_info=True)
            raise MainMenuError(error_message) from e

    @log_method
    def _delete_seedkeeper_menu(self):
        if hasattr(self, 'menu') and self.menu:
            self.menu.destroy()
            self.menu = None
        logger.debug("Seedkeeper menu destroyed")

    #############################################################
    # FOR SATOCHIP-UTILS

    @log_method
    def create_satochip_utils_menu(self):
        self._delete_seedkeeper_menu()  # Ensure old menu is removed
        self.menu = self._satochip_utils_lateral_menu()
        self.menu.place(relx=0, rely=0, relwidth=0.25, relheight=1)
        logger.debug("Satochip-utils menu created")

    @log_method
    def _satochip_utils_lateral_menu(self, state=None, frame=None):
        logger.info("IN View.main_menu")
        try:
            if state is None:
                state = "normal" if self.controller.cc.card_present else "disabled"
                logger.info(f"Card {'detected' if state == 'normal' else 'undetected'}, setting state to {state}")

            menu_frame = customtkinter.CTkFrame(self.main_frame, width=250, height=600,
                                                bg_color=BG_MAIN_MENU,
                                                fg_color=BG_MAIN_MENU, corner_radius=0, border_color="black",
                                                border_width=0)
            logger.debug("Menu frame created successfully")

            # Logo section
            image_frame = customtkinter.CTkFrame(menu_frame, bg_color=BG_MAIN_MENU, fg_color=BG_MAIN_MENU,
                                                 width=284, height=126)
            image_frame.place(rely=0, relx=0.5, anchor="n")
            logo_image = Image.open("./pictures_db/logo.png")
            logo_photo = ImageTk.PhotoImage(logo_image)
            canvas = customtkinter.CTkCanvas(image_frame, width=284, height=127, bg=BG_MAIN_MENU,
                                             highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(142, 63, image=logo_photo, anchor="center")
            canvas.image = logo_photo  # conserver une référence
            logger.debug("Logo section setup complete")

            if self.controller.cc.card_present:
                if not self.controller.cc.setup_done:
                    logger.info("Setup not done, enabling 'Setup My Card' button")
                    self._create_button_for_main_menu_item(menu_frame, "Setup My Card", "setup_my_card_icon.png", 0.26,
                                                           0.60,
                                                           state='normal', command=lambda: None)
                else:
                    if not self.controller.cc.is_seeded and self.controller.cc.card_type != "Satodime":
                        logger.info("Card not seeded, enabling 'Setup Seed' button")
                        self._create_button_for_main_menu_item(menu_frame, "Setup Seed", "seed.png", 0.26, 0.575,
                                                               state='normal',
                                                               command=lambda: None)
                    else:
                        logger.info("Setup completed, disabling 'Setup Done' button")
                        self._create_button_for_main_menu_item(menu_frame,
                                                               "Setup Done" if self.controller.cc.card_present else 'Insert Card',
                                                               "setup_done_icon.jpg" if self.controller.cc.card_present else "insert_card_icon.jpg",
                                                               0.26,
                                                               0.575 if self.controller.cc.card_present else 0.595,
                                                               state='disabled', command=lambda: None)
            else:
                logger.info("Card not present, setting 'Setup My Card' button state")
                self._create_button_for_main_menu_item(menu_frame, "Insert a Card", "insert_card_icon.jpg", 0.26, 0.585,
                                                       state='normal', command=lambda: None)

            if self.controller.cc.card_type != "Satodime" and self.controller.cc.setup_done:
                logger.debug("Enabling 'Change Pin' button")
                self._create_button_for_main_menu_item(menu_frame, "Change Pin", "change_pin_icon.png", 0.33, 0.567,
                                                       state='normal', command=lambda: None)
            else:
                logger.info(f"Card type is {self.controller.cc.card_type} | Disabling 'Change Pin' button")
                self._create_button_for_main_menu_item(menu_frame, "Change Pin", "change_pin_locked_icon.jpg", 0.33,
                                                       0.57,
                                                       state='disabled', command=lambda: None)

            if self.controller.cc.setup_done:
                self._create_button_for_main_menu_item(menu_frame, "Edit Label", "edit_label_icon.png", 0.40, 0.537,
                                                       state='normal', command=lambda: [None])
            else:
                self._create_button_for_main_menu_item(menu_frame, "Edit Label", "edit_label_locked_icon.jpg", 0.40,
                                                       0.546,
                                                       state='disabled', command=lambda: None)

            def before_check_authenticity():
                logger.info("IN View.main_menu() | Requesting card verification PIN")
                if self.controller.cc.card_type != "Satodime":
                    if self.controller.cc.is_pin_set():
                        self.controller.cc.card_verify_PIN_simple()
                    else:
                        self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')

            if self.controller.cc.setup_done:
                self._create_button_for_main_menu_item(menu_frame, "Check Authenticity", "check_authenticity_icon.png",
                                                       0.47, 0.775,
                                                       state='normal', command=lambda: [before_check_authenticity(),
                                                                                        None])
            else:
                self._create_button_for_main_menu_item(menu_frame, "Check Authenticity",
                                                       "check_authenticity_locked_icon.jpg", 0.47, 0.66,
                                                       state='disabled',
                                                       command=lambda: None)
            if self.controller.cc.card_present:
                if self.controller.cc.card_type != "Satodime":
                    self._create_button_for_main_menu_item(menu_frame, "Reset my Card", "reset_icon.png", 0.54, 0.665,
                                                           state='normal', command=lambda: None)
                else:
                    # TODO: remove button?
                    self._create_button_for_main_menu_item(menu_frame, "Reset my Card", "reset_locked_icon.jpg",
                                                           0.54, 0.595,
                                                           state='disabled', command=lambda: None)
                self._create_button_for_main_menu_item(menu_frame, "About", "about_icon.jpg", rel_y=0.73, rel_x=0.476,
                                                       state='normal', command=lambda: None)
            else:
                self._create_button_for_main_menu_item(menu_frame, "Reset my Card", "reset_locked_icon.jpg", 0.54,
                                                       0.595,
                                                       state='disabled', command=lambda: None)
                self._create_button_for_main_menu_item(menu_frame, "About", "about_locked_icon.jpg", rel_y=0.73,
                                                       rel_x=0.5052, state='disabled', command=lambda: None)

            self._create_button_for_main_menu_item(menu_frame, "Go to the Webshop", "webshop_icon.png", 0.95, 0.805,
                                                   state='normal',
                                                   command=lambda: webbrowser.open("https://satochip.io/shop/", new=2))

            logger.info("Main menu setup complete")
            return menu_frame

        except Exception as e:
            logger.error(f"An error occurred in main_menu: {e}", exc_info=True)

    @log_method
    def _delete_satochip_utils_menu(self):
        self.menu.destroy()
        logger.debug("Satochip-utils menu destroyed")

    # FOR CARD INFORMATION

    @log_method
    def update_status(self, isConnected=None):
        try:
            if self.controller.cc.mode_factory_reset == True:
                # we are in factory reset mode
                if isConnected is True:
                    logger.info(f"Card inserted for Reset Factory!")
                    try:
                        # Mettre à jour les labels et les boutons en fonction de l'insertion de la carte
                        # self.reset_button.configure(text='Reset', state='normal')
                        self.show_button.configure(text='Reset', state='normal')
                        logger.debug("Labels and button updated for card insertion")
                    except Exception as e:
                        logger.error(f"An error occurred while updating labels and button for card insertion: {e}",
                                     exc_info=True)

                elif isConnected is False:
                    logger.info(f"Card removed for Reset Factory!")
                    try:
                        # Mettre à jour les labels et les boutons en fonction du retrait de la carte
                        self.show_button.configure(text='Insert card', state='disabled')
                        logger.debug("Labels and button updated for card removal")
                    except Exception as e:
                        logger.error(f"An error occurred while updating labels and button for card removal: {e}",
                                     exc_info=True)
                else:  # None
                    pass
            else:
                # normal mode
                logger.info("CC UTILS: View.update_status | Entering update_status method")
                if isConnected is True:
                    try:
                        logger.info("Getting card status")
                        self.controller.get_card_status()
                        self.lets_go_button.configure(text="Let's go", command=self.show_secrets, state='normal')
                    except Exception as e:
                        logger.error(f"An error occurred while getting card status: {e}", exc_info=True)

                elif isConnected is False:
                    try:
                        logger.info("Card disconnected, resetting status")
                        self.welcome()
                        self.lets_go_button.configure(text="Insert card", command=None, state='disabled')
                    except Exception as e:
                        logger.error(f"An error occurred while resetting card status: {e}", exc_info=True)
                    logger.info("Exiting update_status method successfully")

                else:  # isConnected is None
                    pass

        except Exception as e:
            logger.error(f"An unexpected error occurred in update_status method: {e}", exc_info=True)

    @log_method
    def get_passphrase(self, msg):
        logger.info("Initiating passphrase entry")
        try:
            popup = customtkinter.CTkToplevel(self)
            popup.title("PIN Required")
            popup.configure(fg_color='whitesmoke')
            popup.protocol("WM_DELETE_WINDOW", lambda: popup.destroy())

            popup_width, popup_height = 400, 200
            position_right = int(self.winfo_screenwidth() / 2 - popup_width / 2)
            position_down = int(self.winfo_screenheight() / 2 - popup_height / 2)
            popup.geometry(f"{popup_width}x{popup_height}+{position_right}+{position_down}")
            logger.debug("Passphrase popup created and positioned")

            icon_image = Image.open("./pictures_db/change_pin_popup_icon.jpg")
            icon = customtkinter.CTkImage(light_image=icon_image, size=(20, 20))
            icon_label = customtkinter.CTkLabel(popup, image=icon, text="\nEnter the PIN code of your card.",
                                                compound='top',
                                                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"))
            icon_label.pack(pady=(0, 10))
            logger.debug("Icon and label added to popup")

            passphrase_entry = customtkinter.CTkEntry(popup, show="*", corner_radius=10, border_width=0,
                                                      width=229, height=37, bg_color='whitesmoke',
                                                      fg_color=BG_BUTTON, text_color='grey')
            popup.after(100, passphrase_entry.focus_force)
            passphrase_entry.pack(pady=15)
            logger.debug("Passphrase entry field added to popup")

            pin = None

            def submit_passphrase():
                nonlocal pin
                pin = passphrase_entry.get()
                popup.destroy()
                logger.debug("Passphrase submitted")
                self.update_status()

            submit_button = customtkinter.CTkButton(popup, bg_color='whitesmoke', fg_color=BG_MAIN_MENU,
                                                    width=120, height=35, corner_radius=34,
                                                    hover_color=BG_HOVER_BUTTON, text="Submit",
                                                    command=submit_passphrase,
                                                    font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                               weight="normal"))
            submit_button.pack(pady=10)
            logger.debug("Submit button added to popup")

            popup.transient(self)
            popup.bind('<Return>', lambda event: submit_passphrase())
            self.wait_window(popup)

            logger.log(SUCCESS, "Passphrase entry completed")
            return pin

        except Exception as e:
            logger.error(f"Error in get_passphrase: {e}", exc_info=True)
            return None

    # Revised show methods with basic implementation
    @log_method
    def show_secrets(self):
        try:
            logger.info("Initiating show secrets process")
            self.welcome_in_display = False
            self._clear_welcome_frame()
            secrets_data = self.controller.retrieve_secrets_stored_into_the_card()
            self.my_secrets(secrets_data)
            logger.log(SUCCESS, "Secrets displayed successfully")
        except Exception as e:
            logger.error(f"Error in show_secrets: {e}", exc_info=True)
            self._handle_view_error(f"Failed to show secrets: {e}")

    @log_method
    def show_generate_secret(self):
        try:
            logger.info("Initiating secret generation process")
            # TODO: Implement full functionality to generate a secret
            logger.log(SUCCESS, "Secret generation process initiated")
        except Exception as e:
            logger.error(f"Error in generate_secret: {e}", exc_info=True)
            self._handle_view_error(f"Failed to generate secret: {e}")

    @log_method
    def show_import_secret(self):
        try:
            logger.info("Initiating secret import process")
            # TODO: Implement full functionality to import a secret
            logger.log(SUCCESS, "Secret import process initiated")
        except Exception as e:
            logger.error(f"Error in import_secret: {e}", exc_info=True)
            self._handle_view_error(f"Failed to import secret: {e}")

    @log_method
    def show_settings(self):
        try:
            logger.info("Displaying settings")
            self._delete_seedkeeper_menu()
            self.start_setup()
            self.create_satochip_utils_menu()
            logger.log(SUCCESS, "Settings displayed successfully")
        except Exception as e:
            logger.error(f"Error in show_settings: {e}", exc_info=True)
            self._handle_view_error(f"Failed to show settings: {e}")

    @log_method
    def show_help(self):
        try:
            logger.info("Displaying help information")
            # TODO: Implement full functionality to show help
            logger.log(SUCCESS, "Help information displayed successfully")
        except Exception as e:
            logger.error(f"Error in show_help: {e}", exc_info=True)
            self._handle_view_error(f"Failed to show help: {e}")

    @log_method
    def show(self, title, msg: str, button_txt="Ok", cmd=None, icon_path=None):
        try:
            logger.info(f"Showing popup: {title}")
            popup = self._create_popup(title)
            self._add_content_to_popup(popup, msg, icon_path)
            self._add_button_to_popup(popup, button_txt, cmd)
            logger.log(SUCCESS, f"Popup '{title}' displayed successfully")
        except Exception as e:
            logger.error(f"Error in show: {e}", exc_info=True)
            raise UIElementError(f"Failed to show popup: {e}") from e

    @log_method
    def _create_popup(self, title):
        popup = customtkinter.CTkToplevel(self)
        popup.title(title)
        popup.configure(fg_color='whitesmoke')
        popup.protocol("WM_DELETE_WINDOW", popup.destroy)
        self._center_popup(popup)
        return popup

    @log_method
    def _center_popup(self, popup):
        popup_width, popup_height = 400, 200
        position_right = int(self.winfo_screenwidth() / 2 - popup_width / 2)
        position_down = int(self.winfo_screenheight() / 2 - popup_height / 2)
        popup.geometry(f"{popup_width}x{popup_height}+{position_right}+{position_down}")

    @log_method
    def _add_content_to_popup(self, popup, msg, icon_path):
        if icon_path:
            icon_image = Image.open(icon_path)
            icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
            label = customtkinter.CTkLabel(popup, image=icon, text=f"\n{msg}", compound='top',
                                           font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"))
        else:
            label = customtkinter.CTkLabel(popup, text=msg,
                                           font=customtkinter.CTkFont(family="Outfit", size=14, weight="bold"))
        label.pack(pady=20)

    @log_method
    def _add_button_to_popup(self, popup, button_txt, cmd):
        close_cmd = lambda: [cmd() if cmd else None, popup.destroy()]
        button = customtkinter.CTkButton(popup, text=button_txt, fg_color=BG_MAIN_MENU,
                                         hover_color=BG_HOVER_BUTTON, bg_color='whitesmoke',
                                         width=120, height=35, corner_radius=34,
                                         font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                                         command=close_cmd)
        button.pack(pady=20)

    # FOR BUILD FRAME
    @log_method
    def create_welcome_button(self, text: str, command: Optional[Callable] = None,
                              frame: Optional[customtkinter.CTkFrame] = None) -> customtkinter.CTkButton:
        try:
            logger.info(f"Creating welcome button: {text}")
            target_frame = frame or self.welcome_frame
            button = customtkinter.CTkButton(
                target_frame,
                text=text,
                command=command,
                corner_radius=100,
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                bg_color=DEFAULT_BG_COLOR,
                fg_color=BG_MAIN_MENU,
                hover_color=BG_HOVER_BUTTON,
                cursor="hand2",
                width=120,
                height=35
            )
            logger.log(SUCCESS, f"Welcome button '{text}' created successfully")
            return button
        except Exception as e:
            error_msg = f"Failed to create welcome button '{text}': {e}"
            logger.error(error_msg, exc_info=True)
            raise UIElementError(error_msg) from e

    """FOR ERRORS MANAGEMENT"""

    # todo: replace handle view error for show_error
    @log_method
    def _handle_view_error(self, message: str):
        logger.error(f"View Error: {message}")
        try:
            error_label = customtkinter.CTkLabel(
                self.current_frame,
                text=message,
                fg_color="red",
                text_color="white",
                corner_radius=8
            )
            error_label.place(relx=0.5, rely=0.9, anchor="center")
            self.after(5000, error_label.destroy)
        except Exception as e:
            logger.critical(f"Failed to display error message: {e}", exc_info=True)
            # Consider implementing a fallback error display method here

    """WELCOME IN SEEDKEEPER TOOL"""

    @log_method
    def welcome(self):
        self.welcome_in_display = True

        def _setup_welcome_frame():
            try:
                logger.info("Setting up welcome frame")
                self.welcome_frame = customtkinter.CTkFrame(self, fg_color=BG_MAIN_MENU)
                self.welcome_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.log(SUCCESS, "Welcome frame set up successfully")
            except Exception as e:
                error_msg = f"Failed to create welcome frame: {e}"
                logger.error(error_msg, exc_info=True)
                raise FrameError(error_msg) from e

        def _create_welcome_background():
            try:
                logger.info("Creating welcome background")
                bg_image = Image.open("./pictures_db/welcome_in_seedkeeper_tool.png")
                self.background_photo = ImageTk.PhotoImage(bg_image)
                self.canvas = customtkinter.CTkCanvas(self.welcome_frame, width=bg_image.width, height=bg_image.height)
                self.canvas.pack(fill="both", expand=True)
                self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
                logger.log(SUCCESS, "Welcome background created successfully")
            except FileNotFoundError:
                logger.error("Background image file not found", exc_info=True)
                raise UIElementError("Background image file not found.")
            except Exception as e:
                logger.error(f"Failed to create welcome background: {e}", exc_info=True)
                raise UIElementError(f"Failed to create welcome background: {e}")

        def _create_welcome_header():
            try:
                logger.info("Creating welcome header")
                header_frame = customtkinter.CTkFrame(self.welcome_frame, width=380, height=178,
                                                      fg_color=DEFAULT_BG_COLOR)
                header_frame.place(relx=0.1, rely=0.03, anchor='nw')

                logo_canvas = customtkinter.CTkCanvas(header_frame, width=400, height=400, bg='black')
                logo_canvas.place(relx=0.5, rely=0.5, anchor='center')

                icon_path = "./pictures_db/icon_welcome_logo.png"
                image = Image.open(icon_path)
                photo = ImageTk.PhotoImage(image)

                logo_canvas_width = logo_canvas.winfo_reqwidth()
                logo_canvas_height = logo_canvas.winfo_reqheight()
                image_width = photo.width()
                image_height = photo.height()

                x_center = (logo_canvas_width - image_width) // 2
                y_center = (logo_canvas_height - image_height) // 2

                logo_canvas.create_image(x_center, y_center, anchor='nw', image=photo)
                logo_canvas.image = photo  # Keep a reference to prevent garbage collection

                logger.log(SUCCESS, "Welcome header created successfully")
            except FileNotFoundError:
                logger.error(f"Logo file not found: {icon_path}", exc_info=True)
            except Exception as e:
                error_msg = f"Failed to create welcome header: {e}"
                logger.error(error_msg, exc_info=True)
                raise UIElementError(error_msg) from e

        def _create_welcome_labels():
            try:
                logger.info("Creating welcome labels")
                labels = [
                    ("Seedkeeper-tool", 0.4, True),
                    ("The companion app for your Seedkeeper card.", 0.5, False),
                    ("It will help you to safely store and manage your crypto-related", 0.55, False),
                    ("secrets including seedphrases, passwords and credentials.", 0.60, False),
                    ('First time using the app? Plug your Seedkeeper card into the', 0.7, False),
                    ('card reader and follow the guide...', 0.75, False)
                ]

                for text, rely, is_bold in labels:
                    label = customtkinter.CTkLabel(
                        self.welcome_frame,
                        text=text,
                        font=customtkinter.CTkFont(size=18, weight='bold' if is_bold else 'normal'),
                        text_color="white"
                    )
                    label.place(relx=0.05, rely=rely, anchor="w")

                logger.log(SUCCESS, "Welcome labels created successfully")
            except Exception as e:
                error_msg = f"Failed to create welcome labels: {e}"
                logger.error(error_msg, exc_info=True)
                raise UIElementError(error_msg) from e

        def _create_welcome_button():
            try:
                logger.info("Creating welcome button")
                self.lets_go_button = self.create_welcome_button('', None)
                self.lets_go_button.place(relx=0.85, rely=0.93, anchor="center")

                logger.log(SUCCESS, "Welcome button created successfully")
            except Exception as e:
                error_msg = f"Failed to create welcome button: {e}"
                logger.error(error_msg, exc_info=True)
                raise UIElementError(error_msg) from e

        logger.info("Initializing welcome view")
        try:
            self._clear_current_frame()
            _setup_welcome_frame()
            _create_welcome_background()
            _create_welcome_header()
            _create_welcome_labels()
            _create_welcome_button()

            logger.log(SUCCESS, "Welcome view created successfully")
            self.update()  # Force update of the window
        except FrameError as e:
            logger.error(f"Frame error in welcome method: {e}", exc_info=True)
            self._handle_view_error("An error occurred while setting up the welcome frame.")
        except UIElementError as e:
            logger.error(f"UI element error in welcome method: {e}", exc_info=True)
            self._handle_view_error("An error occurred while creating UI elements.")
        except Exception as e:
            logger.error(f"Unexpected error in welcome method: {e}", exc_info=True)
            self._handle_view_error("An unexpected error occurred. Please try again.")


    ####################################################################################################################
    """
    FRAMES
    """
    ####################################################################################################################

    #############################################################
    # START SETUP
    @log_method
    def start_setup(self):
        def _create_start_setup_frame():
            self._create_frame()

        def _create_return_button():
            try:
                return_button = self._create_button(text="Back",
                                                    command=lambda: [_destroy_start_setup(), self.show_secrets()])
                return_button.place(relx=0.95, rely=0.95, anchor="se")
                logger.debug("Return button created successfully")
            except Exception as e:
                logger.error(f"Error creating return button: {e}", exc_info=True)
                raise UIElementError(f"Failed to create return button: {e}")

        def _create_start_setup_header():
            self.header = self._create_an_header("Settings", "home_popup_icon.jpg")
            self.header.place(relx=0.03, rely=0.08, anchor="nw")
            logger.debug("Secrets header created")

        def _load_background_image():
            try:
                if self.controller.cc.card_present:
                    image_path = f"./pictures_db/card_{self.controller.cc.card_type.lower()}.png"
                else:
                    image_path = "./pictures_db/insert_card.png"

                self.background_photo = self._create_background_photo(self, image_path)
                self.canvas = self._create_canvas()

                # Ajuster ces valeurs pour centrer l'image
                self.canvas.place(relx=0.4, rely=0.5, anchor="center")

                # Centrer l'image dans le canvas
                self.canvas.create_image(self.canvas.winfo_reqwidth() / 2, self.canvas.winfo_reqheight() / 2,
                                         image=self.background_photo, anchor="center")
            except Exception as e:
                logger.error(f"Error loading background image: {e}", exc_info=True)
                raise UIElementError(f"Failed to load background image: {e}")

        def _create_start_setup_labels():
            try:
                label1 = self._create_label(f"Your {self.controller.cc.card_type} is connected.")
                label1.place(relx=0.29, rely=0.27, anchor="w")

                label2 = self._create_label("Select on the menu the action you wish to perform.")
                label2.place(relx=0.29, rely=0.32, anchor="w")
            except Exception as e:
                logger.error(f"Error creating start setup labels: {e}", exc_info=True)
                raise UIElementError(f"Failed to create start setup labels: {e}")

        def _destroy_start_setup():
            try:
                if hasattr(self, 'current_frame'):
                    self.current_frame.destroy()
                    delattr(self, 'current_frame')
                if hasattr(self, 'header'):
                    self.header.destroy()
                    delattr(self, 'header')
                if hasattr(self, 'canvas'):
                    self.canvas.destroy()
                    delattr(self, 'canvas')
                logger.debug("Start setup view destroyed successfully")
            except Exception as e:
                logger.error(f"Error destroying start setup view: {e}", exc_info=True)
                raise UIElementError(f"Failed to destroy start setup view: {e}")

        logger.info("Initializing start setup view")
        try:
            self.welcome_in_display = False

            # Create a new frame for start setup
            _create_start_setup_frame()

            # Load background image
            _load_background_image()

            _create_start_setup_header()

            # Create and place labels
            _create_start_setup_labels()

            # Add return button
            _create_return_button()

            logger.log(SUCCESS, "Start setup view initialized successfully")
        except Exception as e:
            logger.error(f"Error in _start_setup: {e}", exc_info=True)
            raise UIElementError(f"Failed to initialize start setup view: {e}")

    #############################################################
    # MY SECRETS
    """
    # the first frame where the users fall after 'welcome in seedkeeper tool'
    # showing all the secrets that are stored on seedkeeper card into a table including three columns
    # allowing to select a secret and display its details
    # including V1/V2 seedkeeper
    """

    @log_method
    def my_secrets(self, secrets_data: Dict[str, Any]):
        def _create_secrets_frame():
            self._create_frame()
            logger.debug("Secrets frame created")

        def _create_secrets_header():
            self.header = self._create_an_header("My Secrets", "secrets_icon_ws.png")
            self.header.place(relx=0.03, rely=0.08, anchor="nw")
            logger.debug("Secrets header created")

        def _create_secrets_table(secrets_data):

            def _on_mouse_on_secret(event, buttons):
                for button in buttons:
                    button.configure(fg_color=HIGHLIGHT_COLOR, cursor="hand2")

            def _on_mouse_out_secret(event, buttons):
                for button in buttons:
                    button.configure(fg_color=button.default_color)

            def _show_secret_details(secret):
                try:
                    self._create_frame()

                    secret_details = self.controller.retrieve_details_about_secret_selected(secret['id'])
                    logger.log(SUCCESS, f"secret detail : {secret_details}")

                    self.header = self._create_an_header("Secret Details", "secrets_icon_ws.png")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")

                    self.create_seedkeeper_menu()

                    if secret['type'] == 'Password':
                        self._create_password_secret_frame(secret_details)
                    elif secret['type'] == 'Masterseed':
                        self._create_mnemonic_secret_frame(secret_details)
                    else:
                        logger.warning(f"Unsupported secret type: {secret['type']}")
                        self._create_generic_secret_frame(secret_details)

                    back_button = self._create_button(text="Back", command=self.show_secrets)
                    back_button.place(relx=0.95, rely=0.98, anchor="se")

                    logger.log(SUCCESS, f"Secret details displayed for ID: {secret['id']}")
                except Exception as e:
                    logger.error(f"Error displaying secret details: {e}", exc_info=True)
                    self._handle_view_error(f"Failed to display secret details: {e}")

            logger.info("Creating secrets table")

            # Introduce table
            label_text = self._create_label(text="Click on a secret to manage it:")
            label_text.place(relx=0.285, rely=0.25, anchor="w")

            # Define headers
            headers = ["Id", "Type of secret", "Label"]
            rely = 0.3

            # Create header labels
            header_frame = customtkinter.CTkFrame(self.current_frame, width=750, bg_color=DEFAULT_BG_COLOR,
                                                  corner_radius=0, fg_color=DEFAULT_BG_COLOR)
            header_frame.place(relx=0.05, rely=rely, relwidth=0.9, anchor="w")

            header_widths = [50, 250, 300]  # Define specific widths for each header
            for col, width in zip(headers, header_widths):
                header_button = customtkinter.CTkButton(header_frame, text=col,
                                                        font=customtkinter.CTkFont(size=14, family='Outfit',
                                                                                   weight="bold"),
                                                        corner_radius=0, state='disabled', text_color='white',
                                                        fg_color=BG_MAIN_MENU, width=width)
                header_button.pack(side="left", expand=True, fill="both")

            logger.debug("Table headers created")

            # Create rows of labels with alternating colors
            for i, secret in enumerate(secrets_data['headers']):
                try:
                    rely += 0.06
                    row_frame = customtkinter.CTkFrame(self.current_frame, width=750, bg_color=DEFAULT_BG_COLOR,
                                                       fg_color=DEFAULT_BG_COLOR)
                    row_frame.place(relx=0.05, rely=rely, relwidth=0.9, anchor="w")

                    fg_color = DEFAULT_BG_COLOR if i % 2 == 0 else BG_HOVER_BUTTON
                    text_color = TEXT_COLOR if i % 2 == 0 else BUTTON_TEXT_COLOR

                    buttons = []
                    values = [secret['id'], secret['type'], secret['label']]
                    for value, width in zip(values, header_widths):
                        cell_button = customtkinter.CTkButton(row_frame, text=value, text_color=text_color,
                                                              fg_color=fg_color,
                                                              font=customtkinter.CTkFont(size=14, family='Outfit'),
                                                              hover_color=HIGHLIGHT_COLOR,
                                                              corner_radius=0, width=width)
                        cell_button.default_color = fg_color  # Store the default color
                        cell_button.pack(side='left', expand=True, fill="both")
                        buttons.append(cell_button)

                    # Bind hover events to change color for all buttons in the row
                    for button in buttons:
                        button.bind("<Enter>", lambda event, btns=buttons: _on_mouse_on_secret(event, btns))
                        button.bind("<Leave>", lambda event, btns=buttons: _on_mouse_out_secret(event, btns))
                        button.configure(command=lambda s=secret: _show_secret_details(s))

                    logger.debug(f"Row created for secret ID: {secret['id']}")
                except Exception as e:
                    logger.error(f"Error creating row for secret {secret['id']}: {str(e)}")
                    raise UIElementError(f"Failed to create row for secret {secret['id']}") from e

            logger.log(SUCCESS, "Secrets table created successfully")

        try:
            logger.info("Creating secrets frame")
            _create_secrets_frame()
            _create_secrets_header()
            _create_secrets_table(secrets_data)
            self.create_seedkeeper_menu()
            logger.log(SUCCESS, "Secrets frame created successfully")
        except Exception as e:
            error_msg = f"Failed to create secrets frame: {e}"
            logger.error(error_msg, exc_info=True)
            raise SecretFrameCreationError(error_msg) from e

    @log_method
    def _create_password_secret_frame(self, secret_details):
        # Create labels and entry fields
        labels = ['Label:', 'Login:', 'URL:']
        entries = {}

        for i, label_text in enumerate(labels):
            label = self._create_label(label_text)
            label.place(relx=0.1, rely=0.2 + i * 0.1, anchor="w")

            entry = customtkinter.CTkEntry(self.current_frame, width=300)
            entry.place(relx=0.3, rely=0.2 + i * 0.1, anchor="w")
            entries[label_text.lower()[:-1]] = entry

        # Set values (you'll need to fetch these from your data source)
        entries['label'].insert(0, secret_details['label'])
        entries['login'].insert(0, "Placeholder Login")  # Replace with actual data
        entries['url'].insert(0, "Placeholder URL")  # Replace with actual data

        # Create password field
        password_label = self._create_label("Password:")
        password_label.place(relx=0.1, rely=0.5, anchor="w")

        password_entry = customtkinter.CTkEntry(self.current_frame, width=300, show="*")
        password_entry.place(relx=0.3, rely=0.5, anchor="w")
        password_entry.insert(0, "********")  # Replace with actual password

        # Create action buttons
        delete_button = self._create_button(text="Delete", command=lambda: None)  # self._delete_secret(secret['id']))
        delete_button.place(relx=0.7, rely=0.9, anchor="se")

        show_button = self._create_button(text="Show", command=lambda: None)  # self._toggle_password_visibility(password_entry))
        show_button.place(relx=0.85, rely=0.9, anchor="se")

    @log_method
    def _create_mnemonic_secret_frame(self, secret_details):
        # Create labels and entry fields
        labels = ['Label:', 'Mnemonic type:']
        entries = {}

        for i, label_text in enumerate(labels):
            label = self._create_label(label_text)
            label.place(relx=0.285, rely=0.2 + i * 0.15, anchor="w")

            entry = self._create_entry()
            entry.place(relx=0.04, rely=0.27 + i * 0.15, anchor="w")
            entries[label_text.lower()[:-1]] = entry

        # Set values (you'll need to fetch these from your data source)
        entries['label'].insert(0, secret_details['label'])
        entries['mnemonic type'].insert(0, secret_details['type'])
        # entries['passphrase'].insert(0, "Placeholder Passphrase")  # Replace with actual data

        xpub_button = self._create_button(text="Xpub", command=lambda: None)  # self._show_xpub(secret['id']))
        xpub_button.place(relx=0.60, rely=0.53, anchor="se")

        seedqr_button = self._create_button(text="SeedQR", command=lambda: None)  # self._show_seedqr(secret['id']))
        seedqr_button.place(relx=0.78, rely=0.53, anchor="se")

        # Create passphrase field
        passphrase_label = self._create_label("Passphrase:")
        passphrase_label.place(relx=0.285, rely=0.58, anchor="w")

        passphrase_entry = self._create_entry()
        passphrase_entry.place(relx=0.2, rely=0.58, anchor="w", relwidth=0.585)
        passphrase_entry.insert(0, "Comment récupérer la passhprase ?")  # Replace with actual data

        # Create mnemonic field
        mnemonic_label = self._create_label("Mnemonic:")
        mnemonic_label.place(relx=0.285, rely=0.65, anchor="w")

        mnemonic_entry = self._create_entry(show_option='*')
        mnemonic_entry.place(relx=0.04, rely=0.8, relheight=0.23, anchor="w")
        mnemonic_entry.insert(0, secret_details['secret'])  # Replace with actual mnemonic

        # Create action buttons
        delete_button = self._create_button(text="Delete", command=lambda: None)  # self._delete_secret(secret['id']))
        delete_button.place(relx=0.95, rely=0.3, anchor="se")

        show_button = self._create_button(text="Show", command=lambda: _toggle_mnemonic_visibility(mnemonic_entry))
        show_button.place(relx=0.95, rely=0.8, anchor="e")

        @log_method
        def _toggle_mnemonic_visibility(entry):
            current_state = entry.cget("show")
            entry.configure(show="" if current_state == "*" else "*")


    @log_method
    def _create_generic_secret_frame(self, secret_details):
        try:
            for key, value in secret_details.items():
                label = self._create_label(f"{key}:")
                label.place(relx=0.1, rely=0.2 + len(secret_details) * 0.05, anchor="w")

                entry = self._create_entry(show="*" if key.lower() == "value" else None)
                entry.insert(0, value)
                entry.configure(state="readonly")
                entry.place(relx=0.3, rely=0.2 + len(secret_details) * 0.05, anchor="w")

            logger.log(SUCCESS, "Generic secret frame created")
        except Exception as e:
            logger.error(f"Error creating generic secret frame: {e}", exc_info=True)
            raise UIElementError(f"Failed to create generic secret frame: {e}")



if __name__ == "__main__":
    setup_logging()
    try:
        app = View(loglevel=logging.DEBUG)  # ou le niveau que vous préférez
        app.welcome()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}", exc_info=True)
        sys.exit(1)
