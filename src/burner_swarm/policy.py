"""
Swarm Policy Engine

Defines and enforces policies for burner wallet lifecycle, rotation, and funding.
"""

from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime, timedelta
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SwarmPolicy:
    """
    Policy engine for burner swarm management
    
    Enforces rules for:
    - Wallet lifecycle (creation, funding, rotation, retirement)
    - Risk-based rotation schedules
    - Funding limits and diversity
    - Pool size management
    """
    
    def __init__(
        self,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        min_reserve_size: int = 5,
        max_active_size: int = 10,
        max_uses: int = 1,
        max_age_hours: int = 24
    ):
        """
        Initialize policy engine
        
        Args:
            risk_level: Current risk level
            min_reserve_size: Minimum reserve pool size
            max_active_size: Maximum active pool size
            max_uses: Maximum uses per wallet
            max_age_hours: Maximum age in hours
        """
        self.risk_level = risk_level
        self.min_reserve_size = min_reserve_size
        self.max_active_size = max_active_size
        
        # Risk-based policy adjustment
        self.max_uses = self._adjust_max_uses(max_uses, risk_level)
        self.max_age_hours = self._adjust_max_age_hours(max_age_hours, risk_level)
        
        logger.info(
            f"SwarmPolicy initialized: risk={risk_level.value}, "
            f"max_uses={self.max_uses}, max_age_hours={self.max_age_hours}"
        )
    
    def _adjust_max_uses(self, base_max_uses: int, risk_level: RiskLevel) -> int:
        """
        Adjust max uses based on risk level
        
        Higher risk → lower max uses (more frequent rotation)
        
        Args:
            base_max_uses: Base maximum uses
            risk_level: Risk level
            
        Returns:
            Adjusted max uses
        """
        adjustments = {
            RiskLevel.LOW: 1.0,        # No adjustment
            RiskLevel.MEDIUM: 0.8,     # 20% reduction
            RiskLevel.HIGH: 0.5,       # 50% reduction
            RiskLevel.CRITICAL: 0.3    # 70% reduction
        }
        
        adjustment = adjustments.get(risk_level, 1.0)
        adjusted = max(1, int(base_max_uses * adjustment))
        
        return adjusted
    
    def _adjust_max_age_hours(self, base_max_age_hours: int, risk_level: RiskLevel) -> int:
        """
        Adjust max age based on risk level
        
        Higher risk → shorter max age (more frequent rotation)
        
        Args:
            base_max_age_hours: Base maximum age in hours
            risk_level: Risk level
            
        Returns:
            Adjusted max age in hours
        """
        adjustments = {
            RiskLevel.LOW: 1.0,        # No adjustment
            RiskLevel.MEDIUM: 0.7,     # 30% reduction
            RiskLevel.HIGH: 0.4,       # 60% reduction
            RiskLevel.CRITICAL: 0.2     # 80% reduction
        }
        
        adjustment = adjustments.get(risk_level, 1.0)
        adjusted = max(1, int(base_max_age_hours * adjustment))
        
        return adjusted
    
    def should_rotate(
        self,
        usage_count: int,
        created_at: datetime,
        last_used: Optional[datetime] = None
    ) -> bool:
        """
        Determine if wallet should be rotated
        
        Args:
            usage_count: Number of times wallet has been used
            created_at: When wallet was created
            last_used: When wallet was last used (optional)
            
        Returns:
            True if wallet should be rotated
        """
        # Check usage-based rotation
        if usage_count >= self.max_uses:
            logger.debug(f"Rotation triggered: usage_count {usage_count} >= {self.max_uses}")
            return True
        
        # Check age-based rotation
        age = datetime.utcnow() - created_at
        if age >= timedelta(hours=self.max_age_hours):
            logger.debug(f"Rotation triggered: age {age} >= {self.max_age_hours}h")
            return True
        
        return False
    
    def get_rotation_schedule(
        self,
        current_time: datetime,
        num_wallets: int
    ) -> Dict[str, Any]:
        """
        Get rotation schedule for wallets
        
        Args:
            current_time: Current time
            num_wallets: Number of wallets to schedule
            
        Returns:
            Rotation schedule
        """
        # Calculate rotation frequency based on risk
        rotation_frequency_hours = self.max_age_hours
        
        # Add jitter to rotation timing
        import random
        jitter_hours = random.uniform(0, rotation_frequency_hours * 0.2)
        
        schedule = []
        for i in range(num_wallets):
            # Stagger rotations
            rotation_time = current_time + timedelta(
                hours=rotation_frequency_hours + (i * jitter_hours / num_wallets)
            )
            
            schedule.append({
                "wallet_index": i,
                "rotation_time": rotation_time,
                "rotation_timestamp": int(rotation_time.timestamp())
            })
        
        return {
            "schedule": schedule,
            "rotation_frequency_hours": rotation_frequency_hours,
            "risk_based": True,
            "risk_level": self.risk_level.value
        }
    
    def get_funding_policy(self) -> Dict[str, Any]:
        """
        Get funding policy
        
        Returns:
            Funding policy configuration
        """
        # Risk-based funding limits
        funding_limits = {
            RiskLevel.LOW: {"min": 0.01, "max": 1.0},
            RiskLevel.MEDIUM: {"min": 0.05, "max": 0.5},
            RiskLevel.HIGH: {"min": 0.1, "max": 0.3},
            RiskLevel.CRITICAL: {"min": 0.2, "max": 0.2}
        }
        
        limits = funding_limits.get(self.risk_level, funding_limits[RiskLevel.MEDIUM])
        
        return {
            "min_amount": limits["min"],
            "max_amount": limits["max"],
            "amount_bucketing": True,
            "jitter_enabled": True,
            "stagger_enabled": True
        }
    
    def update_risk_level(self, new_risk_level: RiskLevel):
        """
        Update risk level and adjust policies
        
        Args:
            new_risk_level: New risk level
        """
        old_risk = self.risk_level
        self.risk_level = new_risk_level
        
        # Recalculate policies
        self.max_uses = self._adjust_max_uses(self.max_uses, new_risk_level)
        self.max_age_hours = self._adjust_max_age_hours(self.max_age_hours, new_risk_level)
        
        logger.info(
            f"Risk level updated: {old_risk.value} → {new_risk_level.value}, "
            f"max_uses={self.max_uses}, max_age_hours={self.max_age_hours}"
        )

