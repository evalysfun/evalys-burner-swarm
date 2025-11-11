"""
Encryption utilities for secure key storage
"""

import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def derive_key(password: Optional[str] = None, salt: Optional[bytes] = None) -> bytes:
    """
    Derive encryption key from password
    
    Args:
        password: Optional password (uses default if None)
        salt: Optional salt (generates new if None)
        
    Returns:
        Encryption key
    """
    if password is None:
        password = "evalys-default-key"  # In production, use secure default
    
    if salt is None:
        salt = b'evalys_salt_12345678'  # In production, generate random salt
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_key(data: bytes, password: Optional[str] = None) -> dict:
    """
    Encrypt data
    
    Args:
        data: Data to encrypt
        password: Optional password
        
    Returns:
        Dictionary with encrypted data and metadata
    """
    key = derive_key(password)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    
    return {
        "encrypted_data": base64.b64encode(encrypted).decode(),
        "algorithm": "fernet",
        "has_password": password is not None
    }


def decrypt_key(encrypted_data: dict, password: Optional[str] = None) -> bytes:
    """
    Decrypt data
    
    Args:
        encrypted_data: Encrypted data dictionary
        password: Password used for encryption
        
    Returns:
        Decrypted bytes
    """
    encrypted_bytes = base64.b64decode(encrypted_data["encrypted_data"])
    key = derive_key(password)
    fernet = Fernet(key)
    
    decrypted = fernet.decrypt(encrypted_bytes)
    return decrypted

