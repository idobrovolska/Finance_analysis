import requests
import pandas as pd

import yfinance as yf
import investpy

from datetime import datetime
import time


class DataCollector:
    def __init__(self, logger=None):
        self.logger = logger

    def date_to_timestamp(self, date_str):
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return int(time.mktime(dt.timetuple()))

    def search_symbol_yahoo(self, query):
        """
        Пошук тикера по назві компанії через Yahoo Finance search API.
        Повертає перший знайдений тикер або None.
        """
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            quotes = data.get("quotes", [])
            if not quotes:
                if self.logger:
                    self.logger.info(f"Не знайдено тикерів для запиту '{query}'")
                return None
            # Повертаємо перший релевантний тикер з типом "EQUITY"
            for item in quotes:
                if item.get("quoteType") == "EQUITY" and "symbol" in item:
                    return item["symbol"]
            # Якщо не знайшли equity, повертаємо перший символ, якщо є
            return quotes[0].get("symbol", None)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Помилка пошуку тикера для '{query}': {e}")
            else:
                print(f"Помилка пошуку тикера для '{query}': {e}")
            return None

    def convert_to_symbol(self, stock_name):
        # Якщо ввели вже тикер (усі великі літери та довжина <=5), просто повертаємо
        if stock_name.isupper() and len(stock_name) <= 5:
            if self.logger:
                self.logger.info(f"Введений рядок '{stock_name}' вважається тикером")
            return stock_name
        # Інакше шукаємо тикер по назві
        symbol = self.search_symbol_yahoo(stock_name)
        if symbol:
            if self.logger:
                self.logger.info(f"Знайдено тикер '{symbol}' для '{stock_name}'")
            else:
                print(f"Знайдено тикер '{symbol}' для '{stock_name}'")
            return symbol
        else:
            if self.logger:
                self.logger.info(f"Не знайдено тикер для '{stock_name}', використовуємо введене як є")
            else:
                print(f"Не знайдено тикер для '{stock_name}', використовуємо введене як є")
            return stock_name.upper()

    def get_empty_df(self) -> pd.DataFrame:
        return pd.DataFrame(columns=['Date', 'Close'])

    def fetch_yahoo(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        data = data.reset_index()[['Date', 'Close']]
        return data

    def fetch_stooq(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        # Stooq uses .us for US stocks (e.g. AAPL.us)
        url = f'https://stooq.com/q/d/l/?s={symbol.lower()}.us&d1={start_date.replace("-", "")}&d2={end_date.replace("-", "")}&i=d'
        df = pd.read_csv(url)
        df = df[['Date', 'Close']]
        df['Date'] = pd.to_datetime(df['Date'])
        return df[df['Date'].between(start_date, end_date)]

    def fetch_investing(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        data = investpy.get_stock_historical_data(stock=symbol,
                                                  country='united states',
                                                  from_date=pd.to_datetime(start_date).strftime("%d/%m/%Y"),
                                                  to_date=pd.to_datetime(end_date).strftime("%d/%m/%Y"))
        data = data.reset_index()[['Date', 'Close']]
        return data

    def fetch_nasdaq(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        url = f"https://api.nasdaq.com/api/quote/{symbol}/chart"
        params = {
            "assetclass": "stocks",
            "fromdate": start_date,
            "todate": end_date
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        rows = []
        for row in data["data"]["chart"]:
            rows.append({"Date": row["x"], "Close": row["y"]})

        df = pd.DataFrame(rows)
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')
        df['Close'] = df['Close'].astype(float)

        return df

    def fetch_data(self, stock, start_date, end_date):
        symbol = self.convert_to_symbol(stock)
        if self.logger:
            self.logger.info(f"Отримуємо дані для символу: {symbol}")
        else:
            print(f"Отримуємо дані для символу: {symbol}")

        data = []
        stock_sites = [
            ['Yahoo Finance', self.fetch_yahoo],
            ['NASDAQ', self.fetch_nasdaq],
            ['STOOQ', self.fetch_stooq],
            ['Investing', self.fetch_investing],
        ]

        for site, fetch in stock_sites:
            if self.logger:
                self.logger.info(f"Отримуємо данні з сайту: {site}")
            else:
                print(f"Отримуємо данні з сайту: {site}")

            try:
                df = fetch(symbol, start_date, end_date)
                data.append((site, df))
            except Exception as e:
                print(e)

        return data

