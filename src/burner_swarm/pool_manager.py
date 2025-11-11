"""
Pool Manager

Manages pools of burner wallets: active, reserve, and retired.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from .wallet_generator import WalletGenerator
from ..utils.logger import get_logger

logger = get_logger(__name__)


class WalletStatus(str, Enum):
    """Wallet status enumeration"""
    ACTIVE = "active"
    RESERVE = "reserve"
    RETIRED = "retired"


@dataclass
class BurnerWallet:
    """
    Burner wallet data structure
    
    Attributes:
        public_key: Wallet public key
        keypair: Keypair instance (in memory, encrypted when stored)
        created_at: Creation timestamp
        last_used: Last usage timestamp
        usage_count: Number of times used
        status: Current status
        encrypted_private_key: Encrypted private key (for storage)
    """
    public_key: Pubkey
    keypair: Keypair
    created_at: datetime
    last_used: Optional[datetime] = None
    usage_count: int = 0
    status: WalletStatus = WalletStatus.RESERVE
    encrypted_private_key: Optional[dict] = None
    
    def mark_used(self):
        """Mark wallet as used"""
        self.last_used = datetime.utcnow()
        self.usage_count += 1
    
    def is_expired(self, max_age_hours: int = 24) -> bool:
        """
        Check if wallet is expired based on age
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            True if expired
        """
        age = datetime.utcnow() - self.created_at
        return age > timedelta(hours=max_age_hours)
    
    def should_retire(self, max_uses: int = 1) -> bool:
        """
        Check if wallet should be retired
        
        Args:
            max_uses: Maximum number of uses before retirement
            
        Returns:
            True if should be retired
        """
        return self.usage_count >= max_uses


class PoolManager:
    """
    Manages pools of burner wallets
    """
    
    def __init__(
        self,
        min_reserve_size: int = 5,
        max_active_size: int = 10,
        wallet_generator: Optional[WalletGenerator] = None
    ):
        """
        Initialize pool manager
        
        Args:
            min_reserve_size: Minimum number of wallets in reserve pool
            max_active_size: Maximum number of wallets in active pool
            wallet_generator: Wallet generator instance
        """
        self.min_reserve_size = min_reserve_size
        self.max_active_size = max_active_size
        self.generator = wallet_generator or WalletGenerator()
        
        # Pools
        self.active_pool: Dict[str, BurnerWallet] = {}
        self.reserve_pool: Dict[str, BurnerWallet] = {}
        self.retired_pool: Dict[str, BurnerWallet] = {}
        
        logger.info(
            f"PoolManager initialized: min_reserve={min_reserve_size}, "
            f"max_active={max_active_size}"
        )
    
    def generate_wallet(self) -> BurnerWallet:
        """
        Generate a new burner wallet
        
        Returns:
            New BurnerWallet instance
        """
        keypair = self.generator.generate_keypair()
        public_key = keypair.pubkey()
        
        wallet = BurnerWallet(
            public_key=public_key,
            keypair=keypair,
            created_at=datetime.utcnow(),
            status=WalletStatus.RESERVE
        )
        
        # Encrypt for storage
        wallet.encrypted_private_key = self.generator.encrypt_keypair(keypair)
        
        logger.debug(f"Generated new wallet: {public_key}")
        return wallet
    
    def add_to_reserve(self, wallet: Optional[BurnerWallet] = None) -> BurnerWallet:
        """
        Add wallet to reserve pool
        
        Args:
            wallet: Wallet to add (generates new if None)
            
        Returns:
            Added wallet
        """
        if wallet is None:
            wallet = self.generate_wallet()
        
        wallet.status = WalletStatus.RESERVE
        self.reserve_pool[str(wallet.public_key)] = wallet
        
        logger.debug(f"Added wallet to reserve: {wallet.public_key}")
        return wallet
    
    def get_from_reserve(self) -> Optional[BurnerWallet]:
        """
        Get wallet from reserve pool
        
        Returns:
            Wallet from reserve or None if empty
        """
        if not self.reserve_pool:
            return None
        
        # Get first available wallet
        wallet = next(iter(self.reserve_pool.values()))
        del self.reserve_pool[str(wallet.public_key)]
        
        logger.debug(f"Retrieved wallet from reserve: {wallet.public_key}")
        return wallet
    
    def activate_wallet(self, wallet: BurnerWallet) -> BurnerWallet:
        """
        Move wallet to active pool
        
        Args:
            wallet: Wallet to activate
            
        Returns:
            Activated wallet
        """
        wallet.status = WalletStatus.ACTIVE
        self.active_pool[str(wallet.public_key)] = wallet
        
        logger.debug(f"Activated wallet: {wallet.public_key}")
        return wallet
    
    def get_active_wallet(self, public_key: Optional[Pubkey] = None) -> Optional[BurnerWallet]:
        """
        Get wallet from active pool
        
        Args:
            public_key: Specific public key (returns random if None)
            
        Returns:
            Active wallet or None
        """
        if public_key:
            return self.active_pool.get(str(public_key))
        
        if not self.active_pool:
            return None
        
        # Return first available
        return next(iter(self.active_pool.values()))
    
    def retire_wallet(self, wallet: BurnerWallet):
        """
        Move wallet to retired pool
        
        Args:
            wallet: Wallet to retire
        """
        # Remove from current pool
        key = str(wallet.public_key)
        if key in self.active_pool:
            del self.active_pool[key]
        elif key in self.reserve_pool:
            del self.reserve_pool[key]
        
        # Add to retired
        wallet.status = WalletStatus.RETIRED
        self.retired_pool[key] = wallet
        
        # Clear sensitive data (keep only public key for tracking)
        wallet.keypair = None  # Clear from memory
        wallet.encrypted_private_key = None
        
        logger.info(f"Retired wallet: {wallet.public_key}")
    
    def get_wallet(self, public_key: Pubkey) -> Optional[BurnerWallet]:
        """
        Get wallet from any pool
        
        Args:
            public_key: Wallet public key
            
        Returns:
            Wallet if found, None otherwise
        """
        key = str(public_key)
        
        if key in self.active_pool:
            return self.active_pool[key]
        elif key in self.reserve_pool:
            return self.reserve_pool[key]
        elif key in self.retired_pool:
            return self.retired_pool[key]
        
        return None
    
    def maintain_reserve_pool(self):
        """
        Maintain reserve pool size by generating new wallets if needed
        """
        current_size = len(self.reserve_pool)
        
        if current_size < self.min_reserve_size:
            needed = self.min_reserve_size - current_size
            logger.info(f"Reserve pool below minimum ({current_size}/{self.min_reserve_size}), generating {needed} wallets")
            
            for _ in range(needed):
                self.add_to_reserve()
    
    def cleanup_expired_wallets(self, max_age_hours: int = 24):
        """
        Clean up expired wallets from all pools
        
        Args:
            max_age_hours: Maximum age in hours
        """
        expired = []
        
        # Check active pool
        for wallet in list(self.active_pool.values()):
            if wallet.is_expired(max_age_hours):
                expired.append(wallet)
        
        # Check reserve pool
        for wallet in list(self.reserve_pool.values()):
            if wallet.is_expired(max_age_hours):
                expired.append(wallet)
        
        # Retire expired wallets
        for wallet in expired:
            self.retire_wallet(wallet)
        
        if expired:
            logger.info(f"Retired {len(expired)} expired wallets")
    
    def get_pool_stats(self) -> dict:
        """
        Get statistics about pools
        
        Returns:
            Dictionary with pool statistics
        """
        return {
            "active": len(self.active_pool),
            "reserve": len(self.reserve_pool),
            "retired": len(self.retired_pool),
            "total": len(self.active_pool) + len(self.reserve_pool) + len(self.retired_pool)
        }

