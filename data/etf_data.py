import pandas as pd
import yfinance as yf
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def get_etf_catalog() -> dict:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT code, nom, indice, gestionnaire, ter, pea, ticker_yf, description
            FROM etf
        """)
        rows = cursor.fetchall()
        catalog = {}
        for row in rows:
            code, nom, indice, gestionnaire, ter, pea, ticker_yf, description = row
            catalog[code] = {
                "nom": nom,
                "indice": indice,
                "gestionnaire": gestionnaire,
                "ter": float(ter),
                "pea": bool(pea),
                "ticker_yf": ticker_yf,
                "description": description
            }
        return catalog
    finally:
        conn.close()


def get_historical_data(ticker_yf: str, start: str, end: str = None) -> pd.DataFrame:
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")
    try:
        df = yf.download(ticker_yf, start=start, end=end, auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        df = df[["Close", "Volume"]].copy()
        df.columns = ["prix_cloture", "volume"]
        df.index = pd.to_datetime(df.index)
        return df.dropna()
    except Exception:
        return pd.DataFrame()


# Chargement au démarrage
try:
    ETF_CATALOG = get_etf_catalog()
except Exception as e:
    print(f"Erreur DB : {e}")
    ETF_CATALOG = {}