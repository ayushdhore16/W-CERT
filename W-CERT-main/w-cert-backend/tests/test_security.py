"""
W-CERT Test Suite — Security Module
Tests encryption, hashing, and integrity verification.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up encryption key for testing
os.environ['ENCRYPTION_KEY'] = 'dGVzdC1lbmNyeXB0aW9uLWtleS0xMjM0NTY3OA=='
# Need a valid Fernet key for tests
from cryptography.fernet import Fernet
os.environ['ENCRYPTION_KEY'] = Fernet.generate_key().decode()

from app.security.encryption import encrypt_pii, decrypt_pii
from app.security.hashing import hash_content, hash_bytes, verify_integrity


class TestEncryption:
    """Tests for AES Fernet encryption."""

    def test_encrypt_decrypt_roundtrip(self):
        """Encrypting then decrypting should return original value."""
        original = "Jane Doe"
        encrypted = encrypt_pii(original)
        decrypted = decrypt_pii(encrypted)
        assert decrypted == original

    def test_encrypt_different_ciphertexts(self):
        """Same plaintext should produce different ciphertexts (Fernet uses IV)."""
        text = "test@example.com"
        enc1 = encrypt_pii(text)
        enc2 = encrypt_pii(text)
        assert enc1 != enc2  # Fernet produces different output each time

    def test_encrypt_empty_string(self):
        """Empty string should return empty string."""
        assert encrypt_pii('') == ''
        assert decrypt_pii('') == ''

    def test_decrypt_invalid_ciphertext(self):
        """Invalid ciphertext should return failure message, not crash."""
        result = decrypt_pii("not-a-valid-ciphertext")
        assert result == '[DECRYPTION_FAILED]'

    def test_encrypt_unicode(self):
        """Unicode characters should be handled correctly."""
        original = "Priya Sharma — प्रिया शर्मा"
        encrypted = encrypt_pii(original)
        decrypted = decrypt_pii(encrypted)
        assert decrypted == original

    def test_encrypt_long_text(self):
        """Long text should encrypt and decrypt correctly."""
        original = "A" * 10000
        encrypted = encrypt_pii(original)
        decrypted = decrypt_pii(encrypted)
        assert decrypted == original


class TestHashing:
    """Tests for SHA-256 hashing."""

    def test_hash_consistency(self):
        """Same input should always produce the same hash."""
        text = "Someone threatened to leak my photos"
        hash1 = hash_content(text)
        hash2 = hash_content(text)
        assert hash1 == hash2

    def test_hash_length(self):
        """SHA-256 should produce a 64-character hex digest."""
        result = hash_content("test")
        assert len(result) == 64

    def test_hash_different_inputs(self):
        """Different inputs should produce different hashes."""
        hash1 = hash_content("input one")
        hash2 = hash_content("input two")
        assert hash1 != hash2

    def test_hash_bytes(self):
        """Bytes hashing should work correctly."""
        data = b"binary evidence data"
        result = hash_bytes(data)
        assert len(result) == 64

    def test_verify_integrity_pass(self):
        """Integrity check should pass for matching data."""
        text = "evidence description"
        h = hash_content(text)
        assert verify_integrity(text, h) is True

    def test_verify_integrity_fail(self):
        """Integrity check should fail for tampered data."""
        text = "original evidence"
        h = hash_content(text)
        assert verify_integrity("tampered evidence", h) is False

    def test_hash_empty(self):
        """Empty input should still produce a valid hash."""
        result = hash_content("")
        assert len(result) == 64


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
