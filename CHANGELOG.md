# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **New secret types**:
  - Support for **Free Text** and **Wallet Descriptor** secrets.
  - Implemented `decode_free_text` and `import_free_text` methods in `controller.py`.
  - Added `_create_free_text_secret_frame` and `_show_import_free_text` in `view.py`.
  - Implemented `decode_wallet_descriptor` and `import_wallet_descriptor` methods in `controller.py`.
  - Added `_create_wallet_descriptor_secret_frame` and `_show_import_wallet_descriptor` in `view.py`.

- **Enhanced logging system**:
  - Added `list_all_loggers()` function in `log_config.py` for comprehensive logger information.
  - Implemented specific colors for `CardConnector` logs in `ColoredFormatter`.
  - Updated `setup_logging()` to prevent duplicate handlers.
  - Removed redundant configurations to avoid log conflicts.
  - Improved flexibility and debugging capabilities of the logging system.

### Changed

- Updated secret type handling in `view_my_secrets` and `import_secret` views to include Free Text and Wallet Descriptor types.
- Enhanced error handling and logging for Free Text and Wallet Descriptor operations.
- Refactored logging configuration for better management of root and module-specific loggers.

### Fixed

- Corrected mnemonic secret frame display logic in `show_secret_details` in `view.py` to ensure proper frame selection based on secret type and subtype.

## [0.3.0] - 2024-09-25

### Added

- **Support for Free Text secret type**:
  - Implemented `decode_free_text` method in `controller.py` to decrypt and parse Free Text secrets.
  - Added `import_free_text` method for importing Free Text secrets.
  - Updated `dic_type` dictionary to include 'Free text' (0xC0) and 'Wallet descriptor' (0xC1).
  - Enhanced error handling and logging for Free Text operations.
  - In `view.py`, added `_create_free_text_secret_frame` to display Free Text secrets.
  - Implemented `_show_import_free_text` for importing Free Text secrets.

- **Wallet Descriptor handling**:
  - Implemented `decode_wallet_descriptor` and `import_wallet_descriptor` methods in `controller.py`.
  - In `view.py`, added `_create_wallet_descriptor_secret_frame` to display wallet descriptor details.
  - Implemented `_show_import_wallet_descriptor` to handle wallet descriptor import UI.

- **Enhanced logging system**:
  - Added `list_all_loggers()` function in `log_config.py` for comprehensive logger information.
  - Implemented specific color for `CardConnector` logs in `ColoredFormatter`.
  - Updated `setup_logging()` to prevent duplicate handlers.
  - Removed redundant configurations to avoid log conflicts.
  - Improved logging system flexibility and debugging capabilities.

### Changed

- Updated secret type handling in `view_my_secrets` and `import_secret` views to include Free Text and Wallet Descriptor types.
- Refactored logging configuration in `log_config.py`:
  - Enhanced log configuration and added debug utilities.
  - Improved handling of root and `pysatochip` loggers.
  - Prevented log duplication by managing logger propagation.
  - Added test logs to verify logger configuration.

### Fixed

- Corrected mnemonic secret frame display logic in `show_secret_details` in `view.py`:
  - Ensured proper frame selection based on secret type and subtype.

## [0.2.0] - 2024-08-28

### Added

- **About view functionality** in `view.py`:
  - Implemented `view_about` method to display application and card information.
  - Added `show_view_about` method to handle About view initialization.
  - Included application version, card label, and other details.

- **Card label retrieval** in `controller.py`:
  - Implemented `get_card_label_infos` method to retrieve card label information.
  - Enhanced error handling in `edit_label` method.
  - Improved logging and error messages across multiple methods.

- **Help functionality** in `view.py`:
  - Added `view_help` method with language selection (English/French).
  - Implemented `_set_package_directory` method for cross-platform path handling.
  - Loaded and displayed help texts from files.

- **Secret import functionality** in `view.py`:
  - Added `view_import_secret` method for secret import selection.
  - Implemented `_show_import_mnemonic` and `_show_import_password` functions.
  - Created UI elements for mnemonic and password import.
  - Enhanced error handling and logging throughout import process.

- **Logs display functionality** in `view.py`:
  - Added `view_logs_details` method with scrollable frame for better user experience.
  - Integrated with controller to fetch and display logs.

- **PIN change functionality**:
  - Implemented `view_change_pin` method in `view.py` with comprehensive UI and error handling.
  - Added `change_card_pin` method in `controller.py` with robust error handling.
  - Introduced new exception types in `exceptions.py` for PIN-related errors:
    - `CardNotSuitableError`, `InvalidPinError`, `PinMismatchError`, `PinChangeError`.

### Changed

- Updated PIN dialog in `view.py` to handle both verification and initial PIN setup.
- Refactored "Couple login/password" to "Login/password" for consistency in `view.py`:
  - Applied this change to both "Generate" and "Import" screens.
- Enhanced error handling and logging throughout `view.py` and `controller.py`.
- Updated `_satochip_utils_lateral_menu` in `view.py` to include About button.
- Refactored `update_status` method in `view.py` for improved clarity and error management.
- Refactored method calls in `controller.py` for consistency.
- Ensured consistent use of `@log_method` decorator in `controller.py`.

### Fixed

- Improved error handling in `edit_label` method of `controller.py`.
- Enhanced logging in `controller.py` with more detailed debug messages.
- Fixed frame clearing and widget destruction issues in `view.py`.

## [0.1.5] - 2024-07-23

### Added

- **New PIN setup functionality** in `controller.py`:
  - Implemented `card_setup_native_pin` method for initial PIN setup.
  - Enhanced security in PIN and passphrase management.
- **Enhanced `get_passphrase` method** in `view.py`:
  - Added support for both PIN setup and verification scenarios.
  - Implemented dynamic popup title and label text based on setup status.
  - Improved error handling and logging.

### Changed

- Modified PIN dialog in `controller.py` to handle both verification and setup.
- Updated secret type selection in `view.py`:
  - Changed "Couple login/password" to "Login/password" in dropdown options.
  - Applied this change to both "Generate" and "Import" screens.

### Improved

- Enhanced error handling and logging in PIN management functions.
- Improved overall user experience during PIN setup and verification processes.
- Reorganized imports and improved code structure.

## [0.1.4] - 2024-07-22

### Added

- **Import secrets functionality** in `view.py`:
  - Implemented `view_import_secret` method for secret import selection.
  - Added `_show_import_mnemonic` and `_show_import_password` methods.
  - Enhanced error handling with specific exception types.
  - Improved method signatures with type hints.
  - Refactored existing methods for better organization.
  - Enhanced logging throughout the file.

- **Log retrieval in `controller.py`**:
  - Implemented `get_logs` method for retrieving and formatting card logs.
  - Improved error handling in `card_setup_native_seed` method.
  - Added section comments for better code organization.

### Changed

- Refactored method calls in `controller.py` for consistency.
- Ensured consistent use of `@log_method` decorator in `controller.py`.
- Updated various "show" methods in `view.py` to use new view names.

### Fixed

- Enhanced logging in `controller.py` with more detailed debug messages.
- Improved error handling and logging throughout both `view.py` and `controller.py`.

## [0.1.3] - 2024-07-21

### Added

- **Logs display functionality** in `view.py`:
  - Implemented `view_logs_details` method with scrollable frame.
  - Added comprehensive error handling for log display.

- **PIN change functionality** in `view.py`:
  - Implemented `view_change_pin` method with full UI and error handling.
  - Enhanced error handling and logging throughout the file.

- **New exception types** in `exceptions.py` for PIN-related errors:
  - `CardNotSuitableError`, `InvalidPinError`, `PinMismatchError`, `PinChangeError`.

### Changed

- Updated error handling and logging throughout `view.py` and `controller.py`.
- Improved code organization and clarity.

## [0.1.2] - 2024-07-18

### Added

- **Secret generation enhancements**:
  - Implemented `generate_secret` method in `view.py` for advanced secret generation.
  - Added selection between mnemonic and login/password generation.
  - Implemented mnemonic seed phrase generation with customizable length and passphrase option.
  - Created login/password generation with customizable length and character types.
  - Added utility method for creating bold text.

- **Controller methods for seed management**:
  - `generate_random_seed`: Generates a random mnemonic of specified length.
  - `import_seed`: Imports a seed to the card after validation.
  - `card_setup_native_seed`: Sets up a native seed on the card.

- **Enhanced error handling**:
  - Added new exception types in `exceptions.py`.
  - Improved logging throughout the application.

### Changed

- Refactored `generate_secret` functionality in `view.py` for better modularity.
- Enhanced UI with sliders, checkboxes, and radio buttons for secret customization.
- Improved error handling and user feedback in `controller.py`.

### Fixed

- Resolved issues with popup window focus and priority.
- Improved error messages and exception handling throughout the application.

## [0.1.1] - 2024-07-17

### Added

- **Refactored `View` class in `view.py`**:
  - Restructured methods for better organization.
  - Added explicit return type annotations to methods.
  - Enhanced documentation of method return values.
  - Improved error handling and logging.

- **Logging enhancements**:
  - Added distinct entry and exit log formats in `log_method` decorator.
  - Improved exception logging with colored output in `log_method`.
  - Updated `ColoredFormatter` to use `CRITICAL` level instead of `EXCEPTION`.

### Changed

- Enhanced secret management UI in `view.py`:
  - Added "Delete secret" button to password and mnemonic secret frames.
  - Improved layout of password secret frame.
  - Adjusted positioning of UI elements for better alignment.

### Fixed

- Corrected error handling in various UI element creation methods.
- Improved error messages and logging throughout the application.

## [0.1.0] - 2024-06-28

### Added

- **Initial release with basic functionality**:
  - Implemented a new `View` class in `view.py` with customtkinter for GUI.
  - Added colored logging functionality with a new `SUCCESS` log level.
  - Created a `setup_logging()` function for consistent log formatting.
  - Implemented `log_method` decorator for detailed function logging.
  - Added `InitializationError` for handling `View` initialization errors.
  - Implemented basic structure for secret and card management functionality.

- **Welcome screen and main menu**:
  - Welcome screen with logo display in `View` class.
  - Main menu implementation with icon buttons in the `View` class.
  - New methods in `View` class for navigation and UI setup.

### Changed

- Updated project structure with new files: `controller.py`, `view.py`, `log_config.py`.
- Refactored main application logic in `seedkeeper_tool.py`.
- Enhanced logging system with `colorama` for better readability.
- Improved initialization process in `seedkeeper_tool.py`.
- Enhanced main menu with new layout and functionality.

### Fixed

- Corrected certificate directory checking logic in `seedkeeper_tool.py`.
- Resolved issues with UI not displaying properly.
- Corrected error handling in various UI element creation methods.

## [0.0.0] - 2024-06-27

Initial release of the project structure and basic functionality.

### Added
- Basic project structure
- Changelog file
- README with initial project description and models