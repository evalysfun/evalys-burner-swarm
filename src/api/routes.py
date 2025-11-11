"""
API Routes for Burner Swarm

REST API endpoints for burner wallet management.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from ..burner_swarm.burner_swarm_fabric import BurnerSwarmFabric
from ..config.settings import Settings
import base64

router = APIRouter(prefix="/api/v1/burner", tags=["burner"])

# Global fabric instance (in production, use dependency injection)
fabric = BurnerSwarmFabric(
    rpc_url=Settings.SOLANA_RPC_URL,
    min_reserve_size=Settings.MIN_RESERVE_SIZE,
    max_active_size=Settings.MAX_ACTIVE_SIZE,
    max_uses=Settings.MAX_USES,
    max_age_hours=Settings.MAX_AGE_HOURS
)


class GetBurnerRequest(BaseModel):
    """Request model for getting burner wallet"""
    auto_fund: bool = Field(False, description="Automatically fund the wallet")
    funding_amount: Optional[float] = Field(None, ge=0.0, description="Amount to fund in SOL")
    source_wallet_keypair: Optional[str] = Field(None, description="Base64 encoded source wallet keypair")


class GetBurnerSwarmRequest(BaseModel):
    """Request model for getting burner swarm"""
    count: int = Field(..., ge=1, le=10, description="Number of wallets to get")
    auto_fund: bool = Field(False, description="Automatically fund wallets")
    funding_amount: Optional[float] = Field(None, ge=0.0, description="Amount to fund per wallet")
    source_wallet_keypair: Optional[str] = Field(None, description="Base64 encoded source wallet keypair")


class WalletResponse(BaseModel):
    """Response model for wallet"""
    public_key: str
    created_at: str
    usage_count: int
    status: str


class FundWalletRequest(BaseModel):
    """Request model for funding wallet"""
    public_key: str
    amount_sol: float = Field(..., ge=0.0, description="Amount to fund in SOL")
    source_wallet_keypair: str = Field(..., description="Base64 encoded source wallet keypair")


def decode_keypair(keypair_str: str) -> Keypair:
    """Decode base64 keypair string"""
    try:
        keypair_bytes = base64.b64decode(keypair_str)
        return Keypair.from_bytes(keypair_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid keypair: {e}")


@router.post("/get", response_model=WalletResponse)
async def get_burner(request: GetBurnerRequest):
    """
    Get a single burner wallet
    
    Returns a burner wallet from the pool.
    """
    try:
        source_wallet = None
        if request.source_wallet_keypair:
            source_wallet = decode_keypair(request.source_wallet_keypair)
        
        wallet = await fabric.get_burner(
            auto_fund=request.auto_fund,
            source_wallet=source_wallet,
            funding_amount=request.funding_amount
        )
        
        return WalletResponse(
            public_key=str(wallet.public_key),
            created_at=wallet.created_at.isoformat(),
            usage_count=wallet.usage_count,
            status=wallet.status.value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-swarm", response_model=List[WalletResponse])
async def get_burner_swarm(request: GetBurnerSwarmRequest):
    """
    Get multiple burner wallets (swarm)
    
    Returns a list of burner wallets.
    """
    try:
        source_wallet = None
        if request.source_wallet_keypair:
            source_wallet = decode_keypair(request.source_wallet_keypair)
        
        wallets = await fabric.get_burner_swarm(
            count=request.count,
            auto_fund=request.auto_fund,
            source_wallet=source_wallet,
            funding_amount=request.funding_amount
        )
        
        return [
            WalletResponse(
                public_key=str(w.public_key),
                created_at=w.created_at.isoformat(),
                usage_count=w.usage_count,
                status=w.status.value
            )
            for w in wallets
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fund")
async def fund_wallet(request: FundWalletRequest):
    """
    Fund a burner wallet
    
    Funds a wallet from a source wallet.
    """
    try:
        source_wallet = decode_keypair(request.source_wallet_keypair)
        public_key = Pubkey.from_string(request.public_key)
        
        # Get wallet from pool
        wallet = fabric.pool_manager.get_wallet(public_key)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found in pool")
        
        signature = await fabric.fund_wallet(
            wallet,
            source_wallet,
            request.amount_sol
        )
        
        return {
            "success": True,
            "signature": signature,
            "public_key": request.public_key,
            "amount_sol": request.amount_sol
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance/{public_key}")
async def get_balance(public_key: str):
    """Get balance of a wallet"""
    try:
        pubkey = Pubkey.from_string(public_key)
        wallet = fabric.pool_manager.get_wallet(pubkey)
        
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found in pool")
        
        balance = await fabric.get_wallet_balance(wallet)
        
        return {
            "public_key": public_key,
            "balance_sol": balance,
            "balance_lamports": int(balance * 1_000_000_000)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-used/{public_key}")
async def mark_wallet_used(public_key: str):
    """Mark a wallet as used"""
    try:
        pubkey = Pubkey.from_string(public_key)
        wallet = fabric.pool_manager.get_wallet(pubkey)
        
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found in pool")
        
        fabric.mark_wallet_used(wallet)
        
        return {
            "success": True,
            "public_key": public_key,
            "usage_count": wallet.usage_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rotate/{public_key}")
async def rotate_wallet(public_key: str):
    """Manually rotate a wallet"""
    try:
        pubkey = Pubkey.from_string(public_key)
        wallet = fabric.pool_manager.get_wallet(pubkey)
        
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found in pool")
        
        fabric.rotate_wallet(wallet)
        
        return {
            "success": True,
            "public_key": public_key,
            "message": "Wallet rotated"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pool-stats")
async def get_pool_stats():
    """Get pool statistics"""
    try:
        stats = fabric.get_pool_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_expired():
    """Clean up expired wallets"""
    try:
        fabric.cleanup_expired_wallets()
        return {
            "success": True,
            "message": "Cleanup completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

