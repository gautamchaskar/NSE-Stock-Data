

# fetch_stock_data_yfinance.py
#
# Description:
# This script downloads historical stock data from Yahoo Finance.
# It is designed to be more robust than using the NSE's direct APIs.
#
# Usage:
# 1. Run the script to download/update data for all available stocks:
#    python fetch_stock_data_yfinance.py
#
# 2. To download/update for a single stock:
#    python fetch_stock_data_yfinance.py --symbol RELIANCE
#

import os
import argparse
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from multiprocessing import Pool, cpu_count
from nsetools import Nse
from tqdm import tqdm

import time
import random
import glob

OUTPUT_DIR = "L1_historical_stock_data"

def get_all_nse_symbols():
    """Fetches a list of all equity symbols from NSE."""
    print("Fetching all stock symbols from NSE...")
    try:
        nse = Nse()
        all_symbols = sorted(nse.get_stock_codes())
        # Clean up the list
        all_symbols = [s for s in all_symbols if s and s.strip()] 
        print(f"Found {len(all_symbols)} stock symbols.")
        return all_symbols
    except Exception as e:
        print(f"Error fetching stock list: {e}")
        return []

def fetch_and_save_stock_data(symbol):
    """Downloads historical data and saves it to a 'SYMBOL - NAME.csv' file."""
    ticker = f"{symbol}.NS"

    try:
        time.sleep(random.uniform(0.5, 1.5))
        stock = yf.Ticker(ticker)
        
        # --- Get company name for the filename ---
        try:
            # --- Check for existing file ---
            existing_files = glob.glob(os.path.join(OUTPUT_DIR, f"{symbol} - *.csv"))
            if existing_files:
                file_path = existing_files[0]
            else:
                company_name = stock.info.get('longName', symbol)
                # Sanitize the name for the filename
                sanitized_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '.')).rstrip()
                file_path = os.path.join(OUTPUT_DIR, f"{symbol} - {sanitized_name}.csv")
        except Exception:
            sanitized_name = symbol
            file_path = os.path.join(OUTPUT_DIR, f"{symbol} - {sanitized_name}.csv")
        # --- END ---

        df_new = stock.history(period="max", auto_adjust=False)

        if df_new.empty:
            return f"{symbol}: No data found on Yahoo Finance."

        df_new.reset_index(inplace=True)
        df_new.rename(columns={'Date': 'DATE', 'Open': 'OPEN', 'High': 'HIGH', 'Low': 'LOW', 'Close': 'CLOSE', 'Volume': 'VOLUME'}, inplace=True)
        
        # We don't need the name column anymore
        df_new = df_new[['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']]
        df_new['DATE'] = pd.to_datetime(df_new['DATE']).dt.date

        df_new.to_csv(file_path, index=False)

        return f"{symbol}: Success. Saved to {file_path}"

    except Exception as e:
        return f"{symbol}: Error - {e}"

def main():
    """Main function to parse arguments and orchestrate the download."""
    parser = argparse.ArgumentParser(description="Download historical stock data from Yahoo Finance.")
    parser.add_argument("--symbol", type=str, help="Download history for a single stock symbol.")
    args = parser.parse_args()

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if args.symbol:
        # Single stock download
        print(fetch_and_save_stock_data(args.symbol.upper()))
    else:
        # All stocks download/update
        symbols = get_all_nse_symbols()
        if not symbols:
            print("Could not retrieve stock list. Exiting.")
            return

        print(f"\nStarting download for {len(symbols)} stocks using yfinance...")
        # Use multiprocessing pool for parallel execution
        with Pool(processes=cpu_count()) as pool:
            results = list(tqdm(pool.imap_unordered(fetch_and_save_stock_data, symbols), total=len(symbols)))

        print("\n--- Download Complete ---")
        # Optional: Print error messages for inspection
        error_count = 0
        for res in results:
            if "Error" in res or "No data" in res:
                print(res)
                error_count += 1
        print(f"\nFinished with {error_count} errors.")

if __name__ == "__main__":
    main()
