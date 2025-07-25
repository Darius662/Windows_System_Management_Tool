"""Operations for environment variables."""
from src.core.logger import setup_logger

class VariableOperations:
    """Handles operations for environment variables."""
    
    def __init__(self, panel):
        """Initialize variable operations.
        
        Args:
            panel: Parent panel (EnvironmentPanel)
        """
        self.panel = panel
        self.logger = setup_logger(self.__class__.__name__)
        
        # Store panel reference only - we'll access other components as properties
        
    # Properties to access panel components safely
    @property
    def manager(self):
        return self.panel.manager
        
    @property
    def variables_view(self):
        return self.panel.variables_view
        
    @property
    def dialog_factory(self):
        return self.panel.dialog_factory
    
    def add_variable(self):
        """Add new environment variable."""
        dialog = self.dialog_factory.create_add_dialog()
        if dialog.exec():
            name, value, var_type = dialog.get_variable()
            try:
                success = False
                if var_type == "System":
                    success = self.manager.set_system_variable(name, value)
                else:
                    success = self.manager.set_user_variable(name, value)
                    
                if success:
                    self.variables_view.add_variable(name, value, var_type)
                    self.logger.info(f"Added {var_type} variable: {name}={value}")
                else:
                    raise Exception("Failed to set variable")
            except Exception as e:
                self.logger.error(f"Failed to add variable: {str(e)}")
                self.dialog_factory.show_error(f"Failed to add variable: {str(e)}")
                
    def edit_variable(self):
        """Edit selected environment variable."""
        variable = self.variables_view.get_selected_variable()
        if not variable:
            self.dialog_factory.show_warning(
                "No Selection",
                "Please select a variable to edit."
            )
            return
            
        name, value, var_type = variable
        dialog = self.dialog_factory.create_add_dialog(name, value, var_type)
        
        if dialog.exec():
            new_name, new_value, new_type = dialog.get_variable()
            try:
                success = False
                # Delete old variable if name changed
                if name != new_name:
                    if var_type == "System":
                        success = self.manager.delete_system_variable(name)
                    else:
                        success = self.manager.delete_user_variable(name)
                    if not success:
                        raise Exception(f"Failed to delete old variable {name}")
                        
                # Set new variable
                if new_type == "System":
                    success = self.manager.set_system_variable(new_name, new_value)
                else:
                    success = self.manager.set_user_variable(new_name, new_value)
                    
                if success:
                    self.variables_view.update_variable(new_name, new_value, new_type)
                    self.logger.info(
                        f"Updated variable: {name}={value} -> {new_name}={new_value}"
                    )
                else:
                    raise Exception("Failed to set new variable value")
            except Exception as e:
                self.logger.error(f"Failed to update variable: {str(e)}")
                self.dialog_factory.show_error(f"Failed to update variable: {str(e)}")
                
    def delete_variable(self):
        """Delete selected environment variable."""
        variable = self.variables_view.get_selected_variable()
        if not variable:
            self.dialog_factory.show_warning(
                "No Selection",
                "Please select a variable to delete."
            )
            return
            
        name, _, var_type = variable
        
        if self.dialog_factory.confirm_delete(var_type, name):
            try:
                success = False
                if var_type == "System":
                    success = self.manager.delete_system_variable(name)
                else:
                    success = self.manager.delete_user_variable(name)
                    
                if success:
                    # Refresh the variables to reflect the deletion
                    self.refresh_variables()
                    self.logger.info(f"Deleted {var_type} variable: {name}")
                else:
                    raise Exception("Failed to delete variable")
            except Exception as e:
                self.logger.error(f"Failed to delete variable: {str(e)}")
                self.dialog_factory.show_error(f"Failed to delete variable: {str(e)}")
                
    def refresh_variables(self):
        """Refresh environment variables list."""
        self.variables_view.clear_variables()
        
        # Add user variables
        for name, value in self.manager.get_user_variables().items():
            self.variables_view.add_variable(name, value, "User")
            
        # Add system variables
        for name, value in self.manager.get_system_variables().items():
            self.variables_view.add_variable(name, value, "System")
