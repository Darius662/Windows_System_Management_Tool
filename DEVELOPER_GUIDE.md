# WinOpsTool - Developer Guide

This comprehensive guide is intended for developers who want to understand, maintain, or extend the WinOpsTool. It provides detailed information about the project structure, architecture patterns, key components, and development guidelines.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Architecture Patterns](#architecture-patterns)
4. [Panel Development](#panel-development)
5. [UI Component Development](#ui-component-development)
6. [Backend Development](#backend-development)
7. [Configuration System](#configuration-system)
8. [Testing Guidelines](#testing-guidelines)
9. [Common Development Tasks](#common-development-tasks)
10. [Troubleshooting](#troubleshooting)

## Project Overview

The WinOpsTool is a comprehensive GUI application for managing Windows systems locally and remotely. It consists of two main applications:

1. **WinOpsTool** (`main.py`): The primary application with multiple panels for different system management tasks.
2. **WinOpsInit** (`config_manager.py`): A tool for creating and managing configuration files that can be imported into the main application.

The project is built using PyQt6 for the UI and leverages various Windows APIs (through libraries like pywin32, psutil, etc.) for system management operations.

## Project Structure

```
Windows_System_Management_Tool/
├── main.py                     # Main application entry point
├── config_manager.py           # WinOpsInit entry point
├── build.py                    # Script for building executables
├── requirements.txt            # Python dependencies
├── README.md                   # User documentation
├── DEVELOPER_GUIDE.md          # This developer documentation
├── LICENSE                     # License information
├── config/                     # Configuration templates and defaults
├── logs/                       # Application logs
├── backups/                    # System backup files
└── src/                        # Source code
    ├── core/                   # Core functionality
    │   ├── config/             # Configuration handling
    │   ├── logger.py           # Logging setup
    │   ├── dependencies.py     # Dependency checking
    │   ├── privileges.py       # Admin privileges handling
    │   ├── config.py           # Global constants and settings
    │   └── config_schema.py    # Configuration schema definition
    ├── managers/               # Backend managers for system operations
    │   ├── environment_manager.py
    │   ├── registry_manager.py
    │   ├── users_manager.py
    │   ├── services_manager.py
    │   ├── firewall_manager.py
    │   ├── software_manager.py
    │   ├── permissions_manager.py
    │   ├── process_manager.py
    │   └── startup_manager.py
    └── ui/                     # User interface components
        ├── base/               # Base classes for UI components
        │   ├── base_panel.py   # Base panel class
        │   └── base_tree.py    # Base tree widget class
        ├── dialogs/            # Common dialog components
        │   ├── error_dialog.py
        │   └── confirmation_dialog.py
        ├── help/               # Help documentation
        │   └── help_window.py
        ├── main/               # Main window components
        │   ├── window.py       # Main application window
        │   └── help_handler.py # Help system handler
        ├── config_manager/     # WinOpsInit UI
        │   ├── main_window.py
        │   ├── config_handler.py
        │   └── tabs/           # Configuration tabs
        └── panels/             # Application panels
            ├── environment/    # Environment Variables panel
            ├── registry/       # Registry panel
            ├── users/          # Users & Groups panel
            ├── services/       # Services panel
            ├── firewall/       # Firewall panel
            │   ├── panel.py    # Main panel class
            │   ├── tree_widget.py # Firewall rules tree
            │   ├── dialogs.py  # Firewall-specific dialogs
            │   └── components/ # Modular UI components
            │       ├── add_button.py
            │       ├── edit_button.py
            │       ├── delete_button.py
            │       ├── refresh_button.py
            │       ├── button_bar.py
            │       └── rule_list.py
            ├── software/       # Software panel
            ├── permissions/    # Permissions panel
            └── applications/   # Applications panel
                ├── panel.py    # Main panel class with tabs
                ├── tree_widget.py # Base tree widget for processes/startup
                ├── dialogs.py  # Application-specific dialogs
                └── components/ # Modular UI components
                    ├── processes/ # Process-specific components
                    │   ├── end_process_button.py
                    │   ├── end_process_tree_button.py
                    │   ├── refresh_button.py
                    │   ├── button_bar.py
                    │   └── processes_list.py
                    └── startup/ # Startup-specific components
                        ├── add_button.py
                        ├── remove_button.py
                        ├── refresh_button.py
                        ├── button_bar.py
                        └── startup_list.py
```

## Architecture Patterns

The WinOpsTool follows several key architecture patterns to ensure maintainability, testability, and clean separation of concerns.

### 1. Model-View-Controller (MVC) Pattern

- **Model**: Backend managers in `src/managers/` handle data and system operations
- **View**: UI components in `src/ui/` display information and capture user input
- **Controller**: Panel classes coordinate between UI and backend managers

### 2. Modular Panel Architecture

Each panel follows a consistent structure:

1. **Backend Logic**
   - `manager.py`: Handles Windows API operations and business logic
   - Error handling and logging
   - Clean separation from UI

2. **UI Components**
   - `tree_widget.py`: Displays data in tree format
   - `dialogs.py`: Handles user input and validation
   - `components/`: Reusable UI elements (buttons, lists, etc.)

3. **Panel Integration**
   - `panel.py`: Coordinates UI and backend
   - Inherits from `BasePanel`
   - Manages tab structure if applicable

### 3. Signal-Slot Communication

- UI components emit signals when user actions occur
- Panel classes connect these signals to appropriate slots
- This decouples UI components from business logic

### 4. Inheritance Hierarchy

- `BasePanel`: Common functionality for all panels
- `BaseTree`: Common functionality for tree widgets
- Panel-specific classes inherit from these base classes

## Panel Development

### Panel Initialization Order

When developing or modifying panels, follow this initialization order:

1. Initialize required resources (managers, etc.)
2. Call `super().__init__()` which sets up UI and connections
3. Perform any post-initialization tasks like data loading

```python
def __init__(self, parent=None):
    # 1. Initialize resources
    self.manager = SomeManager()
    
    # 2. Call super().__init__() which calls setup_ui() and setup_connections()
    super().__init__(parent)
    
    # 3. Post-initialization tasks
    self.refresh_data()
```

### BasePanel Methods

When implementing a panel that inherits from `BasePanel`, you must implement:

1. `setup_ui()`: Create and arrange UI components
   - Use `self.add_widget()` and `self.add_layout()` instead of creating your own layouts
   - Make UI elements class members for better organization

2. `setup_connections()`: Connect signals to slots
   - Keep this separate from UI setup for better organization
   - Connect all signals here, not in `setup_ui()`

```python
def setup_ui(self):
    # Create UI components
    self.tree_widget = MyTreeWidget()
    self.button_bar = MyButtonBar()
    
    # Add to layout using BasePanel methods
    self.add_widget(self.tree_widget)
    self.add_widget(self.button_bar)

def setup_connections(self):
    # Connect signals to slots
    self.button_bar.refresh_clicked.connect(self.refresh_data)
    self.tree_widget.item_selected.connect(self.on_item_selected)
```

### Tabbed Panels

For panels with multiple tabs:

1. Create a `QTabWidget` in the panel's `setup_ui()` method
2. Create separate tab classes for each tab
3. Add tabs to the tab widget

```python
def setup_ui(self):
    self.tab_widget = QTabWidget()
    self.add_widget(self.tab_widget)
    
    self.tab1 = Tab1Class(self.manager)
    self.tab2 = Tab2Class(self.manager)
    
    self.tab_widget.addTab(self.tab1, "Tab 1")
    self.tab_widget.addTab(self.tab2, "Tab 2")
```

## UI Component Development

### Modular Component Structure

For complex panels, create modular components in a `components/` directory:

1. **Button Components**: Single-responsibility button classes
   - Emit specific signals when clicked
   - Handle their own enabled/disabled state

2. **Button Bars**: Group related buttons
   - Aggregate button components
   - Forward signals from buttons
   - Handle layout

3. **List Components**: Combine tree views and button bars
   - Manage selection state
   - Handle refresh operations
   - Emit signals for operations

### Signal-Slot Best Practices

1. **Contextual Signals**: Include relevant data in signals
   ```python
   # Instead of:
   clicked = pyqtSignal()
   
   # Use:
   clicked_with_selection = pyqtSignal(dict)  # Pass selected item data
   ```

2. **Signal Forwarding**: In composite components, forward signals from child components
   ```python
   def __init__(self):
       self.button.clicked.connect(self.on_button_clicked)
       
   def on_button_clicked(self):
       self.button_clicked.emit()  # Forward the signal
   ```

3. **Signal Documentation**: Document signals in class docstrings
   ```python
   class MyButton(QPushButton):
       """Custom button for X operation.
       
       Signals:
           clicked_with_data(dict): Emitted when button is clicked with selected data
       """
   ```

## Backend Development

### Manager Classes

Manager classes handle all backend operations and should:

1. **Encapsulate Windows API Calls**: Hide complexity of system operations
2. **Handle Errors**: Catch and log exceptions, return meaningful error messages
3. **Be Stateless When Possible**: Avoid storing state that could become stale
4. **Use Logging**: Log operations and errors for debugging

```python
class SomeManager:
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        
    def perform_operation(self, param):
        try:
            # Perform Windows API operations
            result = some_api_call(param)
            self.logger.info(f"Operation succeeded with param: {param}")
            return result
        except Exception as e:
            self.logger.error(f"Operation failed: {str(e)}")
            raise OperationError(f"Failed to perform operation: {str(e)}")
```

### Error Handling

1. **Custom Exceptions**: Define custom exceptions for specific error cases
2. **Informative Messages**: Include details about what went wrong
3. **Logging**: Log errors with stack traces for debugging
4. **User Feedback**: Convert exceptions to user-friendly messages

## Configuration System

### Configuration Schema

The configuration schema is defined in `src/core/config_schema.py` and follows a structured format:

```python
CONFIG_SCHEMA = {
    "section_name": {
        "subsection": {
            "type": "type_name",
            "description": "Description of this section",
            "items": {
                # Schema for items if this is a list
            }
        }
    }
}
```

### Configuration Validation

When adding new configuration options:

1. Update the schema in `src/core/config_schema.py`
2. Add validation in `src/core/config/validation.py`
3. Update default configuration in `src/core/config/defaults.py`
4. Update the WinOpsInit UI if needed

## Testing Guidelines

### Unit Testing

1. Create tests in a `tests/` directory mirroring the source structure
2. Mock Windows API calls to avoid system dependencies
3. Test each manager method independently
4. Test UI components with Qt Test framework

### Integration Testing

1. Test interactions between managers and UI components
2. Use test configurations to verify configuration loading/saving
3. Test error handling and edge cases

## Common Development Tasks

### Adding a New Panel

1. Create a new directory under `src/ui/panels/`
2. Create manager class in `src/managers/`
3. Create panel class inheriting from `BasePanel`
4. Add panel to main window in `src/ui/main/window.py`
5. Add configuration schema in `src/core/config_schema.py`
6. Add configuration tab in WinOpsInit if needed

### Adding a New Button Component

1. Create a new file in the panel's `components/` directory
2. Inherit from `QPushButton`
3. Define signals for button actions
4. Implement enable/disable logic
5. Add to a button bar component

### Modifying Configuration Schema

1. Update `src/core/config_schema.py`
2. Update validation in `src/core/config/validation.py`
3. Update default configuration in `src/core/config/defaults.py`
4. Update WinOpsInit UI if needed

## Troubleshooting

### Common Issues

1. **Panel Not Displaying**: Check initialization order and BasePanel usage
2. **Signals Not Working**: Verify connections in `setup_connections()`
3. **Configuration Not Loading**: Check schema and validation
4. **Windows API Errors**: Check for admin privileges and API availability
5. **Logging Issues**: Check log level settings in the Settings dialog or directly in `src/core/logging_config.py`

### Debugging Tips

1. **Logging**: Check logs in the `logs/` directory
2. **Print Statements**: Use temporary print statements for quick debugging
3. **Qt Debug Tools**: Use Qt's debug tools for UI issues
4. **Exception Handling**: Add try/except blocks to narrow down issues

---

## Specific Panel Documentation

### Applications Panel

The Applications Panel is a tabbed interface that allows users to manage running processes and startup items.

#### Structure

```
applications/
├── panel.py           # Main panel class with ProcessesTab and StartupTab
├── tree_widget.py     # Base tree widget for processes/startup
├── dialogs.py         # Application-specific dialogs
└── components/        # Modular UI components
    ├── processes/     # Process-specific components
    │   ├── end_process_button.py
    │   ├── end_process_tree_button.py
    │   ├── refresh_button.py
    │   ├── button_bar.py
    │   └── processes_list.py
    └── startup/       # Startup-specific components
        ├── add_button.py
        ├── remove_button.py
        ├── refresh_button.py
        ├── button_bar.py
        └── startup_list.py
```

#### Key Components

1. **ProcessesList**: Combines ProcessesTree and ButtonBar
   - Manages process selection state
   - Handles refresh timer for auto-updates
   - Emits signals for process operations

2. **StartupList**: Combines StartupTree and ButtonBar
   - Manages startup item selection
   - Handles add/remove operations
   - Emits signals for startup operations

3. **Button Components**: Single-responsibility buttons
   - `EndProcessButton`: Ends selected process
   - `EndProcessTreeButton`: Ends process tree
   - `RefreshButton`: Refreshes process/startup list
   - `AddButton`: Adds startup item
   - `RemoveButton`: Removes startup item

#### Signal Flow

1. User selects a process in ProcessesTree
2. ProcessesTree emits selection_changed signal
3. ProcessesList receives signal and updates button states
4. User clicks EndProcessButton
5. EndProcessButton emits clicked_with_selection signal with process data
6. ProcessesList receives signal and calls process_manager.end_process()
7. ProcessesList refreshes the process list

### Firewall Panel

The Firewall Panel is a tabbed interface that allows users to manage inbound and outbound firewall rules.

#### Structure

```
firewall/
├── panel.py           # Main panel class with tabs
├── tree_widget.py     # Firewall rules tree widget
├── dialogs.py         # Rule editing dialogs
└── components/        # Modular UI components
    ├── add_button.py
    ├── edit_button.py
    ├── delete_button.py
    ├── refresh_button.py
    ├── button_bar.py
    └── rule_list.py
```

#### Key Components

1. **RuleList**: Combines RuleTree and ButtonBar
   - Manages rule selection state
   - Handles rule operations (add, edit, delete)
   - Filters rules by direction (inbound/outbound)

2. **Button Components**: Single-responsibility buttons
   - `AddButton`: Adds new firewall rule
   - `EditButton`: Edits selected rule
   - `DeleteButton`: Deletes selected rule
   - `RefreshButton`: Refreshes rule list

---

This developer guide should be maintained and updated as the project evolves. For questions or clarifications, please contact the project maintainers.

Last updated: July 16, 2025
