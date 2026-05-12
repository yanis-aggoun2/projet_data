"""
utils/etf_enricher.py

Enrichit les données ETF depuis Yahoo Finance :
- Résout le ticker Yahoo Finance (suffixe de marché)
- Récupère nom complet, gestionnaire, indice, description
- Met à jour la base de données
"""

import time
import pandas as pd
import yfinance as yf
import streamlit as st
from data.etf_data import get_connection


# Suffixes de marché à tester dans l'ordre
SUFFIXES = [".DE", ".PA", ".AS", ".L", ".SW", ".MI", ".BR", ".F", ""]


def find_ticker_yf(ticker_justetf: str) -> tuple[str, dict]:
    """
    Trouve le ticker Yahoo Finance et récupère les métadonnées.
    Retourne (ticker_yf, info_dict)
    """
    for suffix in SUFFIXES:
        candidate = f"{ticker_justetf}{suffix}"
        try:
            t = yf.Ticker(candidate)

            # Vérifier que le ticker retourne des données historiques
            hist = t.history(period="5d")
            if hist.empty:
                continue

            # Récupérer les métadonnées
            info = t.info

            return candidate, {
                "nom": info.get("longName") or info.get("shortName") or "",
                "gestionnaire": info.get("fundFamily") or "",
                "indice_replique": info.get("category") or "",
                "ter": (info.get("totalExpenseRatio") or 0),
                "description": info.get("longBusinessSummary") or "",
                "currency": info.get("currency") or "",
            }

        except Exception:
            pass

        time.sleep(0.3)

    return "", {}


def enrich_etf_from_yfinance(ticker_justetf: str) -> dict:
    """
    Enrichit un ETF depuis Yahoo Finance.
    Retourne un dict avec toutes les infos disponibles.
    """
    ticker_yf, info = find_ticker_yf(ticker_justetf)

    if not ticker_yf:
        return {"ticker_yf": "", "succes": False}

    return {
        "ticker_yf": ticker_yf,
        "nom": info.get("nom", ""),
        "gestionnaire": info.get("gestionnaire", ""),
        "indice_replique": info.get("indice_replique", ""),
        "ter": info.get("ter", 0),
        "description": info.get("description", ""),
        "succes": True,
    }


def update_etf_in_db(ticker: str, data: dict) -> bool:
    """Met à jour un ETF en base avec les données enrichies."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE etf SET
                ticker_yf       = COALESCE(NULLIF(%s, ''), ticker_yf),
                nom             = COALESCE(NULLIF(%s, ''), nom),
                gestionnaire    = COALESCE(NULLIF(%s, ''), gestionnaire),
                indice_replique = COALESCE(NULLIF(%s, ''), indice_replique),
                ter             = COALESCE(NULLIF(%s::numeric, 0), ter),
                description     = COALESCE(NULLIF(%s, ''), description)
            WHERE ticker = %s
        """, (
            data.get("ticker_yf", ""),
            data.get("nom", ""),
            data.get("gestionnaire", ""),
            data.get("indice_replique", ""),
            data.get("ter", 0),
            data.get("description", ""),
            ticker,
        ))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        st.error(f"Erreur UPDATE {ticker}: {e}")
        return False
    finally:
        conn.close()


def enrich_all_etfs(tickers: list[str], progress_bar=None, status_text=None) -> dict:
    """
    Enrichit tous les ETFs depuis Yahoo Finance.
    Retourne un rapport {succes: N, echecs: N, details: [...]}
    """
    succes = 0
    echecs = 0
    details = []

    for i, ticker in enumerate(tickers):
        if status_text:
            status_text.text(f"Enrichissement {i+1}/{len(tickers)} : {ticker}...")
        if progress_bar:
            progress_bar.progress((i + 1) / len(tickers))

        data = enrich_etf_from_yfinance(ticker)

        if data["succes"]:
            update_etf_in_db(ticker, data)
            succes += 1
            details.append({
                "ticker": ticker,
                "ticker_yf": data["ticker_yf"],
                "statut": "✅ Enrichi"
            })
        else:
            echecs += 1
            details.append({
                "ticker": ticker,
                "ticker_yf": "",
                "statut": "❌ Non trouvé"
            })

        time.sleep(0.3)

    return {"succes": succes, "echecs": echecs, "details": details}