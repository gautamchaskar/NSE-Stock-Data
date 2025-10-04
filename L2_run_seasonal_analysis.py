import pandas as pd
from tqdm import tqdm
import numpy as np
import concurrent.futures
import os
from datetime import datetime

def calculate_daily_returns(df):
    """
    Calculates the daily returns of a stock.
    """
    df['RETURN'] = df['CLOSE'].pct_change()
    return df

def get_seasonal_heatmap_data(df):
    """
    Prepares the data for the seasonal heatmap.
    """
    df = calculate_daily_returns(df.copy())
    df['YEAR'] = df.index.year
    df['MONTH'] = df.index.month
    monthly_returns = df.groupby(['YEAR', 'MONTH'])['RETURN'].mean().unstack()
    monthly_returns.columns = [pd.to_datetime(str(col), format='%m').strftime('%b') for col in monthly_returns.columns]
    return monthly_returns

def get_custom_period_analysis(df, start_date_str, end_date_str):
    # ... (this function remains the same)
    pass

def analyze_slot(args):
    df, window_size, start_day = args
    yearly_returns = []
    for year in df.index.year.unique():
        start_date = pd.to_datetime(f"{year}-{start_day}", format="%Y-%j")
        end_date = start_date + pd.Timedelta(days=window_size)

        if end_date.year != start_date.year:
            period_data = pd.concat([
                df.loc[f'{start_date.year}-{start_date.month}-{start_date.day}':f'{start_date.year}-12-31'],
                df.loc[f'{end_date.year}-01-01':f'{end_date.year}-{end_date.month}-{end_date.day}']
            ])
        else:
            period_data = df.loc[start_date:end_date]

        if not period_data.empty:
            period_return = (period_data.iloc[-1]['CLOSE'] - period_data.iloc[0]['CLOSE']) / period_data.iloc[0]['CLOSE']
            yearly_returns.append(period_return)
    
    if yearly_returns:
        median_return = np.median(yearly_returns)
        min_return = np.min(yearly_returns)
        max_return = np.max(yearly_returns)
        Standard_Dev = np.std(yearly_returns)
        total_years = len(yearly_returns)
        positive_years_count = sum(1 for r in yearly_returns if r > 0)
        consistency = positive_years_count / total_years

        return {
            "start_day": start_day,
            "end_day": (start_day + window_size) % 365,
            "median_return": median_return,
            "min_return": min_return,
            "max_return": max_return,
            "Standard_Dev": Standard_Dev,
            "consistency": consistency,
            "positive_years": positive_years_count,
            "total_years": total_years,
            "window_size": window_size
        }
    return None

def find_all_seasonal_slots(df, progress_callback, log_callback=None):
    """
    Finds all seasonal slots for all window sizes and returns all results.
    This function is parallelized to speed up the analysis of a single stock.
    """
    all_results = []
    
    tasks = []
    for window_size in range(1, 366):
        for start_day in range(1, 366):
            tasks.append((df, window_size, start_day))

    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Using tqdm to show progress for the inner loop, though this will only be visible
        # if this function is run in a context that displays tqdm's output.
        results = list(tqdm(executor.map(analyze_slot, tasks), total=len(tasks), desc="Analyzing slots"))
        all_results = [res for res in results if res is not None]

    # The progress_callback is not easily supported with this parallel structure,
    # as the tasks are not completed in a predictable order for window_size.
    # If progress reporting is critical, a different approach would be needed.
    if progress_callback:
        progress_callback(1.0) # Mark as complete

    return all_results

def find_ma_crosses(df):
    """
    Finds Golden and Death Crosses in the stock data.
    """
    df['MA50'] = df['CLOSE'].rolling(window=50).mean()
    df['MA200'] = df['CLOSE'].rolling(window=200).mean()
    
    crosses = []
    df_cleaned = df.dropna(subset=['MA50', 'MA200'])
    
    prev_ma50 = df_cleaned['MA50'].shift(1)
    prev_ma200 = df_cleaned['MA200'].shift(1)

    golden_cross_dates = df_cleaned[(df_cleaned['MA50'] > df_cleaned['MA200']) & (prev_ma50 <= prev_ma200)].index
    for date in golden_cross_dates:
        crosses.append({'date': date, 'type': 'Golden Cross'})

    death_cross_dates = df_cleaned[(df_cleaned['MA50'] < df_cleaned['MA200']) & (prev_ma50 >= prev_ma200)].index
    for date in death_cross_dates:
        crosses.append({'date': date, 'type': 'Death Cross'})
        
    return sorted(crosses, key=lambda x: x['date'], reverse=True)

def find_volume_spikes(df, lookback=50, threshold=2.0):
    """
    Finds recent volume spikes.
    """
    df['Volume_MA'] = df['VOLUME'].rolling(window=lookback).mean()
    spikes = df[df['VOLUME'] > (df['Volume_MA'] * threshold)]
    
    spike_details = []
    for date, row in spikes.iterrows():
        price_change = df.loc[date, 'CLOSE'] - df.loc[date, 'OPEN']
        price_pct_change = (price_change / df.loc[date, 'OPEN']) * 100
        spike_details.append({
            'date': date,
            'volume': row['VOLUME'],
            'avg_volume': row['Volume_MA'],
            'price_pct_change': price_pct_change
        })
        
    return sorted(spike_details, key=lambda x: x['date'], reverse=True)

# --- Batch Analysis Logic --- 

# --- Folder Paths (consider making these configurable) ---
data_folder = "/Users/gautamchaskar/Documents/NSE-Stock-Data/L1_historical_stock_data"
results_folder = "/Users/gautamchaskar/Documents/NSE-Stock-Data/L2_seasonal_analysis_reports"

def _run_and_save_single_stock_analysis(stock_file):
    """
    Internal function to run seasonal analysis for a single stock file and save the results.
    """
    try:
        df = pd.read_csv(os.path.join(data_folder, stock_file))
        df['DATE'] = pd.to_datetime(df['DATE'])
        df.set_index('DATE', inplace=True)
        
        # Call the function to get ALL slots
        all_slots = find_all_seasonal_slots(df, progress_callback=None, log_callback=None)
        
        if all_slots:
            results_df = pd.DataFrame(all_slots)
            
            # Extract symbol and name
            parts = stock_file.replace('.csv', '').split(' - ')
            stock_symbol = parts[0]
            stock_name_full = parts[1] if len(parts) > 1 else stock_symbol
            
            # Add the new columns
            results_df['Stock Symbol'] = stock_symbol
            results_df['Stock Name'] = stock_name_full
            
            # Save the entire DataFrame
            results_df.to_csv(os.path.join(results_folder, f"{stock_symbol}.csv"), index=False)
            return f"Successfully processed {stock_file}"
        else:
            return f"No seasonal slots found for {stock_file}"
    except Exception as e:
        return f"Error processing {stock_file}: {e}"

def run_full_batch_analysis():
    """
    Runs the full batch seasonal analysis for all stocks found in the data_folder.
    """
    print(f"[{datetime.now()}] Starting full batch analysis...")

    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    print(f"[{datetime.now()}] Listing stock files from {data_folder}...")
    stock_files = sorted([f for f in os.listdir(data_folder) if f.endswith(".csv")])
    total_stocks = len(stock_files)
    print(f"[{datetime.now()}] Found {total_stocks} stock files.")
    
    # Process stocks sequentially. The parallelism is handled inside find_all_seasonal_slots.
    for i, stock_file in enumerate(stock_files):
        print(f"\n--- Processing stock {i + 1}/{total_stocks}: {stock_file} ---")
        result = _run_and_save_single_stock_analysis(stock_file)
        print(f"--- Finished stock {i + 1}/{total_stocks}: {result} ---")

    print(f"\n[{datetime.now()}] Batch analysis complete!")

if __name__ == '__main__':
    run_full_batch_analysis()