from mcp.server.fastmcp import FastMCP
import requests
import pandas as pd
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

# Create the MCP server
mcp = FastMCP("AlphaVantageTrader", dependencies=["requests", "pandas", "tabulate"])

# Constants and configurations
API_KEY = "ILFDPJR4TNTEL3MC"  # Replace with your actual AlphaVantage API key

@dataclass
class MarketData:
    symbol: str
    interval: str
    data: pd.DataFrame
    last_updated: datetime
    
class AlphaVantageAPI:
    @staticmethod
    def get_intraday_data(symbol: str, interval: str = "1min", outputsize: str = "compact") -> pd.DataFrame:
        """Fetch intraday data from AlphaVantage API"""
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={API_KEY}"
        
        response = requests.get(url)
        data = response.json()
        
        # Check for error responses
        if "Error Message" in data:
            raise ValueError(f"API Error: {data['Error Message']}")
        if "Note" in data:
            print(f"API Note: {data['Note']}")
            
        # Extract time series data
        time_series_key = f"Time Series ({interval})"
        if time_series_key not in data:
            raise ValueError(f"No time series data found for {symbol} with interval {interval}")
            
        time_series = data[time_series_key]
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns and convert to numeric
        df.columns = [col.split(". ")[1] for col in df.columns]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
            
        return df

# In-memory cache for market data
market_data_cache: Dict[str, MarketData] = {}

# Resources
@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"

# Technical Analysis Tools
@mcp.tool()
def calculate_moving_averages(symbol: str, short_period: int = 20, long_period: int = 50) -> Dict[str, Any]:
    """
    Calculate short and long moving averages for a symbol
    
    Args:
        symbol: The ticker symbol to analyze
        short_period: Short moving average period in minutes
        long_period: Long moving average period in minutes
        
    Returns:
        Dictionary with moving average data and analysis
    """
    cache_key = f"{symbol}_1min"
    
    if cache_key not in market_data_cache:
        df = AlphaVantageAPI.get_intraday_data(symbol, "1min", outputsize="full")
        market_data_cache[cache_key] = MarketData(
            symbol=symbol,
            interval="1min",
            data=df,
            last_updated=datetime.now()
        )
    
    data = market_data_cache[cache_key].data
    
    # Calculate moving averages
    data[f'SMA{short_period}'] = data['close'].rolling(window=short_period).mean()
    data[f'SMA{long_period}'] = data['close'].rolling(window=long_period).mean()
    
    # Get latest values
    latest = data.iloc[-1]
    current_price = latest['close']
    short_ma = latest[f'SMA{short_period}']
    long_ma = latest[f'SMA{long_period}']
    
    # Determine signal
    if short_ma > long_ma:
        signal = "BULLISH (Short MA above Long MA)"
    elif short_ma < long_ma:
        signal = "BEARISH (Short MA below Long MA)"
    else:
        signal = "NEUTRAL (MAs are equal)"
    
    # Check for crossover in the last 5 periods
    last_5 = data.iloc[-5:]
    crossover = False
    crossover_type = ""
    
    for i in range(1, len(last_5)):
        prev = last_5.iloc[i-1]
        curr = last_5.iloc[i]
        
        # Golden Cross (short crosses above long)
        if prev[f'SMA{short_period}'] <= prev[f'SMA{long_period}'] and curr[f'SMA{short_period}'] > curr[f'SMA{long_period}']:
            crossover = True
            crossover_type = "GOLDEN CROSS (Bullish)"
            break
            
        # Death Cross (short crosses below long)
        if prev[f'SMA{short_period}'] >= prev[f'SMA{long_period}'] and curr[f'SMA{short_period}'] < curr[f'SMA{long_period}']:
            crossover = True
            crossover_type = "DEATH CROSS (Bearish)"
            break
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        f"SMA{short_period}": short_ma,
        f"SMA{long_period}": long_ma,
        "signal": signal,
        "crossover_detected": crossover,
        "crossover_type": crossover_type if crossover else "None",
        "analysis": f"""Moving Average Analysis for {symbol}:
Current Price: ${current_price:.2f}
{short_period}-period SMA: ${short_ma:.2f}
{long_period}-period SMA: ${long_ma:.2f}
Signal: {signal}
Recent Crossover: {"Yes - " + crossover_type if crossover else "No"}

Recommendation: {
    "STRONG BUY" if crossover and crossover_type == "GOLDEN CROSS (Bullish)" else
    "BUY" if signal == "BULLISH (Short MA above Long MA)" else
    "STRONG SELL" if crossover and crossover_type == "DEATH CROSS (Bearish)" else
    "SELL" if signal == "BEARISH (Short MA below Long MA)" else
    "HOLD"
}"""
    }

@mcp.tool()
def calculate_rsi(symbol: str, period: int = 14) -> Dict[str, Any]:
    """
    Calculate Relative Strength Index (RSI) for a symbol
    
    Args:
        symbol: The ticker symbol to analyze
        period: RSI calculation period in minutes
        
    Returns:
        Dictionary with RSI data and analysis
    """
    cache_key = f"{symbol}_1min"
    
    if cache_key not in market_data_cache:
        df = AlphaVantageAPI.get_intraday_data(symbol, "1min", outputsize="full")
        market_data_cache[cache_key] = MarketData(
            symbol=symbol,
            interval="1min",
            data=df,
            last_updated=datetime.now()
        )
    
    data = market_data_cache[cache_key].data.copy()
    
    # Calculate price changes
    delta = data['close'].diff()
    
    # Create gain and loss series
    gain = delta.copy()
    loss = delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    loss = abs(loss)
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Get latest RSI
    latest_rsi = rsi.iloc[-1]
    
    # Determine signal
    if latest_rsi < 30:
        signal = "OVERSOLD (Potential buy opportunity)"
    elif latest_rsi > 70:
        signal = "OVERBOUGHT (Potential sell opportunity)"
    else:
        signal = "NEUTRAL"
    
    return {
        "symbol": symbol,
        "period": period,
        "rsi": latest_rsi,
        "signal": signal,
        "analysis": f"""RSI Analysis for {symbol}:
{period}-period RSI: {latest_rsi:.2f}
Signal: {signal}

Recommendation: {
    "BUY" if latest_rsi < 30 else
    "SELL" if latest_rsi > 70 else
    "HOLD"
}"""
    }

@mcp.tool()
def trade_recommendation(symbol: str) -> Dict[str, Any]:
    """
    Provide a comprehensive trade recommendation based on multiple indicators
    
    Args:
        symbol: The ticker symbol to analyze
        
    Returns:
        Dictionary with trading recommendation and supporting data
    """
    # Calculate individual indicators
    ma_data = calculate_moving_averages(symbol)
    rsi_data = calculate_rsi(symbol)
    
    # Extract signals
    ma_signal = ma_data["signal"]
    ma_crossover = ma_data["crossover_detected"]
    ma_crossover_type = ma_data["crossover_type"]
    rsi_value = rsi_data["rsi"]
    rsi_signal = rsi_data["signal"]
    
    # Determine overall signal strength
    signal_strength = 0
    
    # MA contribution
    if "BULLISH" in ma_signal:
        signal_strength += 1
    elif "BEARISH" in ma_signal:
        signal_strength -= 1
        
    # Crossover contribution
    if ma_crossover:
        if "GOLDEN" in ma_crossover_type:
            signal_strength += 2
        elif "DEATH" in ma_crossover_type:
            signal_strength -= 2
            
    # RSI contribution
    if "OVERSOLD" in rsi_signal:
        signal_strength += 1.5
    elif "OVERBOUGHT" in rsi_signal:
        signal_strength -= 1.5
    
    # Determine final recommendation
    if signal_strength >= 2:
        recommendation = "STRONG BUY"
    elif signal_strength > 0:
        recommendation = "BUY"
    elif signal_strength <= -2:
        recommendation = "STRONG SELL"
    elif signal_strength < 0:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"
    
    # Calculate risk level (simple version)
    risk_level = "MEDIUM"
    if abs(signal_strength) > 3:
        risk_level = "LOW"  # Strong signal, lower risk
    elif abs(signal_strength) < 1:
        risk_level = "HIGH"  # Weak signal, higher risk
    
    analysis = f"""# Trading Recommendation for {symbol}

## Summary
Recommendation: {recommendation}
Risk Level: {risk_level}
Signal Strength: {signal_strength:.1f} / 4.5

## Technical Indicators
Moving Averages: {ma_signal}
Recent Crossover: {"Yes - " + ma_crossover_type if ma_crossover else "No"}
RSI ({rsi_data["period"]}): {rsi_value:.2f} - {rsi_signal}

## Reasoning
This recommendation is based on a combination of Moving Average analysis and RSI indicators.
{
    f"The {ma_crossover_type} provides a strong directional signal. " if ma_crossover else ""
}{
    f"The RSI indicates the stock is {rsi_signal.split(' ')[0].lower()}. " if "NEUTRAL" not in rsi_signal else ""
}

## Action Plan
{
    "Consider immediate entry with a stop loss at the recent low. Target the next resistance level." if recommendation == "STRONG BUY" else
    "Look for a good entry point on small dips. Set reasonable stop loss." if recommendation == "BUY" else
    "Consider immediate exit or setting tight stop losses to protect gains." if recommendation == "STRONG SELL" else
    "Start reducing position on strength or set trailing stop losses." if recommendation == "SELL" else
    "Monitor the position but no immediate action needed."
}
"""
    
    return {
        "symbol": symbol,
        "recommendation": recommendation,
        "risk_level": risk_level,
        "signal_strength": signal_strength,
        "ma_signal": ma_signal,
        "rsi_signal": rsi_signal,
        "current_price": ma_data["current_price"],
        "analysis": analysis
    }

# Prompts
@mcp.prompt()
def analyze_ticker(symbol: str) -> str:
    """
    Analyze a ticker symbol for trading opportunities
    """
    return f"""You are a professional stock market analyst. I would like you to analyze the stock {symbol} and provide trading insights.

Start by examining the current market data and technical indicators. Here are the specific tasks:

1. First, check the current market data for {symbol}
2. Calculate the moving averages using the calculate_moving_averages tool
3. Calculate the RSI using the calculate_rsi tool
4. Generate a comprehensive trade recommendation using the trade_recommendation tool
5. Based on all this information, provide your professional analysis, highlighting:
   - The current market position
   - Key technical indicators and what they suggest
   - Potential trading opportunities and risks
   - Your recommended action (buy, sell, or hold) with a brief explanation

Please organize your response in a clear, structured format suitable for a professional trader."""

@mcp.prompt()
def compare_tickers(symbols: str) -> str:
    """
    Compare multiple ticker symbols for the best trading opportunity
    
    Args:
        symbols: Comma-separated list of ticker symbols
    """
    symbol_list = [s.strip() for s in symbols.split(",")]
    symbol_section = "\n".join([f"- {s}" for s in symbol_list])
    
    return f"""You are a professional stock market analyst. I would like you to compare these stocks and identify the best trading opportunity:

{symbol_section}

For each stock in the list, please:

1. Check the current market data using the appropriate resource
2. Generate a comprehensive trade recommendation using the trade_recommendation tool
3. Compare all stocks based on:
   - Current trend direction and strength
   - Technical indicator signals
   - Risk/reward profile
   - Trading recommendation strength

After analyzing each stock, rank them from most promising to least promising trading opportunity. Explain your ranking criteria and why you believe the top-ranked stock represents the best current trading opportunity.

Conclude with a specific recommendation on which stock to trade and what action to take (buy, sell, or hold)."""

@mcp.prompt()
def intraday_strategy_builder(symbol: str) -> str:
    """
    Build a custom intraday trading strategy for a specific ticker
    """
    return f"""You are an expert algorithmic trader specializing in intraday strategies. I want you to develop a custom intraday trading strategy for {symbol}.

Please follow these steps:

1. First, analyze the current market data for {symbol} using the market-data resource
2. Calculate relevant technical indicators:
   - Moving averages (short and long periods)
   - RSI
3. Based on your analysis, design an intraday trading strategy that includes:
   - Specific entry conditions (technical setups that would trigger a buy/sell)
   - Exit conditions (both take-profit and stop-loss levels)
   - Position sizing recommendations
   - Optimal trading times during the day
   - Risk management rules

Make your strategy specific to the current market conditions for {symbol}, not just generic advice. Include exact indicator values and price levels where possible.

Conclude with a summary of the strategy and how a trader should implement it for today's trading session."""