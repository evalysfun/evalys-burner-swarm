"""
Burner Swarm Fabric

Main interface for managing burner wallet swarms.
"""

from typing import Optional, List
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from .pool_manager import PoolManager, BurnerWallet, WalletStatus
from .funding_manager import FundingManager
from .rotation_strategy import RotationStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BurnerSwarmFabric:
    """
    Main interface for burner swarm management
    
    Provides high-level API for:
    - Getting burner wallets
    - Managing pools
    - JIT funding
    - Wallet rotation
    """
    
    def __init__(
        self,
        rpc_url: str = "https://api.mainnet-beta.solana.com",
        min_reserve_size: int = 5,
        max_active_size: int = 10,
        max_uses: int = 1,
        max_age_hours: int = 24
    ):
        """
        Initialize burner swarm fabric
        
        Args:
            rpc_url: Solana RPC endpoint
            min_reserve_size: Minimum reserve pool size
            max_active_size: Maximum active pool size
            max_uses: Maximum uses per wallet
            max_age_hours: Maximum age in hours
        """
        self.pool_manager = PoolManager(
            min_reserve_size=min_reserve_size,
            max_active_size=max_active_size
        )
        
        self.funding_manager = FundingManager(rpc_url=rpc_url)
        self.rotation_strategy = RotationStrategy(
            max_uses=max_uses,
            max_age_hours=max_age_hours
        )
        
        # Initialize reserve pool
        self.pool_manager.maintain_reserve_pool()
        
        logger.info("BurnerSwarmFabric initialized")
    
    async def get_burner(
        self,
        auto_fund: bool = False,
        source_wallet: Optional[Keypair] = None,
        funding_amount: Optional[float] = None
    ) -> BurnerWallet:
        """
        Get a burner wallet from the pool
        
        Args:
            auto_fund: Automatically fund the wallet
            source_wallet: Source wallet for funding
            funding_amount: Amount to fund (if auto_fund is True)
            
        Returns:
            BurnerWallet instance
        """
        # Get from reserve or generate new
        wallet = self.pool_manager.get_from_reserve()
        
        if wallet is None:
            logger.info("Reserve pool empty, generating new wallet")
            wallet = self.pool_manager.generate_wallet()
        
        # Activate wallet
        wallet = self.pool_manager.activate_wallet(wallet)
        
        # Auto-fund if requested
        if auto_fund and source_wallet and funding_amount:
            try:
                await self.funding_manager.fund_wallet_jit(
                    wallet.public_key,
                    source_wallet,
                    funding_amount
                )
                logger.info(f"Auto-funded wallet {wallet.public_key} with {funding_amount} SOL")
            except Exception as e:
                logger.error(f"Failed to auto-fund wallet: {e}")
                raise
        
        # Maintain reserve pool
        self.pool_manager.maintain_reserve_pool()
        
        logger.debug(f"Retrieved burner wallet: {wallet.public_key}")
        return wallet
    
    async def get_burner_swarm(
        self,
        count: int,
        auto_fund: bool = False,
        source_wallet: Optional[Keypair] = None,
        funding_amount: Optional[float] = None
    ) -> List[BurnerWallet]:
        """
        Get multiple burner wallets (swarm)
        
        Args:
            count: Number of wallets to get
            auto_fund: Automatically fund wallets
            source_wallet: Source wallet for funding
            funding_amount: Amount to fund per wallet
            
        Returns:
            List of BurnerWallet instances
        """
        wallets = []
        
        for i in range(count):
            wallet = await self.get_burner(
                auto_fund=auto_fund,
                source_wallet=source_wallet,
                funding_amount=funding_amount
            )
            wallets.append(wallet)
        
        logger.info(f"Retrieved burner swarm of {count} wallets")
        return wallets
    
    def mark_wallet_used(self, wallet: BurnerWallet):
        """
        Mark wallet as used
        
        Args:
            wallet: Wallet to mark
        """
        wallet.mark_used()
        
        # Check if should rotate
        if self.rotation_strategy.should_rotate(wallet):
            logger.info(f"Rotating wallet {wallet.public_key} (usage: {wallet.usage_count})")
            self.pool_manager.retire_wallet(wallet)
            self.pool_manager.maintain_reserve_pool()
    
    async def fund_wallet(
        self,
        wallet: BurnerWallet,
        source_wallet: Keypair,
        amount_sol: float
    ) -> str:
        """
        Fund a burner wallet
        
        Args:
            wallet: Wallet to fund
            source_wallet: Source wallet
            amount_sol: Amount in SOL
            
        Returns:
            Transaction signature
        """
        return await self.funding_manager.fund_wallet_jit(
            wallet.public_key,
            source_wallet,
            amount_sol
        )
    
    async def get_wallet_balance(self, wallet: BurnerWallet) -> float:
        """
        Get balance of a wallet
        
        Args:
            wallet: Wallet to check
            
        Returns:
            Balance in SOL
        """
        return await self.funding_manager.get_balance(wallet.public_key)
    
    def rotate_wallet(self, wallet: BurnerWallet):
        """
        Manually rotate a wallet
        
        Args:
            wallet: Wallet to rotate
        """
        self.pool_manager.retire_wallet(wallet)
        self.pool_manager.maintain_reserve_pool()
        logger.info(f"Manually rotated wallet {wallet.public_key}")
    
    def cleanup_expired_wallets(self):
        """Clean up expired wallets"""
        self.pool_manager.cleanup_expired_wallets(
            max_age_hours=self.rotation_strategy.max_age_hours
        )
    
    def get_pool_stats(self) -> dict:
        """
        Get pool statistics
        
        Returns:
            Dictionary with pool stats
        """
        return self.pool_manager.get_pool_stats()
    
    async def close(self):
        """Close connections and cleanup"""
        await self.funding_manager.disconnect()
        logger.info("BurnerSwarmFabric closed")

