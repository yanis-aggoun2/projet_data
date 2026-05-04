import pandas as pd
import yfinance as yf
from datetime import datetime

ETF_CATALOG = {
    "CW8": {
        "nom": "Amundi MSCI World",
        "indice": "MSCI World",
        "gestionnaire": "Amundi",
        "ter": 0.0038,
        "pea": True,
        "ticker_yf": "CW8.PA",
        "description": "Réplique les 1500+ plus grandes entreprises mondiales des pays développés."
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
        "nom": "Lyxor Obligations d'Etat Euro",
        "indice": "EuroMTS Govt Bond",
        "gestionnaire": "Lyxor (Amundi)",
        "ter": 0.0017,
        "pea": False,
        "ticker_yf": "MTH.PA",
        "description": "Réplique les obligations souveraines de la zone euro."
    }
}


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
