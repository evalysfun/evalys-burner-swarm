"""
Example usage of Evalys Burner Swarm
"""

import asyncio
from src.burner_swarm.burner_swarm_fabric import BurnerSwarmFabric
from solders.keypair import Keypair


async def main():
    """Example usage"""
    print("=" * 60)
    print("Evalys Burner Swarm - Example")
    print("=" * 60)
    
    # Initialize fabric (using devnet for testing)
    fabric = BurnerSwarmFabric(
        rpc_url="https://api.devnet.solana.com",  # Use devnet for testing
        min_reserve_size=3,
        max_active_size=5
    )
    
    try:
        # Example 1: Get a single burner wallet
        print("\n📋 Example 1: Get single burner wallet")
        wallet = await fabric.get_burner()
        print(f"   Public Key: {wallet.public_key}")
        print(f"   Status: {wallet.status.value}")
        print(f"   Created: {wallet.created_at}")
        print(f"   Usage count: {wallet.usage_count}")
        
        # Example 2: Get burner swarm
        print("\n📋 Example 2: Get burner swarm")
        swarm = await fabric.get_burner_swarm(count=3)
        print(f"   Retrieved {len(swarm)} wallets:")
        for i, w in enumerate(swarm, 1):
            print(f"   {i}. {w.public_key} (status: {w.status.value})")
        
        # Example 3: Check pool stats
        print("\n📋 Example 3: Pool statistics")
        stats = fabric.get_pool_stats()
        print(f"   Active: {stats['active']}")
        print(f"   Reserve: {stats['reserve']}")
        print(f"   Retired: {stats['retired']}")
        print(f"   Total: {stats['total']}")
        
        # Example 4: Mark wallet as used
        print("\n📋 Example 4: Mark wallet as used")
        if swarm:
            wallet = swarm[0]
            print(f"   Before: Usage count = {wallet.usage_count}")
            fabric.mark_wallet_used(wallet)
            print(f"   After: Usage count = {wallet.usage_count}")
        
        # Example 5: Check wallet balance (will be 0 on devnet without funding)
        print("\n📋 Example 5: Check wallet balance")
        if swarm:
            wallet = swarm[0]
            balance = await fabric.get_wallet_balance(wallet)
            print(f"   Wallet {wallet.public_key}")
            print(f"   Balance: {balance} SOL")
            print(f"   (Note: Balance will be 0 unless funded)")
        
        # Example 6: Rotation recommendation
        print("\n📋 Example 6: Rotation strategy")
        if swarm:
            wallet = swarm[0]
            recommendation = fabric.rotation_strategy.get_rotation_recommendation(wallet)
            print(f"   Should rotate: {recommendation['should_rotate']}")
            print(f"   Usage count: {recommendation['usage_count']}/{recommendation['max_uses']}")
            print(f"   Age: {recommendation['age_hours']:.2f} hours")
        
        # Example 7: Cleanup expired wallets
        print("\n📋 Example 7: Cleanup expired wallets")
        fabric.cleanup_expired_wallets()
        print("   Cleanup completed")
        
        # Final stats
        print("\n📋 Final pool statistics")
        stats = fabric.get_pool_stats()
        print(f"   Active: {stats['active']}")
        print(f"   Reserve: {stats['reserve']}")
        print(f"   Retired: {stats['retired']}")
        print(f"   Total: {stats['total']}")
        
    finally:
        # Cleanup
        await fabric.close()
    
    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

