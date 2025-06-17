[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/hasan-syed25-mcp-server-alphavantage-badge.png)](https://mseep.ai/app/hasan-syed25-mcp-server-alphavantage)

# MCP Server for Stock Market Analysis

## Overview
This project implements a Model Context Protocol (MCP) server designed for stock market analysis. It provides real-time stock price data, calculates key technical indicators like moving averages and RSI, and enables trend detection using AlphaVantage API. The server can be integrated with LLMs like Claude for enhanced financial insights.

## Why I Built It
I developed this MCP server to simplify stock market analysis by automating data fetching and technical indicator calculations. The goal is to help traders and investors make data-driven decisions by leveraging AI-assisted insights. By using MCP, this server can seamlessly connect with LLMs, allowing them to retrieve financial data and perform analysis in real time.

## Features
- **Fetch real-time stock data** using AlphaVantage API
- **Calculate moving averages** (short-term & long-term) to analyze trends
- **Detect trend crossovers** (Golden Cross & Death Cross)
- **Compute Relative Strength Index (RSI)** to determine overbought/oversold conditions
- **Expose MCP tools and resources** for seamless AI integration
- **Future extensibility** (e.g., backtesting strategies, trading platform integration)

## Prerequisites
Before getting started, ensure you have the following:
- **Python 3.10+** installed
- **MCP SDK 1.2.0+**
- **AlphaVantage API key** (Sign up at [AlphaVantage](https://www.alphavantage.co))
- **Basic understanding of Python and stock market indicators**

## Installation
To set up the project, follow these steps:

### 1. Install Dependencies
Using `uv` (recommended):
```sh
uv add mcp[cli] httpx
```
Using `pip`:
```sh
pip install mcp httpx
```

### 2. Get an AlphaVantage API Key
- Register at [AlphaVantage](https://www.alphavantage.co/support/#api-key)
- Note down your **API key** for later use

### 3. Clone the Repository
```sh
git clone https://github.com/your-username/mcp-stock-analysis.git
cd mcp-stock-analysis
```

### 4. Set Up Environment Variables
Create a `.env` file and add your AlphaVantage API key:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

## Running the MCP Server
To start the server, run:
```sh
python server.py
```
Or using MCP:
```sh
mcp install server.py
```
For development mode:
```sh
mcp dev server.py
```

## How It Works
### Fetching Intraday Stock Data
The server fetches real-time stock price data from AlphaVantage:
```python
@mcp.tool()
def fetch_intraday_data(symbol: str, interval: str = "5min") -> dict:
    """Fetches intraday stock price data."""
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={API_KEY}"
    response = httpx.get(url)
    return response.json()
```

### Moving Averages (Short-Term vs Long-Term)
Moving averages help smooth out price data to identify trends:
```python
@mcp.tool()
def calculate_moving_averages(prices: list[float], short_window: int = 50, long_window: int = 200) -> dict:
    """Calculates short-term and long-term moving averages."""
    short_ma = sum(prices[-short_window:]) / short_window
    long_ma = sum(prices[-long_window:]) / long_window
    return {"short_ma": short_ma, "long_ma": long_ma}
```

### Detecting Trend Crossovers (Golden Cross & Death Cross)
- **Golden Cross**: Short-term MA crosses above long-term MA → **Bullish signal**
- **Death Cross**: Short-term MA crosses below long-term MA → **Bearish signal**
```python
@mcp.tool()
def detect_trend_crossover(short_ma: float, long_ma: float) -> str:
    """Detects if a Golden Cross or Death Cross has occurred."""
    if short_ma > long_ma:
        return "Golden Cross - Bullish Trend"
    elif short_ma < long_ma:
        return "Death Cross - Bearish Trend"
    return "No significant crossover"
```

### Relative Strength Index (RSI)
RSI measures momentum and helps determine if a stock is overbought/oversold:
```python
@mcp.tool()
def calculate_rsi(prices: list[float], period: int = 14) -> float:
    """Calculates RSI indicator."""
    gains = [max(0, prices[i] - prices[i-1]) for i in range(1, len(prices))]
    losses = [max(0, prices[i-1] - prices[i]) for i in range(1, len(prices))]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
    return 100 - (100 / (1 + rs))
```

### Overbought/Oversold Conditions
- **RSI > 70** → Overbought (potential sell signal)
- **RSI < 30** → Oversold (potential buy signal)
```python
@mcp.tool()
def determine_rsi_condition(rsi: float) -> str:
    """Determines whether the RSI indicates overbought or oversold conditions."""
    if rsi > 70:
        return "Overbought - Consider Selling"
    elif rsi < 30:
        return "Oversold - Consider Buying"
    return "Neutral"
```

## Future Enhancements
This MCP server can be extended with additional features:
- **More technical indicators**: MACD, Bollinger Bands, etc.
- **Backtesting**: Simulate past trades based on strategy rules
- **Trading platform integration**: Connect with brokers for live trading

## Contributions
Feel free to contribute by submitting pull requests or reporting issues. Let’s make stock market analysis more accessible and AI-driven!

## Connect With Me
If you have any questions or suggestions, feel free to reach out!

🔗 **LinkedIn**: [Syed Hasan](https://www.linkedin.com/in/syedhasan)  
🤗 **Hugging Face**: [Syed-Hasan-8503](https://huggingface.co/Syed-Hasan-8503)

