import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import concurrent.futures
import subprocess
from L2_run_seasonal_analysis import (
    get_seasonal_heatmap_data, 
    get_custom_period_analysis, 
    find_all_seasonal_slots,
    find_ma_crosses,
    find_volume_spikes,
    run_full_batch_analysis
)

# --- Pandas Styler Config (to allow styling large DataFrames) ---
pd.set_option("styler.render.max_elements", 2_000_000)

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Stock Seasonality Analysis", page_icon="✅")

# --- Custom CSS ---
st.markdown("""
<style>
.block-container { 
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# --- Folder Paths ---
data_folder = "/Users/gautamchaskar/Documents/NSE-Stock-Data/L1_historical_stock_data"
results_folder = "/Users/gautamchaskar/Documents/NSE-Stock-Data/L2_seasonal_analysis_reports"

# --- Helper Functions ---
def run_single_stock_analysis(stock_file, progress_callback=None, log_callback=None):
    df = pd.read_csv(os.path.join(data_folder, stock_file))
    df['DATE'] = pd.to_datetime(df['DATE'])
    df.set_index('DATE', inplace=True)
    
    # Call the new function to get ALL slots
    all_slots = find_all_seasonal_slots(df, progress_callback, log_callback)
    
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

# --- Main App Title ---
st.title("Stock Market Screener")

# --- Sidebar ---
st.sidebar.title("Data Management")
if st.sidebar.button("Fetch Latest Historical Data (L1)"):
    with st.spinner("Running L1_fetch_historical_data.py... This may take a while. See console for progress."):
        try:
            result = subprocess.run(
                ["python", "L1_fetch_historical_data.py"],
                capture_output=True,
                text=True,
                check=True
            )
            st.sidebar.success("Data fetch complete!")
            with st.sidebar.expander("See execution log"):
                st.code(result.stdout)
        except subprocess.CalledProcessError as e:
            st.sidebar.error("Error during data fetch.")
            with st.sidebar.expander("See error log"):
                st.code(e.stderr)

st.sidebar.title("Stock Selection")
stock_files = sorted([f for f in os.listdir(data_folder) if f.endswith(".csv")])

if 'selected_stock_file' not in st.session_state:
    st.session_state.selected_stock_file = "RELIANCE - Reliance Industries Limited.csv"

search_term = st.sidebar.text_input("Search for a stock (press Enter to filter)", "")

if search_term:
    filtered_stocks = [s for s in stock_files if search_term.lower() in s.lower()]
    if filtered_stocks:
        if len(filtered_stocks) > 15:
            st.sidebar.info("Showing top 15 results.")
            filtered_stocks = filtered_stocks[:15]
        st.session_state.selected_stock_file = st.sidebar.radio("Select a stock from results", filtered_stocks)
    else:
        st.sidebar.warning("No stocks found.")

st.sidebar.title("Batch Analysis")
if st.sidebar.button("Pre-compute All Stock Analysis"):
    with st.spinner("Running full batch analysis... This will take a long time. Check your console for detailed progress."):
        run_full_batch_analysis()
    st.sidebar.success("Full batch analysis complete!")

# --- System Status ---
st.sidebar.title("System Status")
try:
    import psutil
    cpu_usage = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    mem_usage = mem.percent

    st.sidebar.metric("CPU Usage", f"{cpu_usage:.2f}%")
    st.sidebar.metric("Memory Usage", f"{mem_usage:.2f}%")
except ImportError:
    st.sidebar.warning("Install `psutil` to see system status:\n\n`pip install psutil`")
except Exception as e:
    st.sidebar.error(f"Could not get system status: {e}")

# --- Stock Specific Section ---
selected_stock_file = st.session_state.selected_stock_file
stock_name = selected_stock_file.split(' - ')[0]
result_file_path = os.path.join(results_folder, f"{stock_name}.csv")

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.header(f"✅ {stock_name}")
with header_col2:
    button_label = "Re-run Analysis" if os.path.exists(result_file_path) else "Run Analysis"
    if st.button(button_label, type="secondary"):
        with st.spinner("Running analysis... This may take a while."):
            progress_bar = st.progress(0.0)
            def progress_callback(progress):
                progress_bar.progress(progress)
            run_single_stock_analysis(selected_stock_file, progress_callback)
        st.success("Analysis complete! Results are now saved for future use.")
        st.experimental_rerun()

# Load data
df = pd.read_csv(os.path.join(data_folder, selected_stock_file))
df['DATE'] = pd.to_datetime(df['DATE'])
df.set_index('DATE', inplace=True)

# --- Tabs ---
tab_names = ["✅ Seasonality", "✅ Summary", "✅ Price Chart", "✅ Moving Averages", "✅ Volume Analysis", "✅ Volatility", "📖 Documentation"]
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_names)

with tab1:
    # --- Display Results Section ---
    if os.path.exists(result_file_path):
        with st.spinner("Loading and processing existing analysis..."):
            results_df = pd.read_csv(result_file_path)
            
            # --- Compact Messages ---
            message = "Pre-computed analysis found."
            is_old_format = 'min_return' not in results_df.columns or 'max_return' not in results_df.columns
            if is_old_format:
                message += " (Old format: Re-run analysis to see all columns)."
            st.info(message)

            # --- Handle old CSV files for min/max return ---
            if 'min_return' not in results_df.columns or 'max_return' not in results_df.columns:
                results_df['min_return'] = np.nan
                results_df['max_return'] = np.nan

            # Ensure correct column names for display
            results_df['start_date'] = results_df['start_day'].apply(lambda x: pd.to_datetime(str(x), format='%j').strftime('%B %d'))
            results_df['end_date'] = results_df.apply(lambda row: (pd.to_datetime(str(row['start_day']), format='%j') + pd.Timedelta(days=row['window_size'])).strftime('%B %d'), axis=1)
            
            # --- Handle old CSV files for consistency column --- 
            if 'consistency' not in results_df.columns:
                if 'years_above_median' in results_df.columns:
                    results_df.rename(columns={'years_above_median': 'consistency'}, inplace=True)
                elif 'positive_years' in results_df.columns and 'total_years' in results_df.columns:
                    results_df['consistency'] = results_df['positive_years'] / results_df['total_years']
                else:
                    st.error("Error: Could not find 'consistency' or equivalent columns in the loaded data. Please re-run the analysis.")
                    st.stop()
            # --- End handle old CSV files --- 

            # Drop the columns we don't want to display
            results_df.drop(columns=['Stock Symbol', 'Stock Name'], errors='ignore', inplace=True)

            # Define the desired column order
            desired_column_order = [
                'window_size',
                'start_date',
                'end_date',
                'median_return',
                'min_return',
                'max_return',
                'consistency',
                'positive_years',
                'total_years'
            ]
            results_df = results_df[desired_column_order]

            # Rename columns for display
            results_df.rename(columns={
                'window_size': 'Window Size',
                'start_date': 'Start Date',
                'end_date': 'End Date',
                'median_return': 'Median Return',
                'min_return': 'Min Return',
                'max_return': 'Max Return',
                'consistency': 'Consistency',
                'positive_years': 'Positive Years',
                'total_years': 'Total Years'
            }, inplace=True)
            
            # --- Controls for Sorting and Pagination ---
            # Sorting and Rows per page
            sort_col1, sort_col2, sort_col3 = st.columns([3, 3, 2])
            with sort_col1:
                sort_by = st.selectbox("Sort by", options=results_df.columns, index=4)
            with sort_col2:
                sort_order = st.radio("Order", ["Descending", "Ascending"], index=0, horizontal=True)
            with sort_col3:
                rows_per_page = st.number_input("Rows per page", min_value=10, max_value=100, value=100, step=5)

            # --- Sorting ---
            sorted_results_df = results_df.sort_values(by=sort_by, ascending=(sort_order == "Ascending"))

            # --- Pagination State and Logic ---
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1

            total_rows = len(sorted_results_df)
            total_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page > 0 else 0)

            # --- Display Paginated Data ---
            start_idx = (st.session_state.current_page - 1) * rows_per_page
            end_idx = start_idx + rows_per_page
            paginated_df = sorted_results_df.iloc[start_idx:end_idx]
            
            st.dataframe(paginated_df.style.background_gradient(cmap='RdYlGn', subset=['Median Return', 'Min Return', 'Max Return', 'Consistency', 'Window Size'])
                        .format({'Median Return': '{:.2%}', 'Min Return': '{:.2%}', 'Max Return': '{:.2%}', 'Consistency': '{:.2%}'}))

            # --- Pagination Controls ---
            pag_col1, pag_col2, pag_col3 = st.columns([1, 2, 1])

            with pag_col1:
                if st.button("⬅️ Previous"):
                    if st.session_state.current_page > 1:
                        st.session_state.current_page -= 1
            
            with pag_col2:
                page_input_cols = st.columns([1, 2, 1])
                with page_input_cols[0]:
                    st.write("Page")
                with page_input_cols[1]:
                    st.session_state.current_page = st.number_input("Page number", min_value=1, max_value=total_pages, value=st.session_state.current_page, label_visibility="collapsed")
                with page_input_cols[2]:
                    st.write(f"of {total_pages}")

            with pag_col3:
                if st.button("Next ➡️"):
                    if st.session_state.current_page < total_pages:
                        st.session_state.current_page += 1

    st.subheader("Monthly Performance Heatmap")
    heatmap_data = get_seasonal_heatmap_data(df)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, cmap='RdYlGn', ax=ax)
    st.pyplot(fig)

with tab2:
    st.subheader("Data Summary")
    st.write(df.describe())

with tab3:
    st.subheader("Price Chart")
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['OPEN'], high=df['HIGH'], low=df['LOW'], close=df['CLOSE'])])
    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Moving Average Analysis")
    df['MA20'] = df['CLOSE'].rolling(window=20).mean()
    df['MA50'] = df['CLOSE'].rolling(window=50).mean()
    df['MA200'] = df['CLOSE'].rolling(window=200).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['CLOSE'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], mode='lines', name='20-Day MA'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], mode='lines', name='50-Day MA'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], mode='lines', name='200-Day MA'))

    crosses = find_ma_crosses(df.copy())
    if crosses:
        last_cross = crosses[0]
        fig.add_vline(x=last_cross['date'], line_width=2, line_dash="dash", 
                      line_color="green" if last_cross['type'] == 'Golden Cross' else "red")
        fig.add_annotation(x=last_cross['date'], y=df.loc[last_cross['date']]['CLOSE'], text=f"Recent {last_cross['type']}", showarrow=True, arrowhead=1)

    fig.update_layout(title="Moving Averages and Cross Events", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Insights")
    if not crosses:
        st.info("No Golden or Death cross events in the recent history.")
    else:
        last_cross = crosses[0]
        st.info(f"The last major signal was a **{last_cross['type']}** on **{last_cross['date'].date()}**.")

    if df['MA50'].iloc[-1] > df['MA200'].iloc[-1]:
        st.success("The stock is currently in a **long-term uptrend** (50-day MA is above the 200-day MA).")
    else:
        st.error("The stock is currently in a **long-term downtrend** (50-day MA is below the 200-day MA).")

with tab5:
    st.header("Volume Analysis")
    volume_spikes = find_volume_spikes(df.copy())
    df['Volume_MA'] = df['VOLUME'].rolling(window=50).mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df['VOLUME'], name='Volume'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Volume_MA'], mode='lines', name='50-Day Avg. Volume'))

    fig.update_layout(title="Volume with 50-Day Moving Average", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Insights")
    if not volume_spikes:
        st.info("No significant volume spikes recently.")
    else:
        last_spike = volume_spikes[0]
        direction = "increase" if last_spike['price_pct_change'] > 0 else "decrease"
        st.info(f"The last significant volume spike was on **{last_spike['date'].date()}**. ")
        st.info(f"On that day, the volume was **{last_spike['volume'] / last_spike['avg_volume']:.1f}x** the average, which corresponded with a **{last_spike['price_pct_change']:.2f}%** price {direction}. This suggests strong conviction from traders.")

with tab6:
    st.header("Volatility Analysis (Bollinger Bands)")
    df['20_Day_MA'] = df['CLOSE'].rolling(window=20).mean()
    df['20_Day_Std'] = df['CLOSE'].rolling(window=20).std()
    df['Upper_Band'] = df['20_Day_MA'] + (df['20_Day_Std'] * 2)
    df['Lower_Band'] = df['20_Day_MA'] - (df['20_Day_Std'] * 2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['CLOSE'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Upper_Band'], mode='lines', name='Upper Band', line=dict(color='rgba(255, 255, 255, 0.5)')))
    fig.add_trace(go.Scatter(x=df.index, y=df['Lower_Band'], mode='lines', name='Lower Band', fill='tonexty', fillcolor='rgba(255, 55, 255, 0.1)', line=dict(color='rgba(255, 255, 255, 0.5)')))

    fig.update_layout(title="Bollinger Bands", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Insights")
    last_bandwidth = (df['Upper_Band'].iloc[-1] - df['Lower_Band'].iloc[-1]) / df['20_Day_MA'].iloc[-1]
    st.info(f"The current Bollinger Bandwidth is **{last_bandwidth:.2%}**. A low bandwidth can indicate that the stock is in a period of low volatility, which may be followed by a significant price move (a 'squeeze'). A high bandwidth indicates high volatility.")

with tab7:
    st.header("📖 Project Documentation")
    try:
        with open("SEASONAL_ANALYSIS_DOCUMENTATION.md", "r") as f:
            doc_content = f.read()
        st.markdown(doc_content, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Documentation file not found.")