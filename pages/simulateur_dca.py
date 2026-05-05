import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.etf_data import get_etf_catalog, get_historical_data
from utils.dca_engine import run_dca_simulation, run_dca_sans_frais, calcul_livret_a, calcul_metriques
from utils.style import load_css, dark_layout, _BG, _PAPER, _GRID, _TICK


load_css()

# Chargement catalogue
ETF_CATALOG = get_etf_catalog()
if not ETF_CATALOG:
    st.error("Impossible de charger les ETF depuis la base de données.")
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("## Paramètres")

    ticker = st.selectbox(
        "ETF",
        list(ETF_CATALOG.keys()),
        format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}"
    )
    etf = ETF_CATALOG[ticker]

    capital_initial   = st.number_input("Capital de départ (€)", min_value=0, max_value=100_000, value=1_000, step=100)
    versement_mensuel = st.number_input("Versement mensuel (€)", min_value=0, max_value=10_000, value=200, step=50)
    ter_pct = st.number_input("TER annuel (%)", min_value=0.0, max_value=5.0,
                               value=float(etf["ter"] * 100), step=0.01, format="%.2f")
    taux_la = st.number_input("Taux Livret A (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.25)

    today      = date.today()
    date_debut = st.date_input("Date de début", value=date(2015, 1, 1), max_value=today)
    date_fin   = st.date_input("Date de fin",   value=date(2024, 12, 31), max_value=today)

    lancer = st.button("Lancer la simulation", type="primary", use_container_width=True)

# En-tête
st.markdown("# Simulateur DCA")
st.caption("Module B — Investissement programmé sur données historiques réelles")
st.divider()

# Résultats
if lancer:
    if date_debut >= date_fin:
        st.error("La date de début doit être antérieure à la date de fin.")
        st.stop()

    with st.spinner("Simulation en cours…"):
        df_prix = get_historical_data(etf["ticker_yf"], str(date_debut), str(date_fin))

    if df_prix.empty:
        st.error("Impossible de récupérer les données historiques.")
        st.stop()

    ter      = ter_pct / 100
    df_sim   = run_dca_simulation(df_prix, capital_initial, versement_mensuel, ter,
                                  str(date_debut), str(date_fin))
    df_sf    = run_dca_sans_frais(df_prix, capital_initial, versement_mensuel,
                                  str(date_debut), str(date_fin))
    n_mois   = len(df_sim)
    n_annees = n_mois / 12
    m        = calcul_metriques(df_sim, n_annees)
    livret   = calcul_livret_a(capital_initial, versement_mensuel, taux_la / 100, n_mois)

    # KPI
    st.markdown("### Résultats de la simulation")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital investi",  f"{m['capital_total']:,.0f} €")
    c2.metric("Valeur finale",    f"{m['valeur_finale']:,.0f} €")
    c3.metric("Gain net",         f"{m['gain_net']:+,.0f} €",
              delta=f"{m['gain_net']:+,.0f} €" if m['gain_net'] != 0 else None)
    c4.metric("CAGR",             f"{m['cagr']:+.2f} %/an",
              delta=f"{m['cagr']:+.2f} %/an" if m['cagr'] != 0 else None)

    # Graphique
    st.divider()
    st.markdown("### Évolution du portefeuille")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sim["date"], y=df_sim["capital_investi"],
        name="Capital investi",
        fill="tozeroy", fillcolor="rgba(30,50,80,0.35)",
        line=dict(color="#1e3250", width=1),
        hovertemplate="%{y:,.0f} €<extra>Capital investi</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df_sf["date"], y=df_sf["valeur_portefeuille"],
        name=f"{ticker} sans frais",
        line=dict(color="#475569", width=1.5, dash="dot"),
        hovertemplate="%{y:,.0f} €<extra>Sans frais</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df_sim["date"], y=livret[:n_mois],
        name=f"Livret A ({taux_la}%)",
        line=dict(color="#f59e0b", width=1.8, dash="dash"),
        hovertemplate="%{y:,.0f} €<extra>Livret A</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df_sim["date"], y=df_sim["valeur_portefeuille"],
        name=f"{ticker} avec TER ({ter_pct:.2f}%)",
        line=dict(color="#3b82f6", width=2.5),
        hovertemplate="%{y:,.0f} €<extra>" + ticker + " (TER)</extra>",
    ))

    layout = dark_layout(height=480)
    layout["yaxis"]["title"] = dict(text="Valeur (€)", font=dict(color=_TICK))
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)

    # Impact des frais
    st.divider()
    st.markdown("### Impact des frais TER")

    val_sf = df_sf["valeur_portefeuille"].iloc[-1]
    manque = val_sf - m["valeur_finale"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Valeur avec TER",   f"{m['valeur_finale']:,.2f} €")
    c2.metric("Valeur sans frais", f"{val_sf:,.2f} €")
    c3.metric("Manque à gagner",   f"{manque:,.2f} €",
              delta=f"-{manque:,.2f} €" if manque > 0 else None,
              delta_color="inverse")

    st.warning(
        f"Sur **{n_annees:.1f} ans**, un TER de **{ter_pct:.2f}%/an** "
        f"a coûté **{m['frais_totaux']:,.2f} €** de frais cumulés."
    )
    st.info("⚠️ Le backtesting illustre les performances passées. Il ne garantit pas les performances futures.")

    with st.expander("Tableau détaillé mois par mois"):
       rows_html = ""
       for _, row in df_sim.iterrows():
           rows_html += f'<tr><td style="color:#7a90a8;font-size:0.82rem;">{row["date"].strftime("%b %Y")}</td><td style="color:#f1f5f9;font-weight:600;font-family:monospace;">{row["prix"]:,.2f} €</td><td style="color:#60a5fa;font-family:monospace;">{row["parts_achetees"]:,.4f}</td><td style="color:#60a5fa;font-family:monospace;">{row["parts_cumulees"]:,.4f}</td><td style="color:#10b981;font-weight:700;font-family:monospace;">{row["valeur_portefeuille"]:,.2f} €</td><td style="color:#c5d4e8;font-family:monospace;">{row["capital_investi"]:,.2f} €</td><td style="color:#ef4444;font-family:monospace;">{row["frais_cumules"]:,.2f} €</td></tr>'

       st.markdown(f'<table class="etf-table"><thead><tr><th>Mois</th><th>Prix</th><th>Parts achetées</th><th>Parts cumulées</th><th>Valeur portefeuille</th><th>Capital investi</th><th>Frais cumulés</th></tr></thead><tbody>{rows_html}</tbody></table>', unsafe_allow_html=True)

else:
    with st.container(border=True):
        st.markdown("### Prêt à simuler")
        st.markdown(
            "Configurez vos paramètres dans le **panneau latéral gauche** "
            "puis cliquez sur **Lancer la simulation** pour visualiser l'évolution de votre portefeuille."
        )
