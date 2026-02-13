# x402 Protocol Documentation

## Overview

x402 is an open, internet-native payment protocol developed by Coinbase that enables:
- **Micropayments** as low as $0.001 per request
- **AI agent payments** - autonomous, programmatic transactions
- **Pay-per-use APIs** - no subscriptions, accounts, or API keys needed

---

## How x402 Works (Step by Step)

```
┌─────────────┐     1. Request      ┌─────────────┐
│   Client    │ ─────────────────▶  │   Server    │
│  (AI Agent) │                     │ (GasChecker)│
└─────────────┘                     └─────────────┘
       │                                   │
       │    2. HTTP 402 Payment Required   │
       │ ◀─────────────────────────────────│
       │    (includes payment instructions)│
       │                                   │
       ▼                                   │
┌─────────────┐                           │
│  Blockchain │  3. Execute payment       │
│    (Base)   │                           │
└─────────────┘                           │
       │                                   │
       │    4. Retry with payment proof    │
       │ ─────────────────────────────────▶│
       │                                   │
       │    5. Verify via Facilitator      │
       │                           ┌───────▼───────┐
       │                           │  Facilitator  │
       │                           │  (Coinbase)   │
       │                           └───────────────┘
       │                                   │
       │    6. Return requested resource   │
       │ ◀─────────────────────────────────│
```

---

## HTTP Headers

| Header | Direction | Purpose |
|--------|-----------|---------|
| `PAYMENT-REQUIRED` | Server → Client | Payment instructions in 402 response |
| `PAYMENT-SIGNATURE` | Client → Server | Payment proof when retrying |
| `X-PAYMENT` | Client → Server | Alternative payment header |

---

## Seller Integration (Our Side)

### Minimal Implementation

```javascript
import { paymentMiddleware } from '@coinbase/x402-sdk';

app.use(
  paymentMiddleware({
    "GET /gas": {
      price: "0.001",           // $0.001 per request
      currency: "USDC",
      recipient: "0xYourWallet",
      network: "base",
      description: "Multi-chain gas prices"
    },
    "GET /gas/:chain": {
      price: "0.0005",
      currency: "USDC",
      recipient: "0xYourWallet",
      network: "base",
      description: "Single chain gas price"
    }
  })
);
```

### Python FastAPI Integration

```python
from x402 import X402Middleware

app.add_middleware(
    X402Middleware,
    routes={
        "/gas": {"price": "0.001", "currency": "USDC"},
        "/gas/{chain}": {"price": "0.0005", "currency": "USDC"}
    },
    recipient="0xYourWallet",
    network="base"
)
```

---

## Supported Networks & Currencies

| Network | Chain ID | CAIP-2 ID | Status |
|---------|----------|-----------|--------|
| Base | 8453 | eip155:8453 | ✅ Primary |
| Ethereum | 1 | eip155:1 | ✅ Supported |
| Solana | - | solana:mainnet | ✅ Supported |

**Currencies:**
- USDC (primary)
- Additional stablecoins planned

---

## Facilitator Service

The **Facilitator** handles payment verification so sellers don't need blockchain infrastructure.

**Coinbase CDP Facilitator:**
- Free tier: 1,000 transactions/month
- Then: $0.001 per transaction
- Handles: verification, settlement, fraud protection

---

## Pricing Strategy for GasChecker

| Endpoint | Tool | Price | Rationale |
|----------|------|-------|----------|
| `/gas` | `gas_all` | $0.001 | All 5 chains |
| `/gas/{chain}` | `gas_now` | $0.0005 | Single chain |
| `/gas/recommend` | `gas_recommend` | $0.001 | Analysis + recommendation |
| `/healthz` | - | FREE | Health checks always free |

**Expected Revenue:**
- 1000 requests/day × $0.001 = $1/day = $30/month
- Higher volume = more revenue
- Near-zero operating costs (serverless)

---

## Client Integration (For Testing)

Other AI agents will use something like:

```javascript
import { X402Client } from '@coinbase/x402-sdk';

const client = new X402Client({
  privateKey: process.env.WALLET_KEY,
  network: 'base'
});

// Automatic payment handling
const gasData = await client.fetch('https://gaschecker.com/gas');
// If 402 received, client auto-pays and retries
```

---

## Resources

- Official Site: https://www.x402.org/
- Coinbase Docs: https://docs.cdp.coinbase.com/x402/
- Base Docs: https://docs.base.org/base-app/agents/x402-agents
- Whitepaper: https://www.x402.org/x402-whitepaper.pdf
- GitHub: https://github.com/coinbase/x402

---

*Document created: 2026-02-13*
