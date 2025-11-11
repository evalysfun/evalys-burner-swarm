# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Setup Shared Virtual Environment (Recommended)

Since Evalys uses multiple components, use a **shared virtual environment** at the root level:

```bash
# From evalys root directory (if not already set up)
cd ..  # Go to evalys root

# Activate virtual environment (if not already activated)
venv\Scripts\Activate.ps1  # Windows PowerShell
$env:PYTHONPATH = "."

# Navigate to burner swarm directory
cd evalys-burner-swarm

# Install dependencies
pip install -r requirements.txt
```

**Note**: The shared venv approach avoids duplication. All Evalys components share the same environment.

### 2. Run Example

```bash
# Make sure you're in evalys-burner-swarm directory
# and venv is activated with PYTHONPATH set
python example.py
```

This will demonstrate all the features of the Burner Swarm.

### 3. Use as Python Library

```python
import asyncio
from src.burner_swarm.burner_swarm_fabric import BurnerSwarmFabric

async def main():
    fabric = BurnerSwarmFabric(rpc_url="https://api.devnet.solana.com")
    
    try:
        # Get a burner wallet
        wallet = await fabric.get_burner()
        print(f"Public Key: {wallet.public_key}")
        
        # Get pool stats
        stats = fabric.get_pool_stats()
        print(stats)
    finally:
        await fabric.close()

asyncio.run(main())
```

### 4. Run as API Server

```bash
# Start the API server
python -m src.api.server

# Or use uvicorn directly
uvicorn src.api.server:app --host 0.0.0.0 --port 8001 --reload
```

Then visit:
- API Docs: http://localhost:8001/docs
- Health Check: http://localhost:8001/health

### 5. Test API

```bash
# Get a burner wallet
curl -X POST "http://localhost:8001/api/v1/burner/get" \
  -H "Content-Type: application/json" \
  -d '{}'

# Get pool stats
curl http://localhost:8001/api/v1/burner/pool-stats
```

### 6. Run Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

## 📚 Next Steps

- Read the [README.md](README.md) for detailed documentation
- Check out the [example.py](example.py) for more usage examples
- Explore the API at http://localhost:8001/docs when server is running

## 🐛 Troubleshooting

### Import Errors
Make sure:
1. Virtual environment is activated
2. PYTHONPATH is set (see step 1)
3. You're in the evalys-burner-swarm directory

### Solana RPC Connection Issues
If you get connection errors:
- Check your internet connection
- Try using devnet: `rpc_url="https://api.devnet.solana.com"`
- Verify the RPC URL is correct

### Module Not Found
Make sure:
1. Virtual environment is activated
2. PYTHONPATH is set (see step 1)
3. You're in the evalys-burner-swarm directory

```bash
# Verify PYTHONPATH is set
echo $env:PYTHONPATH  # Windows PowerShell
# or
echo $PYTHONPATH      # Linux/Mac

# Run from component directory
python -m src.api.server
```

### Port Already in Use
Change the port in environment variable:
```bash
export API_PORT=8002
```

