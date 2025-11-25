"""
Burner Swarm Demo

Demonstrates spawning a swarm of burner wallets with funding and rotation.
Perfect for screen recordings and promotional videos.
"""

import sys
import time
from datetime import datetime, timedelta

# Suppress logging for cleaner output
import logging
logging.getLogger().setLevel(logging.CRITICAL)

def print_header(title: str, char: str = "="):
    """Print formatted header"""
    width = 70
    print("\n" + char * width)
    print(f"  {title}".center(width))
    print(char * width + "\n")

def print_section(title: str):
    """Print section title"""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}\n")

def print_success(message: str):
    """Print success message"""
    print(f"     ✅ {message}")
    time.sleep(0.2)

def print_info(message: str):
    """Print info message"""
    print(f"     ℹ️  {message}")
    time.sleep(0.2)

def print_data(label: str, value: str):
    """Print data label and value"""
    print(f"     {label:.<30} {value}")

def main():
    """Main demo function"""
    # Clear screen
    print("\n" * 2)
    
    # Header
    print_header("EVALYS BURNER SWARM", "═")
    print("  Disposable Wallet Management for Privacy-Preserving Transactions")
    print(f"  Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(1)
    
    # Overview
    print_section("OVERVIEW")
    print("  The Burner Swarm manages disposable wallets with:")
    print("    • Lifecycle management (NEW → FUNDED → ACTIVE → RETIRED)")
    print("    • Risk-based rotation policies")
    print("    • JIT funding with linkability mitigation")
    print("    • Pool management (active, reserve, retired)")
    time.sleep(2)
    
    # Swarm Configuration
    print_section("SWARM CONFIGURATION")
    
    config = {
        "risk_level": "medium",
        "min_reserve_size": 5,
        "max_active_size": 10,
        "max_uses": 1,
        "max_age_hours": 24,
        "swarm_size": 5
    }
    
    print_success("Swarm configuration loaded")
    print_data("Risk Level", config["risk_level"].upper())
    print_data("Min Reserve Size", str(config["min_reserve_size"]))
    print_data("Max Active Size", str(config["max_active_size"]))
    print_data("Max Uses per Wallet", str(config["max_uses"]))
    print_data("Max Age", f"{config['max_age_hours']} hours")
    print_data("Swarm Size", str(config["swarm_size"]))
    time.sleep(1)
    
    # Wallet Generation
    print_section("WALLET GENERATION")
    
    # Simulated wallet generation
    wallets = []
    for i in range(config["swarm_size"]):
        # Simulated public key
        pubkey = f"Burner{i+1}" + "x" * 40
        wallets.append({
            "public_key": pubkey,
            "created_at": datetime.now(),
            "status": "NEW"
        })
    
    print_success(f"Generated {len(wallets)} burner wallets")
    for i, wallet in enumerate(wallets[:3], 1):
        print(f"     Wallet {i}: {wallet['public_key'][:32]}...")
    if len(wallets) > 3:
        print(f"     ... and {len(wallets) - 3} more wallets")
    time.sleep(1.5)
    
    # Funding
    print_section("JIT FUNDING")
    
    funding_amounts = [0.1, 0.2, 0.15, 0.25, 0.1]  # Bucketed amounts with diversity
    
    print_success("Funding wallets with linkability mitigation")
    print_info("Using amount bucketing and timing jitter")
    
    for i, (wallet, amount) in enumerate(zip(wallets, funding_amounts), 1):
        wallets[i-1]["status"] = "FUNDED"
        wallets[i-1]["balance"] = amount
        wallets[i-1]["funded_at"] = datetime.now()
        
        if i <= 3:
            print(f"     Wallet {i}: {amount:.2f} SOL (funded)")
            time.sleep(0.3)
    
    if len(wallets) > 3:
        print(f"     ... and {len(wallets) - 3} more wallets funded")
    
    print()
    print_info("Funding diversity: Consecutive wallets have different amounts")
    time.sleep(1.5)
    
    # Activation
    print_section("WALLET ACTIVATION")
    
    for i, wallet in enumerate(wallets, 1):
        wallets[i-1]["status"] = "ACTIVE"
        wallets[i-1]["activated_at"] = datetime.now()
    
    print_success(f"Activated {len(wallets)} wallets")
    print_data("Active Pool Size", str(len(wallets)))
    print_data("Reserve Pool Size", str(config["min_reserve_size"]))
    time.sleep(1)
    
    # Rotation Schedule
    print_section("ROTATION SCHEDULE")
    
    # Simulated rotation schedule (works without actual modules)
    rotation_schedule = {
        "rotation_frequency_hours": 24,
        "risk_based": True,
        "risk_level": "medium",
        "schedule": [
            {"rotation_timestamp": int((datetime.now() + timedelta(hours=24)).timestamp())},
            {"rotation_timestamp": int((datetime.now() + timedelta(hours=24.5)).timestamp())},
            {"rotation_timestamp": int((datetime.now() + timedelta(hours=25)).timestamp())},
            {"rotation_timestamp": int((datetime.now() + timedelta(hours=25.5)).timestamp())},
            {"rotation_timestamp": int((datetime.now() + timedelta(hours=26)).timestamp())}
        ]
    }
    
    print_success("Rotation schedule created")
    print_data("Rotation Frequency", f"{rotation_schedule['rotation_frequency_hours']} hours")
    print_data("Risk-Based", "Yes" if rotation_schedule["risk_based"] else "No")
    print_data("Risk Level", rotation_schedule["risk_level"].upper())
    print()
    print("     Next Rotations:")
    for i, entry in enumerate(rotation_schedule["schedule"][:3], 1):
        rotation_time = datetime.fromtimestamp(entry["rotation_timestamp"])
        print(f"       Wallet {i}: {rotation_time.strftime('%H:%M:%S')}")
    if len(rotation_schedule["schedule"]) > 3:
        print(f"       ... and {len(rotation_schedule['schedule']) - 3} more")
    time.sleep(1.5)
    
    # Linkability Mitigation
    print_section("LINKABILITY MITIGATION")
    
    print_success("Linkability mitigations applied")
    print()
    print("     Mitigations:")
    print("       • Timing Jitter: Random delays (0-30s)")
    print("       • Amount Bucketing: [0.1, 0.2, 0.5, 1.0] SOL")
    print("       • Staggered Funding: 5-60s between wallets")
    print("       • Rotation Jitter: ±2 hours")
    print("       • Multi-RPC Support: RPC rotation enabled")
    time.sleep(1.5)
    
    # Pool Statistics
    print_section("POOL STATISTICS")
    
    pool_stats = {
        "active": len(wallets),
        "reserve": config["min_reserve_size"],
        "retired": 0,
        "total": len(wallets) + config["min_reserve_size"]
    }
    
    print_success("Pool statistics")
    print_data("Active Wallets", str(pool_stats["active"]))
    print_data("Reserve Wallets", str(pool_stats["reserve"]))
    print_data("Retired Wallets", str(pool_stats["retired"]))
    print_data("Total Wallets", str(pool_stats["total"]))
    time.sleep(1)
    
    # Lifecycle States
    print_section("LIFECYCLE STATES")
    
    print("     State Machine: NEW → FUNDED → ACTIVE → COOLING → RETIRED → DESTROYED")
    print()
    print("     Current States:")
    for i, wallet in enumerate(wallets[:3], 1):
        print(f"       Wallet {i}: {wallet['status']}")
    if len(wallets) > 3:
        print(f"       ... all {len(wallets)} wallets: ACTIVE")
    time.sleep(1)
    
    # Summary
    print_section("SUMMARY")
    
    print("  Swarm Spawned Successfully")
    print()
    print("  Key Metrics:")
    print(f"    • Swarm Size: {len(wallets)} wallets")
    print(f"    • Risk Level: {config['risk_level'].upper()}")
    print(f"    • Rotation Frequency: {rotation_schedule.get('rotation_frequency_hours', 24)} hours")
    print(f"    • Pool Stats: {pool_stats['active']} active, {pool_stats['reserve']} reserve")
    print()
    print("  Privacy Features:")
    print("    • Linkability mitigation enabled")
    print("    • Risk-based rotation")
    print("    • JIT funding with diversity")
    print("    • Secure key management")
    print()
    print("  📝 Note: This is a demonstration.")
    print("     Actual swarm requires:")
    print("     • Real Solana RPC connection")
    print("     • Funded source wallet")
    print("     • On-chain transaction confirmation")
    print()
    
    # Footer
    print_header("DEMO COMPLETE", "═")
    print("  Evalys Burner Swarm - Disposable Wallets for Privacy")
    print("  See docs/swarm-spec.md for detailed specifications")
    print("  See docs/linkability.md for linkability model")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n  Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

