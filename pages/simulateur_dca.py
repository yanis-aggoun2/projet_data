import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.etf_data import ETF_CATALOG, get_historical_data
from utils.dca_engine import run_dca_simulation, run_dca_sans_frais, calcul_livret_a, calcul_metriques

st.set_page_config(page_title="Simulateur DCA", page_icon="📊", layout="wide")

st.title("📊 Simulateur DCA")
st.markdown("---")

# Paramètres dans le sidebar
with st.sidebar:
    st.markdown("## Paramètres")

    ticker = st.selectbox(
        "ETF",
        list(ETF_CATALOG.keys()),
        format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}"
    )
    etf = ETF_CATALOG[ticker]

    capital_initial = st.number_input("Capital de départ (€)", min_value=0, max_value=100000, value=1000, step=100)
    versement_mensuel = st.number_input("Versement mensuel (€)", min_value=0, max_value=10000, value=200, step=50)
    ter_pct = st.number_input("TER annuel (%)", min_value=0.0, max_value=5.0,
                               value=float(etf["ter"] * 100), step=0.01, format="%.2f")
    taux_la = st.number_input("Taux Livret A (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.25)

    today = date.today()
    date_debut = st.date_input("Date de début", value=date(2015, 1, 1), max_value=today)
    date_fin = st.date_input("Date de fin", value=date(2024, 12, 31), max_value=today)

    lancer = st.button("🚀 Lancer la simulation", type="primary", use_container_width=True)

# Résultats
if lancer:
    if date_debut >= date_fin:
        st.error("La date de début doit être avant la date de fin.")
        st.stop()

    with st.spinner("Simulation en cours..."):
        df_prix = get_historical_data(etf["ticker_yf"], str(date_debut), str(date_fin))

    if df_prix.empty:
        st.error("Impossible de récupérer les données.")
        st.stop()

    ter = ter_pct / 100
    df_sim = run_dca_simulation(df_prix, capital_initial, versement_mensuel, ter, str(date_debut), str(date_fin))
    df_sf = run_dca_sans_frais(df_prix, capital_initial, versement_mensuel, str(date_debut), str(date_fin))
    n_mois = len(df_sim)
    n_annees = n_mois / 12
    m = calcul_metriques(df_sim, n_annees)
    livret = calcul_livret_a(capital_initial, versement_mensuel, taux_la / 100, n_mois)

    # Métriques
    st.markdown("### Résultats")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital investi", f"{m['capital_total']:,.0f} €")
    c2.metric("Valeur finale", f"{m['valeur_finale']:,.0f} €")
    c3.metric("Gain net", f"{m['gain_net']:+,.0f} €")
    c4.metric("CAGR", f"{m['cagr']:+.2f}%/an")

    # Graphique
    st.markdown("### Evolution du portefeuille")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sim["date"], y=df_sim["valeur_portefeuille"],
                             name=f"{ticker} avec TER ({ter_pct:.2f}%)",
                             line=dict(color="#2563eb", width=2)))
    fig.add_trace(go.Scatter(x=df_sf["date"], y=df_sf["valeur_portefeuille"],
                             name=f"{ticker} sans frais",
                             line=dict(color="#94a3b8", width=1.5, dash="dot")))
    fig.add_trace(go.Scatter(x=df_sim["date"], y=df_sim["capital_investi"],
                             name="Capital investi",
                             fill="tozeroy", fillcolor="rgba(226,232,240,0.3)",
                             line=dict(color="#e2e8f0", width=1.5)))
    fig.add_trace(go.Scatter(x=df_sim["date"], y=livret[:n_mois],
                             name=f"Livret A ({taux_la}%)",
                             line=dict(color="#f59e0b", width=1.5, dash="dash")))
    fig.update_layout(height=450, plot_bgcolor="white", paper_bgcolor="white",
                      hovermode="x unified", yaxis_title="Valeur (€)",
                      margin=dict(l=0, r=0, t=20, b=0))
    fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
    st.plotly_chart(fig, use_container_width=True)

    # Impact des frais
    st.markdown("### Impact des frais TER")
    val_sf = df_sf["valeur_portefeuille"].iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("Avec TER", f"{m['valeur_finale']:,.2f} €")
    c2.metric("Sans frais", f"{val_sf:,.2f} €")
    c3.metric("Manque à gagner", f"{val_sf - m['valeur_finale']:,.2f} €")

    st.warning(f"Sur {n_annees:.1f} ans, un TER de {ter_pct:.2f}%/an a coûté **{m['frais_totaux']:,.2f} €** au total.")
    st.info("⚠️ Le backtesting illustre le passé. Il ne garantit pas les performances futures.")

    # Tableau détaillé
    with st.expander("Tableau mois par mois"):
        st.dataframe(df_sim.round(2), use_container_width=True, hide_index=True)

else:
    st.info("Configurez les paramètres dans le panneau latéral puis cliquez sur **Lancer la simulation**.")
