# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Implemented proper MVC architecture with Controller initialization in View
- Added loglevel parameter to Controller and View for better logging control
- Improved error handling and logging throughout the application

### Changed
- Refactored View class to properly initialize and use Controller
- Updated main script (seedkeeper_tool.py) to pass loglevel to View
- Modified Controller class to accept loglevel parameter
- Updated CardConnector initialization in Controller to use loglevel

### Fixed
- Resolved issue with missing smartcard module by adding pyscard to requirements
- Fixed unexpected keyword argument 'loglevel' error in Controller initialization

### Development
- Added instructions for switching to 64-bit Python for improved cryptographic performance

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
  - Added specific exception classes: `SeedkeeperError`, `ViewError`, `FrameError`, `UIElementError`, `InitializationError`, `ControllerError`, `CardError`, `ButtonCreationError`, `MainMenuError`
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