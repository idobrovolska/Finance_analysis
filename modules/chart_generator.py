import matplotlib.pyplot as plt
import os
import pandas as pd

class ChartGenerator:
    def __init__(self, logger, charts_dir="charts"):
        self.logger = logger
        self.charts_dir = charts_dir
        os.makedirs(self.charts_dir, exist_ok=True)

    def generate_price_chart(self, data, ticker=""):
        self.logger.info(f"📈 Генерація графіку для {ticker} за даними з сайтів...")

        plt.figure(figsize=(10, 6))
        plt.title(f"Динаміка ціни акції {ticker}")
        plt.xlabel("Дата")
        plt.ylabel("Ціна закриття")
        plt.grid(True)

        for site, df in data:
            try:
                if df.empty:
                     self.logger.error(f"❌ Таблиця для сайту {site} порожня")
                # if 'Date' not in df.columns:
                #     self.logger.error("❌ Відсутня колонка 'Date' у CSV.")
                #     return None
                #
                # df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                # df.dropna(subset=['Date'], inplace=True)
                #
                # if 'Close' not in df.columns:
                #     self.logger.error("❌ Відсутня колонка 'Close' у CSV.")
                #     return None

                plt.plot(df['Date'], df['Close'], label=f'{site}')

            except Exception as e:
                self.logger.error(f"❌ Помилка під час генерації графіку: {e}")
                return None


        plt.legend()
        filename = os.path.join(self.charts_dir, f"{ticker}_price_chart.png")
        plt.savefig(filename)
        plt.close()

        self.logger.info(f"✅ Графік збережено у {filename}")
        return filename

