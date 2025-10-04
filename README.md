<div align="center">
  <h1>NSE Stock Data Analysis 📈</h1>
  <p>
    A Python-based tool to fetch, analyze, and screen National Stock Exchange (NSE) data for seasonal trading insights.
  </p>

  [![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by-nc/4.0/)
  [![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![Built with Streamlit](https://img.shields.io/badge/built%20with-Streamlit-ff69b4.svg)](https://www.streamlit.io/)

</div>

---

## 📚 Table of Contents
- [🚀 Prerequisites](#-prerequisites)
- [🛠️ Installation](#️-installation)
- [⚙️ Project Pipeline (L1-L2-L3)](#️-project-pipeline-l1-l2-l3)
- [▶️ How to Run the Pipeline](#️-how-to-run-the-pipeline)
- [🧠 Analysis Deep Dive](#-analysis-deep-dive)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

---

## 🚀 Prerequisites

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

## 🛠️ Installation

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

## ⚙️ Project Pipeline (L1-L2-L3)

This project is structured as a three-level data pipeline. Each level has a dedicated script and data folder, making the workflow clear and modular.

| Level | Script | Input Folder | Output Folder | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **L1** | `L1_fetch_historical_data.py` | (None) | `L1_historical_stock_data/` | Fetches raw historical stock data from yfinance. |
| **L2** | `L2_run_seasonal_analysis.py` | `L1_historical_stock_data/` | `L2_seasonal_analysis_reports/` | Runs an exhaustive seasonal analysis on each stock. |
| **L3** | `L3_generate_insights.py` | `L2_seasonal_analysis_reports/` | `L3_actionable_insights/` | Filters and ranks the L2 data to find actionable insights. |

## ▶️ How to Run the Pipeline

Run the scripts in order from your terminal.

> **Note:** The L2 analysis is the most computationally intensive step and may take a significant amount of time to complete for all stocks.

### Step 1: Fetch Raw Data (L1)
```bash
python L1_fetch_historical_data.py
```

### Step 2: Run Seasonal Analysis (L2)
```bash
python -u L2_run_seasonal_analysis.py
```

### Step 3: Generate Actionable Insights (L3)
```bash
python L3_generate_insights.py
```

## 🧠 Analysis Deep Dive

This section provides a conceptual overview of the logic used in the L2 and L3 scripts.

### Level 2: The Calculation

To find the best seasonal periods, the tool performs an exhaustive, three-level analysis by testing every possible time window (from 1 to 365 days) at every possible starting point within the year.

#### Evaluating a "Slot"
A "slot" is the combination of a time window (e.g., 30 days) and a starting point (e.g., March 1st). Each slot is evaluated by looking at its historical performance across all available years.

1.  **Gathering Yearly Returns:** It finds the return for that slot for every single year in the dataset.
2.  **Finding the "Typical" Return (Median):** It calculates the **median return** from the list of yearly returns to get a realistic picture of the slot's typical performance.
3.  **Measuring Consistency:** It calculates the percentage of years where the return was **greater than 0%**.

The final output for each slot includes metrics like `median_return`, `consistency`, `min_return`, `max_return`, `Standard_Dev`, and `total_years`. This entire list of over 130,000 evaluated slots is saved to a CSV file for each stock in the `L2_seasonal_analysis_reports/` folder.

### Level 3: Actionable Insights Strategy

The L3 script filters the 130,000+ slots from the L2 analysis to find the single "best" opportunity for each stock using a two-stage process.

#### Stage 1: Minimum Quality Filter
A slot must meet all of the following strict criteria to be considered:
- **Consistency:** `> 80%`
- **Data History:** `>= 2 years`
- **Minimum Return:** `>= +15%` (The worst performance was still a 15% gain)
- **Slot Time:** `3 to 15 days`

#### Stage 2: The Quality Score
Any slot that passes the filter is then ranked using a weighted **Quality Score** to balance safety, return, and risk:

`Quality Score = (Consistency * 50%) + (Median Return * 30%) + (Risk-Adjusted Return * 20%)`

Where `Risk-Adjusted Return` is calculated as `Median Return / Standard Deviation`. The opportunity with the highest final Quality Score for each stock is saved to `L3_actionable_insights/actionable_insights.csv`.

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📜 License

Copyright (c) 2025 Gautam Chaskar

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](http://creativecommons.org/licenses/by-nc/4.0/).

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial** — You may not use the material for commercial purposes.
