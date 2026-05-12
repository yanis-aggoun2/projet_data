import pandas as pd
import streamlit as st
from data.etf_data import get_connection


def fetch_etfs_from_justetf(strategy: str = "epg-longOnly", max_etfs: int = 50) -> pd.DataFrame:
    try:
        import justetf_scraping

        df = justetf_scraping.load_overview(strategy=strategy)

        if df.empty:
            return pd.DataFrame()

        df_clean = pd.DataFrame()
        df_clean["ticker"]          = df["ticker"].str.strip() if "ticker" in df.columns else df.index
        df_clean["nom"]             = df["name"].str.strip() if "name" in df.columns else ""
        df_clean["indice_replique"] = ""
        df_clean["gestionnaire"]    = ""
        df_clean["ter"]             = pd.to_numeric(df.get("ter", 0), errors="coerce") / 100
        df_clean["eligible_pea"]    = False
        df_clean["ticker_yf"]       = ""
        df_clean["description"]     = ""

        df_clean = df_clean.dropna(subset=["ticker"])
        df_clean = df_clean[df_clean["ticker"] != ""]

        return df_clean.head(max_etfs)

    except Exception as e:
        st.error(f"Erreur scraping JustETF : {e}")
        return pd.DataFrame()


def save_etfs_to_db(df: pd.DataFrame) -> tuple[int, int]:
    if df.empty:
        return 0, 0

    conn = get_connection()
    inseres = 0
    ignores = 0

    try:
        cursor = conn.cursor()
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO etf (ticker, nom, indice_replique, gestionnaire, ter, eligible_pea, ticker_yf, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ticker) DO NOTHING
                """, (
                    str(row.get("ticker", "")),
                    str(row.get("nom", "")),
                    str(row.get("indice_replique", "")),
                    str(row.get("gestionnaire", "")),
                    float(row.get("ter", 0)) if pd.notna(row.get("ter")) else None,
                    bool(row.get("eligible_pea", False)),
                    str(row.get("ticker_yf", "")),
                    str(row.get("description", "")),
                ))
                if cursor.rowcount > 0:
                    inseres += 1
                else:
                    ignores += 1
            except Exception:
                ignores += 1
                continue
        conn.commit()
    finally:
        conn.close()

    return inseres, ignores