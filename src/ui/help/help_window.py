"""Help window for System Management Tool."""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QTextEdit
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class HelpWindow(QMainWindow):
    """Help window for System Management Tool."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Management Tool Help")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Overview tab
        overview = QWidget()
        overview_layout = QVBoxLayout(overview)
        overview_text = QTextEdit()
        overview_text.setReadOnly(True)
        overview_text.setHtml("""
        <h2>Windows System Management Tool</h2>
        <p>A powerful tool for managing Windows systems locally and remotely. This application allows you 
        to configure and manage multiple aspects of Windows systems through a modern graphical interface.</p>
        
        <h3>Key Features</h3>
        <ul>
            <li>Local system configuration</li>
            <li>Remote PC management</li>
            <li>Configuration import/export</li>
            <li>File transfer capabilities</li>
            <li>Multi-PC operations</li>
        </ul>
        
        <h3>Basic Usage</h3>
        <ol>
            <li>Use the tabs to access different management features</li>
            <li>Configure settings as needed</li>
            <li>Apply changes locally or to remote PCs</li>
            <li>Import/export configurations for reuse</li>
        </ol>
        
        <h3>Remote Management</h3>
        <p>To manage remote PCs:</p>
        <ol>
            <li>Use Remote -> Manage Connections to add PCs</li>
            <li>Configure settings in any tab</li>
            <li>Use Remote -> Apply to All Connected PCs</li>
        </ol>
        """)
        overview_layout.addWidget(overview_text)
        tabs.addTab(overview, "Overview")
        
        # Features tab
        features = QWidget()
        features_layout = QVBoxLayout(features)
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setHtml("""
        <h2>Features Guide</h2>
        
        <h3>Environment Variables</h3>
        <p>Manage system and user environment variables:</p>
        <ul>
            <li>View current variables</li>
            <li>Add/modify/delete variables</li>
            <li>Apply to remote PCs</li>
        </ul>
        
        <h3>Registry Editor</h3>
        <p>Windows Registry management:</p>
        <ul>
            <li>Browse registry structure</li>
            <li>Add/modify/delete values</li>
            <li>Import/export registry settings</li>
        </ul>
        
        <h3>Users & Groups</h3>
        <p>User account and group management:</p>
        <ul>
            <li>Create/modify user accounts</li>
            <li>Manage group memberships</li>
            <li>Set account properties</li>
        </ul>
        
        <h3>Services</h3>
        <p>Windows services control:</p>
        <ul>
            <li>View service status</li>
            <li>Start/stop services</li>
            <li>Change startup type</li>
        </ul>
        
        <h3>Firewall</h3>
        <p>Windows Firewall configuration:</p>
        <ul>
            <li>View existing rules</li>
            <li>Create new rules</li>
            <li>Modify rule properties</li>
        </ul>
        
        <h3>Software</h3>
        <p>Software management:</p>
        <ul>
            <li>Install applications</li>
            <li>Uninstall software</li>
            <li>Verify installations</li>
        </ul>
        
        <h3>Permissions</h3>
        <p>File and folder permissions:</p>
        <ul>
            <li>View current permissions</li>
            <li>Modify access rights</li>
            <li>Set ownership</li>
        </ul>
        
        <h3>Applications</h3>
        <p>Application control with modular components:</p>
        <ul>
            <li>Processes tab: View and manage running processes</li>
            <li>End individual processes or process trees</li>
            <li>Startup tab: Manage Windows startup applications</li>
            <li>Add or remove startup items</li>
            <li>Auto-refresh capabilities for real-time monitoring</li>
        </ul>
        
        <h3>Disk Management</h3>
        <p>Disk and volume management:</p>
        <ul>
            <li>View disk and volume information</li>
            <li>Map network drives with custom or Windows credentials</li>
            <li>Disconnect network drives</li>
            <li>Monitor disk health and status</li>
        </ul>
        
        <h3>Drivers</h3>
        <p>Driver management:</p>
        <ul>
            <li>View installed drivers</li>
            <li>Check driver status and details</li>
            <li>Manage driver operations</li>
        </ul>
        
        <h3>Network</h3>
        <p>Network configuration:</p>
        <ul>
            <li>View network adapters</li>
            <li>Monitor connection status</li>
            <li>Configure network settings</li>
        </ul>
        
        <h3>Packages</h3>
        <p>Package management:</p>
        <ul>
            <li>View installed packages</li>
            <li>Package information and details</li>
            <li>Manage package operations</li>
        </ul>
        
        <h3>Processes</h3>
        <p>Process management:</p>
        <ul>
            <li>Detailed process information</li>
            <li>Process monitoring</li>
            <li>Process control operations</li>
        </ul>
        
        <h3>Task Scheduler</h3>
        <p>Windows Task Scheduler management:</p>
        <ul>
            <li>View scheduled tasks</li>
            <li>Create and modify tasks</li>
            <li>Enable/disable scheduled tasks</li>
        </ul>
        
        <h3>Event Viewer</h3>
        <p>Windows Event Log viewer:</p>
        <ul>
            <li>Browse hierarchical event logs</li>
            <li>View event details</li>
            <li>Filter events by criteria</li>
        </ul>
        
        <h3>Remote Management</h3>
        <p>Remote PC features:</p>
        <ul>
            <li>Connect to multiple PCs</li>
            <li>Transfer files</li>
            <li>Apply changes remotely</li>
        </ul>
        
        <h3>Configuration</h3>
        <p>Configuration management:</p>
        <ul>
            <li>Import settings</li>
            <li>Export settings</li>
            <li>Apply to multiple PCs</li>
        </ul>
        
        <h3>Settings</h3>
        <p>Application settings:</p>
        <ul>
            <li>Log level configuration (DEBUG, INFO, WARNING, ERROR, CRITICAL)</li>
            <li>View log file location</li>
            <li>Apply settings changes in real-time</li>
        </ul>
        """)
        features_layout.addWidget(features_text)
        tabs.addTab(features, "Features")
