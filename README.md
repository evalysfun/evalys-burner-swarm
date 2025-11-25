# Evalys Burner Swarm

Burner Swarm Fabric - Manages disposable wallets (burner wallets) for privacy-preserving transactions on Solana.

## 🎯 Overview

The Burner Swarm provides:
- 🔥 **Disposable Wallets**: Generate and manage burner wallets
- 🏊 **Pool Management**: Active, reserve, and retired pools
- 💰 **JIT Funding**: Just-In-Time funding of wallets
- 🔄 **Rotation Strategies**: Automatic wallet rotation
- 🔐 **Secure Storage**: Encrypted key management

## ✨ Features

- 🔑 **Wallet Generation**: Secure Solana keypair generation
- 📦 **Pool Management**: Automatic pool maintenance
- 💸 **JIT Funding**: Fund wallets only when needed
- 🔄 **Smart Rotation**: Usage and time-based rotation
- 🌐 **REST API**: Full API for integration
- 📦 **Standalone**: Can be used independently

## 🚀 Installation

### From Source (Recommended: Shared Virtual Environment)

For the Evalys ecosystem, use a **shared virtual environment** at the root level:

```bash
# From evalys root directory (if not already set up)
python -m venv venv
venv\Scripts\Activate.ps1  # Windows PowerShell
$env:PYTHONPATH = "."

# Navigate to component directory
cd evalys-burner-swarm

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

**Note**: Using a shared venv at the root avoids duplication. All Evalys components share the same environment.

### Standalone Installation

If using this component independently:

```bash
git clone https://github.com/evalysfun/evalys-burner-swarm
cd evalys-burner-swarm
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .
```

## 📖 Usage

### As Python Library

```python
import asyncio
from src.burner_swarm.burner_swarm_fabric import BurnerSwarmFabric

async def main():
    # Initialize fabric
    fabric = BurnerSwarmFabric(
        rpc_url="https://api.devnet.solana.com",
        min_reserve_size=5
    )
    
    try:
        # Get a burner wallet
        wallet = await fabric.get_burner()
        print(f"Public Key: {wallet.public_key}")
        
        # Get multiple wallets (swarm)
        swarm = await fabric.get_burner_swarm(count=3)
        
        # Mark wallet as used
        fabric.mark_wallet_used(wallet)
        
        # Check pool stats
        stats = fabric.get_pool_stats()
        print(f"Active: {stats['active']}, Reserve: {stats['reserve']}")
        
    finally:
        await fabric.close()

asyncio.run(main())
```

### With Auto-Funding

```python
from solders.keypair import Keypair

# Source wallet (your main wallet)
source_wallet = Keypair()  # Or load from file

# Get burner with auto-funding
wallet = await fabric.get_burner(
    auto_fund=True,
    source_wallet=source_wallet,
    funding_amount=0.1  # SOL
)
```

### As REST API

```bash
# Start the API server
python -m src.api.server

# Or use uvicorn directly
uvicorn src.api.server:app --host 0.0.0.0 --port 8001
```

#### API Endpoints

- `POST /api/v1/burner/get` - Get a single burner wallet
- `POST /api/v1/burner/get-swarm` - Get multiple wallets
- `POST /api/v1/burner/fund` - Fund a wallet
- `GET /api/v1/burner/balance/{public_key}` - Get wallet balance
- `POST /api/v1/burner/mark-used/{public_key}` - Mark wallet as used
- `POST /api/v1/burner/rotate/{public_key}` - Rotate a wallet
- `GET /api/v1/burner/pool-stats` - Get pool statistics
- `POST /api/v1/burner/cleanup` - Clean up expired wallets
- `GET /health` - Health check

#### Example API Request

```bash
# Get a burner wallet
curl -X POST "http://localhost:8001/api/v1/burner/get" \
  -H "Content-Type: application/json" \
  -d '{}'

# Get pool stats
curl http://localhost:8001/api/v1/burner/pool-stats
```

## 🏗️ Architecture

```
Burner Swarm Fabric
├── Swarm Manager         # Lifecycle orchestrator
├── Policy Engine         # Rotation & funding rules
├── Scheduler             # Timing jitter / cadence
├── Wallet Generator      # Keypair generation
├── Pool Manager          # Pool management (active, reserve, retired)
├── Funding Manager       # JIT funding with linkability mitigation
└── Rotation Strategy     # Rotation logic
```

**Lifecycle States**: `NEW → FUNDED → ACTIVE → COOLING → RETIRED → DESTROYED`

See [Swarm Spec](docs/swarm-spec.md) for detailed lifecycle and state transitions.

## 🔧 Configuration

Set environment variables:

```bash
export SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
export MIN_RESERVE_SIZE=5
export MAX_ACTIVE_SIZE=10
export MAX_USES=1
export MAX_AGE_HOURS=24
export API_HOST=0.0.0.0
export API_PORT=8001
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run invariant tests
pytest tests/test_invariants.py

# With coverage
pytest --cov=src --cov-report=html
```

### Invariant Tests

The swarm includes tests that prove invariants always hold:

- **Lifecycle Correctness**: Burner cannot jump states or revert
- **Retirement Irreversibility**: Retired burner never becomes active again
- **Rotation Monotonicity**: Higher risk → more frequent rotation
- **Funding Diversity**: Consecutive burners have different funding patterns
- **No Secret Leakage**: Private keys never logged or serialized

See `tests/test_invariants.py` for details.

### Demo

Run the interactive demo:

```bash
python examples/demo-spawn.py
```

This demonstrates:
- Swarm configuration
- Wallet generation
- JIT funding with linkability mitigation
- Wallet activation
- Rotation scheduling
- Pool management

Perfect for screen recordings and promotional videos.

## 📦 Project Structure

```
evalys-burner-swarm/
├── src/
│   ├── burner_swarm/     # Core burner swarm logic
│   │   ├── swarm_manager.py      # Lifecycle orchestrator
│   │   ├── policy.py             # Rotation & funding rules
│   │   ├── scheduler.py           # Timing jitter / cadence
│   │   ├── wallet_generator.py   # Keypair generation
│   │   ├── pool_manager.py       # Pool management
│   │   ├── funding_manager.py    # JIT funding
│   │   ├── rotation_strategy.py # Rotation logic
│   │   └── burner_swarm_fabric.py
│   ├── api/              # REST API
│   ├── config/           # Configuration
│   └── utils/            # Utilities
├── docs/
│   ├── swarm-spec.md     # Swarm specification
│   └── linkability.md    # Linkability model
├── examples/
│   └── demo-spawn.py     # Runnable demo
├── tests/
│   ├── test_invariants.py # Invariant tests
│   └── ...
├── CHANGELOG.md
├── ROADMAP.md
├── requirements.txt
├── setup.py
└── README.md
```

## 📝 Implementation Status

### Implemented (v0.1)

- ✅ **Lifecycle Management**: Full state machine (NEW → FUNDED → ACTIVE → RETIRED → DESTROYED)
- ✅ **Policy Engine**: Risk-based rotation and funding policies
- ✅ **Scheduler**: Timing jitter and staggered operations
- ✅ **Pool Management**: Active, reserve, and retired pools
- ✅ **JIT Funding**: Just-in-time funding with linkability mitigation
- ✅ **Rotation Strategy**: Usage and time-based rotation
- ✅ **Linkability Mitigation**: Timing jitter, amount bucketing, staggered funding
- ✅ **Invariant Tests**: Lifecycle, rotation, funding diversity, secret leakage
- ✅ **REST API**: Full API for integration
- ✅ **Python Library**: Standalone library interface
- ✅ **Documentation**: Swarm spec and linkability model

### Planned

- ⏳ **Multi-Hop Funding Relays**: Relay network for funding paths
- ⏳ **Adaptive Policy**: Policy tied to curve intelligence risk scores
- ⏳ **Arcium-Gated Funding**: Confidential funding via Arcium (if applicable)
- ⏳ **Advanced Linkability**: ML-based correlation detection and mitigation
- ⏳ **IP Diversity**: VPN/proxy rotation for additional privacy
- ⏳ **Cross-Wallet Analysis**: Detect and break correlation patterns

## 🔐 Security

- **Key Storage**: Private keys encrypted in memory, never persisted
- **Key Zeroization**: Keys securely zeroized on retirement
- **No Logging**: Private keys never logged or serialized
- **Funding Diversity**: Consecutive burners have different funding patterns
- **Rotation Timing**: Randomized rotation timing to reduce correlation

See [Swarm Spec](docs/swarm-spec.md) for security considerations.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines first.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- [evalys-privacy-engine](https://github.com/evalysfun/evalys-privacy-engine) - Privacy mode orchestration
- [evalys-launchpad-adapters](https://github.com/evalysfun/evalys-launchpad-adapters) - Launchpad integrations
- [evalys-curve-intelligence](https://github.com/evalysfun/evalys-curve-intelligence) - Curve analysis
- [evalys-execution-engine](https://github.com/evalysfun/evalys-execution-engine) - Transaction execution

## 📚 Documentation

- **[Swarm Spec](docs/swarm-spec.md)**: Detailed specification of lifecycle, states, policies, and invariants
- **[Linkability Model](docs/linkability.md)**: Linkability risks and mitigation strategies
- **[Changelog](CHANGELOG.md)**: Version history
- **[Roadmap](ROADMAP.md)**: Planned features and improvements

## 📊 Measurable Behavior

Instead of vague claims, here's what the swarm actually does:

**Lifecycle States**:
- `NEW`: Wallet generated, not funded
- `FUNDED`: Wallet funded, ready for use
- `ACTIVE`: Wallet in use
- `COOLING`: Wallet used, waiting for retirement
- `RETIRED`: Wallet retired, keys marked for cleanup
- `DESTROYED`: Keys zeroized, wallet removed

**Rotation Policy**:
- Usage-based: Rotate after `max_uses` transactions
- Time-based: Rotate after `max_age_hours` hours
- Risk-based: Higher risk → lower `max_uses` and `max_age_hours` (more frequent rotation)

**Linkability Mitigation**:
- Timing Jitter: Random delays (0-30s) for funding
- Amount Bucketing: [0.1, 0.2, 0.5, 1.0] SOL with ±5% noise
- Staggered Funding: 5-60s delays between wallets
- Rotation Jitter: ±2 hours randomization

**Invariants**:
- Lifecycle correctness: No invalid state transitions
- Retirement irreversibility: Retired never becomes active
- Rotation monotonicity: Higher risk never reduces rotation frequency
- Funding diversity: Consecutive burners have different patterns
- No secret leakage: Private keys never logged or serialized

See [Swarm Spec](docs/swarm-spec.md) and [Linkability Model](docs/linkability.md) for detailed specifications.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/evalysfun/evalys-burner-swarm/issues)
- **Documentation**: See `docs/` directory
- **Related Projects**: See below

## 🔗 Related Projects

- [evalys-privacy-engine](https://github.com/evalysfun/evalys-privacy-engine) - Privacy mode orchestration
- [evalys-launchpad-adapters](https://github.com/evalysfun/evalys-launchpad-adapters) - Launchpad integrations
- [evalys-curve-intelligence](https://github.com/evalysfun/evalys-curve-intelligence) - Curve analysis
- [evalys-execution-engine](https://github.com/evalysfun/evalys-execution-engine) - Transaction execution

---

**Evalys Burner Swarm** - Disposable wallets with formal lifecycle and linkability mitigation 🔥

