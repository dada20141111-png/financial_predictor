import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_predictions(y_true, y_pred, title="Price Prediction"):
    """
    Plots Actual vs Predicted values.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(y_true.index, y_true, label="Actual", color='blue')
    plt.plot(y_true.index, y_pred, label="Predicted", color='red', linestyle='--')
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    # Save to file in headless env
    plt.savefig("prediction_plot.png")
    print("Plot saved to prediction_plot.png")

def plot_equity_curve(returns, title="Equity Curve"):
    """
    Plots cumulative returns.
    """
    cumulative = (1 + returns).cumprod()
    plt.figure(figsize=(12, 6))
    plt.plot(cumulative.index, cumulative, label="Strategy Equity")
    plt.title(title)
    plt.grid(True)
    plt.savefig("equity_curve.png")
