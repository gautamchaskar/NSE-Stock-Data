
# fetch_intraday_data.py
#
# Description:
# This script fetches historical intraday (1-minute) stock data from the NSE
# for a given symbol and date range.
#
# Usage:
# 1. Ensure you are in the project's virtual environment.
#    source .venv/bin/activate
#
# 2. Run the script with a symbol and date range:
#    python fetch_intraday_data.py --symbol RELIANCE --start 2024-07-01 --end 2024-07-05
#

import argparse
import os
from datetime import datetime
from openchart.core import NSEData

OUTPUT_DIR = "nsc_intraday_data"

def fetch_intraday_data(symbol, start_date, end_date):
    """Fetches 1-minute intraday data and saves it to a CSV file."""
    print(f"Fetching 1-minute intraday data for {symbol} from {start_date} to {end_date}...")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    # The filename will include the symbol and date range
    file_path = os.path.join(OUTPUT_DIR, f"{symbol}_{start_date}_to_{end_date}.csv")

    try:
        # Initialize the chart object
        chart = NSEData()
        chart.download()

        # Fetch the data for the specified timeframe
        # The library expects datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')

        # Set the interval to 1 minute
        df = chart.historical(symbol=symbol, exchange='NSE', start=start_dt, end=end_dt, interval='1m')

        if df.empty:
            print(f"No intraday data found for {symbol} in the given date range.")
            return

        # Save the data to a CSV file
        df.to_csv(file_path, index=True) # Keep the datetime index

        print(f"Successfully saved intraday data to {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    """Main function to parse arguments and fetch the data."""
    parser = argparse.ArgumentParser(description="Fetch historical intraday stock data from NSE.")
    parser.add_argument("--symbol", type=str, required=True, help="Stock symbol (e.g., RELIANCE).")
    parser.add_argument("--start", type=str, required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end", type=str, required=True, help="End date in YYYY-MM-DD format.")
    args = parser.parse_args()

    fetch_intraday_data(args.symbol.upper(), args.start, args.end)

if __name__ == "__main__":
    main()
