import pandas as pd
import yfinance as yf
import investpy
import requests


def fetch_yahoo(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)
    data = data.reset_index()[['Date', 'Close']]
    return data


def fetch_stooq(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    # Stooq uses .us for US stocks (e.g. AAPL.us)
    url = f'https://stooq.com/q/d/l/?s={symbol.lower()}.us&d1={start_date.replace("-", "")}&d2={end_date.replace("-", "")}&i=d'
    df = pd.read_csv(url)
    df = df[['Date', 'Close']]
    df['Date'] = pd.to_datetime(df['Date'])
    return df[df['Date'].between(start_date, end_date)]


def fetch_investing(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    data = investpy.get_stock_historical_data(stock=symbol,
                                              country='united states',
                                              from_date=pd.to_datetime(start_date).strftime("%d/%m/%Y"),
                                              to_date=pd.to_datetime(end_date).strftime("%d/%m/%Y"))
    data = data.reset_index()[['Date', 'Close']]
    return data



def fetch_nasdaq(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
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


