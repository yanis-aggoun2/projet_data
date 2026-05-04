import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.etf_data import ETF_CATALOG, get_historical_data
from utils.regression_engine import run_regression

st.set_page_config(page_title="Regression Lineaire", page_icon="📉", layout="wide")

st.title("📉 Régression Linéaire & Analyse de Tendance")
st.markdown("---")

# Paramètres dans le sidebar
with st.sidebar:
    st.markdown("## Paramètres")
    ticker = st.selectbox(
        "ETF à analyser",
        list(ETF_CATALOG.keys()),
        format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}"
    )
    fenetre = st.slider("Fenêtre d'analyse (années)", min_value=3, max_value=15, value=10)
    projection = st.checkbox("Afficher la projection 12 mois", value=True)
    lancer = st.button("📈 Lancer la régression", type="primary", use_container_width=True)

etf = ETF_CATALOG[ticker]

if lancer:
    date_debut = (datetime.today() - timedelta(days=fenetre * 365)).strftime("%Y-%m-%d")

    with st.spinner("Calcul de la régression..."):
        df_prix = get_historical_data(etf["ticker_yf"], date_debut)

    if df_prix.empty or len(df_prix) < 60:
        st.error("Données insuffisantes.")
        st.stop()

    res = run_regression(df_prix)

    # Métriques
    st.markdown("### Métriques")
    p_fmt = f"{res['p_value']:.2e}" if res['p_value'] < 0.001 else f"{res['p_value']:.4f}"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("R²", f"{res['r2']:.4f}")
    c2.metric("Pente β₁ (€/jour)", f"{res['beta1']:+.4f}")
    c3.metric("Pente annualisée", f"{res['pente_annuelle_pct']:+.2f}%/an")
    c4.metric("Durbin-Watson", f"{res['dw_stat']:.4f}")
    st.caption(f"P-value sur β₁ : {p_fmt} — {'✅ Très significatif' if res['p_value'] < 0.001 else '⚠️ Significatif' if res['p_value'] < 0.05 else '❌ Non significatif'}")

    # Graphique 1 : cours + droite + IC
    st.markdown("### Cours historique avec droite de régression")
    dates = pd.to_datetime(res["dates"])

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=list(dates) + list(dates[::-1]),
        y=list(res["ci_upper"]) + list(res["ci_lower"][::-1]),
        fill="toself", fillcolor="rgba(148,163,184,0.2)",
        line=dict(color="rgba(0,0,0,0)"), name="IC 95%"
    ))
    fig1.add_trace(go.Scatter(x=dates, y=res["Y"], name="Cours réel",
                              line=dict(color="#2563eb", width=1.5), opacity=0.8))
    fig1.add_trace(go.Scatter(x=dates, y=res["Y_pred"], name="Droite OLS",
                              line=dict(color="#f97316", width=2.5)))

    if projection:
        last_date = dates[-1]
        dates_proj = pd.date_range(start=last_date, periods=253, freq="B")[1:]
        n = min(len(dates_proj), len(res["Y_futur"]))
        fig1.add_trace(go.Scatter(x=dates_proj[:n], y=res["Y_futur"][:n],
                                  name="Projection 12 mois",
                                  line=dict(color="#f97316", width=2, dash="dash")))
        fig1.add_trace(go.Scatter(
            x=[last_date, last_date],
            y=[min(res["Y"]), max(res["Y"])],
            mode="lines",
            line=dict(color="#94a3b8", width=1, dash="dot"),
            name="Aujourd'hui",
            showlegend=True
        ))

    fig1.update_layout(height=450, plot_bgcolor="white", paper_bgcolor="white",
                       hovermode="x unified", yaxis_title="Prix (€)",
                       margin=dict(l=0, r=0, t=20, b=0))
    fig1.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
    fig1.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
    st.plotly_chart(fig1, use_container_width=True)

    if projection:
        st.warning("La projection est une extrapolation mécanique. L'IC s'élargit dans le futur : la prédiction devient de moins en moins fiable.")

    # Graphique 2 : résidus
    st.markdown("### Graphique des résidus")
    fig2 = go.Figure()
    fig2.add_hline(y=0, line_color="#e2e8f0", line_width=1.5)
    fig2.add_trace(go.Scatter(x=dates, y=res["residus"], name="Résidus",
                              line=dict(color="#8b5cf6", width=1.2)))
    std = np.std(res["residus"])
    fig2.add_trace(go.Scatter(x=dates, y=[std*2]*len(dates), name="+2σ",
                              line=dict(color="#f87171", width=1, dash="dot")))
    fig2.add_trace(go.Scatter(x=dates, y=[-std*2]*len(dates), name="-2σ",
                              line=dict(color="#f87171", width=1, dash="dot")))
    fig2.update_layout(height=300, plot_bgcolor="white", paper_bgcolor="white",
                       hovermode="x unified", yaxis_title="Résidu (€)",
                       margin=dict(l=0, r=0, t=20, b=0))
    fig2.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
    fig2.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
    st.plotly_chart(fig2, use_container_width=True)

    # Interprétation critique
    st.markdown("---")
    st.markdown("### Interprétation critique")

    dw = res["dw_stat"]
    dw_interp = "Autocorrélation positive forte" if dw < 1.5 else ("Autocorrélation négative forte" if dw > 2.5 else "Pas d'autocorrélation significative")

    st.markdown(f"""
**R² = {res['r2']:.4f}** — La droite explique {res['r2']*100:.1f}% de la variance du prix.
Sur une série temporelle croissante, un R² élevé est quasi-automatique (**régression fallacieuse**).
Cela ne signifie pas que le modèle peut prédire les cours futurs.

**Résidus non aléatoires** — Le graphique des résidus montre des cycles, des crises et des bulles.
C'est la signature d'un marché efficient mais non-prédictible à court terme.

**Durbin-Watson = {dw}** — {dw_interp}.
Une valeur proche de 2 indique l'absence d'autocorrélation dans les résidus.

**Conclusion** — La régression confirme une tendance haussière ({res['pente_annuelle_pct']:+.2f}%/an),
mais pas un timing. C'est pourquoi le DCA est plus rationnel que d'essayer de trouver
le bon moment pour investir.
    """)

    # Tableau de synthèse
    with st.expander("Tableau de synthèse complet"):
        st.dataframe(pd.DataFrame({
            "Indicateur": ["R²", "β₀", "β₁ (€/jour)", "Pente (%/an)", "P-value", "Durbin-Watson", "Observations"],
            "Valeur": [f"{res['r2']:.6f}", f"{res['beta0']:.4f}", f"{res['beta1']:+.6f}",
                       f"{res['pente_annuelle_pct']:+.2f}%", p_fmt, str(dw), str(res['n_obs'])],
        }), use_container_width=True, hide_index=True)

else:
    st.info("Sélectionnez un ETF et une fenêtre d'analyse dans le panneau latéral, puis cliquez sur **Lancer la régression**.")
