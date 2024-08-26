import logging
import sys
import os
from tkinter import StringVar
from typing import Optional, Dict, Callable, Any, Tuple
import gc
import webbrowser

import customtkinter
import tkinter
from PIL import Image, ImageTk
from customtkinter import CTkOptionMenu

from controller import Controller

from log_config import log_method
from exceptions import *

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


class View(customtkinter.CTk):
    @log_method
    def __init__(self, loglevel=logging.INFO):
        try:
            logger.info("001 Starting View initialization")
            super().__init__()

            try:
                self._initialize_attributes()
                logger.debug("002 Attributes initialized successfully")
            except AttributeError as e:
                logger.error(f"003 Failed to initialize attributes: {e}")
                raise InitializationError("004 Attribute initialization failed") from e

            try:
                self._set_package_directory()
                logger.debug("004 Package directory set successfully")
            except InitializationError as e:
                logger.error(f"005 Failed to set package directory: {e}")
                raise InitializationError("007 Package directory setup failed") from e

            try:
                self._setup_main_window()
                logger.debug("006 Main window set up successfully")
            except tkinter.TclError as e:
                logger.error(f"007 Failed to set up main window: {e}")
                raise InitializationError("008 Main window setup failed") from e

            try:
                self._declare_widgets()
                logger.debug("009 Widgets declared successfully")
            except tkinter.TclError as e:
                logger.error(f"010 Failed to declare widgets: {e}")
                raise InitializationError("011 Widget declaration failed") from e

            try:
                self._set_close_protocol()
                logger.debug("012 Close protocol set successfully")
            except AttributeError as e:
                logger.error(f"013 Failed to set close protocol: {e}")
                raise InitializationError("014 Close protocol setup failed") from e

            try:
                self.controller = Controller(None, self, loglevel=loglevel)
                logger.debug("015 Controller initialized successfully")
            except Exception as e:
                logger.error(f"016 Failed to initialize controller: {e}")
                raise InitializationError("017 Controller initialization failed") from e

            logger.log(SUCCESS, "018 View initialization completed successfully")
        except InitializationError as e:
            logger.critical(f"019 View initialization failed: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.critical(f"020 Unexpected error during View initialization: {e}", exc_info=True)
            raise InitializationError(f"021 Unexpected error during View initialization: {e}") from e

    ####################################################################################################################
    """ UTILS """

    ########################################
    # FOR INITIALIZATION
    ########################################

    @log_method
    def _initialize_attributes(self):
        try:
            logger.info("001 Starting attribute initialization")

            # Card-related attributes
            self.card_type: Optional[str] = None
            self.card_version: Optional[str] = None
            self.card_present: Optional[bool] = None
            self.card_label: Optional[str] = None
            logger.debug("002 Card-related attributes initialized")

            # Card status attributes
            self.setup_done: Optional[bool] = None
            self.is_seeded: Optional[bool] = None
            self.needs2FA: Optional[bool] = None
            self.is_seedkeeper_v1: Optional[bool] = None
            logger.debug("003 Card status attributes initialized")

            # Application state attributes
            self.menu = None
            self.app_open: bool = True
            self.welcome_in_display: bool = True
            self.spot_if_unlock: bool = False
            self.pin_left: Optional[int] = None
            self.mnemonic_textbox_active: bool = False
            self.mnemonic_textbox: Optional[customtkinter.CTkTextbox] = None
            self.password_text_box_active: bool = False
            self.password_text_box: Optional[customtkinter.CTkTextbox] = None
            logger.debug("004 Application state attributes initialized")

            logger.log(SUCCESS, "005 All attributes initialized successfully to their default values")
        except AttributeError as e:
            logger.error(f"006 AttributeError in _initialize_attributes: {e}", exc_info=True)
            raise AttributeInitializationError(f"007 Failed to initialize attributes: {e}") from e
        except Exception as e:
            logger.error(f"008 Unexpected error in _initialize_attributes: {e}", exc_info=True)
            raise InitializationError(f"009 Unexpected error during attribute initialization: {e}") from e

    @log_method
    def _set_package_directory(self):
        try:
            logger.info("001 Setting package directory")
            if getattr(sys, 'frozen', False):
                # Running in a bundle
                logger.debug("002 Running in a bundled application")
                if sys.platform == "darwin":  # MacOS
                    self.pkg_dir = os.path.join(sys._MEIPASS, "seedkeeper")
                    logger.debug("003 Running on MacOS, setting pkg_dir with 'seedkeeper' subdirectory")
                else:
                    self.pkg_dir = sys._MEIPASS
                    logger.debug("004 Running on non-MacOS platform, setting pkg_dir to sys._MEIPASS")
            else:
                # Running live
                self.pkg_dir = os.path.split(os.path.realpath(__file__))[0]
                logger.debug("005 Running live, setting pkg_dir to script directory")

            logger.debug(f"006 PKGDIR set to: {self.pkg_dir}")
            logger.log(SUCCESS, "007 Package directory set successfully")
        except Exception as e:
            logger.error(f"008 Error setting package directory: {e}", exc_info=True)
            raise InitializationError(f"009 Failed to set package directory: {e}") from e

    @log_method
    def _setup_main_window(self):
        try:
            logger.info("001 Starting main window setup")

            try:
                self.title("SEEDKEEPER TOOL")
                logger.debug("002 Window title set successfully")
            except tkinter.TclError as e:
                logger.error(f"003 Failed to set window title: {e}")
                raise WindowSetupError("004 Failed to set window title") from e

            try:
                window_width = 1000
                window_height = 600
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                center_x = int((screen_width - window_width) / 2)
                center_y = int((screen_height - window_height) / 2)
                self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
                logger.debug(
                    f"005 Window geometry set successfully to {window_width}x{window_height}, centered on screen")
            except tkinter.TclError as e:
                logger.error(f"006 Failed to set window geometry: {e}")
                raise WindowSetupError("007 Failed to set window geometry") from e

            try:
                self.main_frame = customtkinter.CTkFrame(self, width=1000, height=600, bg_color='black',
                                                         fg_color='black')
                self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.debug("008 Main frame created and placed successfully")
            except tkinter.TclError as e:
                logger.error(f"009 Failed to create or place main frame: {e}")
                raise FrameCreationError("010 Failed to create or place main frame") from e

            logger.log(SUCCESS, "011 Main window setup completed successfully")
        except (WindowSetupError, FrameCreationError) as e:
            logger.error(f"012 Error in _setup_main_window: {e}", exc_info=True)
            raise UIElementError(f"013 Failed to set up main window: {e}") from e
        except Exception as e:
            logger.error(f"014 Unexpected error in _setup_main_window: {e}", exc_info=True)
            raise UIElementError(f"015 Unexpected error during main window setup: {e}") from e

    @log_method
    def _declare_widgets(self):
        try:
            logger.info("001 Starting widget declaration")
            self.current_frame: Optional[customtkinter.CTkFrame] = None
            logger.debug("002 Current frame initialized")

            self.canvas: Optional[customtkinter.CTkCanvas] = None
            self.background_photo: Optional[ImageTk.PhotoImage] = None
            self.create_background_photo: Optional[callable] = None
            logger.debug("003 Canvas and background photo attributes initialized")

            self.header: Optional[customtkinter.CTkLabel] = None
            self.text_box: Optional[customtkinter.CTkTextbox] = None
            logger.debug("004 Header and text box attributes initialized")

            self.button: Optional[customtkinter.CTkButton] = None
            self.finish_button: Optional[customtkinter.CTkButton] = None
            logger.debug("005 Button attributes initialized")

            self.menu: Optional[customtkinter.CTkFrame] = None
            self.counter: Optional[int] = None
            self.display_menu: bool = False
            logger.debug("006 Menu attributes initialized")

            logger.log(SUCCESS, "007 All widgets declared successfully")
        except AttributeError as e:
            logger.error(f"008 AttributeError in _declare_widgets: {e}", exc_info=True)
            raise UIElementError(f"009 Failed to declare widgets: {e}") from e
        except Exception as e:
            logger.error(f"010 Unexpected error in _declare_widgets: {e}", exc_info=True)
            raise UIElementError(f"011 Unexpected error during widget declaration: {e}") from e

    @log_method
    def _set_close_protocol(self):
        try:
            logger.info("001 Starting close protocol setup")
            self.protocol("WM_DELETE_WINDOW", self._on_close_app)
            logger.log(SUCCESS, "002 Close protocol set successfully")
        except tkinter.TclError as e:
            logger.error(f"003 TclError in _set_close_protocol: {e}", exc_info=True)
            raise UIElementError(f"004 Failed to set close protocol: {e}") from e
        except Exception as e:
            logger.error(f"005 Unexpected error in _set_close_protocol: {e}", exc_info=True)
            raise UIElementError(f"006 Unexpected error during close protocol setup: {e}") from e

    # for main windows
    @log_method
    def _on_close_app(self):
        try:
            logger.info("001 Starting application closure")
            self.app_open = False
            logger.debug("002 App open flag set to False")
            self.controller.cc.card_disconnect()
            logger.log(SUCCESS, "003 Card disconnected successfully")
            self.destroy()
            logger.log(SUCCESS, "004 Application closed successfully")
        except tkinter.TclError as e:
            logger.error(f"005 TclError while closing application: {e}", exc_info=True)
            # Even if there's an error, we should try to force close the application
            self.quit()
            logger.warning("006 Forced application quit due to error during normal closure")
        except Exception as e:
            logger.error(f"007 Unexpected error while closing application: {e}", exc_info=True)
            # Even if there's an unexpected error, we should try to force close the application
            self.quit()
            logger.warning("008 Forced application quit due to unexpected error during closure")

    @log_method
    def _restart_app(self):
        try:
            logger.info("001 Starting application restart")
            self.destroy()
            logger.debug("002 Current application instance destroyed")
            logger.log(SUCCESS, "003 Application restart initiated successfully")
            os.execl(sys.executable, sys.executable, *sys.argv)
        except OSError as e:
            logger.error(f"004 OSError during application restart: {e}", exc_info=True)
            raise ApplicationRestartError(f"005 Failed to restart application: {e}") from e
        except Exception as e:
            logger.error(f"006 Unexpected error during application restart: {e}", exc_info=True)
            raise ApplicationRestartError(f"007 Unexpected error during application restart: {e}") from e

    ########################################
    # FOR UI MANAGEMENT
    ########################################

    @log_method
    def _create_label(
            self,
            text,
            bg_fg_color: str = None,
            frame=None
    ) -> customtkinter.CTkLabel:
        try:
            logger.info(f"001 Starting label creation with text: '{text}'")
            label = None

            if bg_fg_color is not None:
                try:
                    logger.debug(f"002 Creating label with background color: {bg_fg_color}")
                    label = customtkinter.CTkLabel(self.current_frame, text=text, bg_color=bg_fg_color,
                                                   fg_color=bg_fg_color,
                                                   font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                              weight="normal"))
                    logger.debug("003 Label created with specified background color")
                except Exception as e:
                    logger.warning(f"004 ThemeError while creating label with background color: {e}")
                    # Continue to try creating a default label

            if label is None:
                try:
                    logger.debug("005 Creating label with default whitesmoke background")
                    label = customtkinter.CTkLabel(self.current_frame, text=text, bg_color="whitesmoke",
                                                   fg_color="whitesmoke",
                                                   font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                              weight="normal"))
                    logger.debug("006 Label created with default background")
                except Exception as e:
                    logger.warning(f"007 ThemeError while creating label with default background: {e}")
                    # Continue to try creating a label with transparent background

            if label is None:
                logger.debug("008 Creating label with transparent background")
                label = customtkinter.CTkLabel(self.current_frame, text=text, bg_color="transparent",
                                               fg_color="transparent",
                                               font=customtkinter.CTkFont(family="Outfit", size=16,
                                                                          weight="normal"))
                logger.debug("009 Label created with transparent background")

            logger.log(SUCCESS, f"010 Label created successfully with text: '{text}'")
            return label
        except Exception as e:
            logger.error(f"011 Unexpected error in _create_label: {e}", exc_info=True)
            raise LabelCreationError(f"012 Failed to create label: {e}") from e

    @log_method
    def _make_text_bold(
            self,
            size=None
    ) -> customtkinter.CTkFont:
        try:
            logger.debug("Entering make_text_bold method")
            logger.debug("Configuring bold font")

            try:
                if size is not None:
                    logger.debug(f"Setting bold font with size: {size}")
                    result = customtkinter.CTkFont(weight="bold", size=size)
                else:
                    logger.debug("Setting bold font with default size")
                    result = customtkinter.CTkFont(weight="bold", size=18)
            except Exception as e:
                logger.error(f"An error occurred while setting the bold font: {e}", exc_info=True)
                raise

            logger.debug("make_text_bold method completed successfully")
            return result
        except Exception as e:
            logger.error(f"An unexpected error occurred in make_text_bold: {e}", exc_info=True)

    @log_method
    def _create_entry(
            self,
            show_option: Optional[str] = None
    ) -> customtkinter.CTkEntry:
        try:
            logger.info("001 Starting entry creation")
            entry = None

            try:
                if show_option is not None:
                    logger.debug(f"002 Creating entry with secure write option: {show_option}")
                    entry = customtkinter.CTkEntry(self.current_frame, width=555, height=37, corner_radius=10,
                                                   bg_color='white', fg_color=BG_BUTTON, border_color=BG_BUTTON,
                                                   show=f"{show_option}", text_color='grey')
                    logger.debug("003 Entry created with secure write option")
                else:
                    logger.debug("004 Creating entry without secure write option")
                    entry = customtkinter.CTkEntry(self.current_frame, width=555, height=37, corner_radius=10,
                                                   bg_color='white', fg_color=BG_BUTTON, border_color=BG_BUTTON,
                                                   text_color='grey')
                    logger.debug("005 Entry created without secure write option")

                logger.log(SUCCESS, "006 Entry created successfully")
                return entry
            except Exception as e:
                logger.error(f"007 ThemeError while creating entry: {e}", exc_info=True)
                raise EntryCreationError(f"008 Failed to create entry due to theme error: {e}") from e

        except Exception as e:
            logger.error(f"009 Unexpected error in _create_entry: {e}", exc_info=True)
            raise EntryCreationError(f"010 Unexpected error during entry creation: {e}") from e

    @log_method
    def create_option_list(
            self,
            options,
            default_value: Optional[str] = None,
            width: int = 300
    ) -> Tuple[StringVar, CTkOptionMenu]:
        try:
            logger.info(f"001 Creating option list with options: {options}")
            variable = customtkinter.StringVar(value=default_value if default_value else options[0])

            option_menu = customtkinter.CTkOptionMenu(
                self.current_frame,
                variable=variable,
                values=options,
                width=width,
                fg_color=BG_BUTTON,  # Utilisez la même couleur que pour les entrées
                button_color=BG_BUTTON,  # Couleur du bouton déroulant
                button_hover_color=BG_HOVER_BUTTON,  # Couleur au survol du bouton
                dropdown_fg_color=BG_MAIN_MENU,  # Couleur de fond du menu déroulant
                dropdown_hover_color=BG_HOVER_BUTTON,  # Couleur au survol des options
                dropdown_text_color="white",  # Couleur du texte des options
                text_color="grey",  # Couleur du texte sélectionné
                font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal"),
                dropdown_font=customtkinter.CTkFont(family="Outfit", size=13, weight="normal"),
                corner_radius=10,  # Même rayon de coin que les entrées
            )

            logger.log(SUCCESS, f"002 Option list created successfully with {len(options)} options")
            return variable, option_menu
        except Exception as e:
            logger.error(f"003 Error creating option list: {e}", exc_info=True)
            raise UIElementError(f"004 Failed to create option list: {e}") from e

    @log_method
    def _create_welcome_button(
            self,
            text: str,
            command: Optional[Callable] = None,
            frame: Optional[customtkinter.CTkFrame] = None
    ) -> customtkinter.CTkButton:
        try:
            logger.info(f"001 Creating welcome button: {text}")
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
            logger.log(SUCCESS, f"002 Welcome button '{text}' created successfully")
            return button
        except Exception as e:
            error_msg = f"003 Failed to create welcome button '{text}': {e}"
            logger.error(error_msg, exc_info=True)
            raise UIElementError(error_msg) from e

    @log_method
    def _create_button(
            self,
            text: Optional[str] = None,
            command: Optional[Callable] = None,
            frame: Optional[customtkinter.CTkFrame] = None
    ) -> customtkinter.CTkButton:
        try:
            logger.info(f"001 Starting button creation with text: '{text}'")
            button = None

            try:
                if command is None:
                    logger.debug("002 Creating button without command")
                    button = customtkinter.CTkButton(self.current_frame, text=text, corner_radius=100,
                                                     font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                                weight="normal"),
                                                     bg_color='white', fg_color=BG_MAIN_MENU,
                                                     hover_color=BG_HOVER_BUTTON, cursor="hand2", width=120, height=35)
                    logger.debug("003 Button created without command")
                else:
                    logger.debug("004 Creating button with command")
                    button = customtkinter.CTkButton(self.current_frame, text=text, corner_radius=100,
                                                     font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                                weight="normal"),
                                                     bg_color='white', fg_color=BG_MAIN_MENU,
                                                     hover_color=BG_HOVER_BUTTON, cursor="hand2", width=120, height=35,
                                                     command=command)
                    logger.debug("005 Button created with command")

                logger.log(SUCCESS, f"006 Button created successfully with text: '{text}'")
                return button
            except Exception as e:
                logger.error(f"007 Error while creating button: {e}", exc_info=True)
                raise ButtonCreationError(f"008 Failed to create button: {e}") from e

        except Exception as e:
            logger.error(f"009 Unexpected error in _create_button: {e}", exc_info=True)
            raise ButtonCreationError(f"010 Unexpected error during button creation: {e}") from e

    @log_method
    def _create_an_header(
            self,
            title_text: Optional[str] = None,
            icon_name: Optional[str] = None,
    ) -> customtkinter.CTkFrame:
        try:
            logger.info(f"001 Starting header creation with title: '{title_text}' and icon: '{icon_name}'")

            header_frame = customtkinter.CTkFrame(self.current_frame, fg_color="whitesmoke", bg_color="whitesmoke",
                                                  width=750,
                                                  height=40)
            logger.debug("002 Header frame created")

            if title_text and icon_name:
                icon_path = f"{ICON_PATH}{icon_name}"
                try:
                    image = Image.open(icon_path)
                    photo_image = customtkinter.CTkImage(image, size=(40, 40))
                    logger.debug("003 Icon loaded and resized")

                    button = customtkinter.CTkButton(header_frame, text=f"   {title_text}", image=photo_image,
                                                     font=customtkinter.CTkFont(family="Outfit", size=25,
                                                                                weight="bold"),
                                                     bg_color="whitesmoke", fg_color="whitesmoke", text_color="black",
                                                     hover_color="whitesmoke", compound="left")
                    button.image = photo_image
                    button.place(rely=0.5, relx=0, anchor="w")
                    logger.debug("004 Header button created and placed")
                except FileNotFoundError:
                    logger.error(f"005 Icon file not found: {icon_path}")
                    raise HeaderCreationError(f"006 Failed to load icon: {icon_path}")
                except Exception as e:
                    logger.error(f"007 Error while creating header button: {e}")
                    raise HeaderCreationError(f"008 Failed to create header button: {e}")

            logger.log(SUCCESS, "009 Header created successfully")
            return header_frame
        except Exception as e:
            logger.error(f"010 Unexpected error in _create_an_header: {e}", exc_info=True)
            raise HeaderCreationError(f"011 Failed to create header: {e}") from e

    @log_method
    def _create_frame(self):
        try:
            logger.info("001 Starting frame creation")
            self._clear_current_frame()
            logger.debug("002 Current frame cleared")

            self.current_frame = customtkinter.CTkFrame(self.main_frame, width=750, height=600,
                                                        fg_color=DEFAULT_BG_COLOR,
                                                        bg_color=DEFAULT_BG_COLOR)
            self.current_frame.place(relx=0.250, rely=0.5, anchor='w')
            logger.log(SUCCESS, "003 New frame created and placed successfully")
        except Exception as e:
            logger.error(f"004 Error in _create_frame: {e}", exc_info=True)
            raise FrameCreationError(f"005 Failed to create frame: {e}") from e

    @log_method
    def _create_scrollable_frame(
            self,
            parent_frame,
            width,
            height,
            x,
            y
    ) -> customtkinter.CTkFrame:
        try:
            logger.info("001 Starting scrollable frame creation")

            # Create a frame to hold the canvas and scrollbar
            container = customtkinter.CTkFrame(parent_frame, width=width, height=height, fg_color=DEFAULT_BG_COLOR)
            container.place(x=x, y=y)
            container.pack_propagate(False)  # Prevent the frame from shrinking to fit its contents

            # Create a canvas with specific dimensions
            canvas = customtkinter.CTkCanvas(container, bg=DEFAULT_BG_COLOR, highlightthickness=0)
            canvas.pack(side="left", fill="both", expand=True)

            # Add a scrollbar to the canvas
            scrollbar = customtkinter.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill="y")

            # Configure scrollbar colors
            scrollbar.configure(fg_color=DEFAULT_BG_COLOR, button_color=DEFAULT_BG_COLOR,
                                button_hover_color=BG_HOVER_BUTTON)

            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)

            # Create a frame inside the canvas
            inner_frame = customtkinter.CTkFrame(canvas, fg_color=DEFAULT_BG_COLOR)

            # Add that frame to a window in the canvas
            canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            def _configure_inner_frame(event):
                # Update the scrollregion to encompass the inner frame
                canvas.configure(scrollregion=canvas.bbox("all"))

                # Resize the inner frame to fit the canvas width
                canvas.itemconfig(canvas_window, width=canvas.winfo_width())

            inner_frame.bind("<Configure>", _configure_inner_frame)

            def _configure_canvas(event):
                # Resize the inner frame to fit the canvas width
                canvas.itemconfig(canvas_window, width=event.width)

            canvas.bind("<Configure>", _configure_canvas)

            def _on_mousewheel(event):
                # Check if there's actually something to scroll
                if canvas.bbox("all")[3] <= canvas.winfo_height():
                    return  # No scrolling needed, so do nothing

                if event.delta > 0:
                    canvas.yview_scroll(-1, "units")
                elif event.delta < 0:
                    canvas.yview_scroll(1, "units")

            # Bind mouse wheel to the canvas
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            logger.log(SUCCESS, "002 Scrollable frame created successfully")
            return inner_frame
        except Exception as e:
            logger.error(f"003 Error in _create_scrollable_frame: {e}", exc_info=True)
            raise FrameCreationError(f"004 Failed to create scrollable frame: {e}") from e

    @log_method
    def _clear_current_frame(self):
        try:
            def _unbind_mousewheel():
                self.unbind_all("<MouseWheel>")
                self.unbind_all("<Button-4>")
                self.unbind_all("<Button-5>")

            _unbind_mousewheel()
            if self.app_open is True and self.current_frame is not None:
                logger.info("001 Starting current frame clearing process")
                if hasattr(self, 'current_frame') and self.current_frame:
                    for widget in self.current_frame.winfo_children():
                        widget.destroy()
                        logger.debug("002 Widget destroyed")
                    self.current_frame.destroy()
                    logger.debug("003 Current frame destroyed")
                    self.current_frame = None
                    if self.mnemonic_textbox_active is True and self.mnemonic_textbox is not None:
                        self.mnemonic_textbox.destroy()
                        self.mnemonic_textbox_active = False
                        self.mnemonic_textbox = None
                    elif self.password_text_box_active is True and self.password_text_box is not None:
                        self.password_text_box.destroy()
                        self.password_text_box_active = False
                        self.password_text_box = None
                    logger.debug("004 Current frame reference set to None")
                else:
                    pass

            # Nettoyage des attributs spécifiques
            attributes_to_clear = ['header', 'canvas', 'background_photo', 'text_box', 'button', 'finish_button',
                                   'menu']
            for attr in attributes_to_clear:
                if hasattr(self, attr):
                    attr_value = getattr(self, attr)
                    if attr_value:
                        if isinstance(attr_value, (customtkinter.CTkBaseClass, tkinter.BaseWidget)):
                            attr_value.destroy()
                            logger.debug(f"005 Attribute {attr} destroyed")
                        elif isinstance(attr_value, ImageTk.PhotoImage):
                            del attr_value
                            logger.debug(f"006 ImageTk.PhotoImage {attr} deleted")
                    setattr(self, attr, None)
                    logger.debug(f"007 Attribute {attr} set to None")

            # Réinitialisation des variables d'état si nécessaire
            self.display_menu = False
            self.counter = None
            logger.debug("008 State variables reset")

            # Forcer le garbage collector
            gc.collect()
            logger.debug("009 Garbage collection forced")

            logger.log(SUCCESS, "010 Current frame and associated objects cleared successfully")
        except Exception as e:
            logger.error(f"011 Unexpected error in _clear_current_frame: {e}", exc_info=True)
            raise FrameClearingError(f"012 Failed to clear current frame: {e}") from e

    @log_method
    def _clear_welcome_frame(self):
        try:
            logger.info("001 Starting welcome frame clearing process")
            if hasattr(self, 'welcome_frame'):
                try:
                    self.welcome_frame.destroy()
                    logger.debug("002 Welcome frame destroyed")
                    delattr(self, 'welcome_frame')
                    logger.debug("003 Welcome frame attribute removed")
                    logger.log(SUCCESS, "004 Welcome frame cleared successfully")
                except Exception as e:
                    logger.error(f"005 Error while clearing welcome frame: {e}", exc_info=True)
                    raise FrameClearingError(f"006 Failed to clear welcome frame: {e}") from e
            else:
                logger.debug("007 No welcome frame to clear")
        except Exception as e:
            logger.error(f"008 Unexpected error in _clear_welcome_frame: {e}", exc_info=True)
            raise FrameClearingError(f"009 Unexpected error during welcome frame clearing: {e}") from e

    @staticmethod
    @log_method
    def _create_background_photo(
            self,
            picture_path
    ) -> ImageTk.PhotoImage:
        try:
            logger.info(f"001 Starting background photo creation with path: {picture_path}")

            try:
                if getattr(sys, 'frozen', False):
                    application_path = sys._MEIPASS
                    logger.debug(f"002 Running in a bundled application, application path: {application_path}")
                else:
                    application_path = os.path.dirname(os.path.abspath(__file__))
                    logger.debug(f"003 Running in a regular script, application path: {application_path}")
            except Exception as e:
                logger.error(f"004 Error determining application path: {e}", exc_info=True)
                raise BackgroundPhotoError("005 Failed to determine application path") from e

            try:
                pictures_path = os.path.join(application_path, picture_path)
                logger.debug(f"006 Full path to background photo: {pictures_path}")
            except Exception as e:
                logger.error(f"007 Error constructing full path: {e}", exc_info=True)
                raise BackgroundPhotoError("008 Failed to construct full path to background photo") from e

            try:
                background_image = Image.open(pictures_path)
                logger.debug("009 Background image opened successfully")
            except FileNotFoundError as e:
                logger.error(f"010 File not found: {pictures_path}", exc_info=True)
                raise BackgroundPhotoError(f"011 Background image file not found: {pictures_path}") from e
            except Exception as e:
                logger.error(f"012 Error opening background image: {e}", exc_info=True)
                raise BackgroundPhotoError("013 Failed to open background image") from e

            try:
                photo_image = ImageTk.PhotoImage(background_image)
                logger.debug("014 Background photo converted to PhotoImage successfully")
            except Exception as e:
                logger.error(f"015 Error converting background image to PhotoImage: {e}", exc_info=True)
                raise BackgroundPhotoError("016 Failed to convert background image to PhotoImage") from e

            logger.log(SUCCESS, "017 Background photo created successfully")
            return photo_image
        except Exception as e:
            logger.error(f"018 Unexpected error in _create_background_photo: {e}", exc_info=True)
            raise BackgroundPhotoError(f"019 Unexpected error during background photo creation: {e}") from e

    @log_method
    def _create_canvas(
            self,
            frame=None
    ) -> customtkinter.CTkCanvas:
        try:
            logger.info("001 Starting canvas creation")
            canvas = customtkinter.CTkCanvas(self.current_frame, bg="whitesmoke", width=750, height=600)
            logger.debug("002 Canvas created successfully")
            logger.log(SUCCESS, "003 Canvas creation completed")
            return canvas
        except Exception as e:
            logger.error(f"004 Unexpected error in _create_canvas: {e}", exc_info=True)
            raise CanvasCreationError(f"005 Failed to create canvas: {e}") from e

    @log_method
    def _update_textbox(self, text):
        try:
            logger.info("001 Starting _update_textbox method")

            @log_method
            def _clear_textbox():
                try:
                    logger.info("002 Clearing the current content of the textbox")
                    self.text_box.delete(1.0, "end")
                    logger.log(SUCCESS, "003 Textbox content cleared successfully")
                except Exception as e:
                    logger.error(f"004 Error clearing textbox content: {e}", exc_info=True)
                    raise UIElementError(f"005 Failed to clear textbox content: {e}") from e

            @log_method
            def _insert_new_text():
                try:
                    logger.info("006 Inserting new text into the textbox")
                    self.text_box.insert("end", text)
                    logger.log(SUCCESS, "007 New text inserted into textbox successfully")
                except Exception as e:
                    logger.error(f"008 Error inserting new text into textbox: {e}", exc_info=True)
                    raise UIElementError(f"009 Failed to insert new text into textbox: {e}") from e

            _clear_textbox()
            _insert_new_text()

            logger.log(SUCCESS, "010 _update_textbox method completed successfully")
        except Exception as e:
            logger.error(f"011 Unexpected error in _update_textbox: {e}", exc_info=True)
            raise ViewError(f"012 Failed to update textbox: {e}") from e

    ########################################
    # FOR CARD INFORMATION
    ########################################

    @log_method
    def update_status(
            self,
            isConnected=None
    ):
        try:
            logger.info("001 Starting status update")
            if self.controller.cc.mode_factory_reset == True:
                # we are in factory reset mode
                if isConnected is True:
                    logger.info("002 Card inserted for Reset Factory!")
                    try:
                        self.show_button.configure(text='Reset', state='normal')
                        logger.debug("003 Labels and button updated for card insertion")
                    except Exception as e:
                        logger.error(f"004 Error updating labels and button for card insertion: {e}", exc_info=True)
                        raise UIElementError(f"005 Failed to update UI elements for card insertion: {e}") from e

                elif isConnected is False:
                    logger.info("006 Card removed for Reset Factory!")
                    try:
                        self.show_button.configure(text='Insert card', state='disabled')
                        logger.debug("007 Labels and button updated for card removal")
                    except Exception as e:
                        logger.error(f"008 Error updating labels and button for card removal: {e}", exc_info=True)
                        raise UIElementError(f"009 Failed to update UI elements for card removal: {e}") from e
                else:  # None
                    logger.debug("010 No connection status change")
            else:
                # normal mode
                logger.info("011 Updating status in normal mode")
                if isConnected is True:
                    try:
                        logger.info("012 Getting card status")
                        self.controller.get_card_status()
                        logger.debug("013 Card status updated and button configured")
                    except Exception as e:
                        logger.error(f"014 Error getting card status: {e}", exc_info=True)
                        raise CardError(f"015 Failed to get card status: {e}") from e

                elif isConnected is False:
                    try:
                        logger.info("016 Card disconnected, resetting status")
                        self.view_welcome()
                        logger.debug("017 Status reset for card disconnection")
                    except Exception as e:
                        logger.error(f"018 Error resetting card status: {e}", exc_info=True)
                        raise UIElementError(f"019 Failed to reset UI for card disconnection: {e}") from e

                else:  # isConnected is None
                    logger.debug("020 No connection status change")

            logger.log(SUCCESS, "021 Status update completed successfully")
        except Exception as e:
            logger.error(f"022 Unexpected error in update_status: {e}", exc_info=True)
            raise ViewError(f"023 Failed to update status: {e}") from e

    @log_method
    def get_passphrase(
            self,
            msg
    ) -> Optional[str]:
        try:
            logger.info("001 Initiating passphrase entry")
            popup = customtkinter.CTkToplevel(self)
            popup.title("PIN Required") if self.controller.cc.setup_done else popup.title("PIN setup")
            popup.configure(fg_color='whitesmoke')
            popup.protocol("WM_DELETE_WINDOW", lambda: [self.show(
                "WARNING",
                "You can't open app without password",
                "Ok", None, "./pictures_db/change_pin_popup_icon.jpg")])

            popup_width, popup_height = 400, 200
            position_right = int(self.winfo_screenwidth() / 2 - popup_width / 2)
            position_down = int(self.winfo_screenheight() / 2 - popup_height / 2)
            popup.geometry(f"{popup_width}x{popup_height}+{position_right}+{position_down}")
            logger.debug("002 Passphrase popup created and positioned")

            icon_image = Image.open("./pictures_db/change_pin_popup_icon.jpg")
            icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
            icon_label = customtkinter.CTkLabel(
                popup, image=icon, text="\nEnter the PIN code of your card." if self.controller.cc.setup_done else "Create a PIN code",
                compound='top',
                font=customtkinter.CTkFont(
                    family="Outfit",
                    size=18,
                    weight="normal"
                )
            )
            icon_label.pack(pady=(10, 5))
            logger.debug("003 Icon and label added to popup")

            passphrase_entry = customtkinter.CTkEntry(popup, show="*", corner_radius=10, border_width=0,
                                                      width=229, height=37, bg_color='whitesmoke',
                                                      fg_color=BG_BUTTON, text_color='grey')
            popup.after(100, passphrase_entry.focus_force)
            passphrase_entry.pack(pady=(5, 5))
            logger.debug("004 Passphrase entry field added to popup")

            pin = None

            def submit_passphrase():
                nonlocal pin
                pin = passphrase_entry.get()
                popup.destroy()
                logger.debug("005 Passphrase submitted")
                self.update_status()

            submit_button = customtkinter.CTkButton(popup, bg_color='whitesmoke', fg_color=BG_MAIN_MENU,
                                                    width=120, height=35, corner_radius=34,
                                                    hover_color=BG_HOVER_BUTTON, text="Submit",
                                                    command=submit_passphrase,
                                                    font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                               weight="normal"))
            submit_button.pack(pady=10)
            logger.debug("006 Submit button added to popup")

            popup.transient(self)
            popup.bind('<Return>', lambda event: submit_passphrase())
            self.wait_window(popup)

            logger.log(SUCCESS, "007 Passphrase entry completed")
            return pin

        except Exception as e:
            logger.error(f"008 Error in get_passphrase: {e}", exc_info=True)
            raise UIElementError(f"009 Failed to get passphrase: {e}") from e

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
            logger.info(f"001 Starting main menu button creation for '{button_label}'")

            icon_path = f"{ICON_PATH}{icon_name}"
            try:
                image = Image.open(icon_path)
                image = image.resize((25, 25), Image.LANCZOS)
                photo_image = customtkinter.CTkImage(image)
                logger.debug(f"002 Icon loaded and resized: {icon_path}")
            except FileNotFoundError:
                logger.error(f"003 Icon file not found: {icon_path}")
                raise ButtonCreationError(f"004 Failed to load icon: {icon_path}")
            except IOError as e:
                logger.error(f"005 Error processing icon: {e}")
                raise ButtonCreationError(f"006 Failed to process icon: {e}") from e

            try:
                button = customtkinter.CTkButton(
                    frame,
                    text=button_label,
                    text_color=text_color if text_color != "white" else "white",
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
                logger.debug(f"007 Button created and placed: {button_label}")
            except Exception as e:
                logger.error(f"008 Error while creating button: {e}")
                raise ButtonCreationError(f"009 Failed to create button: {e}") from e

            logger.log(SUCCESS, f"010 Main menu button '{button_label}' created successfully")
            return button

        except Exception as e:
            logger.error(f"011 Unexpected error creating button: {e}")
            raise ButtonCreationError(f"012 Failed to create button: {e}") from e

    ########################################
    # FOR SEEDKEEPER
    ########################################

    @log_method
    def create_seedkeeper_menu(self):
        try:
            logger.info("001 Starting Seedkeeper menu creation")
            self.menu = self._seedkeeper_lateral_menu()
            logger.debug("002 Seedkeeper lateral menu created")
            self.menu.place(relx=0.250, rely=0.5, anchor="e")
            logger.debug("003 Seedkeeper menu placed")
            logger.log(SUCCESS, "004 Seedkeeper menu created and placed successfully")
        except Exception as e:
            logger.error(f"005 Error in create_seedkeeper_menu: {e}", exc_info=True)
            raise MenuCreationError(f"006 Failed to create Seedkeeper menu: {e}") from e

    @log_method
    def _seedkeeper_lateral_menu(
            self,
            state=None,
            frame=None
    ) -> customtkinter.CTkFrame:
        try:
            logger.info("001 Starting Seedkeeper lateral menu creation")
            if self.menu:
                self.menu.destroy()
                logger.debug("002 Existing menu destroyed")

            if state is None:
                state = "normal" if self.controller.cc.card_present else "disabled"
                logger.info(f"003 Card {'detected' if state == 'normal' else 'undetected'}, setting state to {state}")

            menu_frame = customtkinter.CTkFrame(self.main_frame, width=250, height=600,
                                                bg_color=BG_MAIN_MENU,
                                                fg_color=BG_MAIN_MENU, corner_radius=0, border_color="black",
                                                border_width=0)
            logger.debug("004 Main menu frame created")

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
            logger.debug("005 Logo section created")

            if self.controller.cc.card_present:
                logger.log(SUCCESS, "006 Card Present")
            else:
                logger.error(f"007 Card not present")

            # Menu items
            self._create_button_for_main_menu_item(menu_frame,
                                                   "My secrets" if self.controller.cc.card_present else "Insert card",
                                                   "secrets_icon.png" if self.controller.cc.card_present else "insert_card_icon.jpg",
                                                   0.26, 0.585 if self.controller.cc.card_present else 0.578,
                                                   state=state,
                                                   command=self.show_view_my_secrets if self.controller.cc.card_present else None)
            self._create_button_for_main_menu_item(menu_frame, "Generate",
                                                   "generate_icon.png" if self.controller.cc.card_present else "generate_locked_icon.png",
                                                   0.33, 0.56, state=state,
                                                   command=self.show_view_generate_secret if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self._create_button_for_main_menu_item(menu_frame, "Import",
                                                   "import_icon.png" if self.controller.cc.card_present else "import_locked_icon.png",
                                                   0.40, 0.51, state=state,
                                                   command=self.show_view_import_secret if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self._create_button_for_main_menu_item(menu_frame, "Logs",
                                                   "logs_icon.png" if self.controller.cc.card_present else "settings_locked_icon.png",
                                                   0.47, 0.49, state=state,
                                                   command=self.show_view_logs if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self._create_button_for_main_menu_item(menu_frame, "Settings",
                                                   "settings_icon.png" if self.controller.cc.card_present else "settings_locked_icon.png",
                                                   0.74, 0.546, state=state,
                                                   command=self.show_view_about if self.controller.cc.card_present else None,
                                                   text_color="white" if self.controller.cc.card_present else "grey")
            self._create_button_for_main_menu_item(menu_frame, "Help", "help_icon.png", 0.81, 0.49, state='normal',
                                                   command=self.show_view_help, text_color="white")
            self._create_button_for_main_menu_item(menu_frame, "Go to the webshop", "webshop_icon.png", 0.95, 0.82,
                                                   state='normal',
                                                   command=lambda: webbrowser.open("https://satochip.io/shop/", new=2))
            logger.debug("008 Menu items created")
            logger.log(SUCCESS, "009 Seedkeeper lateral menu created successfully")
            return menu_frame
        except Exception as e:
            logger.error(f"010 Unexpected error in _seedkeeper_lateral_menu: {e}", exc_info=True)
            raise MenuCreationError(f"011 Failed to create Seedkeeper lateral menu: {e}") from e

    @log_method
    def _delete_seedkeeper_menu(self):
        try:
            logger.info("001 Starting Seedkeeper menu deletion")
            if hasattr(self, 'menu') and self.menu:
                self.menu.destroy()
                logger.debug("002 Menu widget destroyed")
                self.menu = None
                logger.debug("003 Menu attribute set to None")
            logger.log(SUCCESS, "004 Seedkeeper menu deleted successfully")
        except Exception as e:
            logger.error(f"005 Unexpected error in _delete_seedkeeper_menu: {e}", exc_info=True)
            raise MenuDeletionError(f"006 Failed to delete Seedkeeper menu: {e}") from e

    ########################################
    # FOR SATOCHIP-UTILS
    ########################################

    @log_method
    def create_satochip_utils_menu(self):
        try:
            logger.info("001 Starting Satochip-utils menu creation")
            self._delete_seedkeeper_menu()  # Ensure old menu is removed
            logger.debug("002 Old Seedkeeper menu deleted")
            self.menu = self._satochip_utils_lateral_menu()
            logger.debug("003 Satochip-utils lateral menu created")
            self.menu.place(relx=0, rely=0, relwidth=0.25, relheight=1)
            logger.debug("004 Satochip-utils menu placed")
            logger.log(SUCCESS, "005 Satochip-utils menu created and placed successfully")
        except Exception as e:
            logger.error(f"006 Error in create_satochip_utils_menu: {e}", exc_info=True)
            raise MenuCreationError(f"007 Failed to create Satochip-utils menu: {e}") from e

    @log_method
    def _satochip_utils_lateral_menu(
            self,
            state=None,
            frame=None
    ) -> customtkinter.CTkFrame:
        try:
            logger.info("001 Starting Satochip-utils lateral menu creation")
            if state is None:
                state = "normal" if self.controller.cc.card_present else "disabled"
                logger.info(f"002 Card {'detected' if state == 'normal' else 'undetected'}, setting state to {state}")

            menu_frame = customtkinter.CTkFrame(self.main_frame, width=250, height=600,
                                                bg_color=BG_MAIN_MENU,
                                                fg_color=BG_MAIN_MENU, corner_radius=0, border_color="black",
                                                border_width=0)
            logger.debug("003 Menu frame created successfully")

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
            logger.debug("004 Logo section setup complete")

            if self.controller.cc.card_present:
                if not self.controller.cc.setup_done:
                    logger.info("005 Setup not done, enabling 'Setup My Card' button")
                    self._create_button_for_main_menu_item(menu_frame, "Setup My Card", "setup_my_card_icon.png", 0.26,
                                                           0.60,
                                                           state='normal', command=lambda: None)
                else:
                    if not self.controller.cc.is_seeded and self.controller.cc.card_type != "Satodime":
                        logger.info("006 Card not seeded, enabling 'Setup Seed' button")
                        self._create_button_for_main_menu_item(menu_frame, "Setup Seed", "seed.png", 0.26, 0.575,
                                                               state='normal',
                                                               command=lambda: None)
                    else:
                        logger.info("007 Setup completed, disabling 'Setup Done' button")
                        self._create_button_for_main_menu_item(menu_frame,
                                                               "Setup Done" if self.controller.cc.card_present else 'Insert Card',
                                                               "setup_done_icon.jpg" if self.controller.cc.card_present else "insert_card_icon.jpg",
                                                               0.26,
                                                               0.575 if self.controller.cc.card_present else 0.595,
                                                               state='disabled', command=lambda: None)
            else:
                logger.info("008 Card not present, setting 'Setup My Card' button state")
                self._create_button_for_main_menu_item(menu_frame, "Insert a Card", "insert_card_icon.jpg", 0.26, 0.585,
                                                       state='normal', command=lambda: None)

            if self.controller.cc.card_type != "Satodime" and self.controller.cc.setup_done:
                logger.debug("009 Enabling 'Change Pin' button")
                self._create_button_for_main_menu_item(menu_frame, "Change Pin", "change_pin_icon.png", 0.33, 0.567,
                                                       state='normal', command=self.show_view_change_pin)
            else:
                logger.info(f"010 Card type is {self.controller.cc.card_type} | Disabling 'Change Pin' button")
                self._create_button_for_main_menu_item(menu_frame, "Change Pin", "change_pin_locked_icon.jpg", 0.33,
                                                       0.57,
                                                       state='disabled', command=lambda: None)

            if self.controller.cc.setup_done:
                self._create_button_for_main_menu_item(menu_frame, "Edit Label", "edit_label_icon.png", 0.40, 0.537,
                                                       state='normal', command=self.show_view_edit_label)
            else:
                self._create_button_for_main_menu_item(menu_frame, "Edit Label", "edit_label_locked_icon.jpg", 0.40,
                                                       0.546,
                                                       state='disabled', command=lambda: None)

            def before_check_authenticity():
                logger.info("011 Requesting card verification PIN")
                if self.controller.cc.card_type != "Satodime":
                    if self.controller.cc.is_pin_set():
                        self.controller.cc.card_verify_PIN_simple()
                    else:
                        self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')

            if self.controller.cc.setup_done:
                self._create_button_for_main_menu_item(menu_frame, "Check Authenticity", "check_authenticity_icon.png",
                                                       0.47, 0.775,
                                                       state='normal', command=lambda: [before_check_authenticity(),
                                                                                        self.show_view_check_authenticity()])
            else:
                self._create_button_for_main_menu_item(menu_frame, "Check Authenticity",
                                                       "check_authenticity_locked_icon.jpg", 0.47, 0.66,
                                                       state='disabled',
                                                       command=lambda: None)
            if self.controller.cc.card_present:
                self._create_button_for_main_menu_item(menu_frame, "About", "about_icon.jpg", rel_y=0.73, rel_x=0.476,
                                                       state='normal', command=self.show_view_about)
            else:
                self._create_button_for_main_menu_item(menu_frame, "About", "about_locked_icon.jpg", rel_y=0.73,
                                                       rel_x=0.5052, state='disabled', command=lambda: None)

            self._create_button_for_main_menu_item(menu_frame, "Go to the Webshop", "webshop_icon.png", 0.95, 0.805,
                                                   state='normal',
                                                   command=lambda: webbrowser.open("https://satochip.io/shop/", new=2))

            logger.log(SUCCESS, "012 Satochip-utils lateral menu setup completed successfully")
            return menu_frame
        except Exception as e:
            logger.error(f"013 Unexpected error in _satochip_utils_lateral_menu: {e}", exc_info=True)
            raise MenuCreationError(f"014 Failed to create Satochip-utils lateral menu: {e}") from e

    @log_method
    def _delete_satochip_utils_menu(self):
        try:
            logger.info("001 Starting Satochip-utils menu deletion")
            if hasattr(self, 'menu') and self.menu:
                self.menu.destroy()
                logger.debug("002 Satochip-utils menu destroyed")
                self.menu = None
                logger.debug("003 Menu attribute set to None")
            logger.log(SUCCESS, "004 Satochip-utils menu deleted successfully")
        except Exception as e:
            logger.error(f"005 Unexpected error in _delete_satochip_utils_menu: {e}", exc_info=True)
            raise MenuDeletionError(f"006 Failed to delete Satochip-utils menu: {e}") from e

    ####################################################################################################################
    """ METHODS TO DISPLAY A VIEW FROM MENU SELECTION """

    ####################################################################################################################

    # SEEDKEEPER MENU SELECTION
    @log_method
    def show_view_my_secrets(self):
        try:
            logger.info("001 Initiating show secrets process")
            self.welcome_in_display = False
            self._clear_welcome_frame()
            self._clear_current_frame()
            logger.debug("002 Welcome frame cleared")
            secrets_data = self.controller.retrieve_secrets_stored_into_the_card()
            logger.debug("003 Secrets data retrieved from card")
            self.view_my_secrets(secrets_data)
            logger.log(SUCCESS, "004 Secrets displayed successfully")
        except Exception as e:
            logger.error(f"005 Error in show_secrets: {e}", exc_info=True)
            raise ViewError(f"006 Failed to show secrets: {e}") from e

    @log_method
    def show_view_generate_secret(self):
        try:
            logger.info("001 Initiating secret generation process")
            self.welcome_in_display = False
            logger.debug("002 Welcome frame cleared")
            self._clear_current_frame()
            self.view_generate_secret()
            logger.log(SUCCESS, "003 Secret generation process initiated")
        except Exception as e:
            logger.error(f"004 Error in show_generate_secret: {e}", exc_info=True)
            raise ViewError(f"005 Failed to show generate secret: {e}")

    @log_method
    def show_view_import_secret(self):
        try:
            logger.info("001 Initiating secret import process")
            self.welcome_in_display = False
            self._clear_current_frame()
            logger.debug("002 Welcome frame cleared")
            self.view_import_secret()
            logger.log(SUCCESS, "002 Secret import process initiated")
        except Exception as e:
            logger.error(f"003 Error in import_secret: {e}", exc_info=True)
            raise ViewError(f"004 Failed to import secret: {e}") from e

    def show_view_logs(self):
        total_number_of_logs, total_number_available_logs, logs = self.controller.get_logs()
        self.view_logs_details(logs)

    @log_method
    def show_view_settings(self):
        try:
            logger.info("001 Displaying settings")
            self._delete_seedkeeper_menu()
            logger.debug("002 Seedkeeper menu deleted")
            self.view_start_setup()
            logger.debug("003 Setup started")
            self.create_satochip_utils_menu()
            logger.debug("004 Satochip utils menu created")
            logger.log(SUCCESS, "005 Settings displayed successfully")
        except Exception as e:
            logger.error(f"006 Error in show_settings: {e}", exc_info=True)
            raise ViewError(f"007 Failed to show settings: {e}") from e

    # SETTINGS MENU SELECTION
    @log_method
    def show_view_start_setup(self):
        try:
            logger.info("001 Starting show_view_start_setup method")

            self.welcome_in_display = False
            self._clear_welcome_frame()
            self._clear_current_frame()
            logger.debug("002 Welcome and current frames cleared")

            self.view_start_setup()
            logger.log(SUCCESS, "003 Start setup view displayed successfully")
        except Exception as e:
            logger.error(f"004 Error in show_view_start_setup: {e}", exc_info=True)
            raise ViewError(f"005 Failed to show start setup view: {e}") from e

    @log_method
    def show_view_change_pin(self):
        try:
            logger.info("001 Starting show_view_change_pin method")

            self.welcome_in_display = False
            self._clear_welcome_frame()
            self._clear_current_frame()
            logger.debug("002 Welcome and current frames cleared")

            self.view_change_pin()
            logger.log(SUCCESS, "003 Change PIN view displayed successfully")
        except Exception as e:
            logger.error(f"004 Error in show_view_change_pin: {e}", exc_info=True)
            raise ViewError(f"005 Failed to show change PIN view: {e}") from e

    @log_method
    def show_view_edit_label(self):
        try:
            logger.info("001 Starting show_view_edit_label method")

            self.welcome_in_display = False
            self._clear_welcome_frame()
            self._clear_current_frame()
            logger.debug("002 Welcome and current frames cleared")

            self.view_edit_label()
            logger.log(SUCCESS, "003 Edit label view displayed successfully")
        except Exception as e:
            logger.error(f"004 Error in show_view_edit_label: {e}", exc_info=True)
            raise ViewError(f"005 Failed to show edit label view: {e}") from e

    @log_method
    def show_view_check_authenticity(self):
        try:
            logger.info("001 Starting show_view_check_authenticity method")

            self.welcome_in_display = False
            self._clear_welcome_frame()
            self._clear_current_frame()
            logger.debug("002 Welcome and current frames cleared")

            self.view_check_authenticity()
            logger.log(SUCCESS, "003 Check authenticity view displayed successfully")
        except Exception as e:
            logger.error(f"004 Error in show_view_check_authenticity: {e}", exc_info=True)
            raise ViewError(f"005 Failed to show check authenticity view: {e}") from e

    @log_method
    def show_view_about(self):
        try:
            logger.info("001 Initiating about view process")
            self.welcome_in_display = False
            self._clear_welcome_frame()
            self._clear_current_frame()
            logger.debug("002 Welcome and current frames cleared")
            self.view_about()
            logger.log(SUCCESS, "003 About view displayed successfully")
        except Exception as e:
            logger.error(f"004 Error in show_view_about: {e}", exc_info=True)
            raise ViewError(f"005 Failed to show about view: {e}") from e

    @log_method
    def show_view_help(self):
        try:
            logger.info("001 Displaying help information")
            self.welcome_in_display = False
            self._clear_current_frame()
            self._clear_welcome_frame()
            logger.debug("002 Welcome and current frames cleared")
            self.view_help()
            logger.log(SUCCESS, "003 Help information displayed successfully")
        except Exception as e:
            logger.error(f"003 Error in show_help: {e}", exc_info=True)
            raise ViewError(f"004 Failed to show help: {e}") from e

    ########################################
    # POPUP
    ########################################

    @log_method
    def show(
            self,
            title: str,
            msg: str,
            button_txt: str = "Ok",
            cmd: Optional[Callable] = None,
            icon_path: Optional[str] = None
    ):
        try:
            logger.info(f"001 Showing popup: {title}")

            @log_method
            def create_popup(title):
                try:
                    popup = customtkinter.CTkToplevel(self)
                    popup.title(title)
                    popup.configure(fg_color='whitesmoke')
                    popup.protocol("WM_DELETE_WINDOW", popup.destroy)
                    logger.debug("002 Popup window created")
                    return popup
                except Exception as e:
                    logger.error(f"003 Error in create_popup: {e}", exc_info=True)
                    raise UIElementError(f"004 Failed to create popup: {e}") from e

            @log_method
            def center_popup(popup):
                try:
                    popup_width, popup_height = 400, 220
                    position_right = int(self.winfo_screenwidth() / 2 - popup_width / 2)
                    position_down = int(self.winfo_screenheight() / 2 - popup_height / 2)
                    popup.geometry(f"{popup_width}x{popup_height}+{position_right}+{position_down}")
                    logger.debug("005 Popup window centered")
                except Exception as e:
                    logger.error(f"006 Error in center_popup: {e}", exc_info=True)
                    raise UIElementError(f"007 Failed to center popup: {e}") from e

            @log_method
            def add_content(popup, msg, icon_path):
                try:
                    if icon_path:
                        try:
                            icon_image = Image.open(icon_path)
                            icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
                            label = customtkinter.CTkLabel(popup, image=icon, text=f"\n{msg}", compound='top',
                                                           font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                                      weight="normal"))
                        except FileNotFoundError:
                            logger.warning(f"008 Icon file not found: {icon_path}")
                            label = customtkinter.CTkLabel(popup, text=msg,
                                                           font=customtkinter.CTkFont(family="Outfit", size=14,
                                                                                      weight="bold"))
                    else:
                        label = customtkinter.CTkLabel(popup, text=msg,
                                                       font=customtkinter.CTkFont(family="Outfit", size=14,
                                                                                  weight="bold"))
                    label.pack(pady=20)
                    logger.debug("009 Content added to popup")
                except Exception as e:
                    logger.error(f"010 Error in add_content: {e}", exc_info=True)
                    raise UIElementError(f"011 Failed to add content to popup: {e}") from e

            @log_method
            def add_button(popup, button_txt, cmd):
                try:
                    close_cmd = lambda: [cmd() if cmd else None, popup.destroy()]
                    button = customtkinter.CTkButton(popup, text=button_txt, fg_color=BG_MAIN_MENU,
                                                     hover_color=BG_HOVER_BUTTON, bg_color='whitesmoke',
                                                     width=120, height=35, corner_radius=34,
                                                     font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                                weight="normal"),
                                                     command=close_cmd)
                    button.pack(pady=20)
                    logger.debug("012 Button added to popup")
                except Exception as e:
                    logger.error(f"013 Error in add_button: {e}", exc_info=True)
                    raise UIElementError(f"014 Failed to add button to popup: {e}") from e

            @log_method
            def make_popup_priority(popup):
                popup.transient(self)
                popup.grab_set()
                popup.attributes("-topmost", True)
                logger.debug("015 Priority added to popup")

            popup = create_popup(title)
            center_popup(popup)
            add_content(popup, msg, icon_path)
            add_button(popup, button_txt, cmd)
            make_popup_priority(popup)

            logger.log(SUCCESS, f"016 Popup '{title}' displayed successfully")
        except Exception as e:
            logger.error(f"017 Error in show: {e}", exc_info=True)
            raise UIElementError(f"018 Failed to show popup: {e}") from e

    ####################################################################################################################
    """ VIEWS """

    ####################################################################################################################
    @log_method
    def view_welcome(self):
        self.welcome_in_display = True

        @log_method
        def _setup_welcome_frame():
            try:
                logger.info("001 Setting up welcome frame")
                self.welcome_frame = customtkinter.CTkFrame(self, fg_color=BG_MAIN_MENU)
                self.welcome_frame.place(relx=0.5, rely=0.5, anchor="center")
                logger.log(SUCCESS, "002 Welcome frame set up successfully")
            except Exception as e:
                error_msg = f"003 Failed to create welcome frame: {e}"
                logger.error(error_msg, exc_info=True)
                raise FrameError(error_msg) from e

        @log_method
        def _create_welcome_background():
            try:
                logger.info("004 Creating welcome background")
                bg_image = Image.open("./pictures_db/welcome_in_seedkeeper_tool.png")
                self.background_photo = ImageTk.PhotoImage(bg_image)
                self.canvas = customtkinter.CTkCanvas(self.welcome_frame, width=bg_image.width, height=bg_image.height)
                self.canvas.pack(fill="both", expand=True)
                self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
                logger.log(SUCCESS, "005 Welcome background created successfully")
            except FileNotFoundError:
                logger.error("006 Background image file not found", exc_info=True)
                raise UIElementError("007 Background image file not found.")
            except Exception as e:
                logger.error(f"008 Failed to create welcome background: {e}", exc_info=True)
                raise UIElementError(f"009 Failed to create welcome background: {e}")

        @log_method
        def _create_welcome_header():
            try:
                logger.info("010 Creating welcome header")
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

                logger.log(SUCCESS, "011 Welcome header created successfully")
            except FileNotFoundError:
                logger.error(f"012 Logo file not found: {icon_path}", exc_info=True)
            except Exception as e:
                error_msg = f"013 Failed to create welcome header: {e}"
                logger.error(error_msg, exc_info=True)
                raise UIElementError(error_msg) from e

        @log_method
        def _create_welcome_labels():
            try:
                logger.info("014 Creating welcome labels")
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

                logger.log(SUCCESS, "015 Welcome labels created successfully")
            except Exception as e:
                error_msg = f"016 Failed to create welcome labels: {e}"
                logger.error(error_msg, exc_info=True)
                raise UIElementError(error_msg) from e

        @log_method
        def _create_welcome_button():
            try:
                logger.info("017 Creating welcome button")
                self.lets_go_button = self._create_welcome_button("Let's go", self.show_view_my_secrets)
                self.lets_go_button.place(relx=0.85, rely=0.93, anchor="center")

                logger.log(SUCCESS, "018 Welcome button created successfully")
            except Exception as e:
                error_msg = f"019 Failed to create welcome button: {e}"
                logger.error(error_msg, exc_info=True)
                raise UIElementError(error_msg) from e

        logger.info("020 Initializing welcome view")

        try:
            self._clear_current_frame()
            _setup_welcome_frame()
            _create_welcome_background()
            _create_welcome_header()
            _create_welcome_labels()
            _create_welcome_button()

            logger.log(SUCCESS, "021 Welcome view created successfully")
            self.update()  # Force update of the window
        except FrameError as e:
            logger.error(f"022 Frame error in welcome method: {e}", exc_info=True)
            raise FrameError(f"023 Failed to initialize welcome view due to frame error: {e}") from e
        except UIElementError as e:
            logger.error(f"024 UI element error in welcome method: {e}", exc_info=True)
            raise UIElementError(f"025 Failed to initialize welcome view due to UI element error: {e}") from e
        except Exception as e:
            logger.error(f"026 Unexpected error in welcome method: {e}", exc_info=True)
            raise ViewError(f"027 Unexpected error while initializing welcome view: {e}") from e

    ####################################################################################################################
    """ SPECIFIC VIEW OF SATOCHIP UTIL FOR MANAGE SETTINGS """

    ####################################################################################################################
    @log_method
    def view_start_setup(self):

        @log_method
        def _create_start_setup_frame():
            try:
                logger.info("001 Creating start setup frame")
                self._create_frame()
                logger.log(SUCCESS, "002 Start setup frame created successfully")
            except Exception as e:
                logger.error(f"003 Error creating start setup frame: {e}", exc_info=True)
                raise FrameCreationError(f"004 Failed to create start setup frame: {e}") from e

        @log_method
        def _create_return_button():
            try:
                logger.info("005 Creating return button")
                return_button = self._create_button(text="Back",
                                                    command=lambda: [self.show_view_my_secrets()])
                return_button.place(relx=0.95, rely=0.95, anchor="se")
                logger.log(SUCCESS, "006 Return button created successfully")
            except Exception as e:
                logger.error(f"007 Error creating return button: {e}", exc_info=True)
                raise UIElementError(f"008 Failed to create return button: {e}") from e

        @log_method
        def _create_start_setup_header():
            try:
                logger.info("009 Creating start setup header")
                self.header = self._create_an_header("Settings", "home_popup_icon.jpg")
                self.header.place(relx=0.03, rely=0.08, anchor="nw")
                logger.log(SUCCESS, "010 Start setup header created successfully")
            except Exception as e:
                logger.error(f"011 Error creating start setup header: {e}", exc_info=True)
                raise UIElementError(f"012 Failed to create start setup header: {e}") from e

        @log_method
        def _load_background_image():
            try:
                logger.info("013 Loading background image")
                if self.controller.cc.card_present:
                    image_path = f"./pictures_db/card_{self.controller.cc.card_type.lower()}.png"
                else:
                    image_path = "./pictures_db/insert_card.png"

                self.background_photo = self._create_background_photo(self, image_path)
                self.canvas = self._create_canvas()

                self.canvas.place(relx=0.4, rely=0.5, anchor="center")
                self.canvas.create_image(self.canvas.winfo_reqwidth() / 2, self.canvas.winfo_reqheight() / 2,
                                         image=self.background_photo, anchor="center")
                logger.log(SUCCESS, "014 Background image loaded successfully")
            except Exception as e:
                logger.error(f"015 Error loading background image: {e}", exc_info=True)
                raise UIElementError(f"016 Failed to load background image: {e}") from e

        @log_method
        def _create_start_setup_labels():
            try:
                logger.info("017 Creating start setup labels")
                label1 = self._create_label(f"Your {self.controller.cc.card_type} is connected.")
                label1.place(relx=0.045, rely=0.27, anchor="w")

                label2 = self._create_label("Select on the menu the action you wish to perform.")
                label2.place(relx=0.045, rely=0.32, anchor="w")
                logger.log(SUCCESS, "018 Start setup labels created successfully")
            except Exception as e:
                logger.error(f"019 Error creating start setup labels: {e}", exc_info=True)
                raise UIElementError(f"020 Failed to create start setup labels: {e}") from e

        @log_method
        def _destroy_start_setup():
            try:
                logger.info("021 Destroying start setup view")
                if hasattr(self, 'current_frame'):
                    self.current_frame.destroy()
                    delattr(self, 'current_frame')
                if hasattr(self, 'header'):
                    self.header.destroy()
                    delattr(self, 'header')
                if hasattr(self, 'canvas'):
                    self.canvas.destroy()
                    delattr(self, 'canvas')
                logger.log(SUCCESS, "022 Start setup view destroyed successfully")
            except Exception as e:
                logger.error(f"023 Error destroying start setup view: {e}", exc_info=True)
                raise UIElementError(f"024 Failed to destroy start setup view: {e}") from e

        logger.info("025 Initializing start setup view")
        try:
            self.welcome_in_display = False
            _create_start_setup_frame()
            _load_background_image()
            _create_start_setup_header()
            _create_start_setup_labels()
            _create_return_button()
            self.create_satochip_utils_menu()
            logger.log(SUCCESS, "026 Start setup view initialized successfully")
        except (FrameCreationError, UIElementError) as e:
            logger.error(f"027 Error in start_setup: {e}", exc_info=True)
            raise ViewError(f"028 Failed to initialize start setup view: {e}") from e
        except Exception as e:
            logger.error(f"029 Unexpected error in start_setup: {e}", exc_info=True)
            raise ViewError(f"030 Unexpected error during start setup initialization: {e}") from e

    @log_method
    def view_change_pin(self):
        try:
            logger.info("001 Starting change_pin method")

            @log_method
            def _create_change_pin_frame():
                try:
                    logger.info("002 Creating change PIN frame")
                    self._create_frame()
                    logger.log(SUCCESS, "003 Change PIN frame created successfully")
                except Exception as e:
                    logger.error(f"004 Error creating change PIN frame: {e}", exc_info=True)
                    raise FrameCreationError(f"005 Failed to create change PIN frame: {e}") from e

            @log_method
            def _create_change_pin_header():
                try:
                    logger.info("006 Creating change PIN header")
                    self.header = self._create_an_header("Change PIN", "change_pin_popup_icon.jpg")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")
                    logger.log(SUCCESS, "007 Change PIN header created successfully")
                except Exception as e:
                    logger.error(f"008 Error creating change PIN header: {e}", exc_info=True)
                    raise UIElementError(f"009 Failed to create change PIN header: {e}") from e

            @log_method
            def _create_change_pin_content():
                try:
                    logger.info("010 Creating change PIN content")

                    instructions = [
                        "Change your personal PIN code.",
                        "We strongly encourage you to set up a strong password between 4 and 16",
                        "characters. You can use symbols, lower and upper cases, letters and",
                        "numbers."
                    ]

                    for i, text in enumerate(instructions):
                        label = self._create_label(text)
                        label.place(relx=0.05, rely=0.20 + i * 0.05, anchor="w")

                    pin_entries = [
                        ("Current PIN:", 0.40, "current_pin_entry"),
                        ("New PIN code:", 0.55, "new_pin_entry"),
                        ("Repeat new PIN code:", 0.70, "confirm_new_pin_entry")
                    ]

                    for label_text, rely, entry_name in pin_entries:
                        label = self._create_label(label_text)
                        label.configure(font=self._make_text_bold(18))
                        label.place(relx=0.05, rely=rely, anchor="w")

                        entry = self._create_entry(show_option="*")
                        entry.place(relx=0.05, rely=rely + 0.05, anchor="w")
                        setattr(self, entry_name, entry)

                    self.after(100, self.current_pin_entry.focus_force)

                    logger.log(SUCCESS, "011 Change PIN content created successfully")
                except Exception as e:
                    logger.error(f"012 Error creating change PIN content: {e}", exc_info=True)
                    raise UIElementError(f"013 Failed to create change PIN content: {e}") from e

            @log_method
            def _create_change_pin_buttons():
                try:
                    logger.info("014 Creating change PIN buttons")

                    cancel_button = self._create_button("Cancel", command=self.view_start_setup)
                    cancel_button.place(relx=0.63, rely=0.9, anchor="w")

                    change_button = self._create_button("Change it", command=_perform_pin_change)
                    change_button.place(relx=0.8, rely=0.9, anchor="w")

                    self.bind('<Return>', lambda event: _perform_pin_change())

                    logger.log(SUCCESS, "015 Change PIN buttons created successfully")
                except Exception as e:
                    logger.error(f"016 Error creating change PIN buttons: {e}", exc_info=True)
                    raise UIElementError(f"017 Failed to create change PIN buttons: {e}") from e

            @log_method
            def _perform_pin_change():
                try:
                    current_pin = self.current_pin_entry.get()
                    new_pin = self.new_pin_entry.get()
                    confirm_new_pin = self.confirm_new_pin_entry.get()
                    self.controller.change_card_pin(current_pin, new_pin, confirm_new_pin)
                except Exception as e:
                    logger.error(f"018 Error performing PIN change: {e}", exc_info=True)
                    self.show("ERROR", "Failed to change PIN", "Ok")

            _create_change_pin_frame()
            _create_change_pin_header()
            _create_change_pin_content()
            _create_change_pin_buttons()
            self.create_satochip_utils_menu()

            logger.log(SUCCESS, "019 change_pin method completed successfully")
        except Exception as e:
            logger.error(f"020 Unexpected error in change_pin: {e}", exc_info=True)
            raise ViewError(f"021 Failed to display change PIN view: {e}")

    @log_method
    def view_edit_label(self):
        try:
            logger.info("001 Starting view_edit_label method")

            @log_method
            def _create_edit_label_frame():
                try:
                    logger.info("002 Creating edit label frame")
                    self._create_frame()
                    logger.log(SUCCESS, "003 Edit label frame created successfully")
                except Exception as e:
                    logger.error(f"004 Error creating edit label frame: {e}", exc_info=True)
                    raise FrameCreationError(f"005 Failed to create edit label frame: {e}") from e

            @log_method
            def _create_edit_label_header():
                try:
                    logger.info("006 Creating edit label header")
                    header_text = "Edit Label"
                    self.header = self._create_an_header(header_text, "edit_label_icon_ws.jpg")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")
                    logger.log(SUCCESS, "007 Edit label header created successfully")
                except Exception as e:
                    logger.error(f"008 Error creating edit label header: {e}", exc_info=True)
                    raise UIElementError(f"009 Failed to create edit label header: {e}") from e

            @log_method
            def _create_edit_label_content():
                try:
                    logger.info("010 Creating edit label content")

                    instructions = [
                        f"Edit the label of your {self.controller.cc.card_type}.",
                        "The label is a tag that identifies your card. It can be used to distinguish",
                        "several cards, or to associate it with a person, a name or a story."
                    ]

                    for i, text in enumerate(instructions):
                        label = self._create_label(text)
                        label.place(relx=0.05, rely=0.20 + i * 0.05, anchor="w")

                    label_entries = [
                        ("Label:", 0.40, "edit_card_entry")
                    ]

                    for label_text, rely, entry_name in label_entries:
                        label = self._create_label(label_text)
                        label.configure(font=self._make_text_bold(18))
                        label.place(relx=0.05, rely=rely, anchor="w")

                        entry = self._create_entry()
                        entry.place(relx=0.05, rely=rely + 0.05, anchor="w")
                        setattr(self, entry_name, entry)

                    self.after(100, self.edit_card_entry.focus_force)

                    logger.log(SUCCESS, "011 Edit label content created successfully")
                except Exception as e:
                    logger.error(f"012 Error creating edit label content: {e}", exc_info=True)
                    raise UIElementError(f"013 Failed to create edit label content: {e}") from e

            @log_method
            def _create_edit_label_buttons():
                try:
                    logger.info("014 Creating edit label buttons")
                    self.cancel_button = self._create_button("Cancel", command=self.show_view_start_setup)
                    self.cancel_button.place(relx=0.63, rely=0.9, anchor="w")

                    self.finish_button = self._create_button("Change it", command=lambda: self.controller.edit_label(
                        self.edit_card_entry.get()))
                    self.finish_button.place(relx=0.8, rely=0.9, anchor="w")
                    self.bind('<Return>', lambda event: self.controller.edit_label(self.edit_card_entry.get()))
                    logger.log(SUCCESS, "015 Edit label buttons created successfully")
                except Exception as e:
                    logger.error(f"016 Error creating edit label buttons: {e}", exc_info=True)
                    raise UIElementError(f"017 Failed to create edit label buttons: {e}") from e

            @log_method
            def _handle_card_verification():
                try:
                    logger.info("018 Handling card verification")
                    if self.controller.cc.card_type != "Satodime":
                        if self.controller.cc.is_pin_set():
                            self.controller.cc.card_verify_PIN_simple()
                        else:
                            self.controller.PIN_dialog(f'Unlock your {self.controller.cc.card_type}')
                    logger.log(SUCCESS, "019 Card verification handled successfully")
                except Exception as e:
                    logger.error(f"020 Error handling card verification: {e}", exc_info=True)
                    raise ViewError(f"021 Failed to handle card verification: {e}") from e

            self._clear_current_frame()
            _create_edit_label_frame()
            _create_edit_label_header()
            _create_edit_label_content()
            _create_edit_label_buttons()
            _handle_card_verification()
            self.create_satochip_utils_menu()

            logger.log(SUCCESS, "022 Edit label view created successfully")
        except Exception as e:
            logger.error(f"023 Unexpected error in view_edit_label: {e}", exc_info=True)
            raise ViewError(f"024 Failed to create edit label view: {e}") from e

    @log_method
    def view_check_authenticity(self):
        try:
            logger.info("001 Starting view_check_authenticity method")

            @log_method
            def _create_check_authenticity_frame():
                try:
                    logger.info("002 Creating check authenticity frame")
                    self._create_frame()
                    logger.log(SUCCESS, "003 Check authenticity frame created successfully")
                except Exception as e:
                    logger.error(f"004 Error creating check authenticity frame: {e}", exc_info=True)
                    raise FrameCreationError(f"005 Failed to create check authenticity frame: {e}") from e

            @log_method
            def _create_check_authenticity_header():
                try:
                    logger.info("006 Creating check authenticity header")
                    self.header = self._create_an_header("Check authenticity", "check_authenticity_icon_ws.jpg")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")
                    logger.log(SUCCESS, "007 Check authenticity header created successfully")
                except Exception as e:
                    logger.error(f"008 Error creating check authenticity header: {e}", exc_info=True)
                    raise UIElementError(f"009 Failed to create check authenticity header: {e}") from e

            @log_method
            def _create_check_authenticity_content():
                try:
                    logger.info("010 Creating check authenticity content")
                    text = self._create_label("Check whether or not you have a genuine Satochip card.")
                    text.place(relx=0.045, rely=0.20, anchor="w")

                    status_label = self._create_label("Status:")
                    status_label.configure(font=self._make_text_bold())
                    status_label.place(relx=0.045, rely=0.27, anchor="w")

                    if self.controller.cc.card_present:
                        _display_authenticity_status()

                    _create_certificate_radio_buttons()
                    _create_text_box()

                    logger.log(SUCCESS, "011 Check authenticity content created successfully")
                except Exception as e:
                    logger.error(f"012 Error creating check authenticity content: {e}", exc_info=True)
                    raise UIElementError(f"013 Failed to create check authenticity content: {e}") from e

            @log_method
            def _display_authenticity_status():
                icon_path = "./pictures_db/icon_genuine_card.jpg" if is_authentic else "./pictures_db/icon_not_genuine_card.jpg"
                status_text = "Your card is authentic. " if is_authentic else "Your card is not authentic. "

                icon_image = Image.open(icon_path)
                icon = customtkinter.CTkImage(light_image=icon_image, size=(30, 30))
                icon_label = customtkinter.CTkLabel(self.current_frame, image=icon, text=status_text,
                                                    compound='right', bg_color="whitesmoke", fg_color="whitesmoke",
                                                    font=customtkinter.CTkFont(family="Outfit", size=18,
                                                                               weight="normal"))
                icon_label.place(relx=0.15, rely=0.267, anchor="w")

                if not is_authentic:
                    _display_warning_message()

            @log_method
            def _display_warning_message():
                warning_texts = [
                    ("Warning!", 0.7, True),
                    ("We could not authenticate the issuer of this card.", 0.75, False),
                    ("If you did not load the card applet by yourself, be extremely careful!", 0.8, False),
                    ("Contact support@satochip.io to report any suspicious device.", 0.85, False)
                ]

                for text, rely, is_bold in warning_texts:
                    label = self._create_label(text)
                    if is_bold:
                        label.configure(font=self._make_text_bold())
                    label.place(relx=0.33, rely=rely, anchor="w")

            @log_method
            def _create_certificate_radio_buttons():
                self.certificate_radio_value = customtkinter.StringVar(value="")
                radio_buttons = [
                    ("Root CA certificate", "root_ca_certificate", 0.045),
                    ("Sub CA certificate", "sub_ca_certificate", 0.345),
                    ("Device certificate", "device_certificate", 0.645)
                ]

                for text, value, relx in radio_buttons:
                    radio = customtkinter.CTkRadioButton(self.current_frame, text=text,
                                                         variable=self.certificate_radio_value, value=value,
                                                         font=customtkinter.CTkFont(family="Outfit", size=14,
                                                                                    weight="normal"),
                                                         bg_color="whitesmoke", fg_color="green", hover_color="green",
                                                         command=_update_radio_selection)
                    radio.place(relx=relx, rely=0.35, anchor="w")

            @log_method
            def _create_text_box():
                self.text_box = customtkinter.CTkTextbox(self, corner_radius=10,
                                                         bg_color='whitesmoke', fg_color=BG_BUTTON,
                                                         border_color=BG_BUTTON, border_width=0,
                                                         width=581, height=228 if is_authentic else 150,
                                                         text_color="grey",
                                                         font=customtkinter.CTkFont(family="Outfit", size=13,
                                                                                    weight="normal"))

            @log_method
            def _update_radio_selection():
                try:
                    selection = self.certificate_radio_value.get()
                    logger.info(f"014 Radio button selected: {selection}")
                    text_content = {
                        'root_ca_certificate': txt_ca,
                        'sub_ca_certificate': txt_subca,
                        'device_certificate': txt_device
                    }.get(selection, "")
                    self._update_textbox(text_content)
                    self.text_box.place(relx=0.28, rely=0.4, anchor="nw")
                except Exception as e:
                    logger.error(f"015 Error updating radio selection: {e}", exc_info=True)
                    raise UIElementError(f"016 Failed to update radio selection: {e}") from e

            @log_method
            def _create_check_authenticity_buttons():
                try:
                    logger.info("017 Creating check authenticity buttons")
                    self.cancel_button = self._create_button("Back", command=self.view_start_setup)
                    self.cancel_button.place(relx=0.8, rely=0.9, anchor="w")
                    logger.log(SUCCESS, "018 Check authenticity buttons created successfully")
                except Exception as e:
                    logger.error(f"019 Error creating check authenticity buttons: {e}", exc_info=True)
                    raise UIElementError(f"020 Failed to create check authenticity buttons: {e}") from e

            # Main execution
            if self.controller.cc.card_present:
                logger.info("021 Card detected: checking authenticity")
                is_authentic, txt_ca, txt_subca, txt_device, txt_error = self.controller.cc.card_verify_authenticity()
                if txt_error:
                    txt_device = f"{txt_error}\n------------------\n{txt_device}"

            self._clear_current_frame()
            _create_check_authenticity_frame()
            _create_check_authenticity_header()
            _create_check_authenticity_content()
            _create_check_authenticity_buttons()
            self.create_satochip_utils_menu()

            if self.controller.cc.card_type != "Satodime":
                try:
                    self.controller.cc.card_verify_PIN_simple()
                except Exception as e:
                    logger.error(f"022 Error verifying PIN: {e}", exc_info=True)
                    self.view_start_setup()

            logger.log(SUCCESS, "023 view_check_authenticity completed successfully")
        except Exception as e:
            logger.error(f"024 Unexpected error in view_check_authenticity: {e}", exc_info=True)
            raise ViewError(f"025 Failed to create check authenticity view: {e}") from e

    @log_method
    def view_about(self):
        try:
            logger.info("001 Starting view_about method")

            @log_method
            def _create_about_frame():
                try:
                    logger.info("002 Creating about frame")
                    self._create_frame()
                    logger.log(SUCCESS, "003 About frame created successfully")
                except Exception as e:
                    logger.error(f"004 Error creating about frame: {e}", exc_info=True)
                    raise FrameCreationError(f"005 Failed to create about frame: {e}") from e

            @log_method
            def _create_about_header():
                try:
                    logger.info("006 Creating about header")
                    self.header = self._create_an_header("About", "about_icon_ws.jpg")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")
                    logger.log(SUCCESS, "007 About header created successfully")
                except Exception as e:
                    logger.error(f"008 Error creating about header: {e}", exc_info=True)
                    raise UIElementError(f"009 Failed to create about header: {e}") from e

            @log_method
            def _load_background_image():
                try:
                    logger.info("010 Loading background image")
                    self.background_photo = self._create_background_photo(self, "./pictures_db/about.png")
                    self.canvas = self._create_canvas()
                    self.canvas.place(relx=0.5, rely=0.3, anchor="center")
                    self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
                    logger.log(SUCCESS, "011 Background image loaded successfully")
                except Exception as e:
                    logger.error(f"012 Error loading background image: {e}", exc_info=True)
                    raise UIElementError(f"013 Failed to load background image: {e}") from e

            @log_method
            def _create_card_information():
                try:
                    logger.info("014 Creating card information section")
                    card_information = self._create_label("Card information")
                    card_information.place(relx=0.05, rely=0.25, anchor="w")
                    card_information.configure(font=self._make_text_bold())

                    applet_version = self._create_label(
                        f"Applet version: {self.controller.card_status['applet_full_version_string']}")
                    applet_version.place(relx=0.05, rely=0.33)

                    if self.controller.cc.card_type == "Satodime" or self.controller.cc.is_pin_set():
                        _create_authenticated_card_info()

                    logger.log(SUCCESS, "015 Card information section created successfully")
                except Exception as e:
                    logger.error(f"016 Error creating card information section: {e}", exc_info=True)
                    raise UIElementError(f"017 Failed to create card information section: {e}") from e

            @log_method
            def _create_authenticated_card_info():
                if self.controller.cc.card_type != "Satodime":
                    self.controller.cc.card_verify_PIN_simple()
                card_label_named = self._create_label(f"Label: [{self.controller.get_card_label_infos()}]")
                is_authentic, _, _, _, _ = self.controller.cc.card_verify_authenticity()
                card_genuine = self._create_label(f"Genuine: {'YES' if is_authentic else 'NO'}")
                card_label_named.place(relx=0.05, rely=0.28)
                card_genuine.place(relx=0.05, rely=0.38)

            @log_method
            def _create_card_configuration():
                try:
                    logger.info("018 Creating card configuration section")
                    card_configuration = self._create_label("Card configuration")
                    card_configuration.place(relx=0.05, rely=0.48, anchor="w")
                    card_configuration.configure(font=self._make_text_bold())

                    if self.controller.cc.card_type != "Satodime":
                        pin_info = f"PIN counter:[{self.controller.card_status['PIN0_remaining_tries']}] tries remaining"
                    else:
                        pin_info = "No PIN required"
                    self._create_label(pin_info).place(relx=0.05, rely=0.52)

                    if self.controller.cc.card_type == "Satochip":
                        two_fa_status = "2FA enabled" if self.controller.cc.needs_2FA else "2FA disabled"
                        self._create_label(two_fa_status).place(relx=0.05, rely=0.58)

                    logger.log(SUCCESS, "019 Card configuration section created successfully")
                except Exception as e:
                    logger.error(f"020 Error creating card configuration section: {e}", exc_info=True)
                    raise UIElementError(f"021 Failed to create card configuration section: {e}") from e

            @log_method
            def _create_card_connectivity():
                try:
                    logger.info("022 Creating card connectivity section")
                    card_connectivity = self._create_label("Card connectivity")
                    card_connectivity.place(relx=0.05, rely=0.68, anchor="w")
                    card_connectivity.configure(font=self._make_text_bold())

                    nfc_status = {
                        0: "NFC enabled",
                        1: "NFC disabled",
                    }.get(self.controller.cc.nfc_policy, "NFC: [BLOCKED]")
                    self._create_label(nfc_status).place(relx=0.05, rely=0.715)

                    logger.log(SUCCESS, "023 Card connectivity section created successfully")
                except Exception as e:
                    logger.error(f"024 Error creating card connectivity section: {e}", exc_info=True)
                    raise UIElementError(f"025 Failed to create card connectivity section: {e}") from e

            @log_method
            def _create_software_information():
                from version import VERSION
                try:
                    logger.info("026 Creating software information section")
                    software_information = self._create_label("Software information")
                    software_information.place(relx=0.05, rely=0.81, anchor="w")
                    software_information.configure(font=self._make_text_bold())
                    self._create_label(f"SeedKeeper-Tool version: {VERSION}").place(relx=0.05, rely=0.83)
                    self._create_label(f"Pysatochip version: {PYSATOCHIP_VERSION}").place(relx=0.05, rely=0.88)

                    logger.log(SUCCESS, "027 Software information section created successfully")
                except Exception as e:
                    logger.error(f"028 Error creating software information section: {e}", exc_info=True)
                    raise UIElementError(f"029 Failed to create software information section: {e}") from e

            @log_method
            def _create_return_button():
                try:
                    logger.info("005 Creating return button")
                    return_button = self._create_button(text="Back",
                                                        command=lambda: [self.show_view_my_secrets()])
                    return_button.place(relx=0.95, rely=0.95, anchor="se")
                    logger.log(SUCCESS, "006 Return button created successfully")
                except Exception as e:
                    logger.error(f"007 Error creating return button: {e}", exc_info=True)
                    raise UIElementError(f"008 Failed to create return button: {e}") from e

            _create_about_frame()
            _load_background_image()
            _create_about_header()
            _create_card_information()
            _create_card_configuration()
            _create_card_connectivity()
            _create_software_information()
            _create_return_button()
            self.create_satochip_utils_menu()

            logger.log(SUCCESS, "037 view_about method completed successfully")
        except Exception as e:
            logger.error(f"038 Unexpected error in view_about: {e}", exc_info=True)
            raise ViewError(f"039 Failed to display about view: {e}")

    ####################################################################################################################
    """ SPECIFIC VIEW OF SEEDKEEPER """

    ####################################################################################################################
    @log_method
    def view_my_secrets(
            self,
            secrets_data: Dict[str, Any]
    ):
        @log_method
        def _create_secrets_frame():
            try:
                logger.info("001 Creating secrets frame")
                self._create_frame()
                logger.log(SUCCESS, "002 Secrets frame created successfully")
            except Exception as e:
                logger.error(f"003 Error creating secrets frame: {e}", exc_info=True)
                raise FrameCreationError(f"004 Failed to create secrets frame: {e}") from e

        @log_method
        def _create_secrets_header():
            try:
                logger.info("005 Creating secrets header")
                self.header = self._create_an_header("My Secrets", "secrets_icon_ws.png")
                self.header.place(relx=0.03, rely=0.08, anchor="nw")
                logger.log(SUCCESS, "006 Secrets header created successfully")
            except Exception as e:
                logger.error(f"007 Error creating secrets header: {e}", exc_info=True)
                raise UIElementError(f"008 Failed to create secrets header: {e}") from e

        @log_method
        def _create_secrets_table(secrets_data):
            def _on_mouse_on_secret(event, buttons):
                for button in buttons:
                    button.configure(fg_color=HIGHLIGHT_COLOR, cursor="hand2")

            def _on_mouse_out_secret(event, buttons):
                for button in buttons:
                    button.configure(fg_color=button.default_color)

            def _show_secret_details(secret):
                try:
                    logger.info(f"009 Showing details for secret ID: {secret['id']}")
                    self._create_frame()

                    secret_details = self.controller.retrieve_details_about_secret_selected(secret['id'])
                    logger.log(SUCCESS, f"010 Secret details retrieved: {secret_details}")

                    self.header = self._create_an_header("Secret Details", "secrets_icon_ws.png")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")

                    self.create_seedkeeper_menu()

                    if secret['type'] == 'Password':
                        _create_password_secret_frame(secret_details)
                    elif secret['type'] == 'Masterseed':
                        _create_mnemonic_secret_frame(secret_details)
                    else:
                        logger.warning(f"011 Unsupported secret type: {secret['type']}")
                        _create_generic_secret_frame(secret_details)

                    back_button = self._create_button(text="Back", command=self.show_view_my_secrets)
                    back_button.place(relx=0.95, rely=0.98, anchor="se")

                    logger.log(SUCCESS, f"012 Secret details displayed for ID: {secret['id']}")
                except Exception as e:
                    logger.error(f"013 Error displaying secret details: {e}", exc_info=True)
                    raise SecretFrameCreationError("Error displaying secret details") from e

            try:
                logger.info("014 Creating secrets table")

                # Introduce table
                label_text = self._create_label(text="Click on a secret to manage it:")
                label_text.place(relx=0.05, rely=0.25, anchor="w")

                # Define headers
                headers = ["Id", "Type of secret", "Label"]
                rely = 0.3

                # Create header labels
                header_frame = customtkinter.CTkFrame(self.current_frame, width=750, bg_color=DEFAULT_BG_COLOR,
                                                      corner_radius=0, fg_color=DEFAULT_BG_COLOR)
                header_frame.place(relx=0.05, rely=rely, relwidth=0.9, anchor="w")

                header_widths = [100, 250, 350]  # Define specific widths for each header
                for col, width in zip(headers, header_widths):
                    header_button = customtkinter.CTkButton(header_frame, text=col,
                                                            font=customtkinter.CTkFont(size=14, family='Outfit',
                                                                                       weight="bold"),
                                                            corner_radius=0, state='disabled', text_color='white',
                                                            fg_color=BG_MAIN_MENU, width=width)
                    header_button.pack(side="left", expand=True, fill="both")

                logger.debug("015 Table headers created")

                table_frame = self._create_scrollable_frame(self.current_frame, width=700, height=400, x=33.5, y=200)

                # Create rows of labels with alternating colors
                for i, secret in enumerate(secrets_data['headers']):
                    try:
                        rely += 0.06
                        row_frame = customtkinter.CTkFrame(table_frame, width=750, bg_color=DEFAULT_BG_COLOR,
                                                           fg_color=DEFAULT_BG_COLOR)
                        row_frame.pack(pady=2, fill="x")

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

                        logger.debug(f"016 Row created for secret ID: {secret['id']}")
                    except Exception as e:
                        logger.error(f"017 Error creating row for secret {secret['id']}: {str(e)}")
                        raise UIElementError(f"018 Failed to create row for secret {secret['id']}") from e

                logger.log(SUCCESS, "019 Secrets table created successfully")
            except Exception as e:
                logger.error(f"020 Error in _create_secrets_table: {e}", exc_info=True)
                raise UIElementError(f"021 Failed to create secrets table: {e}") from e

        @log_method
        def _create_password_secret_frame(secret_details):
            try:
                delete_button = self._create_button(text="Delete secret",
                                                    command=lambda: None)  # self._delete_secret(secret['id']))
                delete_button.place(relx=0.7, rely=0.15, anchor="se")

                logger.info("001 Creating password secret frame")
                # Create labels and entry fields
                labels = ['Label:', 'Login:', 'URL:']
                entries = {}

                for i, label_text in enumerate(labels):
                    try:
                        label = self._create_label(label_text)
                        label.place(relx=0.045, rely=0.2 + i * 0.15, anchor="w")
                        logger.debug(f"002 Created label: {label_text}")

                        entry = self._create_entry()
                        entry.place(relx=0.04, rely=0.27 + i * 0.15, anchor="w")
                        entries[label_text.lower()[:-1]] = entry
                        logger.debug(f"003 Created entry for: {label_text}")
                    except Exception as e:
                        logger.error(f"004 Error creating label or entry for {label_text}: {e}", exc_info=True)
                        raise UIElementError(f"005 Failed to create label or entry for {label_text}: {e}") from e

                # Set values
                entries['label'].insert(0, secret_details['label'])
                entries['login'].insert(0, "Placeholder Login")  # Replace with actual data
                entries['url'].insert(0, "Placeholder URL")  # Replace with actual data
                logger.debug("006 Entry values set")

                # Create password field
                try:
                    password_label = self._create_label("Password:")
                    password_label.place(relx=0.045, rely=0.7, anchor="w")

                    password_entry = self._create_entry()
                    password_entry.configure(width=500)
                    password_entry.place(relx=0.04, rely=0.77, anchor="w")
                    password_entry.insert(0, "********")  # TODO implement method to retrieve password into controller
                    logger.debug("007 Password field created")
                except Exception as e:
                    logger.error(f"008 Error creating password field: {e}", exc_info=True)
                    raise UIElementError(f"009 Failed to create password field: {e}") from e

                # Create action buttons
                try:
                    show_button = self._create_button(text="Show",
                                                      command=lambda: None)  # self._toggle_password_visibility(password_entry))
                    show_button.place(relx=0.9, rely=0.8, anchor="se")
                    logger.debug("010 Action buttons created")
                except Exception as e:
                    logger.error(f"011 Error creating action buttons: {e}", exc_info=True)
                    raise UIElementError(f"012 Failed to create action buttons: {e}") from e

                logger.log(SUCCESS, "013 Password secret frame created successfully")
            except Exception as e:
                logger.error(f"014 Unexpected error in _create_password_secret_frame: {e}", exc_info=True)
                raise ViewError(f"015 Failed to create password secret frame: {e}") from e

        @log_method
        def _create_mnemonic_secret_frame(secret_details):
            try:
                logger.info("001 Creating mnemonic secret frame")
                # Create labels and entry fields
                labels = ['Label:', 'Mnemonic type:']
                entries = {}

                for i, label_text in enumerate(labels):
                    try:
                        label = self._create_label(label_text)
                        label.place(relx=0.045, rely=0.2 + i * 0.15, anchor="w")
                        logger.debug(f"002 Created label: {label_text}")

                        entry = self._create_entry()
                        entry.place(relx=0.04, rely=0.27 + i * 0.15, anchor="w")
                        entries[label_text.lower()[:-1]] = entry
                        logger.debug(f"003 Created entry for: {label_text}")
                    except Exception as e:
                        logger.error(f"004 Error creating label or entry for {label_text}: {e}", exc_info=True)
                        raise UIElementError(f"005 Failed to create label or entry for {label_text}: {e}") from e

                # Set values
                entries['label'].insert(0, secret_details['label'])
                entries['mnemonic type'].insert(0, secret_details['type'])
                logger.debug("006 Entry values set")

                try:
                    xpub_button = self._create_button(text="Xpub",
                                                      command=lambda: None)  # self._show_xpub(secret['id']))
                    xpub_button.place(relx=0.60, rely=0.53, anchor="se")

                    seedqr_button = self._create_button(text="SeedQR",
                                                        command=lambda: None)  # self._show_seedqr(secret['id']))
                    seedqr_button.place(relx=0.78, rely=0.53, anchor="se")
                    logger.debug("007 Xpub and SeedQR buttons created")
                except Exception as e:
                    logger.error(f"008 Error creating Xpub and SeedQR buttons: {e}", exc_info=True)
                    raise UIElementError(f"009 Failed to create Xpub and SeedQR buttons: {e}") from e

                # Create passphrase field
                try:
                    passphrase_label = self._create_label("Passphrase:")
                    passphrase_label.place(relx=0.045, rely=0.58, anchor="w")

                    passphrase_entry = self._create_entry()
                    passphrase_entry.place(relx=0.2, rely=0.58, anchor="w", relwidth=0.585)
                    passphrase_entry.insert(0, "Comment récupérer la passhprase ?")  # Replace with actual data
                    logger.debug("010 Passphrase field created")
                except Exception as e:
                    logger.error(f"011 Error creating passphrase field: {e}", exc_info=True)
                    raise UIElementError(f"012 Failed to create passphrase field: {e}") from e

                # Create mnemonic field
                try:
                    mnemonic_label = self._create_label("Mnemonic:")
                    mnemonic_label.place(relx=0.045, rely=0.65, anchor="w")

                    mnemonic_entry = self._create_entry(show_option='*')
                    mnemonic_entry.place(relx=0.04, rely=0.8, relheight=0.23, anchor="w")
                    mnemonic_entry.insert(0, secret_details['secret'])  # Replace with actual mnemonic
                    logger.debug("013 Mnemonic field created")
                except Exception as e:
                    logger.error(f"014 Error creating mnemonic field: {e}", exc_info=True)
                    raise UIElementError(f"015 Failed to create mnemonic field: {e}") from e

                @log_method
                def _toggle_mnemonic_visibility(entry):
                    try:
                        logger.info("016 Toggling mnemonic visibility")
                        current_state = entry.cget("show")
                        new_state = "" if current_state == "*" else "*"
                        entry.configure(show=new_state)
                        logger.log(SUCCESS,
                                   f"017 Mnemonic visibility toggled to {'hidden' if new_state == '*' else 'visible'}")
                    except Exception as e:
                        logger.error(f"018 Error toggling mnemonic visibility: {e}", exc_info=True)
                        raise UIElementError(f"019 Failed to toggle mnemonic visibility: {e}") from e

                # Create action buttons
                try:
                    delete_button = self._create_button(text="Delete secret",
                                                        command=lambda: None)  # self._delete_secret(secret['id']))
                    delete_button.place(relx=0.7, rely=0.15, anchor="se")

                    show_button = self._create_button(text="Show",
                                                      command=lambda: _toggle_mnemonic_visibility(mnemonic_entry))
                    show_button.place(relx=0.95, rely=0.8, anchor="e")
                    logger.debug("020 Action buttons created")
                except Exception as e:
                    logger.error(f"021 Error creating action buttons: {e}", exc_info=True)
                    raise UIElementError(f"022 Failed to create action buttons: {e}") from e

                logger.log(SUCCESS, "023 Mnemonic secret frame created successfully")
            except Exception as e:
                logger.error(f"024 Unexpected error in _create_mnemonic_secret_frame: {e}", exc_info=True)
                raise ViewError(f"025 Failed to create mnemonic secret frame: {e}") from e

        @log_method
        def _create_generic_secret_frame(secret_details):
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

        try:
            logger.info("022 Creating secrets frame")
            _create_secrets_frame()
            _create_secrets_header()
            _create_secrets_table(secrets_data)
            self.create_seedkeeper_menu()
            logger.log(SUCCESS, "023 Secrets frame created successfully")
        except Exception as e:
            error_msg = f"024 Failed to create secrets frame: {e}"
            logger.error(error_msg, exc_info=True)
            raise SecretFrameCreationError(error_msg) from e

    @log_method
    def view_generate_secret(self):
        try:
            logger.info("001 Starting generate_secret method")

            @log_method
            def _create_generate_secret_selection_frame():
                @log_method
                def _on_next_clicked():
                    try:
                        logger.info("010 Next button clicked")
                        selected_type = self.secret_type.get()
                        if selected_type == "Mnemonic seedphrase":
                            logger.debug("011 Mnemonic seedphrase selected")
                            _show_generate_mnemonic()
                        elif selected_type == "Couple login/password":
                            logger.debug("012 Couple login/password selected")
                            _show_generate_password()
                        else:
                            logger.warning("013 No secret type selected")
                            self.show("ERROR", "Please select a secret type", "Ok")
                    except Exception as e:
                        logger.error(f"014 Error in _on_next_clicked: {e}", exc_info=True)
                        raise UIElementError(f"015 Failed to process next button click: {e}") from e

                try:
                    logger.info("016 Creating initial selection frame")
                    self._create_frame()

                    self.header = self._create_an_header("Generate secret", "generate_icon_ws.png")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")

                    info_text_line_01 = "Seedkeeper allows you to generate and import a BIP39 mnemonic phrase -aka "
                    info_label = self._create_label(info_text_line_01)
                    info_label.place(relx=0.05, rely=0.22, anchor="w")

                    info_text_line_02 = "seedphrase- or a login/password. Select the type of secret you want to generate."
                    info_label = self._create_label(info_text_line_02)
                    info_label.place(relx=0.05, rely=0.27, anchor="w")

                    type_label = self._create_label("Type of secret:")
                    type_label.place(relx=0.05, rely=0.35, anchor="w")

                    self.secret_type, secret_type_menu = self.create_option_list(
                        ["Mnemonic seedphrase", "Login/password"],
                        default_value="Mnemonic seedphrase",
                        width=555
                    )
                    secret_type_menu.place(relx=0.05, rely=0.40, anchor="w")

                    next_button = self._create_button("Next", command=_on_next_clicked)
                    next_button.place(relx=0.95, rely=0.95, anchor="se")

                    logger.log(SUCCESS, "017 Initial selection frame created successfully")
                except Exception as e:
                    logger.error(f"018 Error creating initial selection frame: {e}", exc_info=True)
                    raise FrameCreationError(f"019 Failed to create initial selection frame: {e}") from e

            @log_method
            def _show_generate_mnemonic():
                try:
                    logger.info("020 Starting _show_generate_mnemonic")

                    @log_method
                    def _generate_mnemonic_frame():
                        try:
                            logger.info("021 Creating generate mnemonic frame")
                            self._create_frame()
                            logger.log(SUCCESS, "022 Generate mnemonic frame created successfully")
                        except Exception as e:
                            logger.error(f"023 Error creating generate mnemonic frame: {e}", exc_info=True)
                            raise FrameCreationError(f"024 Failed to create generate mnemonic frame: {e}") from e

                    @log_method
                    def _generate_mnemonic_header():
                        try:
                            logger.info("025 Creating generate mnemonic header")
                            header_text = "Generate seedphrase"
                            self.header = self._create_an_header(header_text, "generate_icon_ws.png")
                            self.header.place(relx=0.03, rely=0.08, anchor="nw")
                            logger.log(SUCCESS, "026 Generate mnemonic header created successfully")
                        except Exception as e:
                            logger.error(f"027 Error creating generate mnemonic header: {e}", exc_info=True)
                            raise UIElementError(f"028 Failed to create generate mnemonic header: {e}") from e

                    @log_method
                    def _generate_mnemonic_widgets():
                        try:
                            logger.info("029 Creating generate mnemonic content")

                            label = self._create_label("Label:")
                            label.place(relx=0.05, rely=0.20, anchor="nw")

                            label_name = self._create_entry()
                            label_name.place(relx=0.04, rely=0.25, anchor="nw")

                            self.radio_value = customtkinter.StringVar(value="12")
                            self.use_passphrase = customtkinter.BooleanVar(value=False)

                            radio_12 = customtkinter.CTkRadioButton(
                                self.current_frame,
                                text="12 words",
                                variable=self.radio_value,
                                value="12",
                                command=_update_mnemonic
                            )
                            radio_12.place(relx=0.05, rely=0.35, anchor="w")

                            radio_24 = customtkinter.CTkRadioButton(
                                self.current_frame,
                                text="24 words",
                                variable=self.radio_value,
                                value="24",
                                command=_update_mnemonic
                            )
                            radio_24.place(relx=0.2, rely=0.35, anchor="w")

                            self.mnemonic_textbox = customtkinter.CTkTextbox(self, corner_radius=20,
                                                                             bg_color="whitesmoke", fg_color=BG_BUTTON,
                                                                             border_color=BG_BUTTON, border_width=1,
                                                                             width=500, height=83,
                                                                             text_color="grey",
                                                                             font=customtkinter.CTkFont(family="Outfit",
                                                                                                        size=13,
                                                                                                        weight="normal"))
                            self.mnemonic_textbox.place(relx=0.28, rely=0.45, anchor="w")

                            passphrase_checkbox = customtkinter.CTkCheckBox(
                                self.current_frame,
                                text="Use passphrase",
                                variable=self.use_passphrase,
                                command=_toggle_passphrase
                            )
                            passphrase_checkbox.place(relx=0.05, rely=0.57, anchor="w")

                            self.passphrase_entry = customtkinter.CTkEntry(
                                self.current_frame,
                                width=300,
                                placeholder_text="Enter passphrase (optional)",
                                show="*"
                            )
                            self.passphrase_entry.place(relx=0.28, rely=0.57, anchor="w")
                            self.passphrase_entry.configure(state="disabled")

                            generate_mnemonic_button = self._create_button("Generate", command=_generate_new_mnemonic)
                            generate_mnemonic_button.place(relx=0.75, rely=0.45, anchor="w")

                            save_button = self._create_button("Save on card", command=_save_mnemonic_to_card)
                            save_button.place(relx=0.85, rely=0.93, anchor="center")

                            back_button = self._create_button("Back", command=self.show_view_generate_secret)
                            back_button.place(relx=0.65, rely=0.93, anchor="center")

                            logger.log(SUCCESS, "030 Generate mnemonic content created successfully")
                        except Exception as e:
                            logger.error(f"031 Error creating generate mnemonic content: {e}", exc_info=True)
                            raise UIElementError(f"032 Failed to create generate mnemonic content: {e}") from e

                    @log_method
                    def _update_mnemonic():
                        try:
                            logger.info("033 Updating mnemonic")
                            _generate_new_mnemonic()
                            logger.log(SUCCESS, "034 Mnemonic updated successfully")
                        except Exception as e:
                            logger.error(f"035 Error updating mnemonic: {e}", exc_info=True)
                            raise UIElementError(f"036 Failed to update mnemonic: {e}") from e

                    @log_method
                    def _generate_new_mnemonic():
                        try:
                            logger.info("037 Generating new mnemonic")
                            mnemonic_length = int(self.radio_value.get())
                            mnemonic = self.controller.generate_random_seed(mnemonic_length)
                            self.mnemonic_textbox.delete("1.0", customtkinter.END)
                            self.mnemonic_textbox.insert("1.0", mnemonic)
                            logger.log(SUCCESS, "038 New mnemonic generated successfully")
                        except Exception as e:
                            logger.error(f"039 Error generating mnemonic: {e}", exc_info=True)
                            raise UIElementError(f"040 Failed to generate mnemonic: {e}") from e

                    @log_method
                    def _toggle_passphrase():
                        try:
                            logger.info("041 Toggling passphrase")
                            if self.use_passphrase.get():
                                self.passphrase_entry.configure(state="normal")
                                logger.debug("042 Passphrase entry enabled")
                            else:
                                self.passphrase_entry.configure(state="disabled")
                                logger.debug("043 Passphrase entry disabled")
                        except Exception as e:
                            logger.error(f"044 Error toggling passphrase: {e}", exc_info=True)
                            raise UIElementError(f"045 Failed to toggle passphrase: {e}") from e

                    @log_method
                    def _save_mnemonic_to_card():
                        try:
                            logger.info("046 Saving mnemonic to card")
                            mnemonic = self.mnemonic_textbox.get("1.0", customtkinter.END).strip()
                            passphrase = self.passphrase_entry.get() if self.use_passphrase.get() else None
                            if mnemonic:
                                self.controller.import_seed(mnemonic, passphrase)
                                logger.log(SUCCESS, "047 Mnemonic saved to card successfully")
                            else:
                                logger.warning("048 No mnemonic to save")
                                raise ValueError("049 No mnemonic generated")
                        except ValueError as e:
                            logger.error(f"050 Error saving mnemonic to card: {e}", exc_info=True)
                            raise UIElementError(f"051 Failed to save mnemonic to card: {e}") from e
                        except Exception as e:
                            logger.error(f"052 Error saving mnemonic to card: {e}", exc_info=True)
                            raise UIElementError(f"053 Failed to save mnemonic to card: {e}") from e

                    self._clear_current_frame()
                    _generate_mnemonic_frame()
                    _generate_mnemonic_header()
                    _generate_mnemonic_widgets()
                    self.create_seedkeeper_menu()
                    self.mnemonic_textbox_active = True
                    logger.log(SUCCESS, "054 _show_generate_mnemonic completed successfully")
                except Exception as e:
                    logger.error(f"055 Unexpected error in _show_generate_mnemonic: {e}", exc_info=True)
                    raise ViewError(f"056 Failed to show generate mnemonic view: {e}") from e

            @log_method
            def _show_generate_password():
                try:
                    logger.info("057 Starting _show_generate_password method")

                    @log_method
                    def _create_generate_password_frame():
                        try:
                            logger.info("058 Creating generate login/password frame")
                            self._create_frame()
                            logger.log(SUCCESS, "059 Generate login/password frame created successfully")
                        except Exception as e:
                            logger.error(f"060 Error creating generate login/password frame: {e}", exc_info=True)
                            raise FrameCreationError(f"061 Failed to create generate login/password frame: {e}") from e

                    @log_method
                    def _create_generate_password_header():
                        try:
                            logger.info("062 Creating generate login/password header")
                            header_text = "Generate couple login/password"
                            self.header = self._create_an_header(header_text, "generate_icon_ws.png")
                            self.header.place(relx=0.03, rely=0.08, anchor="nw")
                            logger.log(SUCCESS, "063 Generate login/password header created successfully")
                        except Exception as e:
                            logger.error(f"064 Error creating generate login/password header: {e}", exc_info=True)
                            raise UIElementError(f"065 Failed to create generate login/password header: {e}") from e

                    @log_method
                    def _generate_new_password():
                        try:
                            logger.info("066 Generating new login/password")
                            generated_password = "example_password"  # TODO: implement the password generation into controller
                            textbox_width = 100
                            centered_text = generated_password.center(textbox_width)

                            self.password_text_box.configure(state='normal')
                            self.password_text_box.delete("1.0", customtkinter.END)
                            self.password_text_box.insert("1.0", centered_text)
                            self.password_text_box.configure(state='disabled')
                            logger.log(SUCCESS, "067 New login/password generated successfully")
                        except Exception as e:
                            logger.error(f"068 Error generating login/password: {e}", exc_info=True)
                            raise UIElementError(f"069 Failed to generate login/password: {e}") from e

                    @log_method
                    def _update_password():
                        try:
                            logger.info("070 Updating password")
                            _generate_new_password()
                            logger.log(SUCCESS, "071 Password updated successfully")
                        except Exception as e:
                            logger.error(f"072 Error updating password: {e}", exc_info=True)
                            raise UIElementError(f"073 Failed to update password: {e}") from e

                    @log_method
                    def _create_generate_password_content():
                        try:
                            logger.info("074 Creating generate login/password content")

                            # Label and entry creation
                            label = self._create_label("Label:")
                            label.place(relx=0.04, rely=0.20, anchor="nw")

                            label_name = self._create_entry()
                            label_name.place(relx=0.12, rely=0.195, anchor="nw")
                            label_name.configure(width=400)

                            login = self._create_label("Login:")
                            login.place(relx=0.04, rely=0.32, anchor="nw")

                            login_name = self._create_entry()
                            login_name.place(relx=0.12, rely=0.318, anchor="nw")
                            login_name.configure(width=400)

                            url = self._create_label("Url:")
                            url.place(relx=0.04, rely=0.44, anchor="nw")

                            url_name = self._create_entry()
                            url_name.place(relx=0.12, rely=0.438, anchor="nw")
                            url_name.configure(width=400)

                            logger.debug("075 Labels and entries created successfully")

                            # Slide bar creation
                            @log_method
                            def _length_slider_event(value):
                                try:
                                    int_value = int(value)
                                    length_value_label.configure(text=f"{int_value}")
                                    length_value_label.place(x=length_slider.get() * 3.5 + 250, y=324)

                                    if int_value < 8:
                                        length_slider.configure(button_color="red", progress_color="red")
                                    elif int_value == 8:
                                        length_slider.configure(button_color="orange", progress_color="orange")
                                    elif int_value > 8:
                                        length_slider.configure(button_color="green", progress_color="green")

                                    logger.debug(f"076 Slider value updated to {int_value}")
                                except Exception as e:
                                    logger.error(f"077 Error updating slider value: {e}", exc_info=True)
                                    raise UIElementError(f"078 Failed to update slider value: {e}") from e

                            length_slider = customtkinter.CTkSlider(self.current_frame,
                                                                    from_=4, to=16,
                                                                    command=_length_slider_event,
                                                                    width=600,
                                                                    progress_color=BG_HOVER_BUTTON,
                                                                    button_color=BG_MAIN_MENU)
                            length_slider.place(relx=0.15, rely=0.55)

                            length = self._create_label("Length: ")
                            length.place(relx=0.04, rely=0.535)

                            length_value_label = self._create_label("6")
                            length_value_label.configure(font=self._make_text_bold(20))
                            length_value_label.place(x=250, y=324)

                            logger.debug("079 Slider and length labels created successfully")

                            # Checkbox creation
                            characters_used = self._create_label("Characters used: ")
                            characters_used.place(relx=0.04, rely=0.6)

                            self.var_abc = customtkinter.StringVar()
                            self.var_ABC = customtkinter.StringVar()
                            self.var_numeric = customtkinter.StringVar()
                            self.var_symbolic = customtkinter.StringVar()

                            @log_method
                            def checkbox_event():
                                try:
                                    selected_values = [self.var_abc.get(), self.var_ABC.get(), self.var_numeric.get(),
                                                       self.var_symbolic.get()]
                                    logger.debug(
                                        f"080 Checkbox selection updated: {', '.join(filter(None, selected_values))}")
                                except Exception as e:
                                    logger.error(f"081 Error in checkbox event: {e}", exc_info=True)
                                    raise UIElementError(f"082 Failed to handle checkbox event: {e}") from e

                            minus_abc = customtkinter.CTkCheckBox(self.current_frame, text="abc", variable=self.var_abc,
                                                                  onvalue="abc", offvalue="", command=checkbox_event,
                                                                  checkmark_color=BG_MAIN_MENU,
                                                                  fg_color=BG_HOVER_BUTTON)
                            minus_abc.place(relx=0.3, rely=0.6)

                            major_abc = customtkinter.CTkCheckBox(self.current_frame, text="ABC", variable=self.var_ABC,
                                                                  onvalue="ABC", offvalue="", command=checkbox_event,
                                                                  checkmark_color=BG_MAIN_MENU,
                                                                  fg_color=BG_HOVER_BUTTON)
                            major_abc.place(relx=0.4, rely=0.6)

                            numeric_value = customtkinter.CTkCheckBox(self.current_frame, text="123",
                                                                      variable=self.var_numeric,
                                                                      onvalue="123", offvalue="",
                                                                      command=checkbox_event,
                                                                      checkmark_color=BG_MAIN_MENU,
                                                                      fg_color=BG_HOVER_BUTTON)
                            numeric_value.place(relx=0.5, rely=0.6)

                            symbolic_value = customtkinter.CTkCheckBox(self.current_frame, text="#$&",
                                                                       variable=self.var_symbolic,
                                                                       onvalue="#$&", offvalue="",
                                                                       command=checkbox_event,
                                                                       checkmark_color=BG_MAIN_MENU,
                                                                       fg_color=BG_HOVER_BUTTON)
                            symbolic_value.place(relx=0.6, rely=0.6)

                            logger.debug("083 Checkboxes created successfully")

                            password_label = self._create_label("Generated Password:")
                            password_label.place(relx=0.04, rely=0.67, anchor="nw")

                            self.password_text_box = customtkinter.CTkTextbox(self, corner_radius=20,
                                                                              bg_color="whitesmoke", fg_color=BG_BUTTON,
                                                                              border_color=BG_BUTTON, border_width=1,
                                                                              width=500, height=83,
                                                                              text_color="grey",
                                                                              font=customtkinter.CTkFont(
                                                                                  family="Outfit",
                                                                                  size=13,
                                                                                  weight="normal"))
                            self.password_text_box.place(relx=0.28, rely=0.8, anchor="w")
                            self.password_text_box.configure(state='disabled')

                            generate_password_button = self._create_button("Generate", command=_update_password)
                            generate_password_button.place(relx=0.75, rely=0.8, anchor="w")

                            save_button = self._create_button("Save on card", command=_save_password_to_card)
                            save_button.place(relx=0.85, rely=0.93, anchor="center")

                            back_button = self._create_button("Back",
                                                              command=self.show_view_generate_secret)
                            back_button.place(relx=0.65, rely=0.93, anchor="center")

                            logger.log(SUCCESS, "084 Generate login/password content created successfully")
                        except Exception as e:
                            logger.error(f"085 Error creating generate login/password content: {e}", exc_info=True)
                            raise UIElementError(f"086 Failed to create generate login/password content: {e}") from e

                    @log_method
                    def _save_password_to_card():
                        try:
                            logger.info("087 Saving login/password to card")
                            password = self.password_text_box.get("1.0", customtkinter.END).strip()
                            if password:
                                # TODO: Implement actual saving logic
                                logger.log(SUCCESS, "088 Login/password saved to card successfully")
                            else:
                                logger.warning("089 No password to save")
                                raise ValueError("090 No password generated")
                        except ValueError as e:
                            logger.error(f"091 Error saving login/password to card: {e}", exc_info=True)
                            raise UIElementError(f"092 Failed to save login/password to card: {e}") from e
                        except Exception as e:
                            logger.error(f"093 Unexpected error saving login/password to card: {e}", exc_info=True)
                            raise UIElementError(f"094 Unexpected error saving login/password to card: {e}") from e

                    self._clear_current_frame()
                    _create_generate_password_frame()
                    _create_generate_password_header()
                    _create_generate_password_content()
                    self.create_seedkeeper_menu()
                    self.password_text_box_active = True

                    logger.log(SUCCESS, "095 _show_generate_password completed successfully")
                except Exception as e:
                    logger.error(f"096 Unexpected error in _show_generate_password: {e}", exc_info=True)
                    raise ViewError(f"097 Failed to show generate login/password view: {e}") from e

            logger.info("099 Creating generate secret view")

            _create_generate_secret_selection_frame()
            self.create_seedkeeper_menu()
            logger.log(SUCCESS, "100 Generate secret view created successfully")
        except (FrameCreationError, UIElementError) as e:
            logger.error(f"101 Error in generate_secret: {e}", exc_info=True)
            raise ViewError(f"102 Failed to create generate secret view: {e}") from e
        except ViewError as ve:
            logger.error(f"105 View error in generate_secret: {ve}", exc_info=True)
            self.show("ERROR", str(ve), "Ok")
        except Exception as e:
            logger.error(f"103 Unexpected error in generate_secret: {e}", exc_info=True)
            raise ViewError(f"104 Unexpected error during generate secret view creation: {e}")
        finally:
            logger.info("107 Exiting generate_secret method")

    def view_import_secret(self):
        try:
            @log_method
            def _create_import_secret_selection_frame():
                @log_method
                def _on_next_clicked():
                    try:
                        logger.info("001 Next button clicked")
                        selected_type = self.secret_type.get()
                        if selected_type == "Mnemonic seedphrase":
                            logger.debug("002 Mnemonic seedphrase selected")
                            _show_import_mnemonic()
                        elif selected_type == "Couple login/password":
                            logger.debug("003 Couple login/password selected")
                            _show_import_password()
                        else:
                            logger.warning("004 No secret type selected")
                            self.show("ERROR", "Please select a secret type", "Ok")
                    except Exception as e:
                        logger.error(f"005 Error in _on_next_clicked: {e}", exc_info=True)
                        raise UIElementError(f"006 Failed to process next button click: {e}") from e

                try:
                    logger.info("007 Creating initial selection frame for import secret")
                    self._create_frame()

                    self.header = self._create_an_header("Import secret", "import_icon_ws.png")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")

                    info_text_line_01 = "Seedkeeper allows you to import a BIP39 mnemonic phrase -aka seedphrase- or a "
                    info_label = self._create_label(info_text_line_01)
                    info_label.place(relx=0.05, rely=0.22, anchor="w")

                    info_text_line_02 = "login/password. Select the type of secret you want to import."
                    info_label = self._create_label(info_text_line_02)
                    info_label.place(relx=0.05, rely=0.27, anchor="w")

                    type_label = self._create_label("Type of secret:")
                    type_label.place(relx=0.05, rely=0.35, anchor="w")

                    self.secret_type, secret_type_menu = self.create_option_list(
                        ["Mnemonic seedphrase", "Login/password"],
                        default_value="Mnemonic seedphrase",
                        width=555,
                    )
                    secret_type_menu.place(relx=0.05, rely=0.40, anchor="w")

                    next_button = self._create_button("Next", command=_on_next_clicked)
                    next_button.place(relx=0.95, rely=0.95, anchor="se")

                    logger.log(SUCCESS, "008 Initial selection frame created successfully")
                except Exception as e:
                    logger.error(f"009 Error creating initial selection frame: {e}", exc_info=True)
                    raise FrameCreationError(f"010 Failed to create initial selection frame: {e}") from e

            @log_method
            def _show_import_mnemonic():
                try:
                    logger.info("001 Starting _show_import_mnemonic")

                    @log_method
                    def _generate_import_mnemonic_frame():
                        try:
                            logger.info("002 Creating import mnemonic frame")
                            self._create_frame()
                            logger.log(SUCCESS, "003 Import mnemonic frame created successfully")
                        except Exception as e:
                            logger.error(f"004 Error creating import mnemonic frame: {e}", exc_info=True)
                            raise FrameCreationError(f"005 Failed to create import mnemonic frame: {e}") from e

                    @log_method
                    def _generate_import_mnemonic_header():
                        try:
                            logger.info("006 Creating import mnemonic header")
                            header_text = "Import seedphrase"
                            self.header = self._create_an_header(header_text, "import_icon_ws.png")
                            self.header.place(relx=0.03, rely=0.08, anchor="nw")
                            logger.log(SUCCESS, "007 Import mnemonic header created successfully")
                        except Exception as e:
                            logger.error(f"008 Error creating import mnemonic header: {e}", exc_info=True)
                            raise UIElementError(f"009 Failed to create import mnemonic header: {e}") from e

                    @log_method
                    def _generate_import_mnemonic_widgets():
                        try:
                            logger.info("010 Creating import mnemonic content")

                            label = self._create_label("Label:")
                            label.place(relx=0.05, rely=0.20, anchor="nw")

                            label_name = self._create_entry()
                            label_name.place(relx=0.04, rely=0.25, anchor="nw")

                            self.radio_value = customtkinter.StringVar(value="12")
                            self.use_passphrase = customtkinter.BooleanVar(value=False)

                            radio_12 = customtkinter.CTkRadioButton(
                                self.current_frame,
                                text="12 words",
                                variable=self.radio_value,
                                value="12",
                                command=None
                            )
                            radio_12.place(relx=0.05, rely=0.35, anchor="w")

                            radio_24 = customtkinter.CTkRadioButton(
                                self.current_frame,
                                text="24 words",
                                variable=self.radio_value,
                                value="24",
                                command=None
                            )
                            radio_24.place(relx=0.2, rely=0.35, anchor="w")

                            self.mnemonic_textbox = customtkinter.CTkTextbox(self, corner_radius=20,
                                                                             bg_color="whitesmoke", fg_color=BG_BUTTON,
                                                                             border_color=BG_BUTTON, border_width=1,
                                                                             width=500, height=83,
                                                                             text_color="grey",
                                                                             font=customtkinter.CTkFont(family="Outfit",
                                                                                                        size=13,
                                                                                                        weight="normal"))
                            self.mnemonic_textbox.place(relx=0.28, rely=0.45, anchor="w")

                            passphrase_checkbox = customtkinter.CTkCheckBox(
                                self.current_frame,
                                text="Use passphrase",
                                variable=self.use_passphrase,
                                command=_toggle_passphrase_to_import
                            )
                            passphrase_checkbox.place(relx=0.05, rely=0.57, anchor="w")

                            self.passphrase_entry = customtkinter.CTkEntry(
                                self.current_frame,
                                width=300,
                                placeholder_text="Enter passphrase (optional)",
                                show="*"
                            )
                            self.passphrase_entry.place(relx=0.28, rely=0.57, anchor="w")
                            self.passphrase_entry.configure(state="disabled")

                            save_button = self._create_button("Save on card", command=_save_mnemonic_to_import_on_card)
                            save_button.place(relx=0.85, rely=0.93, anchor="center")

                            back_button = self._create_button("Back", command=self.show_view_import_secret)
                            back_button.place(relx=0.65, rely=0.93, anchor="center")

                            logger.log(SUCCESS, "011 Import mnemonic content created successfully")
                        except Exception as e:
                            logger.error(f"012 Error creating import mnemonic content: {e}", exc_info=True)
                            raise UIElementError(f"013 Failed to create import mnemonic content: {e}") from e

                    @log_method
                    def _toggle_passphrase_to_import():
                        try:
                            logger.info("014 Toggling passphrase")
                            if self.use_passphrase.get():
                                self.passphrase_entry.configure(state="normal")
                                logger.debug("015 Passphrase entry enabled")
                            else:
                                self.passphrase_entry.configure(state="disabled")
                                logger.debug("016 Passphrase entry disabled")
                        except Exception as e:
                            logger.error(f"017 Error toggling passphrase: {e}", exc_info=True)
                            raise UIElementError(f"018 Failed to toggle passphrase: {e}") from e

                    @log_method
                    def _save_mnemonic_to_import_on_card():
                        try:
                            logger.info("019 Saving mnemonic to card")
                            mnemonic = self.mnemonic_textbox.get("1.0", customtkinter.END).strip()
                            passphrase = self.passphrase_entry.get() if self.use_passphrase.get() else None
                            if mnemonic and passphrase:
                                self.controller.import_seed(mnemonic, passphrase)
                                logger.log(SUCCESS, "020 Mnemonic with passphrase saved to card successfully")
                            elif mnemonic and not passphrase:
                                self.controller.import_seed(mnemonic)
                                logger.log(SUCCESS, "021 Mnemonic without passphrase saved to card successfully")
                            else:
                                logger.warning("022 No mnemonic to save")
                                raise ValueError("023 No mnemonic generated")
                        except ValueError as e:
                            logger.error(f"024 Error saving mnemonic to card: {e}", exc_info=True)
                            raise UIElementError(f"025 Failed to save mnemonic to card: {e}") from e
                        except Exception as e:
                            logger.error(f"026 Error saving mnemonic to card: {e}", exc_info=True)
                            raise UIElementError(f"027 Failed to save mnemonic to card: {e}") from e

                    self._clear_current_frame()
                    _generate_import_mnemonic_frame()
                    _generate_import_mnemonic_header()
                    _generate_import_mnemonic_widgets()
                    self.create_seedkeeper_menu()
                    self.mnemonic_textbox_active = True
                    logger.log(SUCCESS, "028 _show_import_mnemonic completed successfully")
                except Exception as e:
                    logger.error(f"029 Unexpected error in _show_import_mnemonic: {e}", exc_info=True)
                    raise ViewError(f"030 Failed to show import mnemonic view: {e}") from e

            @log_method
            def _show_import_password():
                try:
                    logger.info("041 Starting _show_import_password method")

                    @log_method
                    def _generate_import_password_frame():
                        try:
                            logger.info("042 Creating import login/password frame")
                            self._create_frame()
                            logger.log(SUCCESS, "043 Import login/password frame created successfully")
                        except Exception as e:
                            logger.error(f"044 Error creating import login/password frame: {e}", exc_info=True)
                            raise FrameCreationError(f"045 Failed to create import login/password frame: {e}") from e

                    @log_method
                    def _generate_import_password_header():
                        try:
                            logger.info("046 Creating import login/password header")
                            header_text = "Import couple login/password"
                            self.header = self._create_an_header(header_text, "import_icon_ws.png")
                            self.header.place(relx=0.03, rely=0.08, anchor="nw")
                            logger.log(SUCCESS, "047 Import login/password header created successfully")
                        except Exception as e:
                            logger.error(f"048 Error creating import login/password header: {e}", exc_info=True)
                            raise UIElementError(f"049 Failed to create import login/password header: {e}") from e

                    @log_method
                    def _generate_import_password_widgets():
                        try:
                            logger.info("050 Creating import login/password widgets")
                            # Label and entry creation
                            label = self._create_label("Label:")
                            label.place(relx=0.04, rely=0.20, anchor="nw")

                            label_name = self._create_entry()
                            label_name.place(relx=0.12, rely=0.195, anchor="nw")
                            label_name.configure(width=400)

                            login = self._create_label("Login:")
                            login.place(relx=0.04, rely=0.32, anchor="nw")

                            login_name = self._create_entry()
                            login_name.place(relx=0.12, rely=0.318, anchor="nw")
                            login_name.configure(width=400)

                            url = self._create_label("Url:")
                            url.place(relx=0.04, rely=0.44, anchor="nw")

                            url_name = self._create_entry()
                            url_name.place(relx=0.12, rely=0.438, anchor="nw")
                            url_name.configure(width=400)

                            logger.debug("051 Labels and entries created successfully")

                            password_label = self._create_label("Password to import:")
                            password_label.place(relx=0.04, rely=0.57, anchor="nw")

                            self.password_text_box = customtkinter.CTkTextbox(self, corner_radius=20,
                                                                              bg_color="whitesmoke", fg_color=BG_BUTTON,
                                                                              border_color=BG_BUTTON, border_width=1,
                                                                              width=500, height=83,
                                                                              text_color="grey",
                                                                              font=customtkinter.CTkFont(
                                                                                  family="Outfit",
                                                                                  size=13,
                                                                                  weight="normal"))
                            self.password_text_box.place(relx=0.28, rely=0.7, anchor="w")

                            save_button = self._create_button("Save on card", command=_save_password_to_import_on_card)
                            save_button.place(relx=0.85, rely=0.93, anchor="center")

                            back_button = self._create_button("Back",
                                                              command=self.show_view_import_secret)
                            back_button.place(relx=0.65, rely=0.93, anchor="center")

                            logger.log(SUCCESS, "052 Import login/password widgets created successfully")
                        except Exception as e:
                            logger.error(f"053 Error creating import login/password widgets: {e}", exc_info=True)
                            raise UIElementError(f"054 Failed to create import login/password widgets: {e}") from e

                    @log_method
                    def _save_password_to_import_on_card():
                        def _save_password_to_import_on_card():
                            try:
                                logger.info("055 Saving login/password to card")
                                password = self.password_text_box.get("1.0", customtkinter.END).strip()
                                if password:
                                    # TODO: Implement actual saving logic
                                    logger.log(SUCCESS, "056 Login/password saved to card successfully")
                                else:
                                    logger.warning("057 No password to save")
                                    raise ValueError("058 No password generated")
                            except ValueError as e:
                                logger.error(f"059 Error saving login/password to card: {e}", exc_info=True)
                                raise UIElementError(f"060 Failed to save login/password to card: {e}") from e
                            except Exception as e:
                                logger.error(f"061 Unexpected error saving login/password to card: {e}", exc_info=True)
                                raise UIElementError(f"062 Unexpected error saving login/password to card: {e}") from e

                    self._clear_current_frame()
                    _generate_import_password_frame()
                    _generate_import_password_header()
                    _generate_import_password_widgets()
                    self.create_seedkeeper_menu()
                    self.password_text_box_active = True

                    logger.log(SUCCESS, "063 _show_import_password completed successfully")
                except Exception as e:
                    logger.error(f"064 Unexpected error in _show_import_password: {e}", exc_info=True)
                    raise ViewError(f"065 Failed to show import login/password view: {e}") from e

            _create_import_secret_selection_frame()
            self.create_seedkeeper_menu()

            logger.log(SUCCESS, "066 Import secret view created successfully")
        except (FrameCreationError, UIElementError) as e:
            logger.error(f"067 Error in import_secret: {e}", exc_info=True)
            raise ViewError(f"068 Failed to create import secret view: {e}") from e
        except ViewError as ve:
            logger.error(f"069 View error in import_secret: {ve}", exc_info=True)
            self.show("ERROR", str(ve), "Ok")
        except Exception as e:
            logger.error(f"070 Unexpected error in import_secret: {e}", exc_info=True)
            raise ViewError(f"071 Unexpected error during import secret view creation: {e}")
        finally:
            logger.info("072 Exiting import_secret method")

    @log_method
    def view_logs_details(
            self,
            logs_details
    ):
        try:
            logger.info("001 Starting view_logs_details method")

            @log_method
            def _create_logs_frame():
                try:
                    logger.info("002 Creating logs frame")
                    self._create_frame()
                    logger.log(SUCCESS, "003 Logs frame created successfully")
                except Exception as e:
                    logger.error(f"004 Error creating logs frame: {e}", exc_info=True)
                    raise FrameCreationError(f"005 Failed to create logs frame: {e}") from e

            @log_method
            def _create_logs_header():
                try:
                    logger.info("006 Creating logs header")
                    self.header = self._create_an_header("Logs History", "secrets_icon_ws.png")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")
                    logger.log(SUCCESS, "007 Logs header created successfully")
                except Exception as e:
                    logger.error(f"008 Error creating logs header: {e}", exc_info=True)
                    raise UIElementError(f"009 Failed to create logs header: {e}") from e

            @log_method
            def _create_logs_table(logs_details):
                try:
                    logger.info("010 Creating logs table")

                    def _on_mouse_on_log(event, buttons):
                        for button in buttons:
                            button.configure(fg_color=HIGHLIGHT_COLOR, cursor="hand2")

                    def _on_mouse_out_log(event, buttons):
                        for button in buttons:
                            button.configure(fg_color=button.default_color)

                    label_text = self._create_label(text="Find what had been done in your Seedkeeper card:")
                    label_text.place(relx=0.05, rely=0.25, anchor="w")

                    headers = ['Operation', 'ID1', 'ID2', 'Result']
                    header_widths = [300, 75, 75, 300]

                    header_frame = customtkinter.CTkFrame(self.current_frame, width=750, bg_color=DEFAULT_BG_COLOR,
                                                          corner_radius=0, fg_color=DEFAULT_BG_COLOR)
                    header_frame.place(relx=0.04, rely=0.3, relwidth=0.9, anchor="w")

                    for col, width in zip(headers, header_widths):
                        header_button = customtkinter.CTkButton(header_frame, text=col,
                                                                font=customtkinter.CTkFont(size=14, family='Outfit',
                                                                                           weight="bold"),
                                                                corner_radius=0, state='disabled', text_color='white',
                                                                fg_color=BG_MAIN_MENU, width=width)
                        header_button.pack(side="left", expand=True, fill="both")

                    logger.debug("011 Table headers created")

                    table_frame = self._create_scrollable_frame(self.current_frame, width=700, height=400, x=26, y=200)

                    for i, log in enumerate(logs_details):
                        row_frame = customtkinter.CTkFrame(table_frame, width=750, bg_color=DEFAULT_BG_COLOR,
                                                           fg_color=DEFAULT_BG_COLOR)
                        row_frame.pack(pady=2, fill="x")

                        fg_color = DEFAULT_BG_COLOR if i % 2 == 0 else BG_HOVER_BUTTON
                        text_color = TEXT_COLOR if i % 2 == 0 else BUTTON_TEXT_COLOR

                        buttons = []
                        values = [log['Operation'], log['ID1'], log['ID2'], log['Result']]
                        for value, width in zip(values, header_widths):
                            cell_button = customtkinter.CTkButton(row_frame, text=value, text_color=text_color,
                                                                  fg_color=fg_color,
                                                                  font=customtkinter.CTkFont(size=14, family='Outfit'),
                                                                  hover_color=HIGHLIGHT_COLOR, width=width,
                                                                  corner_radius=0)
                            cell_button.default_color = fg_color
                            cell_button.pack(side='left', expand=True, fill="both")
                            buttons.append(cell_button)

                        for button in buttons:
                            button.bind("<Enter>", lambda event, btns=buttons: _on_mouse_on_log(event, btns))
                            button.bind("<Leave>", lambda event, btns=buttons: _on_mouse_out_log(event, btns))

                        logger.debug(
                            f"012 Row created for log: {log['Operation'], log['ID1'], log['ID2'], log['Result']}")

                    logger.log(SUCCESS, "013 Logs table created successfully")
                except Exception as e:
                    logger.error(f"014 Error in _create_logs_table: {e}", exc_info=True)
                    raise UIElementError(f"015 Failed to create logs table: {e}") from e

            _create_logs_frame()
            _create_logs_header()
            _create_logs_table(logs_details)
            self.create_seedkeeper_menu()

            logger.log(SUCCESS, "016 view_logs_details completed successfully")
        except Exception as e:
            logger.error(f"017 Unexpected error in view_logs_details: {e}", exc_info=True)
            raise ViewError(f"018 Failed to display logs details: {e}")

    @log_method
    def view_help(self):
        try:
            logger.info("001 Starting view_help method")

            @log_method
            def _create_help_frame():
                try:
                    logger.info("002 Creating help frame")
                    self._create_frame()
                    logger.log(SUCCESS, "003 Help frame created successfully")
                except Exception as e:
                    logger.error(f"004 Error creating help frame: {e}", exc_info=True)
                    raise FrameCreationError(f"005 Failed to create help frame: {e}") from e

            @log_method
            def _create_help_header():
                try:
                    logger.info("006 Creating help header")
                    self.header = self._create_an_header("Help", "about_icon_ws.jpg")
                    self.header.place(relx=0.03, rely=0.08, anchor="nw")
                    logger.log(SUCCESS, "007 Help header created successfully")
                except Exception as e:
                    logger.error(f"008 Error creating help header: {e}", exc_info=True)
                    raise UIElementError(f"009 Failed to create help header: {e}") from e

            @log_method
            def _create_help_content():
                try:
                    logger.info("010 Creating help content")
                    text = self._create_label("Choose a language to find some help:")
                    text.place(relx=0.045, rely=0.20, anchor="w")

                    _create_text_box()
                    _create_language_radio_buttons()

                    logger.log(SUCCESS, "011 Help content created successfully")
                except Exception as e:
                    logger.error(f"012 Error creating help content: {e}", exc_info=True)
                    raise UIElementError(f"013 Failed to create help content: {e}") from e

            @log_method
            def _create_language_radio_buttons():
                self.language_radio_value = customtkinter.StringVar(value="English")  # Default to English
                radio_buttons = [
                    ("French", "Français", 0.045),
                    ("English", "English", 0.345),
                ]

                for text, value, rel_x in radio_buttons:
                    radio = customtkinter.CTkRadioButton(self.current_frame, text=text,
                                                         variable=self.language_radio_value, value=value,
                                                         font=customtkinter.CTkFont(family="Outfit", size=14,
                                                                                    weight="normal"),
                                                         bg_color="whitesmoke", fg_color="green", hover_color="green",
                                                         command=_update_radio_selection)
                    radio.place(relx=rel_x, rely=0.28, anchor="w")

                # Initial load of help text
                _update_radio_selection()

            @log_method
            def _create_text_box():
                self.text_box = customtkinter.CTkTextbox(self.current_frame, corner_radius=10,
                                                         bg_color='whitesmoke', fg_color=BG_BUTTON,
                                                         border_color=BG_BUTTON, border_width=0,
                                                         width=700, height=280,
                                                         text_color="grey",
                                                         font=customtkinter.CTkFont(family="Outfit", size=13,
                                                                                    weight="normal"))
                self.text_box.place(relx=0.04, rely=0.35, anchor="nw")

            @log_method
            def _load_help_texts():
                self.help_texts = {}
                languages = ["Français", "English"]
                for lang in languages:
                    file_path = os.path.join(self.pkg_dir, 'help', f"{lang}.txt")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            self.help_texts[lang] = f.read().strip()
                    except FileNotFoundError:
                        logger.error(f"014 Help file not found: {file_path}")
                        self.help_texts[lang] = f"Help text for {lang} is not available."
                    except Exception as e:
                        logger.error(f"015 Error loading help text for {lang}: {e}", exc_info=True)
                        self.help_texts[lang] = f"An error occurred while loading help text for {lang}."

            @log_method
            def _update_radio_selection():
                try:
                    selection = self.language_radio_value.get()
                    logger.info(f"016 Radio button selected: {selection}")

                    if selection in self.help_texts:
                        text_content = self.help_texts[selection]
                    else:
                        logger.warning(f"017 No help text found for language: {selection}")
                        text_content = "Help text not available for this language."

                    self._update_textbox(text_content)
                except Exception as e:
                    logger.error(f"018 Error updating radio selection: {e}", exc_info=True)
                    raise UIElementError(f"019 Failed to update radio selection: {e}") from e

            @log_method
            def _create_back_button():
                try:
                    logger.info("020 Creating back button")
                    self.back_button = self._create_button("Back", command=self.view_start_setup)
                    self.back_button.place(relx=0.8, rely=0.9, anchor="w")
                    logger.log(SUCCESS, "021 Back button created successfully")
                except Exception as e:
                    logger.error(f"022 Error creating back button: {e}", exc_info=True)
                    raise UIElementError(f"023 Failed to create back button: {e}") from e

            try:
                self._clear_current_frame()
                _load_help_texts()
                _create_help_frame()
                _create_help_header()
                _create_help_content()
                _create_back_button()
                self.create_seedkeeper_menu()

                logger.log(SUCCESS, "024 view_help completed successfully")
            except Exception as e:
                logger.error(f"025 Unexpected error in view_help: {e}", exc_info=True)
                raise ViewError(f"026 Failed to create help view: {e}") from e

        except Exception as e:
            logger.error(f"027 Unexpected error in view_help: {e}", exc_info=True)
            self.view.show("ERROR", "An unexpected error occurred while displaying help", "Ok", None,
                           "./pictures_db/help_icon.png")
