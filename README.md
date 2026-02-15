# Financial Predictor AI (v1.0)

A modular, AI-powered financial market prediction and trading simulation system.

## 🚀 Quick Start

1.  **Double-click `start_app.bat`**.
2.  The application will automatically install required libraries and open in your default web browser.

## 🔑 Configuration (.env)

To use **Real-time Data (OKX)** and **Paper Trading**, you need to configure your API keys.
1.  Open the `.env` file (create one from `.env.example` if missing).
2.  Add your OKX credentials:
    ```ini
    OKX_API_KEY=your_api_key
    OKX_SECRET_KEY=your_secret_key
    OKX_PASSPHRASE=your_passphrase
    ```
    *(Note: For security, never share this file or commit it to version control)*

## 🖥️ Dashboard Features

### Side Bar Controls
-   **Asset Category**: Choose Crypto, Tech Stocks, or Indices.
-   **System Mode**:
    -   **Data Source**: Toggle between *Yahoo Finance* (Free, Delayed) and *OKX* (Real-time).
    -   **Trading Mode**: Toggle between *Backtest* (Historical simulation) and *Paper Trading* (Live simulation).

### Main Panel
-   **Analysis**: Runs the XGBoost model to predict the next price close.
-   **Paper Trading**:
    -   View your simulated balance (starts at $10k USDT).
    -   Execute Buy/Sell orders based on AI predictions.
    -   Balance is saved automatically to `paper_balance.json`.

## 📂 Project Structure
-   `src/`: Source code.
-   `tests/`: Verification scripts.
-   `start_app.bat`: One-click launcher.

## ⚠️ Disclaimer
This software is for **educational and research purposes only**. Do not use it for real financial trading without extensive verification. The authors are not responsible for any financial losses.
