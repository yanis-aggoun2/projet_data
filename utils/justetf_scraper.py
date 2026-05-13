import pandas as pd
import streamlit as st
from data.etf_data import get_connection
import time


def fetch_etfs_from_justetf(strategy: str = "epg-longOnly", max_etfs: int = 50, progress_bar=None, status_text=None) -> pd.DataFrame:
    try:
        import justetf_scraping

        if status_text:
            status_text.text("Récupération de la liste JustETF...")

        df = justetf_scraping.load_overview(strategy=strategy)

        if df.empty:
            return pd.DataFrame()

        df = df.reset_index().head(max_etfs)
        total = len(df)
        results = []

        for i, row in df.iterrows():
            ticker = str(row.get("ticker", "")).strip()
            isin = str(row.get("isin", "")).strip()

            if status_text:
                status_text.text(f"Enrichissement {i+1}/{total} : {ticker}...")
            if progress_bar:
                progress_bar.progress((i + 1) / total)

            # Détails via get_etf_overview
            indice = ""
            gestionnaire = ""
            try:
                details = justetf_scraping.get_etf_overview(isin)
                indice       = details.get("index", "") or ""
                gestionnaire = details.get("fund_provider", "") or ""
            except Exception:
                pass

            results.append({
                "isin":            isin,
                "ticker":          ticker,
                "nom":             str(row.get("name", "")).strip(),
                "indice_replique": indice,
                "gestionnaire":    gestionnaire,
                "ter":             float(row.get("ter", 0)) / 100 if pd.notna(row.get("ter")) else None,
                "eligible_pea":    False,
            })

            time.sleep(0.3)

        return pd.DataFrame(results)

    except Exception as e:
        st.error(f"Erreur : {type(e).__name__}: {e}")
        import traceback
        st.code(traceback.format_exc())
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
                    INSERT INTO etf (isin, ticker, nom, indice_replique, gestionnaire, ter, eligible_pea)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (isin) DO NOTHING
                """, (
                    str(row.get("isin", "")),
                    str(row.get("ticker", "")),
                    str(row.get("nom", "")),
                    str(row.get("indice_replique", "")),
                    str(row.get("gestionnaire", "")),
                    float(row.get("ter", 0)) if pd.notna(row.get("ter")) else None,
                    bool(row.get("eligible_pea", False)),
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