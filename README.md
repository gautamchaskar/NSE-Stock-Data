# NSE Stock Data Analysis

This project contains a series of Python scripts to fetch, analyze, and generate insights from National Stock Exchange (NSE) data.

## Prerequisites

Before you begin, you need to ensure your system has the necessary tools. These steps will guide you through checking for and installing them for both macOS and Windows.

### Step 1: Install a Package Manager

A package manager automates the process of installing, updating, and removing software.

<details>
<summary><strong>macOS (Homebrew)</strong></summary>

*   **To check if you have Homebrew installed**, open your terminal and run:
    ```bash
    brew --version
    ```
*   **If it's installed**, you will see a version number (e.g., `Homebrew 3.6.12`). You can proceed to the next step.
*   **If you get an error** like `command not found: brew`, you need to install it. Run the following command in your terminal:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

</details>

<details>
<summary><strong>Windows (Winget)</strong></summary>

*   **To check if you have Winget installed**, open PowerShell and run:
    ```powershell
    winget --version
    ```
*   **If it's installed**, you will see a version number (e.g., `v1.3.2091`). You can proceed to the next step.
*   **If you get an error**, Winget is included by default in modern versions of Windows. You can install or update it from the Microsoft Store by searching for **"App Installer"**.

</details>

### Step 2: Install Python

This project is built with Python and requires it to run.

<details>
<summary><strong>macOS</strong></summary>

*   **To check if you have Python installed**, run:
    ```bash
    python3 --version
    ```
*   **If it's installed**, you will see a version number (e.g., `Python 3.9.7`).
*   **If you get an error**, you can install Python using Homebrew:
    ```bash
    brew install python
    ```

</details>

<details>
<summary><strong>Windows</strong></summary>

*   **To check if you have Python installed**, open PowerShell and run:
    ```powershell
    python --version
    ```
*   **If it's installed**, you will see a version number (e.g., `Python 3.9.7`).
*   **If you get an error**, you can install Python using Winget:
    ```powershell
    winget install Python.Python.3
    ```

</details>

### Step 3: Check for pip (Python Package Installer)

`pip` is Python's own package manager, used to install the project's dependencies. It typically comes included with Python.

<details>
<summary><strong>macOS</strong></summary>

*   **To check if you have pip installed**, run:
    ```bash
    pip3 --version
    ```
*   **If it's installed**, you will see output like `pip 21.3.1 from ...`.
*   **If you get an error**, it's likely your Python installation is incomplete. Try reinstalling Python (Step 2) or run `python3 -m ensurepip --upgrade`.

</details>

<details>
<summary><strong>Windows</strong></summary>

*   **To check if you have pip installed**, run:
    ```powershell
    pip --version
    ```
*   **If it's installed**, you will see output like `pip 21.3.1 from ...`.
*   **If you get an error**, it's likely your Python installation is incomplete. Try reinstalling Python (Step 2) or run `python -m ensurepip --upgrade`.

</details>

## Installation

Once the prerequisites are met, you can install the project itself.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gautamchaskar/NSE-Stock-Data
    ```
2.  **Navigate into the project directory:**
    ```bash
    cd NSE-Stock-Data
    ```
3.  **Install the required Python libraries:**
    *   On **macOS**, run:
        ```bash
        pip3 install -r requirements.txt
        ```
    *   On **Windows**, run:
        ```powershell
        pip install -r requirements.txt
        ```

## Project Pipeline (L1-L2-L3)

This project is structured as a three-level data pipeline. Each level has a dedicated script and data folder, making the workflow clear and modular.

| Level | Script | Input Folder | Output Folder | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **L1** | `L1_fetch_historical_data.py` | (None) | `L1_historical_stock_data/` | Fetches raw historical stock data from yfinance. |
| **L2** | `L2_run_seasonal_analysis.py` | `L1_historical_stock_data/` | `L2_seasonal_analysis_reports/` | Runs an exhaustive seasonal analysis on each stock. |
| **L3** | `L3_generate_insights.py` | `L2_seasonal_analysis_reports/` | `L3_actionable_insights/` | Filters and ranks the L2 data to find actionable insights. |

## How to Run the Pipeline

Run the scripts in order from your terminal.

### Step 1: Fetch Raw Data (L1)
```bash
python L1_fetch_historical_data.py
```

### Step 2: Run Seasonal Analysis (L2)
This is the most computationally intensive step.
```bash
python -u L2_run_seasonal_analysis.py
```

### Step 3: Generate Actionable Insights (L3)
```bash
python L3_generate_insights.py
```

## Level 2: The Calculation: A Conceptual Overview

To find the best seasonal periods, the tool performs an exhaustive, three-level analysis.

### Testing Every Possible Time Window
First, the system decides on a length of time to test, called a "time window." It starts with a window of 1 day, then 2 days, and so on, all the way up to 365 days.

### Testing Every Starting Point
For each time window, the system then tests every possible starting point within a year. For example, for a 30-day window, it first tests the period from Jan 1st to Jan 30th, then Jan 2nd to Jan 31st, and so on.

> **The "Slot":** The combination of a **Time Window** (e.g., 30 days) and a **Starting Point** (e.g., March 1st) creates a specific "slot" that needs to be evaluated.

### Evaluating a Slot's Historical Performance
To evaluate a single slot, the system looks back through the stock's entire history and analyzes how it performed during that specific period, year after year.

1.  **Gathering Yearly Returns:** It finds the return for that slot for every single year in the dataset. This results in a list of yearly returns for that slot.

2.  **Finding the "Typical" Return (Median):** From that list of yearly returns, it calculates the **median return**. The median is the "middle" value, which gives a realistic picture of the slot's typical performance.

3.  **Measuring Consistency (Positive Years):** It then calculates the percentage of years where the return was **greater than 0%**. This is the traditional measure of consistency.

### Finalizing the Slot's Data
At this point, the analysis for one single slot is complete. The system has now calculated all the necessary metrics for it:

- **`median_return`**: The typical historical return (the median).
- **`consistency`**: The percentage of years that performed with a positive return.
- **`min_return`**: The single worst return the slot has ever had. This is a key measure of historical risk.
- **`max_return`**: The single best return the slot has ever had.
- **`Standard_Dev`**: The standard deviation of returns, which measures the slot's volatility.
- **`total_years`**: The number of years of data used for the analysis.

This process is then repeated for every single `start_day` within a given `window_size`, and then for every `window_size`.

### Final L2 Output
After the entire analysis is complete, the system will have a complete list of **all** evaluated slots (over 130,000 of them). This entire list is saved to a CSV file for the stock in the `L2_seasonal_analysis_reports/` folder.

## Level 3: Actionable Insights Strategy

The L3 script filters the 130,000+ slots from the L2 analysis to find the single "best" opportunity for each stock, based on a two-stage process.

### Stage 1: Minimum Quality Filter

A slot must meet all of the following strict criteria to be considered:

1.  **Consistency:** `> 80%`
2.  **Data History:** `>= 2 years`
3.  **Minimum Return:** `>= +15%` (The worst performance was still a 15% gain)
4.  **Slot Time:** `3 to 15 days`

### Stage 2: The Quality Score

Any slot that passes the filter is then ranked using a weighted **Quality Score** to balance safety, return, and risk:

**`Quality Score = (Consistency * 50%) + (Median Return * 30%) + (Risk-Adjusted Return * 20%)`**

- **Risk-Adjusted Return** is calculated as `Median Return / Standard Deviation`.

For each stock, the opportunity with the highest final Quality Score is selected and saved to `L3_actionable_insights/actionable_insights.csv`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

Copyright (c) 2025 Gautam Chaskar

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](http://creativecommons.org/licenses/by-nc/4.0/).

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial** — You may not use the material for commercial purposes.