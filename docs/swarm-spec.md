# Burner Swarm Specification

## Overview

The Burner Swarm manages disposable wallets (burner wallets) for privacy-preserving transactions on Solana. This document specifies the lifecycle, state transitions, policies, and invariants.

## Burner States

### State Machine

```
NEW → FUNDED → ACTIVE → COOLING → RETIRED → DESTROYED
```

### State Definitions

1. **NEW**: Wallet keypair generated, not yet funded
2. **FUNDED**: Wallet has been funded with SOL, ready for use
3. **ACTIVE**: Wallet is currently being used for transactions
4. **COOLING**: Wallet has been used, waiting for retirement (optional cooldown period)
5. **RETIRED**: Wallet is retired, no longer used, keys marked for cleanup
6. **DESTROYED**: Wallet keys have been zeroized, wallet removed from memory

## State Transitions

### NEW → FUNDED

**Trigger**: Funding transaction confirmed on-chain

**Conditions**:
- Wallet keypair exists
- Funding amount >= minimum funding threshold
- Funding transaction confirmed

**Failure Handling**:
- RPC failure: Retry with exponential backoff (max 3 retries)
- Insufficient funds: Return error, wallet remains in NEW state
- Transaction failure: Return error, wallet remains in NEW state

**Max Time in State**: 5 minutes (if funding fails, wallet is discarded)

### FUNDED → ACTIVE

**Trigger**: Wallet requested from pool via `get_burner()`

**Conditions**:
- Wallet is in FUNDED state
- Wallet has sufficient balance
- Pool has capacity for active wallets

**Failure Handling**:
- Insufficient balance: Mark for refunding or retirement
- Pool full: Wait or create new pool

**Max Time in State**: N/A (active until rotation)

### ACTIVE → COOLING

**Trigger**: Wallet marked as used or rotation policy triggered

**Conditions**:
- Wallet usage count >= max_uses, OR
- Wallet age >= max_age_hours, OR
- Manual rotation requested

**Failure Handling**:
- None (transition always succeeds)

**Max Time in State**: 1 hour (cooldown period)

### COOLING → RETIRED

**Trigger**: Cooldown period expires or immediate retirement

**Conditions**:
- Cooldown period elapsed, OR
- Immediate retirement requested

**Failure Handling**:
- None (transition always succeeds)

**Max Time in State**: N/A (retired until destroyed)

### RETIRED → DESTROYED

**Trigger**: Cleanup process runs

**Conditions**:
- Wallet is in RETIRED state
- Cleanup scheduled or manual cleanup requested

**Failure Handling**:
- Key zeroization failure: Log error, retry cleanup

**Max Time in State**: 24 hours (retired wallets cleaned up within 24h)

## Inputs

### Swarm Configuration

```python
{
    "risk_level": str,              # "low" | "medium" | "high" | "critical"
    "privacy_config": Dict,         # Privacy engine configuration
    "user_budget": float,           # Total budget in SOL
    "target_adapter": str,          # "pumpfun" | "bonkfun"
    "min_reserve_size": int,        # Minimum reserve pool size
    "max_active_size": int,         # Maximum active pool size
    "max_uses": int,                # Maximum uses per wallet
    "max_age_hours": int            # Maximum age in hours
}
```

### Funding Request

```python
{
    "wallet": BurnerWallet,         # Wallet to fund
    "amount": float,                # Amount in SOL
    "source_wallet": Keypair,       # Source wallet (optional)
    "funding_path": str             # "direct" | "relay" | "multi_hop"
}
```

## Outputs

### Active Burners

```python
{
    "burners": List[BurnerWallet],
    "count": int,
    "pool_stats": {
        "active": int,
        "reserve": int,
        "retired": int
    }
}
```

### Rotation Plan

```python
{
    "schedule": List[Dict],         # Rotation schedule
    "next_rotation": int,           # Unix timestamp
    "rotation_frequency": int,     # Seconds between rotations
    "risk_based": bool             # Whether rotation is risk-based
}
```

### Nullifier Commitments

```python
{
    "nullifiers": List[str],        # List of nullifier hashes
    "commitment": str,              # Merkle root of nullifiers
    "timestamp": int                # Unix timestamp
}
```

## Lifecycle Policies

### Creation Policy

- **Min Reserve Size**: Always maintain at least `min_reserve_size` wallets in reserve
- **Generation**: Generate new wallets when reserve pool is below threshold
- **Key Security**: Keys generated using cryptographically secure random

### Funding Policy

- **JIT Funding**: Fund wallets just-in-time when needed
- **Min Funding**: Minimum funding amount (default: 0.01 SOL)
- **Max Funding**: Maximum funding amount (default: 1.0 SOL)
- **Funding Diversity**: Consecutive burners cannot have identical funding patterns

### Rotation Policy

- **Usage-Based**: Rotate after `max_uses` transactions
- **Time-Based**: Rotate after `max_age_hours` hours
- **Risk-Based**: Higher risk → more frequent rotation
- **Monotonicity**: Higher risk never reduces rotation frequency

### Retirement Policy

- **Immediate**: Retire after rotation trigger
- **Cooldown**: Optional cooldown period before retirement
- **Cleanup**: Destroy keys within 24 hours of retirement

## Invariants

### 1. Lifecycle Correctness

**Statement**: Burner cannot jump states or revert to previous states.

**Enforcement**:
- State transitions are strictly ordered
- No backward transitions allowed
- State machine enforces valid transitions only

**Test**: `test_lifecycle_correctness()` - Verify no invalid state transitions

### 2. Retirement Irreversibility

**Statement**: Retired burner never becomes active again.

**Enforcement**:
- RETIRED state is terminal (except → DESTROYED)
- Retired wallets removed from active/reserve pools
- No API allows reactivation of retired wallets

**Test**: `test_retirement_irreversibility()` - Attempt to reactivate retired wallet

### 3. Rotation Monotonicity

**Statement**: Higher risk level never reduces rotation frequency.

**Enforcement**:
- Risk level maps to rotation frequency
- Higher risk → shorter max_age_hours or lower max_uses
- Policy engine enforces monotonicity

**Test**: `test_rotation_monotonicity()` - Compare rotation frequencies for different risk levels

### 4. Funding Diversity

**Statement**: Consecutive burners cannot have identical funding amount+timing pattern.

**Enforcement**:
- Track funding patterns
- Add jitter to funding amounts and timing
- Reject identical consecutive patterns

**Test**: `test_funding_diversity()` - Verify no identical consecutive funding patterns

### 5. No Secret Leakage

**Statement**: Private keys never logged, serialized, or exposed.

**Enforcement**:
- Keys stored encrypted in memory
- No logging of private keys
- Keys zeroized on retirement
- Safe logging rules enforced

**Test**: `test_no_secret_leakage()` - Verify no keys in logs or serialized output

## Failure Modes

### RPC Failures

- **Retry**: Exponential backoff (max 3 retries)
- **Fallback**: Use alternative RPC endpoint if available
- **Degradation**: Continue with cached data if possible

### Insufficient Funds

- **Source Wallet**: Return error if source wallet insufficient
- **Burner Wallet**: Mark for refunding or retirement

### Transaction Failures

- **Funding**: Retry funding transaction (max 3 retries)
- **Rotation**: Log error, retry rotation on next cycle

### Key Management Failures

- **Generation**: Retry key generation (should never fail)
- **Encryption**: Fail fast, do not store unencrypted keys
- **Zeroization**: Retry cleanup, log persistent failures

## Performance Targets

- **Wallet Generation**: < 100ms per wallet
- **Funding**: < 5 seconds per wallet (including confirmation)
- **Rotation**: < 1 second per wallet
- **Pool Maintenance**: < 2 seconds for full pool refresh

## Security Considerations

1. **Key Storage**: Keys encrypted in memory, never persisted
2. **Key Zeroization**: Keys securely zeroized on retirement
3. **No Logging**: Private keys never logged
4. **Funding Paths**: Diverse funding paths to reduce linkability
5. **Rotation Timing**: Randomized rotation timing to reduce correlation

