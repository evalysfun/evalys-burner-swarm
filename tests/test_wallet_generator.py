"""
Tests for wallet generator
"""

import pytest
from src.burner_swarm.wallet_generator import WalletGenerator
from solders.keypair import Keypair


def test_wallet_generator_init():
    """Test wallet generator initialization"""
    generator = WalletGenerator()
    assert generator.generated_count == 0


def test_generate_keypair():
    """Test keypair generation"""
    generator = WalletGenerator()
    
    keypair = generator.generate_keypair()
    
    assert isinstance(keypair, Keypair)
    assert generator.generated_count == 1
    
    # Generate another
    keypair2 = generator.generate_keypair()
    assert generator.generated_count == 2
    assert keypair.pubkey() != keypair2.pubkey()


def test_get_public_key():
    """Test getting public key"""
    generator = WalletGenerator()
    keypair = generator.generate_keypair()
    
    pubkey = generator.get_public_key(keypair)
    assert pubkey == keypair.pubkey()


def test_get_private_key_bytes():
    """Test getting private key bytes"""
    generator = WalletGenerator()
    keypair = generator.generate_keypair()
    
    private_bytes = generator.get_private_key_bytes(keypair)
    assert len(private_bytes) == 64  # Solana keypair is 64 bytes


def test_generate_from_seed():
    """Test generating from seed"""
    generator = WalletGenerator()
    seed = generator.generate_random_seed()
    
    keypair1 = generator.generate_from_seed(seed)
    keypair2 = generator.generate_from_seed(seed)
    
    # Same seed should produce same keypair
    assert keypair1.pubkey() == keypair2.pubkey()


def test_encrypt_decrypt_keypair():
    """Test keypair encryption/decryption"""
    generator = WalletGenerator()
    keypair = generator.generate_keypair()
    
    # Encrypt
    encrypted = generator.encrypt_keypair(keypair)
    assert "public_key" in encrypted
    assert "encrypted_private_key" in encrypted
    
    # Decrypt
    decrypted = generator.decrypt_keypair(encrypted)
    assert decrypted.pubkey() == keypair.pubkey()

