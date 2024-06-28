# DocList

## Models

- Secret
  - Id
  - Type
    - Mnemonic
    - login/password pair
  - Label

- Card
  - Type
  - Label
  - Authenticity
  - Logs
  - Firmware version

- UI
  - Components
    -Frame
    - Button
    - Label
    - Entry
    - Text box
    - Popup
    - List
    - Menu
    
  - Main Window
    - Welcome to View
    - First view displayed when the application opens
    
  - Main Layout
    - Left sidebar menu
    - Main display area on the right
    
  - Left Sidebar Menu
    - My Secrets (default)
    - Generate Secret
    - Import Secret
    - Settings
    - Help
    
  - Main Display Area
    - My Secrets (Home Frame)
      - Table with three columns: ID, Type, Label
        - Lists all secrets present on the card
        
      - Secret Details Frame
        - Displayed when a secret is selected from the list
        - Shows detailed information about the chosen secret
        
    - Generate Secret Frame
      - Interface for automatically generating a new secret
      
    - Import Secret Frame
      - Interface for manually importing secrets
      
    - Settings Frame
      - Displays information about the card
      - Allows card configuration actions not related to secrets
      
    - Help Frame
      - Contains help and support information for the user

## Functionality

- Secret management
  - List the secret
  - Provide secret details
  - Show secret
  - Import an existant secret
  - Generate a new secret
  - Erase secret


- Card management
  - Make a backup
  - Edit label
  - Change PIN
  - Display card authenticity
  - Initialize a Satochip card
  - Display the log usage historic

- Seedkeeper version management
  - Displaying or not some possibility or information depending on the seedkeeper version
  - Between V1 and V2 that contains different functionality added or deprecated