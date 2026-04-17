import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a 256-bit key from a password and salt using Argon2id."""
    return hash_secret_raw(
        secret=password.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=1,
        hash_len=32,
        type=Type.ID
    )

def encrypt_data(data: bytes, password: str) -> bytes:
    """
    Encrypts bytes using AES-256-GCM and Argon2id.
    Returns: salt (16) + nonce (12) + tag (16) + ciphertext
    """
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    # Returns ciphertext + 16-byte tag
    full_cipher = aesgcm.encrypt(nonce, data, None)
    
    tag = full_cipher[-16:]
    ciphertext = full_cipher[:-16]
    
    return salt + nonce + tag + ciphertext

def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
    """
    Decrypts bytes using AES-256-GCM and Argon2id.
    Format: salt (16) + nonce (12) + tag (16) + ciphertext
    """
    if len(encrypted_data) < 16 + 12 + 16:
        raise ValueError("Invalid encrypted data format.")

    salt = encrypted_data[:16]
    nonce = encrypted_data[16:28]
    tag = encrypted_data[28:44]
    ciphertext = encrypted_data[44:]

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    # decrypt expects ciphertext + tag
    return aesgcm.decrypt(nonce, ciphertext + tag, None)

def encrypt_batch(input_dir: str, output_dir: str, password: str):
    """Recursively encrypts all files in a directory."""
    for root, _, files in os.walk(input_dir):
        for file in files:
            in_path = os.path.join(root, file)
            rel_path = os.path.relpath(in_path, input_dir)
            out_path = os.path.join(output_dir, rel_path + ".enc")
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            
            with open(in_path, "rb") as f:
                data = f.read()
            
            encrypted = encrypt_data(data, password)
            
            with open(out_path, "wb") as f:
                f.write(encrypted)
