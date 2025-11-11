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
├── Wallet Generator      # Keypair generation
├── Pool Manager          # Pool management
├── Funding Manager       # JIT funding
└── Rotation Strategy     # Rotation logic
```

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

# With coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_pool_manager.py
```

## 📦 Project Structure

```
evalys-burner-swarm/
├── src/
│   ├── burner_swarm/     # Core burner swarm logic
│   │   ├── wallet_generator.py
│   │   ├── pool_manager.py
│   │   ├── funding_manager.py
│   │   ├── rotation_strategy.py
│   │   └── burner_swarm_fabric.py
│   ├── api/              # REST API
│   ├── config/           # Configuration
│   └── utils/            # Utilities
├── tests/                # Tests
├── requirements.txt
├── setup.py
└── README.md
```

## 🔐 Security

- Private keys are encrypted in memory
- Keys are cleared when wallets are retired
- No persistent storage of private keys
- Secure key derivation for encryption

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

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/evalysfun/evalys-burner-swarm/issues)
- **Discord**: [Coming Soon]

---

**Evalys Burner Swarm** - Disposable wallets for privacy-preserving transactions 🔥

