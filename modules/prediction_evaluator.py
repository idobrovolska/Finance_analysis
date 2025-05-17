import pandas as pd


class PredictionEvaluator:
    def __init__(self, logger):
        self.logger = logger

    def evaluate(self, filepath, prediction):
        self.logger.info(f"📊 Оцінка прогнозу для файлу {filepath}...")
        try:
            data = pd.read_csv(filepath)
            if "Close" not in data.columns:
                self.logger.warning("⚠️ Дані не містять стовпця 'Close'.")
                return None

            # Порівнюємо останню реальну ціну з прогнозом
            actual_price = float(data["Close"].iloc[-1])
            prediction = float(prediction)
            error = abs(actual_price - prediction)
            self.logger.info(f"✅ Прогноз оцінено: фактична ціна {actual_price}, прогноз {prediction}, абсолютна помилка {error:.2f}.")
            return error

        except Exception as e:
            self.logger.error(f"❌ Помилка під час оцінки прогнозу: {e}")
            return None
