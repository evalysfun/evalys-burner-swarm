"""
Evalys Burner Swarm

Manages disposable wallets (burner wallets) for privacy-preserving transactions.
Provides wallet generation, pool management, JIT funding, and rotation strategies.
"""

from .wallet_generator import WalletGenerator
from .pool_manager import PoolManager, BurnerWallet, WalletStatus
from .funding_manager import FundingManager
from .rotation_strategy import RotationStrategy
from .burner_swarm_fabric import BurnerSwarmFabric

__all__ = [
    "WalletGenerator",
    "PoolManager",
    "BurnerWallet",
    "WalletStatus",
    "FundingManager",
    "RotationStrategy",
    "BurnerSwarmFabric",
]

__version__ = "0.1.0"

