"""
Swarm Scheduler

Handles timing jitter, staggered operations, and rotation cadence.
"""

import random
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SwarmScheduler:
    """
    Scheduler for burner swarm operations
    
    Handles:
    - Timing jitter for funding and rotation
    - Staggered operations to reduce correlation
    - Rotation cadence management
    """
    
    def __init__(
        self,
        funding_jitter_seconds: int = 30,
        rotation_jitter_hours: float = 2.0,
        stagger_delay_seconds: int = 60
    ):
        """
        Initialize scheduler
        
        Args:
            funding_jitter_seconds: Maximum jitter for funding operations
            rotation_jitter_hours: Maximum jitter for rotation timing
            stagger_delay_seconds: Delay between staggered operations
        """
        self.funding_jitter_seconds = funding_jitter_seconds
        self.rotation_jitter_hours = rotation_jitter_hours
        self.stagger_delay_seconds = stagger_delay_seconds
        
        logger.info("SwarmScheduler initialized")
    
    def calculate_funding_delay(self) -> float:
        """
        Calculate random delay for funding operation
        
        Returns:
            Delay in seconds
        """
        delay = random.uniform(0, self.funding_jitter_seconds)
        logger.debug(f"Funding delay calculated: {delay:.2f}s")
        return delay
    
    def calculate_rotation_jitter(self, base_rotation_time: datetime) -> datetime:
        """
        Calculate jittered rotation time
        
        Args:
            base_rotation_time: Base rotation time
            
        Returns:
            Jittered rotation time
        """
        jitter_hours = random.uniform(-self.rotation_jitter_hours, self.rotation_jitter_hours)
        jittered_time = base_rotation_time + timedelta(hours=jitter_hours)
        
        logger.debug(f"Rotation jitter: {jitter_hours:.2f}h, new time: {jittered_time}")
        return jittered_time
    
    def calculate_stagger_delay(self, index: int, total: int) -> float:
        """
        Calculate stagger delay for operation
        
        Args:
            index: Operation index (0-based)
            total: Total number of operations
            
        Returns:
            Stagger delay in seconds
        """
        if index == 0:
            return 0.0
        
        # Stagger with some randomness
        base_delay = self.stagger_delay_seconds
        jitter = random.uniform(0, base_delay * 0.3)
        delay = (index * base_delay / total) + jitter
        
        logger.debug(f"Stagger delay for index {index}: {delay:.2f}s")
        return delay
    
    async def schedule_funding_operations(
        self,
        wallets: List[Any],
        funding_func: callable
    ) -> List[Dict[str, Any]]:
        """
        Schedule funding operations with jitter and staggering
        
        Args:
            wallets: List of wallets to fund
            funding_func: Async function to fund a wallet
            
        Returns:
            List of funding results
        """
        results = []
        
        for i, wallet in enumerate(wallets):
            # Calculate stagger delay
            stagger_delay = self.calculate_stagger_delay(i, len(wallets))
            if stagger_delay > 0:
                await asyncio.sleep(stagger_delay)
            
            # Calculate funding delay
            funding_delay = self.calculate_funding_delay()
            if funding_delay > 0:
                await asyncio.sleep(funding_delay)
            
            # Fund wallet
            try:
                result = await funding_func(wallet)
                results.append({
                    "wallet": wallet,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Funding failed for wallet {wallet}: {e}")
                results.append({
                    "wallet": wallet,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def create_rotation_schedule(
        self,
        wallets: List[Any],
        base_rotation_time: datetime,
        rotation_frequency_hours: float
    ) -> List[Dict[str, Any]]:
        """
        Create rotation schedule with jitter
        
        Args:
            wallets: List of wallets
            base_rotation_time: Base rotation time
            rotation_frequency_hours: Rotation frequency in hours
            
        Returns:
            List of rotation schedules
        """
        schedule = []
        
        for i, wallet in enumerate(wallets):
            # Calculate base rotation time for this wallet
            wallet_rotation_time = base_rotation_time + timedelta(
                hours=i * (rotation_frequency_hours / len(wallets))
            )
            
            # Add jitter
            jittered_time = self.calculate_rotation_jitter(wallet_rotation_time)
            
            schedule.append({
                "wallet": wallet,
                "rotation_time": jittered_time,
                "rotation_timestamp": int(jittered_time.timestamp())
            })
        
        logger.info(f"Created rotation schedule for {len(wallets)} wallets")
        return schedule

