"""
W-CERT SHA-256 Hashing Module
Provides forensic-grade hashing for evidence integrity verification.
"""

import hashlib


def hash_content(text):
    """
    Generate SHA-256 hash of text content.
    Used for incident description integrity verification.
    
    Args:
        text (str): The text to hash.
    
    Returns:
        str: Hex digest of the SHA-256 hash.
    """
    if not text:
        return hashlib.sha256(b'').hexdigest()
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def hash_file(filepath):
    """
    Generate SHA-256 hash of a file.
    Reads in chunks for memory efficiency with large files.
    
    Args:
        filepath (str): Path to the file.
    
    Returns:
        str: Hex digest of the SHA-256 hash.
    """
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def hash_bytes(data):
    """
    Generate SHA-256 hash of raw bytes.
    Used for in-memory file hashing before saving.
    
    Args:
        data (bytes): The bytes to hash.
    
    Returns:
        str: Hex digest of the SHA-256 hash.
    """
    return hashlib.sha256(data).hexdigest()


def verify_integrity(data, expected_hash):
    """
    Verify that data matches an expected SHA-256 hash.
    
    Args:
        data (str or bytes): Content to verify.
        expected_hash (str): Expected hex digest.
    
    Returns:
        bool: True if hashes match, False otherwise.
    """
    if isinstance(data, str):
        actual_hash = hash_content(data)
    else:
        actual_hash = hash_bytes(data)
    return actual_hash == expected_hash
