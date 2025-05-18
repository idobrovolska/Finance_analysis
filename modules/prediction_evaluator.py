import pandas as pd


class PredictionEvaluator:
    def __init__(self, logger):
        self.logger = logger

    def evaluate(self, data, prediction):
        self.logger.info(f"📊 Оцінка прогнозу...")

        errors = []
        for site, df in data:
            if df.empty:
                self.logger.error(f"{site} порожні данні ")

            actual_price = float(df["Close"].iloc[-1])
            prediction = float(prediction)
            error = abs(actual_price - prediction)
            errors.append((site, error))
            self.logger.info(f"✅ {site} Прогноз оцінено: фактична ціна {actual_price}, прогноз {prediction}, абсолютна помилка {error:.2f}.")

        return errors
