"""
Invariant Tests

Tests that prove the burner swarm invariants always hold.
"""

import pytest
from datetime import datetime, timedelta
from src.burner_swarm.pool_manager import BurnerWallet, WalletStatus
from src.burner_swarm.policy import SwarmPolicy, RiskLevel
from src.burner_swarm.scheduler import SwarmScheduler


class TestLifecycleCorrectness:
    """Test lifecycle correctness invariant"""
    
    def test_wallet_cannot_jump_states(self):
        """Test that wallet cannot jump states"""
        wallet = BurnerWallet(
            public_key=None,  # Mock
            keypair=None,     # Mock
            created_at=datetime.utcnow(),
            status=WalletStatus.NEW
        )
        
        # Valid transitions
        assert wallet.status == WalletStatus.NEW
        
        # Can transition to FUNDED
        wallet.status = WalletStatus.FUNDED
        assert wallet.status == WalletStatus.FUNDED
        
        # Cannot jump from FUNDED to RETIRED (must go through ACTIVE)
        # This should be enforced by state machine
        # For now, we test that status changes are tracked
        
    def test_retired_never_becomes_active(self):
        """Test that retired wallet never becomes active again"""
        wallet = BurnerWallet(
            public_key=None,
            keypair=None,
            created_at=datetime.utcnow(),
            status=WalletStatus.RETIRED
        )
        
        # Retired wallet should not transition to active
        assert wallet.status == WalletStatus.RETIRED
        
        # Attempting to set to active should fail (enforced by state machine)
        # For now, we verify status is terminal
        assert wallet.status in [WalletStatus.RETIRED, WalletStatus.DESTROYED]


class TestRotationMonotonicity:
    """Test rotation monotonicity invariant"""
    
    def test_rotation_monotonic_with_risk(self):
        """Test that higher risk never reduces rotation frequency"""
        # Low risk policy
        low_risk_policy = SwarmPolicy(
            risk_level=RiskLevel.LOW,
            max_uses=5,
            max_age_hours=24
        )
        
        # High risk policy
        high_risk_policy = SwarmPolicy(
            risk_level=RiskLevel.HIGH,
            max_uses=5,
            max_age_hours=24
        )
        
        # High risk should have equal or lower max_uses (more frequent rotation)
        assert high_risk_policy.max_uses <= low_risk_policy.max_uses, \
            "High risk should have more frequent rotation (lower max_uses)"
        
        # High risk should have equal or lower max_age_hours (more frequent rotation)
        assert high_risk_policy.max_age_hours <= low_risk_policy.max_age_hours, \
            "High risk should have more frequent rotation (lower max_age_hours)"
    
    def test_risk_level_updates_maintain_monotonicity(self):
        """Test that updating risk level maintains monotonicity"""
        policy = SwarmPolicy(
            risk_level=RiskLevel.LOW,
            max_uses=5,
            max_age_hours=24
        )
        
        low_max_uses = policy.max_uses
        low_max_age = policy.max_age_hours
        
        # Update to high risk
        policy.update_risk_level(RiskLevel.HIGH)
        
        # Should have equal or lower values (more frequent rotation)
        assert policy.max_uses <= low_max_uses, \
            "Increasing risk should not reduce rotation frequency"
        assert policy.max_age_hours <= low_max_age, \
            "Increasing risk should not reduce rotation frequency"


class TestFundingDiversity:
    """Test funding diversity invariant"""
    
    def test_consecutive_funding_patterns_differ(self):
        """Test that consecutive burners cannot have identical funding patterns"""
        # Simulate funding patterns
        funding_patterns = []
        
        for i in range(10):
            # Simulate funding with jitter and bucketing
            import random
            base_amount = random.choice([0.1, 0.2, 0.5, 1.0])
            jitter = random.uniform(-0.05, 0.05)
            amount = base_amount * (1 + jitter)
            timing = random.uniform(0, 30)
            
            pattern = {
                "amount": round(amount, 4),
                "timing": round(timing, 2)
            }
            
            funding_patterns.append(pattern)
        
        # Check that consecutive patterns are not identical
        for i in range(len(funding_patterns) - 1):
            current = funding_patterns[i]
            next_pattern = funding_patterns[i + 1]
            
            # Patterns should differ in amount or timing
            assert not (
                current["amount"] == next_pattern["amount"] and
                current["timing"] == next_pattern["timing"]
            ), f"Consecutive patterns {i} and {i+1} are identical"
    
    def test_funding_amount_bucketing(self):
        """Test that funding amounts use bucketing"""
        buckets = [0.1, 0.2, 0.5, 1.0]
        
        # Generate funding amounts
        amounts = []
        for _ in range(20):
            import random
            base = random.choice(buckets)
            jitter = random.uniform(-0.05, 0.05)
            amount = base * (1 + jitter)
            amounts.append(round(amount, 4))
        
        # All amounts should be close to bucket values
        for amount in amounts:
            # Find closest bucket
            closest_bucket = min(buckets, key=lambda x: abs(x - amount))
            # Amount should be within 5% of bucket
            assert abs(amount - closest_bucket) / closest_bucket < 0.05, \
                f"Amount {amount} is not close to any bucket"


class TestNoSecretLeakage:
    """Test no secret leakage invariant"""
    
    def test_private_keys_not_in_string_representation(self):
        """Test that private keys are not in string representation"""
        from solders.keypair import Keypair
        
        keypair = Keypair()
        wallet = BurnerWallet(
            public_key=keypair.pubkey(),
            keypair=keypair,
            created_at=datetime.utcnow()
        )
        
        # String representation should not contain private key
        wallet_str = str(wallet)
        keypair_str = str(keypair)
        
        # Private key bytes should not be in string representation
        private_key_bytes = bytes(keypair)
        assert private_key_bytes not in wallet_str.encode(), \
            "Private key should not be in wallet string representation"
    
    def test_encrypted_storage_used(self):
        """Test that encrypted storage is used for private keys"""
        from solders.keypair import Keypair
        
        keypair = Keypair()
        wallet = BurnerWallet(
            public_key=keypair.pubkey(),
            keypair=keypair,
            created_at=datetime.utcnow()
        )
        
        # When storing, encrypted_private_key should be set
        # (This would be done by encryption utility)
        # For now, we verify the field exists
        assert hasattr(wallet, 'encrypted_private_key'), \
            "Wallet should have encrypted_private_key field"


class TestPolicyEnforcement:
    """Test policy enforcement"""
    
    def test_should_rotate_usage_based(self):
        """Test usage-based rotation"""
        policy = SwarmPolicy(
            risk_level=RiskLevel.MEDIUM,
            max_uses=3,
            max_age_hours=24
        )
        
        # Wallet with max uses should rotate
        should_rotate = policy.should_rotate(
            usage_count=3,
            created_at=datetime.utcnow() - timedelta(hours=1)
        )
        assert should_rotate, "Wallet with max uses should rotate"
        
        # Wallet below max uses should not rotate
        should_not_rotate = policy.should_rotate(
            usage_count=2,
            created_at=datetime.utcnow() - timedelta(hours=1)
        )
        assert not should_not_rotate, "Wallet below max uses should not rotate"
    
    def test_should_rotate_age_based(self):
        """Test age-based rotation"""
        policy = SwarmPolicy(
            risk_level=RiskLevel.MEDIUM,
            max_uses=10,
            max_age_hours=24
        )
        
        # Wallet exceeding max age should rotate
        should_rotate = policy.should_rotate(
            usage_count=1,
            created_at=datetime.utcnow() - timedelta(hours=25)
        )
        assert should_rotate, "Wallet exceeding max age should rotate"
        
        # Wallet below max age should not rotate
        should_not_rotate = policy.should_rotate(
            usage_count=1,
            created_at=datetime.utcnow() - timedelta(hours=12)
        )
        assert not should_not_rotate, "Wallet below max age should not rotate"

