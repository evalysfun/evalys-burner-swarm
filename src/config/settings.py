"""
Configuration settings
"""

import os


class Settings:
    """Application settings"""
    
    # Solana RPC
    SOLANA_RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    
    # Pool settings
    MIN_RESERVE_SIZE: int = int(os.getenv("MIN_RESERVE_SIZE", "5"))
    MAX_ACTIVE_SIZE: int = int(os.getenv("MAX_ACTIVE_SIZE", "10"))
    
    # Rotation settings
    MAX_USES: int = int(os.getenv("MAX_USES", "1"))
    MAX_AGE_HOURS: int = int(os.getenv("MAX_AGE_HOURS", "24"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"

