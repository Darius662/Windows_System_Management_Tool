"""Tree widgets for Windows applications."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from datetime import datetime

class ProcessesTree(QTreeWidget):
    """Tree widget for displaying running processes."""
    
    def __init__(self, parent=None):
        """Initialize processes tree.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget UI."""
        # Set up columns
        self.setHeaderLabels([
            "Name",
            "PID",
            "Status",
            "CPU %",
            "Memory",
            "User",
            "Started"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 200)  # Name
        self.setColumnWidth(1, 80)   # PID
        self.setColumnWidth(2, 80)   # Status
        self.setColumnWidth(3, 80)   # CPU %
        self.setColumnWidth(4, 100)  # Memory
        self.setColumnWidth(5, 150)  # User
        self.setColumnWidth(6, 150)  # Started
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_process(self, name, pid, status, cpu_percent, memory, username, create_time):
        """Add a process to the tree.
        
        Args:
            name: Process name
            pid: Process ID
            status: Process status
            cpu_percent: CPU usage percentage
            memory: Memory usage in bytes
            username: Username
            create_time: Process creation time
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        # Format memory size
        if memory > 1024 * 1024 * 1024:
            mem_str = f"{memory / (1024 * 1024 * 1024):.1f} GB"
        else:
            mem_str = f"{memory / (1024 * 1024):.1f} MB"
            
        # Format creation time
        time_str = create_time.strftime("%Y-%m-%d %H:%M:%S")
        
        item = QTreeWidgetItem([
            name,
            str(pid),
            status,
            f"{cpu_percent:.1f}",
            mem_str,
            username,
            time_str
        ])
        
        self.addTopLevelItem(item)
        return item
        
    def get_process(self, item):
        """Get process details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            dict: Process properties
        """
        return {
            'name': item.text(0),
            'pid': int(item.text(1)),
            'status': item.text(2),
            'cpu_percent': float(item.text(3).rstrip('%')),
            'memory': item.text(4),
            'username': item.text(5),
            'started': item.text(6)
        }
        
    def clear_processes(self):
        """Clear all processes from the tree."""
        self.clear()
        
    def find_process(self, pid):
        """Find a process by PID.
        
        Args:
            pid: Process ID to find
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(str(pid), Qt.MatchFlag.MatchExactly, 1)
        return items[0] if items else None

class StartupTree(QTreeWidget):
    """Tree widget for displaying startup applications."""
    
    def __init__(self, parent=None):
        """Initialize startup tree.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget UI."""
        # Set up columns
        self.setHeaderLabels([
            "Name",
            "Command",
            "Location",
            "Type"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 200)  # Name
        self.setColumnWidth(1, 300)  # Command
        self.setColumnWidth(2, 100)  # Location
        self.setColumnWidth(3, 100)  # Type
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_startup_item(self, name, command, location, item_type):
        """Add a startup item to the tree.
        
        Args:
            name: Item name
            command: Command or path
            location: Registry hive or folder location
            item_type: Type (Run, RunOnce, Startup Folder)
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            name,
            command,
            location,
            item_type
        ])
        
        self.addTopLevelItem(item)
        return item
        
    def get_startup_item(self, item):
        """Get startup item details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            dict: Startup item properties
        """
        return {
            'name': item.text(0),
            'command': item.text(1),
            'location': item.text(2),
            'type': item.text(3)
        }
        
    def clear_startup_items(self):
        """Clear all startup items from the tree."""
        self.clear()
        
    def find_startup_item(self, name):
        """Find a startup item by name.
        
        Args:
            name: Item name to find
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(name, Qt.MatchFlag.MatchExactly, 0)
        return items[0] if items else None
