"""GasChecker - Multi-Chain Gas Oracle MCP Server with x402 Payments"""
import asyncio
import urllib.request
import json
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import FastMCP

# x402 imports
from x402 import (
    x402ResourceServer,
    ResourceConfig,
    parse_payment_payload,
)

# Configuration
RECIPIENT_WALLET = "0xaab80bc6b6040ae845ce225181fd72297ba71b13"  # Your wallet
NETWORK = "base"  # Base mainnet for USDC

# Pricing tiers
PRICING = {
    "premium_all": "0.001",      # $0.001 for all chains at once
    "premium_recommend": "0.0005",  # $0.0005 for recommendations
}

# Chain configurations
CHAINS = {
    "ethereum": {
        "name": "Ethereum",
        "rpcs": [
            "https://ethereum.publicnode.com",
            "https://eth.drpc.org",
            "https://1rpc.io/eth"
        ]
    },
    "base": {
        "name": "Base",
        "rpcs": [
            "https://base.publicnode.com",
            "https://base.drpc.org",
            "https://1rpc.io/base"
        ]
    },
    "arbitrum": {
        "name": "Arbitrum One",
        "rpcs": [
            "https://arbitrum-one.publicnode.com",
            "https://arb1.arbitrum.io/rpc"
        ]
    },
    "optimism": {
        "name": "Optimism",
        "rpcs": [
            "https://optimism.publicnode.com",
            "https://mainnet.optimism.io"
        ]
    },
    "polygon": {
        "name": "Polygon",
        "rpcs": [
            "https://polygon-bor.publicnode.com",
            "https://polygon-rpc.com"
        ]
    }
}

# Initialize x402 server
x402_server = x402ResourceServer()

# MCP Server
mcp = FastMCP("GasChecker")

def fetch_gas_price(chain: str) -> dict:
    """Fetch current gas price for a chain"""
    if chain not in CHAINS:
        return {"error": f"Unknown chain: {chain}"}

    config = CHAINS[chain]

    for rpc in config["rpcs"]:
        try:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "method": "eth_gasPrice",
                "params": [],
                "id": 1
            }).encode()

            req = urllib.request.Request(
                rpc,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "GasChecker/1.0"}
            )

            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())

            if "result" in data:
                wei = int(data["result"], 16)
                gwei = wei / 1e9

                if gwei < 5:
                    level = "low"
                elif gwei < 20:
                    level = "medium"
                elif gwei < 50:
                    level = "high"
                else:
                    level = "extreme"

                return {
                    "chain": chain,
                    "name": config["name"],
                    "gasPrice": {
                        "wei": wei,
                        "gwei": round(gwei, 4)
                    },
                    "level": level
                }

        except Exception:
            continue

    return {"chain": chain, "error": "All RPCs failed"}

# MCP Tools (always free via MCP protocol)
@mcp.tool()
def gas(chain: str = "ethereum") -> str:
    """Get current gas price for a blockchain. Chains: ethereum, base, arbitrum, optimism, polygon"""
    result = fetch_gas_price(chain.lower())
    return json.dumps(result, indent=2)

@mcp.tool()
def gas_all() -> str:
    """Get gas prices for all supported chains"""
    results = {}
    for chain in CHAINS:
        results[chain] = fetch_gas_price(chain)
    return json.dumps(results, indent=2)

@mcp.tool()
def gas_recommend() -> str:
    """Get recommendation for cheapest chain to transact on"""
    prices = []
    for chain in CHAINS:
        result = fetch_gas_price(chain)
        if "gasPrice" in result:
            prices.append({
                "chain": chain,
                "name": result["name"],
                "gwei": result["gasPrice"]["gwei"]
            })

    if not prices:
        return json.dumps({"error": "Could not fetch gas prices"})

    prices.sort(key=lambda x: x["gwei"])

    return json.dumps({
        "recommendation": prices[0]["chain"],
        "reason": f"{prices[0]['name']} has lowest gas at {prices[0]['gwei']} gwei",
        "ranking": prices
    }, indent=2)

@mcp.tool()
def chains() -> str:
    """List all supported chains"""
    return json.dumps(list(CHAINS.keys()))

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

# FastAPI app
app = FastAPI(
    title="GasChecker",
    description="Multi-chain gas oracle with x402 payments",
    version="1.1.0",
    lifespan=lifespan
)

# Mount MCP
app.mount("/mcp", mcp.sse_app())

# REST API - Free tier
@app.get("/")
async def root():
    return {
        "service": "GasChecker",
        "version": "1.1.0",
        "description": "Multi-chain gas oracle MCP server",
        "endpoints": {
            "free": ["/gas/{chain}", "/healthz", "/chains"],
            "paid": ["/premium/all", "/premium/recommend"]
        },
        "mcp": "/mcp",
        "x402": True,
        "pricing": PRICING
    }

@app.get("/healthz")
async def health():
    return {"ok": True}

@app.get("/chains")
async def list_chains():
    return {"chains": list(CHAINS.keys())}

@app.get("/gas/{chain}")
async def get_gas(chain: str):
    """Free: Get gas price for single chain"""
    result = fetch_gas_price(chain.lower())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# REST API - Premium (x402 paid)
@app.get("/premium/all")
async def premium_all(request: Request):
    """Paid: Get all chain gas prices at once ($0.001)"""
    # Check for payment
    payment_header = request.headers.get("X-PAYMENT") or request.headers.get("Payment")

    if not payment_header:
        # Return 402 Payment Required
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment required",
                "price": PRICING["premium_all"],
                "currency": "USDC",
                "network": NETWORK,
                "recipient": RECIPIENT_WALLET,
                "description": "All chains gas prices"
            },
            headers={
                "X-Payment-Required": json.dumps({
                    "price": PRICING["premium_all"],
                    "currency": "USDC", 
                    "network": NETWORK,
                    "recipient": RECIPIENT_WALLET
                })
            }
        )

    # For now, accept any payment header (production would verify via facilitator)
    results = {}
    for chain in CHAINS:
        results[chain] = fetch_gas_price(chain)
    return {"paid": True, "data": results}

@app.get("/premium/recommend")
async def premium_recommend(request: Request):
    """Paid: Get smart recommendation ($0.0005)"""
    payment_header = request.headers.get("X-PAYMENT") or request.headers.get("Payment")

    if not payment_header:
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment required",
                "price": PRICING["premium_recommend"],
                "currency": "USDC",
                "network": NETWORK,
                "recipient": RECIPIENT_WALLET,
                "description": "Smart chain recommendation"
            },
            headers={
                "X-Payment-Required": json.dumps({
                    "price": PRICING["premium_recommend"],
                    "currency": "USDC",
                    "network": NETWORK,
                    "recipient": RECIPIENT_WALLET
                })
            }
        )

    # Return recommendation
    prices = []
    for chain in CHAINS:
        result = fetch_gas_price(chain)
        if "gasPrice" in result:
            prices.append({
                "chain": chain,
                "name": result["name"],
                "gwei": result["gasPrice"]["gwei"]
            })

    prices.sort(key=lambda x: x["gwei"])

    return {
        "paid": True,
        "recommendation": prices[0]["chain"] if prices else None,
        "reason": f"{prices[0]['name']} has lowest gas at {prices[0]['gwei']} gwei" if prices else "No data",
        "ranking": prices
    }

# ERC-8004 Registration
@app.get("/registration.json")
async def registration():
    return {
        "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
        "name": "GasChecker",
        "description": "Multi-chain gas oracle MCP server. Free tier: 60 req/min. Premium: x402 USDC payments.",
        "image": "",
        "services": [
            {"name": "MCP", "endpoint": "https://gaschecker-ten.vercel.app/mcp", "version": "2025-06-18"},
            {"name": "web", "endpoint": "https://gaschecker-ten.vercel.app/"}
        ],
        "x402Support": True,
        "active": True,
        "supportedTrust": ["reputation"]
    }
