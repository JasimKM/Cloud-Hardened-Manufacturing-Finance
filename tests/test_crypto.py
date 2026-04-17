import pytest
import os
import sys
from app.crypto_utils import encrypt_data, decrypt_data

# Ensure app directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_crypto_round_trip():
    """Verify that data encrypted can be successfully decrypted with correct password."""
    original_data = b"Critical manufacturing process parameters: RPM=2500, TEMP=42C"
    password = "HardenedIndustrialSecret123!"
    
    # Encrypt
    encrypted_blob = encrypt_data(original_data, password)
    assert len(encrypted_blob) > 44  # Header (44) + Ciphertext
    
    # Decrypt
    decrypted_data = decrypt_data(encrypted_blob, password)
    assert decrypted_data == original_data

def test_crypto_wrong_password():
    """Verify that decryption fails securely with an incorrect password."""
    data = b"Secret PLC Logic"
    password = "CorrectPass123"
    wrong_password = "WrongPass456"
    
    encrypted_blob = encrypt_data(data, password)
    
    with pytest.raises(Exception):
        decrypt_data(encrypted_blob, wrong_password)

def test_tamper_detection():
    """Verify that even a single bit change in ciphertext triggers tag mismatch."""
    data = b"Instruction: STOP_SPINDLE"
    password = "VaultPassword"
    
    encrypted_blob = bytearray(encrypt_data(data, password))
    
    # Modify one byte of the ciphertext (last byte)
    encrypted_blob[-1] ^= 0xFF
    
    with pytest.raises(Exception):
        decrypt_data(bytes(encrypted_blob), password)
