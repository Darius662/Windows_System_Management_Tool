"""Disk manager module for managing disk operations."""

import os
import re
import subprocess
import psutil
import logging
import platform
import json
from PyQt6.QtCore import QObject, pyqtSignal

class DiskManager(QObject):
    """Manager for disk operations."""
    
    # Signals
    volumes_refreshed = pyqtSignal(list)
    volume_mounted = pyqtSignal(dict)
    volume_unmounted = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the disk manager."""
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.volumes = []
    
    def get_volumes(self):
        """Get the list of volumes (compatibility wrapper).
        
        Returns:
            list: List of volume information dictionaries
        """
        return self.refresh_volumes()
        
    def get_drive_letters_info(self):
        """Get information about available and used drive letters.
        
        Returns:
            dict: Dictionary with keys:
                - all_letters: List of all possible drive letters (A-Z)
                - used_letters: List of currently used drive letters
                - available_letters: List of available drive letters
        """
        try:
            # Get all possible drive letters (A-Z)
            all_letters = [f"{chr(i)}:" for i in range(65, 91)]  # A-Z
            
            # Get used drive letters from psutil
            used_letters = []
            for partition in psutil.disk_partitions(all=True):
                if partition.device and len(partition.device) >= 2:
                    drive_letter = partition.device[:2]  # Get drive letter with colon
                    used_letters.append(drive_letter)
            
            # Calculate available letters
            available_letters = [letter for letter in all_letters if letter not in used_letters]
            
            return {
                'all_letters': all_letters,
                'used_letters': used_letters,
                'available_letters': available_letters
            }
        except Exception as e:
            self.logger.error(f"Error getting drive letters info: {str(e)}")
            # Fallback to default values
            return {
                'all_letters': [f"{chr(i)}:" for i in range(65, 91)],
                'used_letters': [],
                'available_letters': [f"{chr(i)}:" for i in range(65, 91)]
            }
    
    def get_disks(self):
        """Get the list of physical disks (compatibility wrapper).
        
        Returns:
            list: List of physical disk information dictionaries
        """
        import wmi
        
        try:
            disks = []
            c = wmi.WMI()
            
            # Create a mapping of disk index to disk object
            disk_map = {}
            for disk in c.Win32_DiskDrive():
                disk_index = disk.Index
                disk_map[disk_index] = disk
                
                # Initialize disk info
                disk_info = {
                    'name': disk.Caption,
                    'model': disk.Model,
                    'size': int(disk.Size) if disk.Size else 0,
                    'interface': disk.InterfaceType if hasattr(disk, 'InterfaceType') else 'Unknown',
                    'serial': disk.SerialNumber if hasattr(disk, 'SerialNumber') else 'Unknown',
                    'status': disk.Status if hasattr(disk, 'Status') else 'Unknown',
                    'firmware': disk.FirmwareRevision if hasattr(disk, 'FirmwareRevision') else 'Unknown',
                    'partitions': []  # Initialize empty partitions list
                }
                disks.append(disk_info)
            
            # Get partition information and associate with disks
            for partition in c.Win32_DiskPartition():
                try:
                    disk_index = int(partition.DiskIndex)
                    if disk_index in disk_map:
                        # Find the corresponding disk in our list
                        for disk in disks:
                            if disk['name'] == disk_map[disk_index].Caption:
                                # Add partition info
                                partition_info = {
                                    'name': partition.Name,
                                    'type': partition.Type,
                                    'size': int(partition.Size) if partition.Size else 0,
                                    'bootable': partition.Bootable if hasattr(partition, 'Bootable') else False
                                }
                                disk['partitions'].append(partition_info)
                except Exception as e:
                    self.logger.warning(f"Error processing partition {partition.Name}: {str(e)}")
                    continue
                
            return disks
        except Exception as e:
            self.logger.error(f"Error getting physical disks: {str(e)}")
            return []
        
    def refresh_volumes(self):
        """Refresh the list of volumes.
        
        Returns:
            list: List of volume information dictionaries
        """
        try:
            self.logger.debug("Refreshing volumes")
            volumes = []
            
            # Get all disk partitions
            partitions = psutil.disk_partitions(all=True)
            
            for partition in partitions:
                # Determine volume type based on available information
                volume_type = 'Local Disk'
                if partition.fstype == 'NTFS' and (partition.opts and 'remote' in partition.opts.lower()):
                    volume_type = 'Network Drive'
                elif partition.mountpoint == 'C:\\':
                    volume_type = 'System Drive'
                elif not partition.fstype:
                    volume_type = 'Unknown'
                elif 'cdrom' in partition.opts.lower() if partition.opts else False:
                    volume_type = 'CD/DVD'
                elif 'removable' in partition.opts.lower() if partition.opts else False:
                    volume_type = 'Removable Drive'
                
                volume = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'opts': partition.opts,
                    'is_network_drive': False,
                    'network_path': None,
                    'type': volume_type  # Add the type field
                }
                
                # Add usage information if available
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    volume['total'] = usage.total
                    volume['used'] = usage.used
                    volume['free'] = usage.free
                    volume['percent'] = usage.percent
                except (PermissionError, FileNotFoundError):
                    volume['total'] = 0
                    volume['used'] = 0
                    volume['free'] = 0
                    volume['percent'] = 0
                
                # Check if this is a network drive
                if partition.fstype == 'NTFS' and (partition.opts and 'remote' in partition.opts.lower()):
                    volume['is_network_drive'] = True
                    
                    # Try to get the network path
                    try:
                        # Use net use to get network path
                        drive_letter = partition.device.rstrip('\\')
                        result = subprocess.run(
                            ['net', 'use', drive_letter],
                            capture_output=True,
                            text=True
                        )
                        
                        # Extract network path from output
                        if result.returncode == 0:
                            match = re.search(r'Remote name\s+\\\\([^\s]+)', result.stdout)
                            if match:
                                volume['network_path'] = f"\\\\{match.group(1)}"
                    except Exception as e:
                        self.logger.error(f"Error getting network path: {str(e)}")
                
                volumes.append(volume)
            
            # Get additional information for each volume
            for volume in volumes:
                try:
                    # Get volume label
                    if platform.system() == 'Windows' and volume['mountpoint']:
                        drive_letter = volume['mountpoint'].rstrip('\\')
                        result = subprocess.run(
                            ['cmd', '/c', f'vol {drive_letter}'],
                            capture_output=True,
                            text=True
                        )
                        
                        # Extract volume label from output
                        if result.returncode == 0:
                            match = re.search(r'Volume in drive [A-Z] is (.*)', result.stdout)
                            if match:
                                volume['label'] = match.group(1).strip()
                            else:
                                volume['label'] = 'No Label'
                        else:
                            volume['label'] = 'Unknown'
                    else:
                        volume['label'] = 'Unknown'
                except Exception as e:
                    self.logger.error(f"Error getting volume label: {str(e)}")
                    volume['label'] = 'Error'
            
            self.volumes = volumes
            self.volumes_refreshed.emit(volumes)
            self.logger.debug("Refreshed volumes")
            return volumes
        except Exception as e:
            error_msg = f"Failed to refresh volumes: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return []

    def map_network_drive(self, network_path, drive_letter, use_windows_creds=True, 
                         username='', password='', reconnect=True):
        """Map a network drive.
        
        Args:
            network_path: UNC path to the network share (e.g., \\\\server\\\\share)
            drive_letter: Drive letter to map to (e.g., Z:)
            use_windows_creds: Whether to use current Windows credentials
            username: Username for custom credentials
            password: Password for custom credentials
            reconnect: Whether to reconnect at sign-in
            
        Returns:
            dict: Result with success flag and error message if applicable
        """
        try:
            # Ensure drive letter format is correct
            if len(drive_letter) == 1:
                drive_letter = f"{drive_letter}:"
            
            # First, delete any existing mapping to ensure clean state
            try:
                # Quietly try to delete any existing mapping
                subprocess.run(
                    ["net", "use", drive_letter, "/delete", "/y"],
                    capture_output=True,
                    text=True
                )
            except Exception:
                # Ignore errors here - the drive might not be mapped
                pass
                
            # Use a simple approach that works reliably
            if use_windows_creds:
                # For Windows credentials, use the simple net use command
                self.logger.debug("Using current Windows credentials")
                cmd = [
                    "net", "use", drive_letter, network_path,
                    "/persistent:" + ("yes" if reconnect else "no")
                ]
                
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )
                
                stdout = process.stdout
                stderr = process.stderr
                
            else:
                # For custom credentials, use a direct approach with win32 API
                self.logger.debug(f"Using win32 API to map drive with custom credentials for user: {username}")
                
                # Import win32 modules
                try:
                    import win32wnet
                    import win32netcon
                    import win32api
                    import pywintypes
                    
                    # Set up the NETRESOURCE structure
                    netresource = win32wnet.NETRESOURCE()
                    netresource.lpLocalName = drive_letter
                    netresource.lpRemoteName = network_path
                    netresource.dwType = win32netcon.RESOURCETYPE_DISK
                    
                    # Try to connect with the provided credentials
                    try:
                        # WNetAddConnection2 handles credentials properly
                        win32wnet.WNetAddConnection2(netresource, password, username, 0 if not reconnect else win32netcon.CONNECT_UPDATE_PROFILE)
                        stdout = f"Successfully mapped {network_path} to {drive_letter} using win32 API"
                        stderr = ""
                        self.logger.info(stdout)
                    except pywintypes.error as e:
                        # Handle specific error codes
                        error_code = e.winerror
                        error_msg = e.strerror
                        
                        # Log detailed error information
                        self.logger.error(f"Win32 API error: {error_code} - {error_msg}")
                        
                        # Special handling for error 1219 (multiple connections)
                        if error_code == 1219:
                            # Get server name from network path (\\server\share)
                            parts = network_path.split('\\')
                            server_name = parts[2] if len(parts) > 2 else "server"
                            
                            self.logger.warning(f"Multiple connection error detected for server: {server_name}")
                            
                            # List existing connections using a separate command
                            try:
                                list_process = subprocess.run(
                                    ["net", "use"],
                                    capture_output=True,
                                    text=True
                                )
                                
                                if list_process.stdout:
                                    self.logger.debug(f"Existing connections:\n{list_process.stdout}")
                                
                                # Create a helpful error message
                                error_msg = (
                                    f"Cannot connect to {network_path} with user '{username}' because you already "
                                    f"have a connection to the same server with different credentials.\n\n"
                                    f"Please disconnect existing connections to {server_name} first using 'net use /delete', "
                                    f"or use the same credentials for all connections to this server."
                                )
                                
                                stdout = ""
                                stderr = error_msg
                                
                            except Exception as list_err:
                                self.logger.error(f"Error listing connections: {str(list_err)}")
                                stderr = f"Multiple connections error: {error_msg}"
                        else:
                            # For other errors, try a fallback approach with the net use command
                            self.logger.debug("Trying fallback with net use command")
                            cmd = [
                                "net", "use", drive_letter, network_path,
                                "/user:" + username, password,
                                "/persistent:" + ("yes" if reconnect else "no")
                            ]
                            
                            process = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True
                            )
                            
                            stdout = process.stdout
                            stderr = process.stderr
                        
                except ImportError as e:
                    self.logger.error(f"Failed to import win32 modules: {str(e)}")
                    stderr = f"Failed to import win32 modules: {str(e)}"
                    stdout = ""
            
            # Log the command output for debugging
            if stdout:
                self.logger.debug(f"Command output: {stdout}")
            if stderr:
                self.logger.debug(f"Command error: {stderr}")
                
            # Check if the operation was successful
            if stderr and "error" in stderr.lower():
                self.logger.error(f"Failed to map network drive: {stderr}")
                self.logger.error(f"Network path: {network_path}, Drive: {drive_letter}")
                self.logger.error(f"Using Windows creds: {use_windows_creds}, Username: {username}")
                
                # Try to get more information about the error
                if not use_windows_creds:
                    self.logger.error(f"Return code: {process.returncode if 'process' in locals() else 2}")
                    self.logger.debug("Attempting diagnostic command...")
                    self.logger.debug(f"Diagnostic command (password redacted): net use {drive_letter} {network_path} /user:{username} PASSWORD /persistent:{'yes' if reconnect else 'no'}")
                    
                    # Try to ping the server to check connectivity
                    try:
                        server = network_path.split('\\')[2]
                        self.logger.debug(f"Attempting to ping server: {server}")
                        ping_result = subprocess.run(
                            ["ping", "-n", "1", server],
                            capture_output=True,
                            text=True
                        )
                        self.logger.debug(f"Network connectivity test: \n{ping_result.stdout}")
                    except Exception as ping_err:
                        self.logger.error(f"Error pinging server: {str(ping_err)}")
                
                self.error_occurred.emit(f"Failed to map network drive: {stderr}")
                return {
                    'success': False,
                    'error': stderr
                }
            else:
                self.logger.info(f"Mapping network drive {network_path} to {drive_letter}")
                
                # Refresh volumes to include the new mapping
                self.refresh_volumes()
                
                # Emit signal
                self.volume_mounted.emit({
                    'device': drive_letter,
                    'mountpoint': drive_letter + '\\',
                    'network_path': network_path,
                    'is_network_drive': True
                })
                
                return {
                    'success': True
                }
        except Exception as e:
            error_msg = f"Failed to map network drive: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return {
                'success': False,
                'error': str(e)
            }

    def disconnect_network_drive(self, drive_letter):
        """Disconnect a network drive.
        
        Args:
            drive_letter: Drive letter to disconnect (e.g., Z:)
            
        Returns:
            dict: Result with success flag and error message if applicable
        """
        try:
            # Ensure drive letter format is correct
            if not drive_letter:
                return {
                    'success': False,
                    'error': "No drive letter specified"
                }
                
            # Normalize drive letter format (ensure it has a colon and no trailing backslash)
            drive_letter = drive_letter.strip()
            if len(drive_letter) == 1:
                drive_letter = f"{drive_letter}:"
            elif drive_letter.endswith('\\'):
                drive_letter = drive_letter[:-1]
            
            # Check if the drive is actually mapped first
            check_process = subprocess.run(
                ["net", "use"],
                capture_output=True,
                text=True
            )
            
            # If the drive isn't in the output, it's not mapped
            if drive_letter.upper() not in check_process.stdout.upper():
                self.logger.warning(f"Drive {drive_letter} is not mapped as a network drive")
                # Still return success to avoid confusing the user with error messages
                # when the end result is what they wanted (drive not mapped)
                return {
                    'success': True,
                    'warning': f"Drive {drive_letter} is not mapped as a network drive"
                }
            
            # Use net use to disconnect
            process = subprocess.run(
                ["net", "use", drive_letter, "/delete", "/y"],  # Added /y to suppress confirmation
                capture_output=True,
                text=True
            )
            
            stdout = process.stdout
            stderr = process.stderr
            
            # Log the command output for debugging
            self.logger.debug(f"Command output: {stdout}")
            if stderr:
                self.logger.debug(f"Command error: {stderr}")
                
            # Check if the operation was successful
            if process.returncode != 0:
                # Some errors are actually warnings and the drive was still disconnected
                if "The network connection could not be found" in stdout:
                    self.logger.info(f"Drive {drive_letter} was already disconnected")
                    # Still return success since the end state is what the user wanted
                    return {
                        'success': True,
                        'warning': "The drive was already disconnected"
                    }
                else:
                    self.logger.error(f"Failed to disconnect network drive: {stdout if stdout else stderr}")
                    self.error_occurred.emit(f"Failed to disconnect network drive: {stdout if stdout else stderr}")
                    return {
                        'success': False,
                        'error': stdout if stdout else stderr
                    }
            else:
                self.logger.info(f"Disconnected network drive {drive_letter}")
                
                # Refresh volumes to remove the disconnected mapping
                self.refresh_volumes()
                
                # Emit signal
                self.volume_unmounted.emit(drive_letter)
                
                return {
                    'success': True
                }
        except Exception as e:
            error_msg = f"Failed to disconnect network drive: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return {
                'success': False,
                'error': str(e)
            }
