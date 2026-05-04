import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta

ETF_CATALOG = {
    "CW8": {
        "nom": "Amundi MSCI World",
        "indice": "MSCI World",
        "gestionnaire": "Amundi",
        "ter": 0.0038,
        "pea": True,
        "ticker_yf": "CW8.PA",
        "description": "Réplique les 1 500+ plus grandes entreprises mondiales des pays développés."
    },
    "PS20": {
        "nom": "Amundi S&P 500",
        "indice": "S&P 500",
        "gestionnaire": "Amundi",
        "ter": 0.0015,
        "pea": True,
        "ticker_yf": "500.PA",
        "description": "Réplique les 500 plus grandes entreprises américaines."
    },
    "ESE": {
        "nom": "iShares MSCI Europe",
        "indice": "MSCI Europe",
        "gestionnaire": "BlackRock (iShares)",
        "ter": 0.0012,
        "pea": False,
        "ticker_yf": "ESEU.AS",
        "description": "Réplique les grandes et moyennes capitalisations européennes."
    },
    "OBLI": {
        "nom": "Lyxor Obligations d'État Euro",
        "indice": "EuroMTS Govt Bond",
        "gestionnaire": "Lyxor (Amundi)",
        "ter": 0.0017,
        "pea": False,
        "ticker_yf": "MTH.PA",
        "description": "Réplique les obligations souveraines de la zone euro."
    }
}

@st.cache_data(ttl=3600)
def get_historical_data(ticker_yf: str, start: str, end: str = None) -> pd.DataFrame:
    """Télécharge les données historiques via yfinance."""
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")
    try:
        df = yf.download(ticker_yf, start=start, end=end, auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        df = df[["Close", "Volume"]].copy()
        df.index = pd.to_datetime(df.index)
        df.columns = ["prix_cloture", "volume"]
        df = df.dropna()
        return df
    except Exception as e:
        st.error(f"Erreur lors du téléchargement des données : {e}")
        return pd.DataFrame()

def get_etf_info(ticker: str) -> dict:
    """Retourne les métadonnées d'un ETF depuis le catalogue."""
    return ETF_CATALOG.get(ticker.upper(), None)

def format_currency(value: float, decimals: int = 2) -> str:
    """Formate un nombre en euros."""
    return f"{value:,.{decimals}f} €".replace(",", " ")

def format_percent(value: float, decimals: int = 2) -> str:
    """Formate un pourcentage."""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f} %"
