import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


class DataCollector:
    def __init__(self, logger, config):
        self.logger = logger
        self.data_sources = config.get("data_sources", [])

    def build_url(self, stock, start_date, end_date, source):
        if "finance.yahoo.com" in source:
            return f"https://finance.yahoo.com/quote/{stock}/history?p={stock}"
        elif "nasdaq.com" in source:
            return f"https://www.nasdaq.com/market-activity/stocks/{stock}/historical"
        elif "investing.com" in source:
            # Investing.com може вимагати інших параметрів
            return f"https://www.investing.com/equities/{stock}-historical-data"
        else:
            self.logger.warning(f"⚠️ Невідомий формат URL для джерела: {source}")
            return None

    def fetch_data(self, stock, start_date, end_date):
        url = self.build_url(stock, start_date, end_date)
        if not url:
            self.logger.error(f"❌ Не вдалося побудувати URL для {stock} з {start_date} до {end_date}.")
            return pd.DataFrame()

        self.logger.info(f"📥 Завантаження даних для {stock} з {start_date} до {end_date}...")
        try:
            response = requests.get(url)
            response.raise_for_status()

            # Парсинг HTML таблиці з даними
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table")
            if not table:
                self.logger.warning(f"⚠️ Не знайдено таблиць для {stock} на {url}.")
                return pd.DataFrame()

            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            rows = [[td.get_text(strip=True) for td in row.find_all("td")] for row in table.find_all("tr")]

            # Перетворюємо на DataFrame
            data = pd.DataFrame(rows, columns=headers)

            # Фільтруємо дані за датою
            data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
            data.dropna(subset=["Date"], inplace=True)
            data = data[(data["Date"] >= pd.to_datetime(start_date)) & (data["Date"] <= pd.to_datetime(end_date))]

            # Скидаємо індекс і повертаємо очищені дані
            data.reset_index(drop=True, inplace=True)
            self.logger.info(f"✅ Дані успішно завантажені: {data.shape[0]} рядків, {data.shape[1]} стовпців.")
            return data

        except Exception as e:
            self.logger.error(f"❌ Помилка завантаження даних для {stock}: {e}")
            return pd.DataFrame()
