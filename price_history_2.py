# Price History Chart

import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


# --- Step 1: User input ---
TICKER = input('Enter a stock ticker (e.g. BHP.AX): ').upper()

# Calculations
def calculate_dividend_yield(dividend, price):
    return dividend / price if price else 0

def calculate_eps(earnings, shares_outstanding):
    return earnings / shares_outstanding if shares_outstanding else 0

def calculate_pe_ratio(price, eps):
    return price / eps if eps else 0

def calculate_roa(earnings, total_assets):
    return earnings / total_assets if total_assets else 0

def price_history_graph(ticker):
    TICKER = ticker.upper()

    try:
        # --- Step 2: Get stock data ---
        stock = yf.Ticker(TICKER)
        stock_prices = stock.history(period="10y")
        stock_info = stock.info
        stock_financials = stock.financials
        stock_balance_sheet = stock.balance_sheet

        # Get last values
        last_price = stock_prices['Close'].iloc[-1]
        earnings = stock_financials.loc["Net Income"].iloc[0]
        dividend = stock_info.get('lastDividendValue', 0)
        shares_outstanding = stock_info.get('sharesOutstanding', 0)

        # Average total assets over last 2 years
        try:
            total_assets = (stock_balance_sheet.loc["Total Assets"].iloc[0] + 
                            stock_balance_sheet.loc["Total Assets"].iloc[1]) / 2
        except:
            total_assets = 0

        # Calculate financial ratios
        dividend_yield = calculate_dividend_yield(dividend, last_price) * 100
        eps = calculate_eps(earnings, shares_outstanding)
        pe_ratio = calculate_pe_ratio(last_price, eps)
        roa = calculate_roa(earnings, total_assets) * 100

        # Print financial summary
        print(f"\nChosen Stock: {TICKER}")
        print(f"Last Share Price: {last_price:.2f}")
        print(f"PE Ratio: {pe_ratio:.2f}")
        print(f"Dividend Yield: {dividend_yield:.2f}%")
        print(f"EPS: {eps:.2f}")
        print(f"ROA: {roa:.2f}%\n")

    except Exception as e:
        print(f"Error getting stock info: {e}")
        return

    # --- Step 3: Load historical price targets from CSV ---
    try:
        targets_df = pd.read_csv('price_targets.csv', parse_dates=['Date'])
    except Exception as e:
        print(f"Could not load price_targets.csv: {e}")
        targets_df = None

    # --- Step 4: Get ASX200 index data ---
    try:
        asx200 = yf.Ticker("^AXJO")
        asx200_history = asx200.history(period="10y")
    except Exception as e:
        print(f"Error loading ASX200 data: {e}")
        asx200_history = None

    # --- Step 5: Plot everything ---
    plt.figure(figsize=(14, 7))

    # Stock price
    plt.plot(stock_prices.index, stock_prices['Close'], label=f"{TICKER} Price", linewidth=2)

    # Research targets
    if targets_df is not None:
        plt.plot(targets_df['Date'], targets_df['PriceTarget'], label="Research Price Target", linestyle='--')

    # ASX200 index
    if asx200_history is not None:
        plt.plot(asx200_history.index, asx200_history['Close'], label="ASX200 Index", alpha=0.7)

    # Final chart formatting
    plt.title(f"{TICKER} vs Research Targets vs ASX200")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()