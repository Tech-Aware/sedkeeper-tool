import sys
from typing import Optional, Callable
from functools import wraps

import customtkinter
from PIL import Image, ImageTk

from log_config import get_logger, SUCCESS, setup_logging
from exceptions import ViewError, FrameError, UIElementError, InitializationError

logger = get_logger(__name__)

# Constants
BG_MAIN_MENU = "#21283b"
BG_BUTTON = "#e1e1e0"
BG_HOVER_BUTTON = "grey"
TEXT_COLOR = "black"
BUTTON_TEXT_COLOR = "white"
ICON_PATH = "./pictures_db/icon_"

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

    """UTILS FOR INITIALIZATION"""

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
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        logger.debug("WM_DELETE_WINDOW protocol set successfully")

    """UTILS FOR MAIN WINDOW"""
    @log_method
    def on_close(self):
        logger.info("Closing App")
        self.app_open = False
        self.destroy()
        # Assuming self.controller.cc.card_disconnect() exists
        # self.controller.cc.card_disconnect()

    """UTILS"""
    @log_method
    def _clear_current_frame(self):
        if self.current_frame:
            logger.debug("Clearing current frame")
            try:
                self.current_frame.destroy()
            except Exception as e:
                raise FrameError(f"Failed to clear current frame: {e}")

    @log_method
    def create_button(self, text: str, command: Optional[Callable] = None, frame: Optional[customtkinter.CTkFrame] = None) -> customtkinter.CTkButton:
        logger.debug("Creating button")
        try:
            target_frame = frame or self.current_frame
            button = customtkinter.CTkButton(
                target_frame,
                text=text,
                command=command,
                corner_radius=100,
                font=customtkinter.CTkFont(family="Outfit", size=18, weight="normal"),
                bg_color='white',
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
            self.current_frame = customtkinter.CTkFrame(self, fg_color=BG_MAIN_MENU)
            self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            raise FrameError(f"Failed to create welcome frame: {e}")

    @log_method
    def _create_welcome_background(self):
        logger.debug("Creating welcome background")
        try:
            bg_image = Image.open("./pictures_db/welcome_in_seedkeeper_tool.png")
            self.background_photo = ImageTk.PhotoImage(bg_image)
            self.canvas = customtkinter.CTkCanvas(self.current_frame, width=bg_image.width, height=bg_image.height)
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
            header_frame = customtkinter.CTkFrame(self.current_frame, width=380, height=178, fg_color='white')
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
                ("Seedkeeper-tool\n______________", 0.4),
                ("The companion app for your Seedkeeper card.", 0.5),
                ("It will help you to safely store and manage your crypto-related", 0.55),
                ("secrets including seedphrases, passwords and credentials.", 0.65),
            ]

            for text, rely in labels:
                label = customtkinter.CTkLabel(
                    self.current_frame,
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
            self.lets_go_button = self.create_button("Let's go", self.start_setup)
            self.lets_go_button.place(relx=0.85, rely=0.93, anchor="center")
        except Exception as e:
            raise UIElementError(f"Failed to create welcome button: {e}")

    @log_method
    def start_setup(self):
        logger.info("Starting setup process")
        self.welcome_in_display = False
        # Implement the start_setup logic here
        pass

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


if __name__ == "__main__":
    setup_logging()
    try:
        app = View()
        app.welcome()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}", exc_info=True)
        sys.exit(1)