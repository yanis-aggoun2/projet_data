import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.etf_data import get_etf_catalog
from utils.style import load_css

load_css()

# Chargement catalogue
ETF_CATALOG = get_etf_catalog()
if not ETF_CATALOG:
    st.error("Impossible de charger les ETF depuis la base de données.")
    st.stop()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="fade-title">
        Port<span style="background: linear-gradient(135deg, #3b82f6, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">ify</span>
    </div>
    <div class="hero-sub fade-sub">M2 MIAGE · Université Paris-Saclay · Simulateur de portefeuille passif</div>
    <div class="hero-badges fade-badges">
        <span class="badge">Données réelles</span>
        <span class="badge green">Backtesting DCA</span>
        <span class="badge purple">Régression OLS</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Stats bar ─────────────────────────────────────────────────────────────────
n_etf = len(ETF_CATALOG)
ter_moyen = sum(v["ter"] for v in ETF_CATALOG.values()) / n_etf * 100

st.markdown(f"""
<div class="stat-bar">
    <div class="stat-item">
        <div class="stat-val">{n_etf}</div>
        <div class="stat-lbl">ETF disponibles</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">{ter_moyen:.2f}%</div>
        <div class="stat-lbl">TER moyen</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">3</div>
        <div class="stat-lbl">Modules d'analyse</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">10 ans</div>
        <div class="stat-lbl">Historique max</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">Live</div>
        <div class="stat-lbl">Source Yahoo Finance</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Modules ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Modules</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="module-card blue">
        <span class="module-icon"></span>
        <div class="module-tag blue">Module A</div>
        <div class="module-title">Explorateur d'ETF</div>
        <div class="module-desc">
            Recherchez et analysez un ETF, visualisez son évolution sur 1 à 10 ans
            et comparez deux instruments côte à côte sur une base normalisée 100.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="module-card green">
        <span class="module-icon"></span>
        <div class="module-tag green">Module B</div>
        <div class="module-title">Simulateur DCA</div>
        <div class="module-desc">
            Simulez une stratégie d'investissement programmé sur données historiques réelles.
            Mesurez l'impact du TER, comparez au Livret A et calculez le CAGR.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="module-card purple">
        <span class="module-icon"></span>
        <div class="module-tag purple">Module C</div>
        <div class="module-title">Régression Linéaire</div>
        <div class="module-desc">
            Analysez la tendance long terme via régression OLS, visualisez les résidus
            avec bandes ±2σ et comprenez les limites statistiques de la prédiction.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tableau ETF ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">ETF de référence</div>', unsafe_allow_html=True)

rows_html = ""
for code, info in ETF_CATALOG.items():
    ter = info["ter"] * 100
    ter_class = "low" if ter < 0.20 else "mid" if ter < 0.40 else "high"
    pea_badge = '<span class="pea-yes">✓ PEA</span>' if info["pea"] else '<span class="pea-no">Non éligible</span>'
    rows_html += f'<tr><td><span class="etf-ticker">{code}</span></td><td><div class="etf-nom">{info["nom"]}</div><div class="etf-indice">{info["indice"]}</div></td><td>{info["gestionnaire"]}</td><td><span class="etf-ter {ter_class}">{ter:.2f}%</span></td><td>{pea_badge}</td></tr>'

st.markdown(f'<table class="etf-table"><thead><tr><th>Ticker</th><th>Nom / Indice</th><th>Gestionnaire</th><th>TER annuel</th><th>Éligibilité</th></tr></thead><tbody>{rows_html}</tbody></table>', unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    ⚠️ <strong>Avertissement</strong> — Les performances passées ne préjugent pas des performances futures.
    Cette application est réalisée à des fins <strong>pédagogiques uniquement</strong>
    dans le cadre du M2 MIAGE — Université Paris-Saclay.
    Aucun élément présenté ne constitue un conseil en investissement.
</div>
""", unsafe_allow_html=True)