import yfinance as yf
import pandas as pd
import numpy as np
import datetime

def get_stock_data(ticker):
    """Fetches stock data using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        return stock
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def calculate_price_metrics(stock):
    """Calculates various price-related metrics."""
    try:
        # Get stock info dict first
        info = stock.info
        
        # Initialize the metrics dictionary
        price_metrics = {}
        
        # Get direct info from info dictionary
        if info:
            price_metrics['current_price'] = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            price_metrics['52w_high'] = info.get('fiftyTwoWeekHigh')
            price_metrics['52w_low'] = info.get('fiftyTwoWeekLow')
            price_metrics['market_cap'] = info.get('marketCap')
        
        # Try to get historical data for additional metrics
        hist = stock.history(period="1y")
        
        if not hist.empty:
            # Calculate price change
            if 'Close' in hist.columns and len(hist) > 0:
                current_price = hist['Close'].iloc[-1]
                price_year_ago = hist['Close'].iloc[0] if len(hist) >= 252 else None
                
                if price_year_ago is not None and price_year_ago > 0:
                    price_metrics['price_change_1y'] = ((current_price / price_year_ago) - 1) * 100
                
                # Calculate moving averages
                if len(hist) >= 200:
                    price_metrics['ma_50'] = hist['Close'].rolling(window=50).mean().iloc[-1]
                    price_metrics['ma_200'] = hist['Close'].rolling(window=200).mean().iloc[-1]
                
                # Calculate average daily volume
                if 'Volume' in hist.columns:
                    price_metrics['avg_volume'] = hist['Volume'].mean()
        
        return price_metrics
    except Exception as e:
        print(f"Warning: Error calculating price metrics: {e}")
        return {}

def calculate_valuation_ratios(stock):
    """Calculates valuation ratios."""
    try:
        info = stock.info
        valuation_ratios = {}
        
        # Direct from info dictionary
        valuation_ratios['pe_ratio'] = info.get('trailingPE')
        valuation_ratios['forward_pe'] = info.get('forwardPE')
        valuation_ratios['pb_ratio'] = info.get('priceToBook')
        valuation_ratios['ps_ratio'] = info.get('priceToSalesTrailing12Months')
        valuation_ratios['peg_ratio'] = info.get('pegRatio')
        valuation_ratios['ev_to_ebitda'] = info.get('enterpriseToEbitda')
        
        # Calculate dividend yield
        if 'dividendYield' in info and info['dividendYield'] is not None:
            valuation_ratios['dividend_yield'] = info['dividendYield'] * 100
        elif 'trailingAnnualDividendYield' in info and info['trailingAnnualDividendYield'] is not None:
            valuation_ratios['dividend_yield'] = info['trailingAnnualDividendYield'] * 100
        
        return valuation_ratios
    except Exception as e:
        print(f"Warning: Error calculating valuation ratios: {e}")
        return {}

def calculate_profitability_ratios(stock):
    """Calculates profitability ratios."""
    try:
        info = stock.info
        profitability_ratios = {}
        
        # Get relevant financial data from info
        balance_sheet = stock.balance_sheet
        income_stmt = stock.income_stmt
        
        # Check if we have the data to calculate these ratios
        if not balance_sheet.empty and not income_stmt.empty:
            latest_bs = balance_sheet.iloc[:, 0]
            latest_is = income_stmt.iloc[:, 0]
            
            # Calculate ROE
            if 'totalStockholderEquity' in latest_bs.index and 'netIncome' in latest_is.index:
                equity = latest_bs['totalStockholderEquity']
                net_income = latest_is['netIncome']
                if equity != 0:
                    profitability_ratios['roe'] = (net_income / equity) * 100
            
            # Calculate ROA
            if 'totalAssets' in latest_bs.index and 'netIncome' in latest_is.index:
                assets = latest_bs['totalAssets']
                net_income = latest_is['netIncome']
                if assets != 0:
                    profitability_ratios['roa'] = (net_income / assets) * 100
            
            # Calculate margins
            if 'totalRevenue' in latest_is.index:
                revenue = latest_is['totalRevenue']
                if revenue != 0:
                    if 'grossProfit' in latest_is.index:
                        profitability_ratios['gross_margin'] = (latest_is['grossProfit'] / revenue) * 100
                    
                    if 'operatingIncome' in latest_is.index:
                        profitability_ratios['operating_margin'] = (latest_is['operatingIncome'] / revenue) * 100
                    
                    if 'netIncome' in latest_is.index:
                        profitability_ratios['profit_margin'] = (latest_is['netIncome'] / revenue) * 100
        
        # Use info dictionary as fallback
        if 'returnOnEquity' in info and info['returnOnEquity'] is not None and 'roe' not in profitability_ratios:
            profitability_ratios['roe'] = info['returnOnEquity'] * 100
            
        if 'returnOnAssets' in info and info['returnOnAssets'] is not None and 'roa' not in profitability_ratios:
            profitability_ratios['roa'] = info['returnOnAssets'] * 100
            
        if 'grossMargins' in info and info['grossMargins'] is not None and 'gross_margin' not in profitability_ratios:
            profitability_ratios['gross_margin'] = info['grossMargins'] * 100
            
        if 'operatingMargins' in info and info['operatingMargins'] is not None and 'operating_margin' not in profitability_ratios:
            profitability_ratios['operating_margin'] = info['operatingMargins'] * 100
            
        if 'profitMargins' in info and info['profitMargins'] is not None and 'profit_margin' not in profitability_ratios:
            profitability_ratios['profit_margin'] = info['profitMargins'] * 100
        
        return profitability_ratios
    except Exception as e:
        print(f"Warning: Error calculating profitability ratios: {e}")
        return {}

def calculate_liquidity_ratios(stock):
    """Calculates liquidity and solvency ratios."""
    try:
        liquidity_ratios = {}
        balance_sheet = stock.balance_sheet
        income_stmt = stock.income_stmt
        
        if not balance_sheet.empty:
            latest_bs = balance_sheet.iloc[:, 0]
            
            # Calculate current ratio
            if 'totalCurrentAssets' in latest_bs.index and 'totalCurrentLiabilities' in latest_bs.index:
                current_assets = latest_bs['totalCurrentAssets']
                current_liabilities = latest_bs['totalCurrentLiabilities']
                if current_liabilities != 0:
                    liquidity_ratios['current_ratio'] = current_assets / current_liabilities
            
            # Calculate quick ratio
            if 'totalCurrentAssets' in latest_bs.index and 'inventory' in latest_bs.index and 'totalCurrentLiabilities' in latest_bs.index:
                current_assets = latest_bs['totalCurrentAssets']
                inventory = latest_bs['inventory']
                current_liabilities = latest_bs['totalCurrentLiabilities']
                if current_liabilities != 0:
                    liquidity_ratios['quick_ratio'] = (current_assets - inventory) / current_liabilities
            
            # Calculate debt-to-equity
            if 'totalLiabilities' in latest_bs.index and 'totalStockholderEquity' in latest_bs.index:
                total_debt = latest_bs['totalLiabilities']
                equity = latest_bs['totalStockholderEquity']
                if equity != 0:
                    liquidity_ratios['debt_to_equity'] = total_debt / equity
            
            # Calculate interest coverage
            if not income_stmt.empty:
                latest_is = income_stmt.iloc[:, 0]
                if 'operatingIncome' in latest_is.index and 'interestExpense' in latest_is.index:
                    operating_income = latest_is['operatingIncome']
                    interest_expense = latest_is['interestExpense']
                    if interest_expense != 0:
                        liquidity_ratios['interest_coverage'] = operating_income / abs(interest_expense)
        
        return liquidity_ratios
    except Exception as e:
        print(f"Warning: Error calculating liquidity ratios: {e}")
        return {}

def calculate_growth_rates(stock):
    """Calculates year-over-year growth rates."""
    try:
        growth_rates = {}
        income_stmt = stock.income_stmt
        
        if not income_stmt.empty and income_stmt.shape[1] >= 2:
            current_year = income_stmt.iloc[:, 0]
            prev_year = income_stmt.iloc[:, 1]
            
            # Revenue growth
            if 'totalRevenue' in current_year.index and 'totalRevenue' in prev_year.index:
                current_revenue = current_year['totalRevenue']
                prev_revenue = prev_year['totalRevenue']
                if prev_revenue != 0:
                    growth_rates['revenue_growth'] = ((current_revenue / prev_revenue) - 1) * 100
            
            # Earnings growth
            if 'netIncome' in current_year.index and 'netIncome' in prev_year.index:
                current_earnings = current_year['netIncome']
                prev_earnings = prev_year['netIncome']
                if prev_earnings != 0:
                    growth_rates['earnings_growth'] = ((current_earnings / prev_earnings) - 1) * 100
            
            # EBITDA growth
            if 'ebitda' in current_year.index and 'ebitda' in prev_year.index:
                current_ebitda = current_year['ebitda']
                prev_ebitda = prev_year['ebitda']
                if prev_ebitda != 0:
                    growth_rates['ebitda_growth'] = ((current_ebitda / prev_ebitda) - 1) * 100
        
        return growth_rates
    except Exception as e:
        print(f"Warning: Error calculating growth rates: {e}")
        return {}

def get_financial_ratios(ticker):
    """Main function to retrieve all financial ratios for a given stock ticker."""
    stock = get_stock_data(ticker)
    if not stock:
        return None
    
    # Calculate all ratios
    price_metrics = calculate_price_metrics(stock)
    valuation_ratios = calculate_valuation_ratios(stock)
    profitability_ratios = calculate_profitability_ratios(stock)
    liquidity_ratios = calculate_liquidity_ratios(stock)
    growth_rates = calculate_growth_rates(stock)
    
    # Combine all ratios into a single dictionary
    return {
        'ticker': ticker,
        'price_metrics': price_metrics,
        'valuation_ratios': valuation_ratios,
        'profitability_ratios': profitability_ratios,
        'liquidity_ratios': liquidity_ratios,
        'growth_rates': growth_rates
    }

def format_value(value, is_percentage=False, prefix='$'):
    """Helper function to format values nicely for display."""
    if value is None or value == '' or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    
    if is_percentage:
        return f"{value:.2f}%"
    elif isinstance(value, (int, float)):
        if prefix == '$' and value >= 1e9:
            return f"{prefix}{value/1e9:.2f}B"
        elif prefix == '$' and value >= 1e6:
            return f"{prefix}{value/1e6:.2f}M"
        elif prefix == '$':
            return f"{prefix}{value:.2f}"
        else:
            return f"{value:.2f}"
    else:
        return str(value)

def format_financial_ratios_summary(ratios):
    """Creates a neatly formatted summary of financial ratios."""
    if not ratios:
        return "Could not generate summary. No data available."
    
    ticker = ratios['ticker']
    price_metrics = ratios['price_metrics']
    valuation_ratios = ratios['valuation_ratios']
    profitability_ratios = ratios['profitability_ratios']
    liquidity_ratios = ratios['liquidity_ratios']
    growth_rates = ratios['growth_rates']
    
    summary = []
    summary.append("=" * 53)
    summary.append(f"FINANCIAL RATIOS SUMMARY FOR {ticker}")
    summary.append("=" * 53)
    summary.append("")
    
    # Price metrics
    summary.append("PRICE METRICS:")
    summary.append("-" * 53)
    current_price = format_value(price_metrics.get('current_price'))
    low_52w = format_value(price_metrics.get('52w_low'))
    high_52w = format_value(price_metrics.get('52w_high'))
    
    summary.append(f"Current Price: {current_price}")
    if low_52w != "N/A" and high_52w != "N/A":
        summary.append(f"52-Week Range: {low_52w} - {high_52w}")
    else:
        summary.append(f"52-Week Range: N/A")
    
    summary.append(f"Price Change (1Y): {format_value(price_metrics.get('price_change_1y'), is_percentage=True)}")
    summary.append(f"Market Cap: {format_value(price_metrics.get('market_cap'))}")
    summary.append("")
    
    # Valuation ratios
    summary.append("VALUATION RATIOS:")
    summary.append("-" * 53)
    summary.append(f"P/E Ratio: {format_value(valuation_ratios.get('pe_ratio'), prefix='')}")
    summary.append(f"Forward P/E: {format_value(valuation_ratios.get('forward_pe'), prefix='')}")
    summary.append(f"P/B Ratio: {format_value(valuation_ratios.get('pb_ratio'), prefix='')}")
    summary.append(f"P/S Ratio: {format_value(valuation_ratios.get('ps_ratio'), prefix='')}")
    summary.append(f"PEG Ratio: {format_value(valuation_ratios.get('peg_ratio'), prefix='')}")
    summary.append(f"EV/EBITDA: {format_value(valuation_ratios.get('ev_to_ebitda'), prefix='')}")
    summary.append(f"Dividend Yield: {format_value(valuation_ratios.get('dividend_yield'), is_percentage=True, prefix='')}")
    summary.append("")
    
    # Profitability ratios
    summary.append("PROFITABILITY RATIOS:")
    summary.append("-" * 53)
    summary.append(f"Return on Equity (ROE): {format_value(profitability_ratios.get('roe'), is_percentage=True, prefix='')}")
    summary.append(f"Return on Assets (ROA): {format_value(profitability_ratios.get('roa'), is_percentage=True, prefix='')}")
    summary.append(f"Gross Margin: {format_value(profitability_ratios.get('gross_margin'), is_percentage=True, prefix='')}")
    summary.append(f"Operating Margin: {format_value(profitability_ratios.get('operating_margin'), is_percentage=True, prefix='')}")
    summary.append(f"Profit Margin: {format_value(profitability_ratios.get('profit_margin'), is_percentage=True, prefix='')}")
    summary.append("")
    
    # Liquidity & Solvency
    summary.append("LIQUIDITY & SOLVENCY:")
    summary.append("-" * 53)
    summary.append(f"Current Ratio: {format_value(liquidity_ratios.get('current_ratio'), prefix='')}")
    summary.append(f"Quick Ratio: {format_value(liquidity_ratios.get('quick_ratio'), prefix='')}")
    summary.append(f"Debt-to-Equity: {format_value(liquidity_ratios.get('debt_to_equity'), prefix='')}")
    summary.append(f"Interest Coverage: {format_value(liquidity_ratios.get('interest_coverage'), prefix='')}")
    summary.append("")
    
    # Growth rates
    summary.append("GROWTH RATES (YoY):")
    summary.append("-" * 53)
    summary.append(f"Revenue Growth: {format_value(growth_rates.get('revenue_growth'), is_percentage=True, prefix='')}")
    summary.append(f"Earnings Growth: {format_value(growth_rates.get('earnings_growth'), is_percentage=True, prefix='')}")
    summary.append(f"EBITDA Growth: {format_value(growth_rates.get('ebitda_growth'), is_percentage=True, prefix='')}")
    summary.append("")
    
    summary.append("=" * 53)
    
    return "\n".join(summary)

if __name__ == "__main__":
    ticker_symbol = input("Enter the stock ticker symbol (e.g., AAPL): ")
    
    if not ticker_symbol:
        print("No ticker symbol provided. Exiting.")
        exit(1)
    
    print(f"\nFetching financial ratios for {ticker_symbol}...\n")
    
    # Get stock data for debugging
    stock = get_stock_data(ticker_symbol)
    if stock:
        print("Direct info from yfinance API:")
        try:
            info = stock.info
            print(f"Current Price: ${info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')}")
            print(f"52-Week High: ${info.get('fiftyTwoWeekHigh')}")
            print(f"52-Week Low: ${info.get('fiftyTwoWeekLow')}")
            print(f"Market Cap: ${info.get('marketCap')}")
            print(f"P/E Ratio: {info.get('trailingPE')}")
            print("\n")
            
            # Print a sample of historical data
            hist = stock.history(period="1y")
            if not hist.empty:
                print("Last 5 days of historical data:")
                print(hist.tail())
                print("\n")
        except Exception as e:
            print(f"Error accessing stock info: {e}")
    
    # Get the ratios
    ratios = get_financial_ratios(ticker_symbol)
    
    if ratios:
        # Print the formatted summary
        summary = format_financial_ratios_summary(ratios)
        print(summary)
    else:
        print(f"Failed to retrieve financial ratios for {ticker_symbol}.")