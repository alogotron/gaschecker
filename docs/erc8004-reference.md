# ERC-8004 Reference Guide

## Official Resources

| Resource | URL | Description |
|----------|-----|-------------|
| **8004.org** | https://www.8004.org/build | Official ERC-8004 community - builders portal |
| **8004agents.ai** | https://8004agents.ai/ | Multichain AI Agent Explorer & Directory |
| **EIP Discussion** | https://ethereum-magicians.org/t/erc-8004-trustless-agents/25098 | Ethereum Magicians discussion |
| **Agent0 SDK (Python)** | https://pypi.org/project/agent0-sdk/ | Python SDK for ERC-8004 |
| **Agent0 SDK (GitHub)** | https://github.com/agent0lab/agent0-py | Source code & examples |
| **Agent0 Telegram** | https://t.me/agent0kitchen | Community support channel |

---

## What is ERC-8004?

ERC-8004 is an Ethereum standard for **Trustless Autonomous Agents** that enables:

1. **Discovery** - Find agents across organizational boundaries
2. **Trust** - Establish trust through reputation and validation
3. **Interaction** - Enable open-ended agent economies

### Key Authors
- Marco De Rossi (@MarcoMetaMask)
- Davide Crapis (@dcrapis) - Ethereum Foundation
- Jordan Ellis - Google
- Erik Reppel - Coinbase

---

## Three Core Registries

### 1. Identity Registry
- Based on ERC-721 (NFT standard)
- Each agent gets unique on-chain identity
- Global identifier format: `{namespace}:{chainId}:{identityRegistry}:{agentId}`
- Example: `eip155:8453:0x742...:17171` (Base chain)

### 2. Reputation Registry
- Post and fetch feedback signals
- On-chain scoring for composability
- Off-chain aggregation for algorithms
- Enables auditor networks & insurance pools

### 3. Validation Registry
- Independent validator checks
- Support for: stakers, zkML verifiers, TEE oracles, trusted judges

---

## Agent Registration File Format

```json
{
  "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
  "name": "myAgentName",
  "description": "What the agent does, pricing, interaction methods",
  "image": "https://example.com/agentimage.png",
  "services": [
    {
      "name": "MCP",
      "endpoint": "https://mcp.agent.example/",
      "version": "2025-06-18"
    },
    {
      "name": "A2A",
      "endpoint": "https://agent.example/.well-known/agent-card.json",
      "version": "0.3.0"
    }
  ],
  "x402Support": true,
  "active": true,
  "trustModels": {
    "reputation": true,
    "cryptoEconomic": true
  }
}
```

---

## Supported Chains

| Chain | Chain ID | Status |
|-------|----------|--------|
| Ethereum Mainnet | 1 | ✅ Supported |
| Ethereum Sepolia | 11155111 | ✅ Testnet |
| Base | 8453 | ✅ Supported |
| Linea | 59144 | ✅ Supported |
| Polygon | 137 | ✅ Supported |
| Arbitrum | 42161 | ✅ Supported |
| Optimism | 10 | ✅ Supported |

---

## Quick Start with Agent0 SDK

### Installation
```bash
pip install agent0-sdk
```

### Register an Agent
```python
from agent0_sdk import SDK
import os

# Initialize SDK
sdk = SDK(
    chainId=8453,  # Base
    rpcUrl=os.getenv("RPC_URL"),
    signer=os.getenv("PRIVATE_KEY"),
    ipfs="pinata",
    pinataJwt=os.getenv("PINATA_JWT")
)

# Create agent
agent = sdk.createAgent(
    name="GasChecker",
    description="Multi-chain gas price oracle for AI agents",
    image="https://example.com/gas-icon.png"
)

# Configure MCP endpoint
agent.setMCP("https://gaschecker.example.com/")
agent.setTrust(reputation=True)
agent.setActive(True)

# Register on-chain
reg_tx = agent.registerIPFS()
print(f"Registered! Agent ID: {reg_tx.agentId}")
```

### Search for Agents
```python
# Search by capability
results = sdk.searchAgents(
    capabilities=["gas-prices", "blockchain"],
    chains=[8453],
    limit=10
)

for agent in results:
    print(f"{agent.name}: {agent.services}")
```

---

## Integration with Other Protocols

### MCP (Model Context Protocol)
- Servers list capabilities: prompts, resources, tools
- ERC-8004 publishes MCP endpoints for discovery

### A2A (Agent2Agent)
- Agent authentication and skills advertisement
- Direct messaging and task orchestration
- ERC-8004 adds trust layer on top

### x402 (HTTP Payments)
- Micropayments for agent services
- USDC on Base network
- Enriches feedback signals with payment data

---

## GasChecker Registration Example

Our GasChecker agent is registered at:
- **Chain:** Base (8453)
- **Agent ID:** 17171
- **Full ID:** `eip155:8453:<registry>:17171`
- **Registration File:** https://raw.githubusercontent.com/alogotron/gaschecker/main/registration.json

### Registration File
```json
{
  "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
  "name": "GasChecker",
  "description": "Multi-chain gas price oracle MCP server for AI agents",
  "services": [
    {
      "name": "MCP",
      "endpoint": "https://gaschecker-alogotrons-projects.vercel.app/mcp",
      "version": "2025-06-18"
    }
  ],
  "x402Support": true,
  "active": true
}
```

---

## Trust Models

ERC-8004 supports pluggable trust models:

| Model | Use Case | Security Level |
|-------|----------|----------------|
| **Reputation** | Client feedback | Low-Medium |
| **Stake-secured** | Re-execution by stakers | Medium-High |
| **zkML Proofs** | Verifiable inference | High |
| **TEE Oracles** | Trusted execution | High |

Security is proportional to value at risk:
- Low stakes (ordering pizza) → reputation only
- High stakes (medical diagnosis) → zkML + TEE

---

## Related Documentation

- [Agent0 SDK Guide](./agent0-sdk.md) - Detailed SDK usage
- [x402 Protocol](./x402-protocol.md) - Payment integration
- [Subgraph API](./8004-subgraph.md) - Indexing and search

---

*Last updated: 2026-02-13*
