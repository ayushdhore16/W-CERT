"""
W-CERT AES Encryption Module
Uses Fernet (AES-128-CBC) for encrypting personally identifiable information (PII).
Key is loaded from environment — persistent across server restarts.
"""

import os
from cryptography.fernet import Fernet, InvalidToken


_cipher = None


def _get_cipher():
    """Get or create the Fernet cipher using the persistent encryption key."""
    global _cipher
    if _cipher is not None:
        return _cipher

    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        # Generate a new key and warn — this should be saved to .env
        key = Fernet.generate_key().decode()
        print(f"[!] WARNING: No ENCRYPTION_KEY found in environment.")
        print(f"[!] Generated temporary key: {key}")
        print(f"[!] Save this to your .env file to persist encryption across restarts!")

    _cipher = Fernet(key.encode() if isinstance(key, str) else key)
    return _cipher


def encrypt_pii(plaintext):
    """
    Encrypt personally identifiable information.
    
    Args:
        plaintext (str): The text to encrypt (e.g., name, contact info).
    
    Returns:
        str: Base64-encoded ciphertext.
    """
    if not plaintext:
        return ''
    cipher = _get_cipher()
    return cipher.encrypt(plaintext.encode('utf-8')).decode('utf-8')


def decrypt_pii(ciphertext):
    """
    Decrypt personally identifiable information.
    
    Args:
        ciphertext (str): Base64-encoded ciphertext.
    
    Returns:
        str: Original plaintext, or '[DECRYPTION_FAILED]' if key mismatch.
    """
    if not ciphertext:
        return ''
    try:
        cipher = _get_cipher()
        return cipher.decrypt(ciphertext.encode('utf-8')).decode('utf-8')
    except (InvalidToken, Exception):
        return '[DECRYPTION_FAILED]'
