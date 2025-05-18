import pandas as pd

class DataProcessor:
    def __init__(self, logger):
        self.logger = logger

    def clean_data(self, df):
        self.logger.info("🧹 Очищення даних...")
        try:
            # Видаляємо порожні рядки та стовпці
            df.dropna(how="all", inplace=True)
            df.dropna(axis=1, how="all", inplace=True)

            # Видалення дублікатів (якщо є)
            df.drop_duplicates(inplace=True)

            # Скидаємо індекс для коректної роботи з даними
            df.reset_index(drop=True, inplace=True)

            # Переконаємось, що колонка Date — у datetime форматі
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df.dropna(subset=['Date'], inplace=True)  # видаляємо рядки з некоректними датами

            self.logger.info(f"✅ Дані очищено: {df.shape[0]} рядків, {df.shape[1]} стовпців.")
            return df
        except Exception as e:
            self.logger.error(f"❌ Помилка під час очищення даних: {e}")
            return pd.DataFrame()

    def transform_data(self, df):
        self.logger.info("🔄 Трансформація даних...")
        try:
            # Створюємо колонку з відсотковою зміною ціни закриття
            if "Close" in df.columns:
                df["Returns"] = df["Close"].pct_change()
            self.logger.info("✅ Трансформація завершена.")
            return df
        except Exception as e:
            self.logger.error(f"❌ Помилка під час трансформації даних: {e}")
            return pd.DataFrame()
