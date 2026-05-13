import pandas as pd
import yfinance as yf
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_connection():
    try:
        url = st.secrets["DATABASE_URL"]
    except Exception:
        url = os.getenv("DATABASE_URL")
    return psycopg2.connect(url)


@st.cache_data(ttl=300)
def get_etf_catalog() -> dict:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ticker, nom, indice_replique, gestionnaire, ter, eligible_pea, isin
            FROM etf
        """)
        rows = cursor.fetchall()
        catalog = {}
        for row in rows:
            ticker, nom, indice, gestionnaire, ter, pea, isin = row
            catalog[ticker] = {
                "nom": nom or "",
                "indice": indice or "",
                "gestionnaire": gestionnaire or "",
                "ter": float(ter) if ter else 0.0,
                "pea": bool(pea),
                "isin": isin or "",
            }
        return catalog
    finally:
        conn.close()

# @st.cache_data(ttl=900)  # cache 15 minutes
# def get_historical_data(ticker_yf: str, start: str, end: str = None) -> pd.DataFrame:
#     """
#     Télécharge les données historiques via yfinance.
#     avec le ticker Yahoo Finance (VUSA.AS).
#     """
#     if end is None:
#         end = datetime.today().strftime("%Y-%m-%d")
#     try:
#         df = yf.download(ticker_yf, start=start, end=end, auto_adjust=True, progress=False)
#         if df.empty:
#             return pd.DataFrame()
#         df = df[["Close", "Volume"]].copy()
#         df.columns = ["prix_cloture", "volume"]
#         df.index = pd.to_datetime(df.index)
#         return df.dropna()
#     except Exception:
#         return pd.DataFrame()

@st.cache_data(ttl=900)
def get_historical_data(identifier: str, start: str, end: str = None) -> pd.DataFrame:
    """
    Télécharge les données historiques via yfinance.
    avec identifier : ISIN (IE00B5BMR087)
    L'ISIN est préféré car il est universel et parce que quand je récupére les données depuis JustETF je n'ai pas le ticker_yf ce qui été un probléme pour appeller l'api yfinance.
    """
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")
    try:
        df = yf.download(identifier, start=start, end=end, auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        df = df[["Close", "Volume"]].copy()
        df.columns = ["prix_cloture", "volume"]
        df.index = pd.to_datetime(df.index)
        return df.dropna()
    except Exception:
        return pd.DataFrame()
