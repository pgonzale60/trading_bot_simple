"""Asset universe definitions for portfolio and multi-asset workflows.

The lists centralise the equity and crypto selections so both the
multi-asset tester and the upcoming portfolio engine draw from the same
universe without duplicating hard-coded symbols.
"""

from __future__ import annotations

from typing import List

# 2019 perspective universe: mix of market-cap leaders and thematic growth picks
STOCK_UNIVERSE_2019: List[str] = [
    # Safe: 2019 Market Cap Leaders
    'AAPL',  # Apple - largest by market cap (2019)
    'MSFT',  # Microsoft - 2nd largest (2019)
    'GOOGL',  # Alphabet - 4th largest (2019)
    'AMZN',  # Amazon - 3rd largest (2019)
    'JPM',  # JPMorgan - financials outperformed 2019
    'JNJ',  # J&J - healthcare stability
    'SPY',  # S&P 500 ETF - broad market
    'QQQ',  # Nasdaq ETF - tech exposure

    # Riskier: Emerging Trends & Growth (visible by 2019)
    'NVDA',  # NVIDIA - GPU/AI trend emerging
    'META',  # Meta - social platform dominance
    'TSLA',  # Tesla - EV revolution starting
    'V',     # Visa - digital payments growth
    'NFLX',  # Netflix - streaming wars heating up
    'AMD',   # AMD - competing with Intel in CPUs
    'CRM',   # Salesforce - cloud/SaaS boom
    'SQ',    # Block (Square) - fintech/small business payments
    'SHOP',  # Shopify - e-commerce platform growth
    'ZM',    # Zoom - remote work trend (pre-COVID)
    'ROKU',  # Roku - streaming platform pure play
    'BYND',  # Beyond Meat - alt protein trend (IPO 2019)
    'UBER',  # Uber - gig economy (IPO 2019)
    'LYFT',  # Lyft - rideshare competitor (IPO 2019)
    'PINS',  # Pinterest - social commerce (IPO 2019)
]

CRYPTO_UNIVERSE_2019: List[str] = [
    # Safe: 2019 Market Cap Leaders
    'BTC-USD',   # Bitcoin - #1 by market cap (2019)
    'ETH-USD',   # Ethereum - #2 by market cap (2019)
    'XRP-USD',   # Ripple - #3 by market cap (2019)
    'LTC-USD',   # Litecoin - #4 by market cap (2019)
    'BNB-USD',   # Binance Coin - #7 by market cap (2019)
    'ADA-USD',   # Cardano - #9 by market cap (2019)
    'LINK-USD',  # Chainlink - oracle infrastructure
    'DOT-USD',   # Polkadot - interoperability

    # Riskier: Emerging DeFi/Alt Coins (gaining momentum by 2019)
    'DOGE-USD',  # Dogecoin - meme coin with community
    'XLM-USD',   # Stellar - payments focus
    'TRX-USD',   # TRON - content/gaming platform
    'EOS-USD',   # EOS - Ethereum competitor
    'XMR-USD',   # Monero - privacy coin
    'DASH-USD',  # Dash - payments/privacy
    'NEO-USD',   # NEO - "Chinese Ethereum"
    'IOTA-USD',  # IOTA - IoT blockchain
    'ETC-USD',   # Ethereum Classic - original chain
    'ZEC-USD',   # Zcash - privacy coin
]

ALL_ASSETS_2019: List[str] = STOCK_UNIVERSE_2019 + CRYPTO_UNIVERSE_2019

# Quick sample sets used for smoke tests and CLI "quick" modes
QUICK_SAMPLE_STOCKS: List[str] = ['AAPL', 'SPY', 'TSLA', 'WMT', 'GLD']
QUICK_SAMPLE_CRYPTO: List[str] = ['BTC-USD', 'ETH-USD', 'ADA-USD']
QUICK_SAMPLE_ALL: List[str] = QUICK_SAMPLE_STOCKS + QUICK_SAMPLE_CRYPTO

__all__ = [
    'ALL_ASSETS_2019',
    'CRYPTO_UNIVERSE_2019',
    'QUICK_SAMPLE_ALL',
    'QUICK_SAMPLE_CRYPTO',
    'QUICK_SAMPLE_STOCKS',
    'STOCK_UNIVERSE_2019',
]
