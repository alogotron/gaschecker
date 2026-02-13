# GasChecker - Reference Documentation

## Overview

This folder contains reference documentation for building and registering GasChecker as an ERC-8004 agent.

---

## Document Index

| Document | Description | Size |
|----------|-------------|------|
| `agent0-py-readme.md` | Python SDK documentation | 17KB |
| `agent0-ts-readme.md` | TypeScript SDK documentation | 19KB |
| `REFERENCES.md` | This file | - |

---

## Key Concepts

### ERC-8004: Trustless Agents

ERC-8004 is an Ethereum standard for AI agent coordination:

- **Identity Registry** - NFT-based agent identity (ERC-721)
- **Reputation Registry** - Feedback and scoring systems  
- **Validation Registry** - Trust verification mechanisms

### Agent0 SDK

Agent0 SDK implements ERC-8004 for Python and TypeScript:

```python
# Python Installation
pip install agent0-sdk

# TypeScript Installation  
npm install agent0-sdk
```

### Core SDK Capabilities

1. **Agent Identity Management**
   - Register on-chain with unique identity
   - Configure name, description, image
   - Set wallet addresses

2. **Capability Advertisement**
   - Publish MCP endpoints
   - Publish A2A endpoints
   - Auto-extract tools/skills from endpoints

3. **Discovery**
   - Search by attributes, capabilities, skills
   - Subgraph indexing for fast retrieval

4. **Reputation**
   - Give/receive feedback
   - Cryptographic authentication

---

## Registration Quick Reference

### Python Example

```python
from agent0_sdk import SDK
import os

# Initialize SDK
sdk = SDK(
    chainId=1,  # Ethereum Mainnet
    rpcUrl=os.getenv("RPC_URL"),
    signer=os.getenv("PRIVATE_KEY"),
    ipfs="pinata",
    pinataJwt=os.getenv("PINATA_JWT")
)

# Create and register agent
agent = sdk.createAgent(
    name="GasChecker",
    description="Multi-chain gas oracle MCP server",
    image="https://example.com/logo.png"
)

# Add MCP endpoint
agent.addEndpoint(
    protocol="MCP",
    url="https://gaschecker.example.com/mcp"
)

# Register on-chain
receipt = agent.register()
print(f"Agent ID: {receipt.agentId}")
```

### TypeScript Example

```typescript
import { SDK } from 'agent0-sdk';

const sdk = new SDK({
    chainId: 1,
    rpcUrl: process.env.RPC_URL!,
    privateKey: process.env.PRIVATE_KEY,
    ipfs: 'pinata',
    pinataJwt: process.env.PINATA_JWT
});

const agent = sdk.createAgent({
    name: "GasChecker",
    description: "Multi-chain gas oracle MCP server"
});

await agent.register();
```

---

## Supported Chains

| Chain | Chain ID | Status |
|-------|----------|--------|
| Ethereum Mainnet | 1 | Production |
| Ethereum Sepolia | 11155111 | Testnet |
| Base | 8453 | Production |
| Base Sepolia | 84532 | Testnet |

---

## External Links

- **8004scan Explorer**: https://www.8004scan.io/
- **Agent0 SDK Docs**: https://sdk.ag0.xyz/docs
- **8004.org**: https://www.8004.org/
- **ERC-8004 Spec**: https://eips.ethereum.org/EIPS/eip-8004
- **GitHub (Python)**: https://github.com/agent0lab/agent0-py
- **GitHub (TypeScript)**: https://github.com/agent0lab/agent0-ts
- **PyPI**: https://pypi.org/project/agent0-sdk/
- **npm**: https://www.npmjs.com/package/agent0-sdk

---

## Requirements for Registration

1. **Wallet with ETH** for gas fees (~$5-20)
2. **IPFS account** (Pinata free tier works)
3. **RPC endpoint** (Alchemy/Infura free tier)
4. **Private key** (for signing transactions)
5. **Deployed MCP endpoint** (public URL)

---

*Last updated: 2026-02-12*
