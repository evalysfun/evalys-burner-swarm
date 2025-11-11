"""
Funding Manager

Manages Just-In-Time (JIT) funding of burner wallets.
"""

from typing import Optional
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.rpc.responses import SendTransactionResp
from solders.transaction import Transaction
from solders.system_program import transfer, TransferParams
from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import asyncio
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FundingManager:
    """
    Manages JIT funding of burner wallets
    """
    
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        """
        Initialize funding manager
        
        Args:
            rpc_url: Solana RPC endpoint URL
        """
        self.rpc_url = rpc_url
        self.client: Optional[AsyncClient] = None
        logger.info(f"FundingManager initialized with RPC: {rpc_url}")
    
    async def connect(self):
        """Connect to Solana RPC"""
        if self.client is None:
            self.client = AsyncClient(self.rpc_url)
            logger.debug("Connected to Solana RPC")
    
    async def disconnect(self):
        """Disconnect from Solana RPC"""
        if self.client:
            await self.client.close()
            self.client = None
            logger.debug("Disconnected from Solana RPC")
    
    async def get_balance(self, public_key: Pubkey) -> float:
        """
        Get SOL balance of a wallet
        
        Args:
            public_key: Wallet public key
            
        Returns:
            Balance in SOL
        """
        await self.connect()
        
        try:
            response = await self.client.get_balance(public_key, commitment=Confirmed)
            lamports = response.value
            sol_balance = lamports / 1_000_000_000  # Convert lamports to SOL
            return sol_balance
        except Exception as e:
            logger.error(f"Error getting balance for {public_key}: {e}")
            raise
    
    async def calculate_funding_amount(
        self,
        required_amount: float,
        transaction_fee: float = 0.000005,  # ~5000 lamports
        buffer: float = 0.001  # Small buffer
    ) -> float:
        """
        Calculate exact funding amount needed
        
        Args:
            required_amount: Amount needed for transaction
            transaction_fee: Estimated transaction fee
            buffer: Safety buffer
            
        Returns:
            Total funding amount
        """
        return required_amount + transaction_fee + buffer
    
    async def fund_wallet(
        self,
        burner_wallet: Pubkey,
        source_wallet: Keypair,
        amount_sol: float,
        priority_fee: Optional[int] = None
    ) -> str:
        """
        Fund a burner wallet from source wallet
        
        Args:
            burner_wallet: Burner wallet public key to fund
            source_wallet: Source wallet keypair
            amount_sol: Amount to send in SOL
            priority_fee: Optional priority fee in microlamports
            
        Returns:
            Transaction signature
        """
        await self.connect()
        
        try:
            # Convert SOL to lamports
            lamports = int(amount_sol * 1_000_000_000)
            
            # Get recent blockhash
            blockhash_resp = await self.client.get_latest_blockhash(commitment=Confirmed)
            recent_blockhash = blockhash_resp.value.blockhash
            
            # Create transfer instruction
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=source_wallet.pubkey(),
                    to_pubkey=burner_wallet,
                    lamports=lamports
                )
            )
            
            # Build transaction
            transaction = Transaction()
            transaction.add(transfer_ix)
            
            # Add priority fee if specified
            if priority_fee:
                transaction.add(set_compute_unit_price(priority_fee))
                transaction.add(set_compute_unit_limit(200_000))
            
            # Sign and send
            transaction.sign([source_wallet], recent_blockhash)
            
            response = await self.client.send_transaction(
                transaction,
                source_wallet,
                commitment=Confirmed
            )
            
            signature = str(response.value)
            logger.info(
                f"Funded wallet {burner_wallet} with {amount_sol} SOL. "
                f"Signature: {signature}"
            )
            
            return signature
            
        except Exception as e:
            logger.error(f"Error funding wallet {burner_wallet}: {e}")
            raise
    
    async def fund_wallet_jit(
        self,
        burner_wallet: Pubkey,
        source_wallet: Keypair,
        required_amount: float,
        priority_fee: Optional[int] = None
    ) -> str:
        """
        Fund wallet Just-In-Time with exact amount needed
        
        Args:
            burner_wallet: Burner wallet to fund
            source_wallet: Source wallet
            required_amount: Amount needed for transaction
            priority_fee: Optional priority fee
            
        Returns:
            Transaction signature
        """
        # Calculate exact amount needed
        funding_amount = await self.calculate_funding_amount(required_amount)
        
        # Fund the wallet
        return await self.fund_wallet(
            burner_wallet,
            source_wallet,
            funding_amount,
            priority_fee
        )
    
    async def check_funding_status(self, public_key: Pubkey) -> dict:
        """
        Check funding status of a wallet
        
        Args:
            public_key: Wallet public key
            
        Returns:
            Dictionary with funding status
        """
        balance = await self.get_balance(public_key)
        
        return {
            "public_key": str(public_key),
            "balance_sol": balance,
            "balance_lamports": int(balance * 1_000_000_000),
            "is_funded": balance > 0
        }

