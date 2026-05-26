"""
W-CERT Secure Evidence Storage
Handles local filesystem storage with hash-based directory structure.
"""

import os
import shutil


def get_storage_path(app_config, file_hash):
    """
    Generate a storage path based on the file's SHA-256 hash.
    Uses first 2 chars as directory, rest as filename.
    This distributes files across directories for performance.
    
    Args:
        app_config: Flask app config dict.
        file_hash (str): SHA-256 hex digest of the file.
    
    Returns:
        str: Absolute path where the file should be stored.
    """
    upload_folder = app_config.get('UPLOAD_FOLDER', 'uploads')
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), upload_folder)

    # Hash-based subdirectory: /uploads/ab/cdef1234...
    sub_dir = os.path.join(base_dir, file_hash[:2])
    os.makedirs(sub_dir, exist_ok=True)

    return os.path.join(sub_dir, file_hash)


def save_file(file_data, storage_path):
    """
    Save file bytes to the storage path.
    
    Args:
        file_data (bytes): Raw file content.
        storage_path (str): Destination path from get_storage_path().
    
    Returns:
        bool: True on success.
    """
    with open(storage_path, 'wb') as f:
        f.write(file_data)
    return True


def retrieve_file(storage_path):
    """
    Retrieve file bytes from storage.
    
    Args:
        storage_path (str): Path from get_storage_path().
    
    Returns:
        bytes: File content, or None if not found.
    """
    if not os.path.exists(storage_path):
        return None
    with open(storage_path, 'rb') as f:
        return f.read()


def delete_file(storage_path):
    """
    Delete a file from storage.
    
    Args:
        storage_path (str): Path to delete.
    
    Returns:
        bool: True if deleted, False if not found.
    """
    if os.path.exists(storage_path):
        os.remove(storage_path)
        return True
    return False


def file_exists(storage_path):
    """Check if a file exists in storage."""
    return os.path.exists(storage_path)


def get_file_size(storage_path):
    """Get file size in bytes."""
    if os.path.exists(storage_path):
        return os.path.getsize(storage_path)
    return 0
