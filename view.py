import logging
import sys
from typing import Optional, Dict, List, Callable
from functools import wraps
import webbrowser

import customtkinter
from PIL import Image, ImageTk

from controller import Controller

from log_config import get_logger, SUCCESS, setup_logging
from exceptions import ViewError, FrameError, UIElementError, InitializationError, ButtonCreationError, MainMenuError

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
            super().__init__()
            self._initialize_attributes()
            self._setup_main_window()
            self._declare_widgets()
            self._set_close_protocol()
            self.controller = Controller(None, self, loglevel=loglevel)
            logger.log(SUCCESS, "View initialization completed successfully")
        except Exception as e:
            logger.critical("Failed to initialize View", exc_info=True)
            raise InitializationError(f"Failed to initialize View: {e}") from e

    """UTILS"""

    # FOR INITIALIZATION
    @log_method
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
        self.is_seedkeeper_v1: Optional[bool] = None

    # FOR MAIN WINDOW
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

        self.main_frame = customtkinter.CTkFrame(self, width=750, height=600, bg_color=DEFAULT_BG_COLOR,
                                                 fg_color=DEFAULT_BG_COLOR)
        self.main_frame.place(relx=0.25, rely=0.5, anchor="e")

    @log_method
    def _declare_widgets(self):
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

    @log_method
    def _set_close_protocol(self):
        self.protocol("WM_DELETE_WINDOW", self.on_close_app)
        logger.debug("WM_DELETE_WINDOW protocol set successfully")

    @log_method
    def on_close_app(self):
        logger.info("Closing App")
        self.app_open = False
        self.destroy()
        # Assuming self.controller.cc.card_disconnect() exists
        # self.controller.cc.card_disconnect()

    # FOR UI MANAGEMENT
    @log_method
    def _clear_current_frame(self):
        if self.current_frame:
            logger.debug("Clearing current frame")
            try:
                self.current_frame.destroy()
            except Exception as e:
                raise FrameError(f"Failed to clear current frame: {e}")

    def clear_welcome_frame(self):
        if self.welcome_frame:
            logger.debug("Clearing current frame")
            try:
                self.welcome_frame.destroy()
            except Exception as e:
                raise FrameError(f"Failed to clear current frame: {e}")

    # FOR CARD INFORMATION
    @log_method
    def update_status(self, is_connected=None):
        logger.info("Entering update_status method")
        try:
            if is_connected is not None:
                if is_connected:
                    try:
                        logger.info("Getting card status")
                        (self.card_present, self.card_version, self.needs2FA, self.is_seeded,
                         self.setup_done, self.card_type, self.pin_left) = self.controller.get_card_status()
                        logger.log(SUCCESS, "Card status retrieved successfully")

                        self.controller.card_event = True
                        logger.debug("Controller card event set to True")

                        self._log_card_status()

                        if not self.welcome_in_display:
                            self.my_secrets_list()

                    except Exception as e:
                        logger.error(f"An error occurred while getting card status: {e}", exc_info=True)
                        raise self.controller.cc.CardError("Failed to get card status") from e

                else:
                    try:
                        logger.info("Card disconnected, resetting status")
                        self.card_present = self.card_version = self.needs2FA = self.is_seeded = None
                        self.setup_done = self.card_type = self.card_label = self.pin_left = None

                        self.controller.card_event = False
                        logger.debug("Controller card event set to False")

                        self._log_card_status()

                        if self.app_open:
                            self.my_secrets_list()

                    except Exception as e:
                        logger.error(f"An error occurred while resetting card status: {e}", exc_info=True)
                        raise self.controller.cc.CardError("Failed to reset card status") from e

            else:
                try:
                    logger.info("Getting current card status")
                    (self.card_present, self.card_version, self.needs2FA, self.is_seeded,
                     self.setup_done, self.card_type, self.pin_left) = self.controller.get_card_status()
                    logger.log(SUCCESS, "Current card status retrieved successfully")

                    self.controller.card_event = True
                    logger.debug("Controller card event set to True")

                    self._log_card_status()

                except Exception as e:
                    logger.error(f"An error occurred while getting current card status: {e}", exc_info=True)
                    raise self.controller.cc.CardError("Failed to get current card status") from e

        except Exception as e:
            logger.error(f"An unexpected error occurred in update_status method: {e}", exc_info=True)
            raise ViewError("An unexpected error occurred in update_status") from e

    def _log_card_status(self):
        logger.info(f"Card presence: {self.card_present}")
        logger.info(f"Applet major version: {self.card_version}")
        logger.info(f"Needs 2FA: {self.needs2FA}")
        logger.info(f"Is seeded: {self.is_seeded}")
        logger.info(f"Setup done: {self.setup_done}")
        logger.info(f"Card type: {self.card_type}")
        logger.info(f"Card label: {self.card_label}")
        logger.info(f"Tries remaining: {self.pin_left}")

    """FOR MAIN MENU"""

    @log_method
    def main_menu(self, state=None, frame=None):
        try:
            if state is None:
                state = "normal" if self.card_present else "disabled"
                logger.info(f"Card {'detected' if state == 'normal' else 'undetected'}, setting state to {state}")

            menu_frame = customtkinter.CTkFrame(self.current_frame, width=250, height=600,
                                                bg_color=BG_MAIN_MENU,
                                                fg_color=BG_MAIN_MENU, corner_radius=0, border_color="black",
                                                border_width=0)

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

            # Menu items
            self.create_button_for_main_menu_item(
                menu_frame,
                "My secrets" if self.controller.card_present else "Insert card",
                "secrets_icon.png" if self.controller.card_present else "insert_card_icon.jpg",
                0.26, 0.585 if self.controller.card_present else 0.578,
                command=self.show_secrets if self.controller.card_present else None,
                state=state,
            )
            self.create_button_for_main_menu_item(
                menu_frame,
                "Generate",
                "generate_icon.png" if self.controller.card_present else "generate_locked_icon.png",
                0.33, 0.56,
                command=self.generate_secret if self.controller.card_present else None,
                state=state,
                text_color="white" if self.controller.card_present else "grey",
            )
            self.create_button_for_main_menu_item(
                menu_frame,
                "Import",
                "import_icon.png" if self.controller.card_present else "import_locked_icon.png",
                0.40, 0.51,
                command=self.import_secret if self.controller.card_present else None,
                state=state,
                text_color="white" if self.controller.card_present else "grey"
            )
            self.create_button_for_main_menu_item(
                menu_frame,
                "Settings",
                "settings_icon.png" if self.controller.card_present else "settings_locked_icon.png",
                0.74, 0.546,
                command=self.show_settings if self.controller.card_present else None,
                state=state,
                text_color="white" if self.controller.card_present else "grey"
            )
            self.create_button_for_main_menu_item(
                menu_frame,
                "Help",
                "help_icon.png",
                0.81, 0.49,
                command=self.show_help,
                state='normal',
                text_color="white"
            )
            self.create_button_for_main_menu_item(
                menu_frame, "Go to the webshop", "webshop_icon.png", 0.95, 0.82,
                command=lambda: webbrowser.open("https://satochip.io/shop/", new=2), state='normal'
            )

            return menu_frame

        except Exception as e:
            error_message = f"An error occurred in main_menu: {e}"
            logger.error(error_message, exc_info=True)
            raise MainMenuError(error_message) from e

    @log_method
    def create_button_for_main_menu_item(
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

    # Revised show methods with basic implementation
    @log_method
    def show_secrets(self):
        # TODO: Implement full functionality to show secrets
        self._show_message("Showing secrets")

    @log_method
    def generate_secret(self):
        # TODO: Implement full functionality to generate a secret
        self._show_message("Generating secret")

    @log_method
    def import_secret(self):
        # TODO: Implement full functionality to import a secret
        self._show_message("Importing secret")

    @log_method
    def show_settings(self):
        # TODO: Implement full functionality to show settings
        self._show_message("Showing settings")

    @log_method
    def show_help(self):
        # TODO: Implement full functionality to show help
        self._show_message("Showing help")

    @log_method
    def _show_message(self, message):
        # This method could update a status bar or show a popup in the UI
        print(message)  # Placeholder: replace with actual UI update
        logger.info(message)

    # FOR BUILD FRAME
    @log_method
    def create_welcome_button(self, text: str, command: Optional[Callable] = None, frame: Optional[customtkinter.CTkFrame] = None) -> customtkinter.CTkButton:
        logger.debug("Creating button")
        try:
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
            logger.debug(f"Button '{text}' created successfully")
            return button
        except Exception as e:
            error_msg = f"Failed to create button '{text}': {e}"
            logger.error(error_msg, exc_info=True)
            raise UIElementError(error_msg) from e

    """FOR ERRORS MANAGEMENT"""
    # todo: replace handle view error for show_error
    @log_method
    def _handle_view_error(self, message: str):
        """Handle view-related errors by showing an error message to the user."""
        try:
            error_label = customtkinter.CTkLabel(
                self,
                text=message,
                fg_color="red",
                text_color="white",
                corner_radius=8
            )
            error_label.place(relx=0.5, rely=0.9, anchor="center")
            self.after(5000, error_label.destroy)  # Remove error message after 5 seconds
        except Exception as e:
            logger.error(f"Failed to display error message: {e}")
            # If we can't even show the error message, log it and potentially quit the application
            # self.quit()  # Uncomment this if you want to quit the app on critical errors

    """WELCOME IN SEEDKEEPER TOOL"""
    @log_method
    def welcome(self):
        logger.info("Entering View.welcome() method")
        try:
            self._clear_current_frame()
            self._setup_welcome_frame()
            self._create_welcome_background()
            self._create_welcome_header()
            self._create_welcome_labels()
            self._create_welcome_button()

            logger.log(SUCCESS, "Welcome view created successfully")
            self.update()  # Force update of the window
        except FrameError as e:
            logger.error(f"Frame error in welcome method: {e}")
            self._handle_view_error("An error occurred while setting up the welcome frame.")
            # todo: replace handle view error for show_error
        except UIElementError as e:
            logger.error(f"UI element error in welcome method: {e}")
            self._handle_view_error("An error occurred while creating UI elements.")
            # todo: replace handle view error for show_error

        except Exception as e:
            logger.error(f"Unexpected error in welcome method: {e}", exc_info=True)
            self._handle_view_error("An unexpected error occurred. Please try again.")
            # todo: replace handle view error for show_error

    @log_method
    def _setup_welcome_frame(self):
        logger.debug("Creating new welcome frame")
        try:
            self.welcome_frame = customtkinter.CTkFrame(self, fg_color=BG_MAIN_MENU)
            self.welcome_frame.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            raise FrameError(f"Failed to create welcome frame: {e}")

    @log_method
    def _create_welcome_background(self):
        logger.debug("Creating welcome background")
        try:
            bg_image = Image.open("./pictures_db/welcome_in_seedkeeper_tool.png")
            self.background_photo = ImageTk.PhotoImage(bg_image)
            self.canvas = customtkinter.CTkCanvas(self.welcome_frame, width=bg_image.width, height=bg_image.height)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
        except FileNotFoundError:
            raise UIElementError("Background image file not found.")
        except Exception as e:
            raise UIElementError(f"Failed to create welcome background: {e}")

    @log_method
    def _create_welcome_header(self):
        logger.debug("Creating welcome header")
        try:
            # Create frame for header
            header_frame = customtkinter.CTkFrame(self.welcome_frame, width=380, height=178, fg_color=DEFAULT_BG_COLOR)
            header_frame.place(relx=0.1, rely=0.03, anchor='nw')

            # Create canvas for logo
            logo_canvas = customtkinter.CTkCanvas(header_frame, width=400, height=400, bg='black')
            logo_canvas.place(relx=0.5, rely=0.5, anchor='center')

            # Load and display logo
            icon_path = "./pictures_db/icon_welcome_logo.png"
            try:
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
            except FileNotFoundError:
                logger.error(f"Logo file not found: {icon_path}")
                # Continue execution even if logo is not found
            logger.debug("Welcome header created successfully")
        except Exception as e:
            error_msg = f"Failed to create welcome header: {e}"
            logger.error(error_msg, exc_info=True)
            raise UIElementError(error_msg) from e

    @log_method
    def _create_welcome_labels(self):
        logger.debug("Creating welcome labels")
        try:
            labels = [
                ("Seedkeeper-tool", 0.4),
                ("The companion app for your Seedkeeper card.", 0.5),
                ("It will help you to safely store and manage your crypto-related", 0.55),
                ("secrets including seedphrases, passwords and credentials.", 0.60),
                ('First time using the app? Plug your Seedkeeper card into the', 0.7),
                ('card reader and follow the guide...', 0.75)
            ]

            for text, rely in labels:
                if text == "Seedkeeper-tool":
                    label = customtkinter.CTkLabel(
                        self.welcome_frame,
                        text=text,
                        font=customtkinter.CTkFont(size=18, weight='bold'),
                        text_color="white"
                    )
                else:
                    label = customtkinter.CTkLabel(
                        self.welcome_frame,
                        text=text,
                        font=customtkinter.CTkFont(size=18),
                        text_color="white"
                    )
                label.place(relx=0.05, rely=rely, anchor="w")
        except Exception as e:
            raise UIElementError(f"Failed to create welcome labels: {e}")

    @log_method
    def _create_welcome_button(self):
        logger.debug("Creating welcome button")
        try:
            self.lets_go_button = self.create_welcome_button("Let's go", self.my_secrets_list)
            self.lets_go_button.place(relx=0.85, rely=0.93, anchor="center")
        except Exception as e:
            raise UIElementError(f"Failed to create welcome button: {e}")

    """FRAMES"""
    """MY SECRETS"""
    # the first frame where the users fall after 'welcome in seedkeeper tool'
    # showing all the secrets that are stored on seedkeeper card into a table including three columns
    # allowing to select a secret and display its details
    # including V1/V2 seedkeeper
    @log_method
    def my_secrets_list(self):
        logger.info("Starting setup process")
        self.welcome_in_display = False
        # Implement the start_setup logic here
        self.clear_welcome_frame()
        self.menu = self.main_menu()
        self.menu.place(relx=0.250, rely=0.5, anchor="e")



if __name__ == "__main__":
    setup_logging()
    try:
        app = View(loglevel=logging.DEBUG)  # ou le niveau que vous préférez
        app.welcome()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}", exc_info=True)
        sys.exit(1)