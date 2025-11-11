"""
Wallet Generator

Generates Solana keypairs for burner wallets with secure key management.
"""

from typing import Optional
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import secrets
from ..utils.logger import get_logger
from ..utils.encryption import encrypt_key, decrypt_key

logger = get_logger(__name__)


class WalletGenerator:
    """
    Generates and manages Solana keypairs for burner wallets
    """
    
    def __init__(self):
        """Initialize wallet generator"""
        self.generated_count = 0
        logger.info("WalletGenerator initialized")
    
    def generate_keypair(self) -> Keypair:
        """
        Generate a new Solana keypair
        
        Returns:
            New Keypair instance
        """
        keypair = Keypair()
        self.generated_count += 1
        logger.debug(f"Generated keypair #{self.generated_count}: {keypair.pubkey()}")
        return keypair
    
    def generate_from_seed(self, seed: bytes) -> Keypair:
        """
        Generate keypair from seed (for deterministic generation if needed)
        
        Args:
            seed: 32-byte seed
            
        Returns:
            Keypair generated from seed
        """
        if len(seed) != 32:
            raise ValueError("Seed must be exactly 32 bytes")
        
        keypair = Keypair.from_bytes(seed)
        logger.debug(f"Generated keypair from seed: {keypair.pubkey()}")
        return keypair
    
    def generate_random_seed(self) -> bytes:
        """
        Generate a random 32-byte seed
        
        Returns:
            Random seed bytes
        """
        return secrets.token_bytes(32)
    
    def get_public_key(self, keypair: Keypair) -> Pubkey:
        """
        Extract public key from keypair
        
        Args:
            keypair: Keypair instance
            
        Returns:
            Public key
        """
        return keypair.pubkey()
    
    def get_private_key_bytes(self, keypair: Keypair) -> bytes:
        """
        Extract private key bytes from keypair
        
        Args:
            keypair: Keypair instance
            
        Returns:
            Private key bytes (64 bytes)
        """
        return bytes(keypair)
    
    def encrypt_keypair(self, keypair: Keypair, password: Optional[str] = None) -> dict:
        """
        Encrypt keypair for secure storage
        
        Args:
            keypair: Keypair to encrypt
            password: Optional password for encryption
            
        Returns:
            Dictionary with encrypted data
        """
        private_key = self.get_private_key_bytes(keypair)
        public_key = str(keypair.pubkey())
        
        encrypted = encrypt_key(private_key, password)
        
        return {
            "public_key": public_key,
            "encrypted_private_key": encrypted,
            "created_at": None  # Will be set by pool manager
        }
    
    def decrypt_keypair(self, encrypted_data: dict, password: Optional[str] = None) -> Keypair:
        """
        Decrypt keypair from encrypted storage
        
        Args:
            encrypted_data: Encrypted keypair data
            password: Password used for encryption
            
        Returns:
            Decrypted Keypair
        """
        encrypted_private_key = encrypted_data["encrypted_private_key"]
        private_key_bytes = decrypt_key(encrypted_private_key, password)
        
        return Keypair.from_bytes(private_key_bytes)

