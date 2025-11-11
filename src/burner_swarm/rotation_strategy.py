"""
Rotation Strategy

Implements wallet rotation strategies to prevent pattern detection.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from .pool_manager import BurnerWallet, WalletStatus
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RotationStrategy:
    """
    Manages wallet rotation strategies
    """
    
    def __init__(
        self,
        max_uses: int = 1,
        max_age_hours: int = 24,
        rotation_on_time: bool = True,
        rotation_on_use: bool = True
    ):
        """
        Initialize rotation strategy
        
        Args:
            max_uses: Maximum uses before rotation
            max_age_hours: Maximum age in hours before rotation
            rotation_on_time: Rotate based on time
            rotation_on_use: Rotate based on usage count
        """
        self.max_uses = max_uses
        self.max_age_hours = max_age_hours
        self.rotation_on_time = rotation_on_time
        self.rotation_on_use = rotation_on_use
        
        logger.info(
            f"RotationStrategy initialized: max_uses={max_uses}, "
            f"max_age_hours={max_age_hours}"
        )
    
    def should_rotate(self, wallet: BurnerWallet) -> bool:
        """
        Determine if wallet should be rotated
        
        Args:
            wallet: Wallet to check
            
        Returns:
            True if should rotate
        """
        # Check usage-based rotation
        if self.rotation_on_use and wallet.should_retire(self.max_uses):
            logger.debug(f"Wallet {wallet.public_key} should rotate: usage count {wallet.usage_count} >= {self.max_uses}")
            return True
        
        # Check time-based rotation
        if self.rotation_on_time and wallet.is_expired(self.max_age_hours):
            logger.debug(f"Wallet {wallet.public_key} should rotate: expired")
            return True
        
        return False
    
    def select_rotation_candidates(
        self,
        wallets: List[BurnerWallet],
        count: Optional[int] = None
    ) -> List[BurnerWallet]:
        """
        Select wallets that should be rotated
        
        Args:
            wallets: List of wallets to check
            count: Maximum number to return (None for all)
            
        Returns:
            List of wallets that should be rotated
        """
        candidates = [w for w in wallets if self.should_rotate(w)]
        
        # Sort by priority (most used or oldest first)
        candidates.sort(
            key=lambda w: (w.usage_count, (datetime.utcnow() - w.created_at).total_seconds()),
            reverse=True
        )
        
        if count:
            return candidates[:count]
        
        return candidates
    
    def get_rotation_recommendation(self, wallet: BurnerWallet) -> dict:
        """
        Get rotation recommendation for a wallet
        
        Args:
            wallet: Wallet to analyze
            
        Returns:
            Dictionary with rotation recommendation
        """
        should_rotate = self.should_rotate(wallet)
        reasons = []
        
        if self.rotation_on_use and wallet.usage_count >= self.max_uses:
            reasons.append(f"Usage count ({wallet.usage_count}) >= max ({self.max_uses})")
        
        if self.rotation_on_time and wallet.is_expired(self.max_age_hours):
            age_hours = (datetime.utcnow() - wallet.created_at).total_seconds() / 3600
            reasons.append(f"Age ({age_hours:.1f}h) >= max ({self.max_age_hours}h)")
        
        return {
            "should_rotate": should_rotate,
            "reasons": reasons,
            "usage_count": wallet.usage_count,
            "age_hours": (datetime.utcnow() - wallet.created_at).total_seconds() / 3600,
            "max_uses": self.max_uses,
            "max_age_hours": self.max_age_hours
        }

