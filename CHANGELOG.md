# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation (swarm-spec.md, linkability.md)
- Policy engine for risk-based rotation and funding
- Scheduler for timing jitter and staggered operations
- Invariant tests (lifecycle, rotation, funding diversity, secret leakage)
- Runnable demo script (examples/demo-spawn.py)
- CHANGELOG.md and ROADMAP.md

### Changed
- Updated README with honest staging (Implemented vs Planned)
- Enhanced architecture documentation with lifecycle states

## [0.1.0] - 2024-01-XX

### Added
- Initial release of Burner Swarm Fabric
- Wallet generation with secure keypair creation
- Pool management (active, reserve, retired pools)
- JIT funding with basic linkability mitigation
- Rotation strategies (usage and time-based)
- REST API with FastAPI
- Python library interface
- Basic test suite

### Known Limitations
- Basic linkability mitigation (v0.1 heuristics)
- No multi-hop funding relays
- No adaptive policy tied to curve intelligence
- Limited correlation detection

