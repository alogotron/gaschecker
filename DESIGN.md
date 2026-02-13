# GasChecker - Design Specification Document

**Version:** 0.1.0 (Draft)  
**Created:** 2026-02-12  
**Status:** In Development  

---

## 1. Project Overview

### 1.1 Purpose
GasChecker is a **multi-chain gas oracle service** that provides real-time gas price information to AI agents via the **Model Context Protocol (MCP)**.

### 1.2 Goals
- Provide free, reliable gas price data for multiple blockchain networks
- Expose functionality via MCP for AI agent integration
- Register as a discoverable service on the **ERC-8004 Trustless Agents Registry**
- Offer simple REST API for non-MCP consumers

### 1.3 Inspiration
- [MeowBlock](https://github.com/Xeift/MeowBlock) - Ethereum JSON-RPC MCP server registered as ERC-8004 Agent #6809
- Agent0 Lab's vision of on-chain discoverable AI agent services

### 1.4 Target Users
- AI agents (Claude, GPT, OpenClaw, Agent Zero, etc.)
- DeFi applications needing gas optimization
- Developers building blockchain-aware AI systems

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   AI Agents     │────▶│   GasChecker    │────▶│  Public RPC      │
│  (MCP clients)  │ MCP │  (FastAPI+MCP)  │HTTP │  Endpoints       │
└─────────────────┘     └─────────────────┘     └──────────────────┘
        │                       │
        │                       ├── Ethereum RPCs (35+)
        │                       ├── Base RPCs (6+)
        │                       ├── Arbitrum RPCs (6+)
        │                       ├── Optimism RPCs (6+)
        │                       └── Polygon RPCs (6+)
        │
        ▼
┌─────────────────┐
│   ERC-8004      │  ← Agent discovery registry
│   Registry      │
└─────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|--------|
| Runtime | Python 3.11+ | Core language |
| Web Framework | FastAPI | REST API & ASGI |
| MCP Server | FastMCP | Model Context Protocol |
| HTTP Client | httpx | Async RPC calls |
| ASGI Server | Uvicorn | Production server |
| Deployment | Vercel | Serverless hosting |

### 2.3 Design Principles

1. **Zero Infrastructure** - No full nodes; use public RPC endpoints
2. **Fault Tolerance** - Multiple fallback endpoints per chain
3. **Rate Limiting** - Protect against abuse (60 req/min default)
4. **Stateless** - No database; read-only from blockchains
5. **Open Source** - MIT licensed, fully transparent

---

## 3. Features

### 3.1 MCP Tools

| Tool | Description | Arguments | Returns |
|------|-------------|-----------|--------|
| `gas` | Quick gas check with emoji | None | String: "🟢 Gas: 12.50 gwei (LOW)" |
| `gas_now` | Detailed gas for one chain | `chain` (optional) | JSON object with full details |
| `gas_all` | All chains at once | None | JSON with all chain data |
| `gas_recommend` | Find cheapest chain | None | Ranking + recommendation |
| `chains` | List supported chains | None | Chain metadata |

### 3.2 REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info & metadata |
| `/healthz` | GET | Health check |
| `/gas` | GET | All chain gas prices |
| `/gas/{chain}` | GET | Specific chain gas |
| `/mcp` | * | MCP protocol endpoint |

### 3.3 Supported Chains

| Chain | Chain ID | Symbol | RPC Count | Gas Thresholds (gwei) |
|-------|----------|--------|-----------|----------------------|
| Ethereum | 1 | ETH | 35+ | Low: ≤15, Med: ≤30, High: ≤60 |
| Base | 8453 | ETH | 6+ | Low: ≤0.005, Med: ≤0.01, High: ≤0.05 |
| Arbitrum | 42161 | ETH | 6+ | Low: ≤0.05, Med: ≤0.1, High: ≤0.5 |
| Optimism | 10 | ETH | 6+ | Low: ≤0.005, Med: ≤0.01, High: ≤0.05 |
| Polygon | 137 | MATIC | 6+ | Low: ≤50, Med: ≤100, High: ≤200 |

---

## 4. Technical Specifications

### 4.1 RPC Fallback Strategy

```python
async def call_rpc(rpc_urls, method, params):
    for url in rpc_urls:
        try:
            response = await client.post(url, json=payload)
            return response.json()
        except:
            continue  # Try next endpoint
    raise RuntimeError("All endpoints failed")
```

### 4.2 Gas Level Classification

Gas prices are classified into four levels:
- **LOW** - Good time to transact
- **MEDIUM** - Normal conditions
- **HIGH** - Consider waiting
- **EXTREME** - Avoid unless urgent

Thresholds are chain-specific (L2s have much lower absolute values).

### 4.3 Rate Limiting

- **Limit:** 60 requests per minute per IP
- **Window:** Sliding 60-second window
- **Response:** HTTP 429 with Retry-After header

### 4.4 Error Handling

| Error Type | Response | Status Code |
|------------|----------|-------------|
| Unknown chain | `{"error": "Unknown chain: xyz"}` | 400 |
| All RPCs failed | `{"error": "All RPC endpoints failed"}` | 502 |
| Rate limited | `{"detail": "Rate limit exceeded"}` | 429 |

---

## 5. Deployment Plan

### 5.1 Development Stages

| Stage | Description | Status |
|-------|-------------|--------|
| 1. Core Development | Build MCP server with gas tools | ✅ Complete |
| 2. Local Testing | Test on gmtek server | ✅ Complete |
| 3. Documentation | Design spec, README | 🔄 In Progress |
| 4. Vercel Deployment | Deploy to serverless platform | ⏳ Pending |
| 5. Domain Setup | Configure custom domain | ⏳ Pending |
| 6. ERC-8004 Registration | Register on-chain | ⏳ Pending |
| 7. OpenClaw Integration | Add as OpenClaw skill | ⏳ Pending |

### 5.2 Deployment Options

**Primary: Vercel (Recommended)**
- Free tier sufficient
- Automatic HTTPS
- Global edge network
- Easy custom domain

**Alternative: Self-hosted**
- Run on gmtek or aiserver
- Use Tailscale Serve for secure exposure
- Requires manual SSL/domain setup

### 5.3 Environment Variables

| Variable | Description | Default |
|----------|-------------|--------|
| `PORT` | Server port | 8000 |
| `ETH_RPC_URL` | Primary ETH RPC | https://eth.llamarpc.com |
| `RPC_TIMEOUT_S` | RPC timeout seconds | 15 |
| `RATE_LIMIT_PER_MINUTE` | Rate limit | 60 |
| `MCP_ALLOWED_HOSTS` | Allowed hosts (comma-sep) | localhost |

---

## 6. ERC-8004 Registration

### 6.1 What is ERC-8004?

ERC-8004 "Trustless Agents" is an Ethereum standard for:
- **Agent Discovery** - Find AI agents on-chain
- **Identity** - NFT-based agent identity (ERC-721)
- **Reputation** - Feedback and scoring systems
- **Validation** - Trust verification mechanisms

### 6.2 Registration Requirements

1. **Wallet** with ETH for gas (~$5-20)
2. **Registration file** (JSON) hosted on IPFS or HTTPS
3. **MCP endpoint** publicly accessible
4. **Contract interaction** to mint agent NFT

### 6.3 Registration File Template

```json
{
  "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
  "name": "GasChecker",
  "description": "Multi-chain gas oracle MCP server. Free. 60 req/min. Real-time gas prices for Ethereum, Base, Arbitrum, Optimism, Polygon.",
  "image": "https://[domain]/logo.png",
  "services": [
    {
      "name": "MCP",
      "endpoint": "https://[domain]/mcp",
      "version": "2025-06-18"
    },
    {
      "name": "web",
      "endpoint": "https://[domain]/"
    }
  ],
  "x402Support": false,
  "active": true,
  "registrations": [
    {
      "agentId": [TBD],
      "agentRegistry": "eip155:1:0x8004...9432"
    }
  ],
  "supportedTrust": ["reputation"]
}
```

### 6.4 Registration Steps

1. Deploy service and get public URL
2. Upload registration.json to IPFS (Pinata/web3.storage)
3. Call `register(ipfsURI)` on Identity Registry contract
4. Receive agentId (NFT token ID)
5. Update registration.json with agentId

---

## 7. OpenClaw Integration

### 7.1 Deployment as OpenClaw Skill

After external deployment, create an OpenClaw skill wrapper:

```
~/.openclaw/workspace/skills/gaschecker/
├── SKILL.md
├── config.json
└── scripts/
    └── check_gas.py
```

### 7.2 Wallet Requirements

For ERC-8004 registration from OpenClaw:
- Use **bagman** skill for secure key management
- Store private key in **1Password**
- OpenClaw agent signs registration transaction

---

## 8. Future Roadmap

### Phase 2: Enhanced Features
- [ ] Gas price history (last hour/day)
- [ ] Gas alerts/notifications
- [ ] EIP-1559 fee breakdown (base + priority)
- [ ] Gas estimation for common operations

### Phase 3: Additional Chains
- [ ] zkSync Era
- [ ] Avalanche C-Chain
- [ ] BNB Smart Chain
- [ ] Fantom

### Phase 4: Premium Features (Optional)
- [ ] x402 micropayments for premium endpoints
- [ ] Higher rate limits for paying users
- [ ] Historical data API

---

## 9. References

### 9.1 Documents to Add
- [ ] ERC-8004 Specification
- [ ] MCP Protocol Documentation
- [ ] Public RPC Endpoint Lists
- [ ] Agent0 Lab research/posts

### 9.2 Related Projects
- [MeowBlock](https://github.com/Xeift/MeowBlock) - ETH RPC MCP server
- [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) - Trustless Agents standard
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - Python MCP SDK

---

## 10. Open Questions

1. **Domain name?** - What domain for gaschecker?
2. **Branding?** - Logo, colors, identity
3. **x402 payments?** - Support micropayments for premium tier?
4. **Additional chains?** - Which chains to prioritize?

---

*Document maintained by: AI development session*  
*Last updated: 2026-02-12*
