import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.regression_engine import run_regression

from data.etf_data import get_etf_catalog, get_historical_data
from utils.style import load_css, dark_layout, _BG, _PAPER, _GRID, _TICK


load_css()

# Chargement catalogue
ETF_CATALOG = get_etf_catalog()
if not ETF_CATALOG:
    st.error("Impossible de charger les ETF depuis la base de données.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Paramètres")
    ticker = st.selectbox(
        "ETF à analyser",
        list(ETF_CATALOG.keys()),
        format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}"
    )
    fenetre    = st.slider("Fenêtre d'analyse (années)", min_value=3, max_value=15, value=10)
    projection = st.checkbox("Afficher la projection 12 mois", value=True)
    lancer     = st.button("Lancer la régression", type="primary", use_container_width=True)

etf = ETF_CATALOG[ticker]

# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown("# Régression Linéaire & Analyse de Tendance")
st.caption("Module C — Modèle OLS, résidus et limites de la prédiction financière")
st.divider()

# ── Résultats ─────────────────────────────────────────────────────────────────
if lancer:
    date_debut = (datetime.today() - timedelta(days=fenetre * 365)).strftime("%Y-%m-%d")

    with st.spinner("Calcul de la régression OLS…"):
        df_prix = get_historical_data(etf["ticker_yf"], date_debut)

    if df_prix.empty or len(df_prix) < 60:
        st.error("Données insuffisantes pour effectuer la régression (< 60 observations).")
        st.stop()

    res   = run_regression(df_prix)
    p_fmt = f"{res['p_value']:.2e}" if res['p_value'] < 0.001 else f"{res['p_value']:.4f}"

    # KPI
    st.markdown("### Métriques de la régression")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("R²",                f"{res['r2']:.4f}")
    c2.metric("Pente β₁ (€/jour)", f"{res['beta1']:+.4f}")
    c3.metric("Pente annualisée",  f"{res['pente_annuelle_pct']:+.2f} %/an")
    c4.metric("Durbin-Watson",     f"{res['dw_stat']:.4f}")

    if res["p_value"] < 0.001:
        st.success(f"✅ P-value sur β₁ : {p_fmt} — Très significatif")
    elif res["p_value"] < 0.05:
        st.warning(f"⚠️ P-value sur β₁ : {p_fmt} — Significatif")
    else:
        st.error(f"❌ P-value sur β₁ : {p_fmt} — Non significatif")

    # Graphique 1 : cours + droite + IC
    st.divider()
    st.markdown("### Cours historique avec droite de régression")
    dates = pd.to_datetime(res["dates"])

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=list(dates) + list(dates[::-1]),
        y=list(res["ci_upper"]) + list(res["ci_lower"][::-1]),
        fill="toself", fillcolor="rgba(59,130,246,0.07)",
        line=dict(color="rgba(0,0,0,0)"),
        name="IC 95%", hoverinfo="skip",
    ))
    fig1.add_trace(go.Scatter(
        x=dates, y=res["Y"], name="Cours réel",
        line=dict(color="#3b82f6", width=1.5), opacity=0.85,
        hovertemplate="%{y:.2f} €<extra>Cours réel</extra>",
    ))
    fig1.add_trace(go.Scatter(
        x=dates, y=res["Y_pred"], name="Droite OLS",
        line=dict(color="#f97316", width=2.5),
        hovertemplate="%{y:.2f} €<extra>Droite OLS</extra>",
    ))

    if projection:
        last_date  = dates[-1]
        dates_proj = pd.date_range(start=last_date, periods=253, freq="B")[1:]
        n = min(len(dates_proj), len(res["Y_futur"]))
        fig1.add_trace(go.Scatter(
            x=dates_proj[:n], y=res["Y_futur"][:n],
            name="Projection 12 mois",
            line=dict(color="#f97316", width=2, dash="dash"),
            hovertemplate="%{y:.2f} €<extra>Projection</extra>",
        ))
        fig1.add_trace(go.Scatter(
            x=[last_date, last_date],
            y=[min(res["Y"]), max(res["Y"])],
            mode="lines",
            line=dict(color="#475569", width=1.5, dash="dot"),
            name="Aujourd'hui",
            hoverinfo="skip",
        ))

    layout1 = dark_layout(height=480)
    layout1["yaxis"]["title"] = dict(text="Prix (€)", font=dict(color=_TICK))
    fig1.update_layout(**layout1)
    st.plotly_chart(fig1, use_container_width=True)

    if projection:
        st.warning("La projection est une extrapolation mécanique. L'IC s'élargit dans le futur : la prédiction devient de moins en moins fiable.")

    # Graphique 2 : résidus
    st.divider()
    st.markdown("### Graphique des résidus")
    std = np.std(res["residus"])

    fig2 = go.Figure()
    fig2.add_hline(y=0,        line_color="#1a2e48", line_width=1.5)
    fig2.add_hline(y= std * 2, line_dash="dot", line_color="rgba(239,68,68,0.5)", line_width=1,
                   annotation_text="+2σ", annotation_font_color="#f87171")
    fig2.add_hline(y=-std * 2, line_dash="dot", line_color="rgba(239,68,68,0.5)", line_width=1,
                   annotation_text="-2σ", annotation_font_color="#f87171")
    fig2.add_trace(go.Scatter(
        x=dates, y=res["residus"], name="Résidus",
        line=dict(color="#8b5cf6", width=1.5),
        hovertemplate="%{y:.2f} €<extra>Résidu</extra>",
    ))
    layout2 = dark_layout(height=300)
    layout2["yaxis"]["title"] = dict(text="Résidu (€)", font=dict(color=_TICK))
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True)

    # Interprétation critique
    st.divider()
    st.markdown("### Interprétation critique")

    dw = res["dw_stat"]
    dw_interp = (
        "Autocorrélation positive forte" if dw < 1.5
        else "Autocorrélation négative forte" if dw > 2.5
        else "Pas d'autocorrélation significative"
    )

    col_l, col_r = st.columns(2, gap="medium")

    with col_l:
        with st.container(border=True):
            st.markdown("**R² — Coefficient de détermination**")
            st.markdown(
                f"R² = **{res['r2']:.4f}** → la droite explique {res['r2']*100:.1f}% de la variance du prix. "
                "Sur une série temporelle croissante, un R² élevé est quasi-automatique "
                "(*régression fallacieuse*). Cela ne signifie pas que le modèle peut prédire les cours futurs."
            )

        with st.container(border=True):
            st.markdown("**Résidus — Structure non aléatoire**")
            st.markdown(
                "Le graphique des résidus révèle des **cycles, crises et bulles** non capturés par le modèle. "
                "C'est la signature d'un marché efficient mais non prédictible à court terme."
            )

    with col_r:
        with st.container(border=True):
            st.markdown("**Durbin-Watson — Autocorrélation**")
            st.markdown(
                f"DW = **{dw:.4f}** → {dw_interp}. "
                "Une valeur proche de 2 indique l'absence d'autocorrélation dans les résidus "
                "(hypothèse nécessaire à la validité de l'OLS)."
            )

        with st.container(border=True):
            st.markdown("**Conclusion — DCA vs timing**")
            st.markdown(
                f"La régression confirme une tendance haussière de **{res['pente_annuelle_pct']:+.2f}%/an**, "
                "mais pas un moment optimal d'entrée. "
                "C'est pourquoi le **DCA est plus rationnel** que de chercher à timer le marché."
            )

    # Tableau de synthèse
    with st.expander("Tableau de synthèse complet"):
       rows_html = ""
       tableau = [
           ("R²",              f"{res['r2']:.6f}",                      "Part de variance expliquée par le temps"),
           ("β₀ (Constante)",  f"{res['beta0']:.4f} €",                 "Prix théorique au jour 0"),
           ("β₁ (€/jour)",     f"{res['beta1']:+.6f}",                  "Hausse moyenne quotidienne"),
           ("Pente (%/an)",    f"{res['pente_annuelle_pct']:+.2f}%",     "Rendement tendanciel annualisé"),
           ("P-value",         p_fmt,                                    "Significativité de la pente"),
           ("Durbin-Watson",   f"{dw:.4f}",                              dw_interp),
           ("Observations",    str(res["n_obs"]),                        "Jours de trading inclus"),
       ]
       for indicateur, valeur, interpretation in tableau:
           rows_html += f'<tr><td style="color:#7a90a8;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;">{indicateur}</td><td style="color:#f1f5f9;font-weight:700;font-family:monospace;">{valeur}</td><td style="color:#475569;font-size:0.85rem;">{interpretation}</td></tr>'

       st.markdown(f'<table class="etf-table"><thead><tr><th>Indicateur</th><th>Valeur</th><th>Interprétation</th></tr></thead><tbody>{rows_html}</tbody></table>', unsafe_allow_html=True)

else:
    with st.container(border=True):
        st.markdown("### prête à démarrer")
        st.markdown(
            "Sélectionnez un ETF et une fenêtre temporelle dans le **panneau latéral**, "
            "puis cliquez sur **Lancer la régression** pour obtenir l'analyse OLS complète."
        )
