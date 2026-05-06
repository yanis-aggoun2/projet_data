# tests/test_dca_engine.py
import pytest
import pandas as pd
import numpy as np
from utils.dca_engine import run_dca_simulation, calcul_metriques

# Données fictives pour les tests — pas besoin de yfinance
def make_prix(n=12, prix=100.0):
    dates = pd.date_range("2020-01-01", periods=n, freq="B")
    return pd.DataFrame({"prix_cloture": [prix] * n}, index=dates)


# ── Test 1 : capital initial = 0 ─────────────────────────────
def test_capital_initial_zero():
    df = make_prix(12)
    result = run_dca_simulation(df, 0, 200, 0.0038, "2020-01-01", "2020-12-31")
    assert not result.empty
    assert result["capital_investi"].iloc[0] == 200  # premier versement uniquement


# ── Test 2 : TER = 0 ─────────────────────────────────────────
def test_ter_zero():
    df = make_prix(12)
    result = run_dca_simulation(df, 1000, 200, 0.0, "2020-01-01", "2020-12-31")
    assert not result.empty
    # Sans frais, frais cumulés doivent être 0
    assert result["frais_cumules"].sum() == 0.0


# ── Test 3 : période d'un seul mois ──────────────────────────
def test_periode_un_mois():
    df = make_prix(1)
    result = run_dca_simulation(df, 1000, 200, 0.0038, "2020-01-01", "2020-01-31")
    assert len(result) == 1  # une seule ligne