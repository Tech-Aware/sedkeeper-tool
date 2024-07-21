# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](git https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New functionality in `view.py` for displaying logs:
  - Implemented `view_logs_details` method with scrollable frame for better user experience
  - Added comprehensive error handling for log display
- New PIN change functionality in `view.py`:
  - Implemented `view_change_pin` method with full UI and error handling
- Enhanced `controller.py` with PIN change functionality:
  - Added `change_card_pin` method with robust error handling
  - Improved `get_logs` method to return formatted log data
- New exception types in `exceptions.py` for PIN-related errors:
  - Added `CardNotSuitableError`, `InvalidPinError`, `PinMismatchError`, and `PinChangeError`
- Improved error handling and logging throughout both `view.py` and `controller.py`
- New edit label functionality:
  - Implemented `view_edit_label` method in `view.py`
  - Added `edit_label` method in `controller.py`

### Changed
- Updated various "show" methods in `view.py` to use new view names (e.g., `show_view_my_secrets`)
- Refactored `view_change_pin` for better organization and error handling
- Enhanced error handling in `change_card_pin` method in `controller.py`

## [0.1.3] - 2024-07-20

### Added
- New functionality in `view.py` for displaying logs:
  - Implemented `view_logs_details` method with scrollable frame for better user experience
  - Added comprehensive error handling for log display
- New PIN change functionality in `view.py`:
  - Implemented `view_change_pin` method with full UI and error handling
- Enhanced `controller.py` with PIN change functionality:
  - Added `change_card_pin` method with robust error handling
  - Improved `get_logs` method to return formatted log data
- New exception types in `exceptions.py` for PIN-related errors:
  - Added `CardNotSuitableError`, `InvalidPinError`, `PinMismatchError`, and `PinChangeError`
- Improved error handling and logging throughout both `view.py` and `controller.py`

### Changed
- Updated various "show" methods in `view.py` to use new view names (e.g., `show_view_my_secrets`)

## [0.1.3] - 2024-07-19

### Added
- New functionality in `view.py` for importing secrets:
  - Implemented `view_import_secret` method for secret import selection
  - Added `_show_import_mnemonic` method for importing mnemonic secrets
  - Added `_show_import_password` method for importing login/password secrets
- Enhanced error handling in `view.py` with more specific exception types
- Improved method signatures in `view.py` with type hints
- Refactored existing methods in `view.py` for better organization
- Enhanced logging throughout `view.py`
- New `get_logs` method in `controller.py` for retrieving and formatting card logs
- Improved error handling in `card_setup_native_seed` method in `controller.py`
- Added section comments in `controller.py` for better code organization

### Changed
- Refactored method calls in `controller.py` for consistency (e.g., `start_setup` to `view_start_setup`)
- Ensured consistent use of `@log_method` decorator in `controller.py`

### Fixed
- Enhanced logging in `controller.py` with more detailed debug messages

## [0.1.2] - 2024-07-18

### Added
- New generate_secret functionality in the View class:
  - Added `generate_secret` method to create a new secret generation frame
  - Implemented radio buttons for selecting 12 or 24-word mnemonics
  - Added a text box for displaying the generated mnemonic
  - Created "Generate" and "Save to Card" buttons for mnemonic management
- New methods in Controller class:
  - `generate_random_seed`: Generates a random mnemonic of specified length
  - `import_seed`: Imports a seed to the card after validation
  - `card_setup_native_seed`: Sets up a native seed on the card
- Enhanced error handling:
  - Added new exception types in exceptions.py (e.g., SeedkeeperError as base exception)
- Improved logging:
  - Added more detailed logging throughout the application
- New picture for menu items
- New `exceptions.py` file for centralized exception handling:
  - Added specific exception classes: `ViewError`, `FrameError`, `UIElementError`, `InitializationError`, `ControllerError`, `CardError`, `ButtonCreationError`, `MainMenuError`, `AttributeInitializationError`, `ApplicationRestartError`, `FrameClearingError`, `MenuDeletionError`, `SecretRetrievalError`, `SecretProcessingError`, `WindowSetupError`, `CanvasCreationError`, `BackgroundPhotoError`, `LabelCreationError`, `EntryCreationError`, `HeaderCreationError`
- Comprehensive logging system with colored output in `log_config.py`
- Welcome screen with logo display in `View` class
- Main menu implementation with icon buttons in the `View` class
- New methods in `View` class:
  - `show_secrets`, `generate_secret`, `import_secret`, `show_settings`, `show_help`
  - `_create_welcome_background`, `_create_welcome_header`, `_create_welcome_labels`, `_create_welcome_button`
  - `create_button_for_main_menu_item` for creating main menu buttons with icons
- Integration with web browser to open the webshop
- `log_method` decorator for detailed function logging
- Constants for UI colors and paths in `view.py`
- New attributes in `View` class for tracking application state (e.g., `card_type`, `setup_done`, `is_seeded`, etc.)
- Implemented `_create_mnemonic_secret_frame` and `_create_generic_secret_frame` methods in `View` class
- Added `retrieve_details_about_secret_selected` method in `Controller` class with secret processing logic

### Changed
- Refactored View class:
  - Updated `show_generate_secret` method to use the new generate_secret functionality
  - Modified `_clear_current_frame` to handle mnemonic text box clearing
- Enhanced Controller class:
  - Improved PIN dialog method with better error handling and user feedback
- Updated error handling:
  - Refactored exception hierarchy for better organization
- Improved UI components:
  - Enhanced popup handling with `_make_popup_as_priority` method
- Refactored `menu item` to do well alignment and conditional behavior
- Refactored `View` class in `view.py` for improved structure and error handling:
  - Implemented `_initialize_attributes` method for better attribute management
  - Updated `__init__` method with more robust error handling
  - Improved `_setup_main_window` and `_declare_widgets` methods
- Updated `create_button` method to `create_welcome_button` for consistent styling and better error management
- Revised `_create_welcome_header` method to include logo display and styled text
- Improved initialization process in `seedkeeper_tool.py`
- Enhanced main menu with new layout and functionality:
  - Added icon support for menu items
  - Implemented state management for menu items based on card presence
- Updated error handling throughout the `View` class with specific exception types
- Modified `on_close_app` method to handle application closure more gracefully
- Refactored `update_status` method in `View` class:
  - Improved error handling with specific exceptions (`CardError`, `ViewError`)
  - Removed `self._handle_view_error()` calls in favor of raising specific exceptions
  - Enhanced logging for better debugging and error tracking
  - Streamlined status updates for connected, disconnected, and current status scenarios
- Improved error handling and logging in `Controller` class
- Updated `my_secrets` method to handle different secret types
- Refactored `_create_password_secret_frame` for better organization and error handling

### Fixed
- Resolved issues with popup window focus and priority
- Improved error messages and exception handling throughout the application
- Resolved issues with UI not displaying properly
- Corrected error handling in various UI element creation methods

### Security
- Enhanced PIN entry process with improved validation and error messaging

### Removed
- Removed outdated TODO comments
- Eliminated `self._handle_view_error()` calls from `update_status` method in favor of more specific exception handling

## [0.1.1] - 2024-07-17

### Added
- New generate_secret functionality in the View class:
  - Added `generate_secret` method to create a new secret generation frame
  - Implemented radio buttons for selecting 12 or 24-word mnemonics
  - Added a text box for displaying the generated mnemonic
  - Created "Generate" and "Save to Card" buttons for mnemonic management
- New methods in Controller class:
  - `generate_random_seed`: Generates a random mnemonic of specified length
  - `import_seed`: Imports a seed to the card after validation
  - `card_setup_native_seed`: Sets up a native seed on the card
- Enhanced error handling:
  - Added new exception types in exceptions.py (e.g., SeedkeeperError as base exception)
- Improved logging:
  - Added more detailed logging throughout the application
- New picture for menu items
- New `exceptions.py` file for centralized exception handling:
  - Added specific exception classes: `ViewError`, `FrameError`, `UIElementError`, `InitializationError`, `ControllerError`, `CardError`, `ButtonCreationError`, `MainMenuError`, `AttributeInitializationError`, `ApplicationRestartError`, `FrameClearingError`, `MenuDeletionError`, `SecretRetrievalError`, `SecretProcessingError`, `WindowSetupError`, `CanvasCreationError`, `BackgroundPhotoError`, `LabelCreationError`, `EntryCreationError`, `HeaderCreationError`
- Comprehensive logging system with colored output in `log_config.py`
- Welcome screen with logo display in `View` class
- Main menu implementation with icon buttons in the `View` class
- New methods in `View` class:
  - `show_secrets`, `generate_secret`, `import_secret`, `show_settings`, `show_help`
  - `_create_welcome_background`, `_create_welcome_header`, `_create_welcome_labels`, `_create_welcome_button`
  - `create_button_for_main_menu_item` for creating main menu buttons with icons
- Integration with web browser to open the webshop
- `log_method` decorator for detailed function logging
- Constants for UI colors and paths in `view.py`
- New attributes in `View` class for tracking application state (e.g., `card_type`, `setup_done`, `is_seeded`, etc.)
- Implemented `_create_mnemonic_secret_frame` and `_create_generic_secret_frame` methods in `View` class
- Added `retrieve_details_about_secret_selected` method in `Controller` class with secret processing logic

### Changed
- Refactored View class:
  - Updated `show_generate_secret` method to use the new generate_secret functionality
  - Modified `_clear_current_frame` to handle mnemonic text box clearing
- Enhanced Controller class:
  - Improved PIN dialog method with better error handling and user feedback
- Updated error handling:
  - Refactored exception hierarchy for better organization
- Improved UI components:
  - Enhanced popup handling with `_make_popup_as_priority` method
- Refactored `menu item` to do well alignment and conditional behavior
- Refactored `View` class in `view.py` for improved structure and error handling:
  - Implemented `_initialize_attributes` method for better attribute management
  - Updated `__init__` method with more robust error handling
  - Improved `_setup_main_window` and `_declare_widgets` methods
- Updated `create_button` method to `create_welcome_button` for consistent styling and better error management
- Revised `_create_welcome_header` method to include logo display and styled text
- Improved initialization process in `seedkeeper_tool.py`
- Enhanced main menu with new layout and functionality:
  - Added icon support for menu items
  - Implemented state management for menu items based on card presence
- Updated error handling throughout the `View` class with specific exception types
- Modified `on_close_app` method to handle application closure more gracefully
- Refactored `update_status` method in `View` class:
  - Improved error handling with specific exceptions (`CardError`, `ViewError`)
  - Removed `self._handle_view_error()` calls in favor of raising specific exceptions
  - Enhanced logging for better debugging and error tracking
  - Streamlined status updates for connected, disconnected, and current status scenarios
- Improved error handling and logging in `Controller` class
- Updated `my_secrets` method to handle different secret types
- Refactored `_create_password_secret_frame` for better organization and error handling

### Fixed
- Resolved issues with popup window focus and priority
- Improved error messages and exception handling throughout the application
- Resolved issues with UI not displaying properly
- Corrected error handling in various UI element creation methods

### Security
- Enhanced PIN entry process with improved validation and error messaging

### Removed
- Removed outdated TODO comments
- Eliminated `self._handle_view_error()` calls from `update_status` method in favor of more specific exception handling


## [0.1.0] - 2024-06-28

### Added
- Implemented a new View class in `view.py` with customtkinter for GUI
- Added colored logging functionality with a new SUCCESS log level
- Created a `setup_logging()` function for consistent log formatting
- Implemented `log_method` decorator for detailed function logging
- Added `InitializationError` for handling View initialization errors
- Implemented basic structure for secret and card management functionality
- Added `get_application_path()` function in `seedkeeper_tool.py`
- Implemented `check_cert_directory()` function for certificate validation
- Created `log_config.py` for centralized logging configuration
- New `exceptions.py` file for centralized exception handling:
  - Added specific exception classes: `ViewError`, `FrameError`, `UIElementError`, `InitializationError`, `ControllerError`, `CardError`, `ButtonCreationError`, `MainMenuError`
- Comprehensive logging system with colored output in `log_config.py`
- Welcome screen with logo display in `View` class
- Main menu implementation with icon buttons in the `View` class
- New methods in `View` class:
  - `show_secrets`, `generate_secret`, `import_secret`, `show_settings`, `show_help`
  - `_create_welcome_background`, `_create_welcome_header`, `_create_welcome_labels`, `_create_welcome_button`
  - `create_button_for_main_menu_item` for creating main menu buttons with icons
- Integration with web browser to open the webshop
- Constants for UI colors and paths in `view.py`
- New attributes in `View` class for tracking application state (e.g., `card_type`, `setup_done`, `is_seeded`, etc.)

### Changed
- Updated project structure with new files: `controller.py`, `view.py`, `requirements.txt`, `log_config.py`
- Refactored main application logic in `seedkeeper_tool.py`
- Enhanced logging system with colorama for better readability
- Refactor `menu item` to do well alignement
- Refactored `View` class in `view.py` for improved structure and error handling:
  - Implemented `_initialize_attributes` method for better attribute management
  - Updated `__init__` method with more robust error handling
  - Improved `_setup_main_window` and `_declare_widgets` methods
- Updated `create_button` method to `create_welcome_button` for consistent styling and better error management
- Revised `_create_welcome_header` method to include logo display and styled text
- Improved initialization process in `seedkeeper_tool.py`
- Enhanced main menu with new layout and functionality:
  - Added icon support for menu items
  - Implemented state management for menu items based on card presence
- Updated error handling throughout the `View` class with specific exception types
- Modified `on_close_app` method to handle application closure more gracefully

### Fixed
- Corrected cert directory checking logic in `seedkeeper_tool.py`
- Resolved issues with UI not displaying properly
- Corrected error handling in various UI element creation methods
- Improved error messages and logging throughout the application

### Removed
- Removed outdated TODO comments

## [0.0.0] - 2024-06-27

Initial release of the project structure and basic functionality.

### Added
- Basic project structure
- Changelog file
- README with initial project description and models