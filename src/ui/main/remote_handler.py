"""Remote management handler for the main window."""
from PyQt6.QtWidgets import QMessageBox
from src.core.logger import setup_logger
from src.core.remote.manager import RemoteManager
from src.ui.dialogs.connection_dialog import ConnectionDialog
from src.ui.dialogs.file_transfer_dialog import FileTransferDialog

class RemoteHandler:
    """Handles remote management functionality."""
    
    def __init__(self, main_window):
        """Initialize remote handler.
        
        Args:
            main_window: MainWindow instance
        """
        self.main_window = main_window
        self.logger = setup_logger(self.__class__.__name__)
        self.remote_manager = RemoteManager()
        self.file_transfer_dialog = None
        
    def connect(self):
        """Show connection dialog and establish remote connection."""
        dialog = ConnectionDialog(self.remote_manager, self.main_window)
        if dialog.exec():
            # Connection is handled by the dialog itself
            if self.remote_manager.is_connected():
                self.main_window.status_handler.set_connection_status(True, self.remote_manager.connection.host)
                self.main_window.status_handler.set_status(f"Connected to {self.remote_manager.connection.host}")
                self.enable_remote_features()

                
    def disconnect(self):
        """Disconnect from remote system."""
        try:
            self.remote_manager.disconnect()
            self.main_window.status_handler.set_connection_status(False)
            self.main_window.status_handler.set_status("Disconnected")
            self.disable_remote_features()
        except Exception as e:
            self.logger.error(f"Error during disconnect: {str(e)}")
            QMessageBox.warning(
                self.main_window,
                "Disconnect Error",
                f"Error during disconnect: {str(e)}"
            )
            
    def show_file_transfer(self):
        """Show file transfer dialog."""
        if not self.remote_manager.is_connected():
            QMessageBox.warning(
                self.main_window,
                "Not Connected",
                "Please connect to a remote system first."
            )
            return
            
        if not self.file_transfer_dialog:
            self.file_transfer_dialog = FileTransferDialog(
                self.main_window,
                self.remote_manager
            )
        self.file_transfer_dialog.show()
        
    def enable_remote_features(self):
        """Enable remote-specific features."""
        # Update UI elements that depend on remote connection
        self.main_window.update_remote_state(True)
        
    def disable_remote_features(self):
        """Disable remote-specific features."""
        # Update UI elements that depend on remote connection
        self.main_window.update_remote_state(False)
        
    def is_connected(self):
        """Check if connected to remote system."""
        return self.remote_manager.is_connected()
        
    def refresh_connections(self):
        """Refresh the list of saved connections."""
        return self.remote_manager.refresh_connections()
        
    def get_connections(self):
        """Get list of saved connections.
        
        Returns:
            list: List of RemoteConnection objects
        """
        return self.remote_manager.get_connections()
        
    def add_connection(self, name, hostname, username, password):
        """Add a new remote connection.
        
        Args:
            name: Display name for the connection
            hostname: Remote hostname or IP
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            bool: True if connection was added successfully
        """
        return self.remote_manager.add_connection(name, hostname, username, password)
        
    def remove_connection(self, name):
        """Remove a saved connection.
        
        Args:
            name: Name of connection to remove
            
        Returns:
            bool: True if connection was removed successfully
        """
        return self.remote_manager.remove_connection(name)
