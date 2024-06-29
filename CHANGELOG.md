# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New `exceptions.py` file for centralized exception handling
- Comprehensive logging system with colored output in `log_config.py`
- Welcome screen with logo display in `View` class

### Changed
- Refactored `View` class in `view.py` for improved structure and error handling
- Updated `create_button` method for consistent styling and better error management
- Revised `_create_welcome_header` method to include logo display and styled text
- Improved initialization process in `seedkeeper_tool.py`

### Fixed
- Resolved issues with UI not displaying properly
- Corrected error handling in various UI element creation methods

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

### Changed
- Updated project structure with new files: `controller.py`, `view.py`, `requirements.txt`, `log_config.py`
- Refactored main application logic in `seedkeeper_tool.py`
- Enhanced logging system with colorama for better readability

### Fixed
- Corrected cert directory checking logic in `seedkeeper_tool.py`

## [0.0.0] - 2024-06-27

Initial release of the project structure and basic functionality.

### Added
- Basic project structure
- Changelog file
- README with initial project description and models