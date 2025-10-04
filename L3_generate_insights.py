
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta

# --- Configuration ---
REPORTS_FOLDER = "/Users/gautamchaskar/Documents/NSE-Stock-Data/L2_seasonal_analysis_reports"
INSIGHTS_FOLDER = "/Users/gautamchaskar/Documents/NSE-Stock-Data/L3_actionable_insights"
OUTPUT_FILE = os.path.join(INSIGHTS_FOLDER, "actionable_insights.csv")

# --- Strategy Parameters (Final Version) ---
MIN_CONSISTENCY = 0.80
MIN_TOTAL_YEARS = 2
MIN_RETURN_THRESHOLD = 0.15  # +15%
MIN_WINDOW_SIZE = 3
MAX_WINDOW_SIZE = 15

def calculate_quality_score(row):
    """
    Calculates the Quality Score for a given seasonal slot.
    Formula: (Consistency * 50%) + (Median Return * 30%) + (Risk-Adjusted Return * 20%)
    """
    if row['Standard_Dev'] > 0:
        risk_adjusted_return = row['median_return'] / row['Standard_Dev']
    else:
        risk_adjusted_return = row['median_return'] / 0.0001 # Avoid division by zero

    score = (row['consistency'] * 0.5) + \
            (row['median_return'] * 0.3) + \
            (risk_adjusted_return * 0.2)
    return score

def generate_insights():
    """
    Analyzes all stock seasonality reports and generates a list of actionable insights
    based on the defined strategy.
    """
    print("--- Starting L3 Insights Generation ---")
    
    if not os.path.exists(REPORTS_FOLDER):
        print(f"Error: L2 reports folder not found at {REPORTS_FOLDER}")
        return
    
    if not os.path.exists(INSIGHTS_FOLDER):
        os.makedirs(INSIGHTS_FOLDER)

    all_best_slots = []
    
    stock_files = [f for f in os.listdir(REPORTS_FOLDER) if f.endswith(".csv")]
    if not stock_files:
        print(f"No L2 analysis reports found in {REPORTS_FOLDER}")
        return

    print(f"Found {len(stock_files)} stock analysis files to process.")

    for i, filename in enumerate(stock_files):
        print(f"Processing {i+1}/{len(stock_files)}: {filename}...")
        
        try:
            filepath = os.path.join(REPORTS_FOLDER, filename)
            df = pd.read_csv(filepath)

            # --- Stage 1: Minimum Quality Filter ---
            filtered_df = df[
                (df['consistency'] > MIN_CONSISTENCY) &
                (df['total_years'] >= MIN_TOTAL_YEARS) &
                (df['min_return'] >= MIN_RETURN_THRESHOLD) &
                (df['window_size'] >= MIN_WINDOW_SIZE) &
                (df['window_size'] <= MAX_WINDOW_SIZE)
            ].copy()

            if filtered_df.empty:
                continue

            # --- Stage 2: Scoring and Ranking ---
            filtered_df['quality_score'] = filtered_df.apply(calculate_quality_score, axis=1)
            
            # --- Stage 3: Final Selection ---
            best_slot = filtered_df.loc[filtered_df['quality_score'].idxmax()]
            
            # Format for final output
            # Use a non-leap year for consistent date formatting
            buy_date = (datetime(2023, 1, 1) + timedelta(days=int(best_slot['start_day']) - 1)).strftime('%b %d')
            sell_date = (datetime(2023, 1, 1) + timedelta(days=int(best_slot['end_day']) - 1)).strftime('%b %d')

            all_best_slots.append({
                'Stock Symbol': best_slot['Stock Symbol'],
                'Stock Name': best_slot['Stock Name'],
                'Buy Date': buy_date,
                'Sell Date': sell_date,
                'Median Return': f"{best_slot['median_return']:.2%}",
                'Consistency': f"{best_slot['consistency']:.2%}",
                'Min Return': f"{best_slot['min_return']:.2%}",
                'Window Size': int(best_slot['window_size']),
                'Quality Score': f"{best_slot['quality_score']:.2f}"
            })

        except Exception as e:
            print(f"  -> Error processing {filename}: {e}")

    if not all_best_slots:
        print("\nNo actionable insights found with the current strict strategy.")
        return

    # --- Create and save the final CSV ---
    insights_df = pd.DataFrame(all_best_slots)
    insights_df.sort_values(by='Quality Score', ascending=False, inplace=True)
    insights_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\nSuccessfully generated {len(insights_df)} actionable insights.")
    print(f"Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_insights()
