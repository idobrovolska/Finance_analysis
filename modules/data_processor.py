import pandas as pd


class DataProcessor:
    def __init__(self, logger):
        self.logger = logger

    def clean_data(self, df):
        self.logger.info("🧹 Очищення даних...")
        try:
            # Видалення порожніх рядків і стовпців
            df.dropna(how="all", inplace=True)
            df.dropna(axis=1, how="all", inplace=True)

            # Видалення дублікатів
            df.drop_duplicates(inplace=True)

            # Скидання індекса для коректного експорту в CSV
            df.reset_index(drop=True, inplace=True)

            self.logger.info(f"✅ Дані очищено: {df.shape[0]} рядків, {df.shape[1]} стовпців.")
            return df
        except Exception as e:
            self.logger.error(f"❌ Помилка під час очищення даних: {e}")
            return pd.DataFrame()

    def transform_data(self, df):
        self.logger.info("🔄 Трансформація даних...")
        try:
            # Трансформація може включати конвертацію типів, створення нових колонок тощо
            if "Close" in df.columns:
                df["Returns"] = df["Close"].pct_change()
            self.logger.info("✅ Трансформація завершена.")
            return df
        except Exception as e:
            self.logger.error(f"❌ Помилка під час трансформації даних: {e}")
            return pd.DataFrame()
