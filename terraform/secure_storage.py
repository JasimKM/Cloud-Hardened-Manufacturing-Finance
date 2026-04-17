import os
import argparse
import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2 import PasswordHasher
import secrets

def derive_key(password: str, salt: bytes) -> bytes:
    from argon2 import low_level
    # Argon2id: 64MiB, 3 passes, 1 parallelism
    return low_level.hash_secret_raw(
        password.encode(),
        salt,
        time_cost=3,
        memory_cost=64000,
        parallelism=1,
        hash_len=32,
        type=low_level.Type.ID
    )

def encrypt_file(file_path: str, password: str):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    salt = secrets.token_bytes(16)
    key = derive_key(password, salt)
    nonce = secrets.token_bytes(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    
    output_path = file_path + ".enc"
    with open(output_path, 'wb') as f:
        f.write(salt + nonce + ciphertext)
    print(f"Encrypted: {file_path} -> {output_path}")

def decrypt_file(file_path: str, password: str):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    salt = data[:16]
    nonce = data[16:28]
    ciphertext = data[28:]
    
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    try:
        decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        output_path = file_path.replace(".enc", "")
        if output_path == file_path:
            output_path += ".dec"
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        print(f"Decrypted: {file_path} -> {output_path}")
    except Exception:
        print("Decryption failed: Wrong password or tampered file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ManufacturingVault CLI - Industrial File Protection")
    parser.add_argument("action", choices=["encrypt", "decrypt"], help="Encryption action")
    parser.add_argument("file", help="Target file path")
    parser.add_argument("--password", required=True, help="Encryption passphrase")
    parser.add_argument("--batch", action="store_true", help="Batch process entire directory")

    args = parser.parse_args()

    if args.batch:
        if os.path.isdir(args.file):
            for filename in os.listdir(args.file):
                f = os.path.join(args.file, filename)
                if os.path.isfile(f):
                    if args.action == "encrypt":
                        encrypt_file(f, args.password)
                    elif args.action == "decrypt" and f.endswith(".enc"):
                        decrypt_file(f, args.password)
        else:
            print("Error: --batch requires a directory path.")
    else:
        if args.action == "encrypt":
            encrypt_file(args.file, args.password)
        else:
            decrypt_file(args.file, args.password)
