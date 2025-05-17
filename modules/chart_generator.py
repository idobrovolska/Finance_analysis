import os
import pandas as pd
import matplotlib.pyplot as plt


class ChartGenerator:
    def __init__(self, logger, charts_dir="charts"):
        self.logger = logger
        os.makedirs(charts_dir, exist_ok=True)
        self.charts_dir = charts_dir

    def generate_price_chart(self, filepath, ticker=None):
        self.logger.info(f"Generating price chart for {filepath}...")
        try:
            df = pd.read_csv(filepath, parse_dates=["Date"])
            if "Close" not in df.columns:
                self.logger.warning(f"'Close' column not found in {filepath}.")
                return None
            if df.empty:
                self.logger.warning(f"No data in {filepath}.")
                return None

            plt.figure(figsize=(10, 6))
            plt.plot(df["Date"], df["Close"], marker="o", linestyle="-")
            plt.xticks(rotation=45)
            plt.title(f"{ticker} Price Dynamics" if ticker else "Stock Price Dynamics")
            plt.xlabel("Date")
            plt.ylabel("Price (USD)")
            plt.tight_layout()

            chart_filename = os.path.join(self.charts_dir, f"{ticker}_price_chart.png" if ticker else "price_chart.png")
            plt.savefig(chart_filename)
            plt.close()

            self.logger.info(f"Price chart saved to {chart_filename}.")
            return chart_filename
        except Exception as e:
            self.logger.error(f"Error generating chart for {filepath}: {e}")
            return None
