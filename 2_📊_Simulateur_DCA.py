import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, date
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.etf_data import ETF_CATALOG, get_historical_data, format_currency, format_percent
from utils.dca_engine import (
    run_dca_simulation, run_dca_sans_frais,
    calcul_livret_a, calcul_metriques
)

st.set_page_config(page_title="Simulateur DCA", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }
.metric-card {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 1.2rem 1.4rem; text-align: center;
}
.metric-card .lbl { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
.metric-card .val { font-size: 2rem; font-weight: 700; color: #0f172a; font-family: 'DM Serif Display', serif; }
.metric-card .sub { font-size: 0.82rem; color: #94a3b8; margin-top: 0.2rem; }
.warning-box { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; font-size: 0.9rem; color: #78350f; margin: 1rem 0; }
.success-box { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; font-size: 0.9rem; color: #15803d; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📊 Simulateur DCA")
st.markdown("Configurez votre stratégie d'investissement programmé et visualisez son évolution historique.")

# ── Panneau de configuration ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Paramètres")
    ticker = st.selectbox(
        "ETF",
        list(ETF_CATALOG.keys()),
        format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}"
    )
    etf = ETF_CATALOG[ticker]

    capital_initial = st.number_input("Capital de départ (€)", min_value=0, max_value=100000, value=1000, step=100)
    versement_mensuel = st.number_input("Versement mensuel DCA (€)", min_value=0, max_value=10000, value=200, step=50)

    ter_pct = st.number_input(
        "TER annuel (%)",
        min_value=0.0, max_value=5.0,
        value=float(etf["ter"] * 100),
        step=0.01, format="%.2f",
        help="Frais de gestion annuels. Pré-rempli selon l'ETF sélectionné."
    )
    ter = ter_pct / 100

    taux_livret_a = st.number_input("Taux Livret A (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.25, format="%.2f")

    today = date.today()
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        date_debut = st.date_input("Début", value=date(2015, 1, 1), min_value=date(2000, 1, 1), max_value=today)
    with col_d2:
        date_fin = st.date_input("Fin", value=date(2024, 12, 31), min_value=date(2000, 1, 1), max_value=today)

    lancer = st.button("🚀 Lancer la simulation", type="primary", use_container_width=True)

# ── Simulation ──────────────────────────────────────────────────────────────
if lancer:
    if date_debut >= date_fin:
        st.error("La date de début doit être antérieure à la date de fin.")
        st.stop()

    with st.spinner("Téléchargement des données et simulation en cours..."):
        df_prix = get_historical_data(etf["ticker_yf"], str(date_debut), str(date_fin))

    if df_prix.empty:
        st.error("Impossible de récupérer les données pour cet ETF sur la période sélectionnée.")
        st.stop()

    df_sim = run_dca_simulation(df_prix, capital_initial, versement_mensuel, ter, str(date_debut), str(date_fin))
    df_sans_frais = run_dca_sans_frais(df_prix, capital_initial, versement_mensuel, str(date_debut), str(date_fin))

    n_mois = len(df_sim)
    n_annees = n_mois / 12

    livret_vals = calcul_livret_a(capital_initial, versement_mensuel, taux_livret_a / 100, n_mois)
    metriques = calcul_metriques(df_sim, n_annees)

    # ── Métriques clés ──────────────────────────────────────────────────────
    st.markdown("### Résultats de la simulation")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="lbl">Capital total investi</div>
            <div class="val">{metriques['capital_total']:,.0f} €</div>
            <div class="sub">{n_mois} versements</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        couleur_val = "#16a34a" if metriques['valeur_finale'] > metriques['capital_total'] else "#dc2626"
        st.markdown(f"""
        <div class="metric-card">
            <div class="lbl">Valeur finale du portefeuille</div>
            <div class="val" style="color:{couleur_val};">{metriques['valeur_finale']:,.0f} €</div>
            <div class="sub">après frais TER réels</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        signe = "+" if metriques['gain_net'] >= 0 else ""
        c_gain = "#16a34a" if metriques['gain_net'] >= 0 else "#dc2626"
        st.markdown(f"""
        <div class="metric-card">
            <div class="lbl">Gain net</div>
            <div class="val" style="color:{c_gain};">{signe}{metriques['gain_net']:,.0f} €</div>
            <div class="sub">{signe}{metriques['gain_pct']:.2f}%</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="lbl">CAGR annualisé</div>
            <div class="val" style="color:#3b82f6;">{metriques['cagr']:+.2f}%</div>
            <div class="sub">rendement moyen/an</div>
        </div>""", unsafe_allow_html=True)

    # ── Graphique principal ─────────────────────────────────────────────────
    st.markdown("### Évolution du portefeuille")

    fig = go.Figure()

    # ETF avec frais
    fig.add_trace(go.Scatter(
        x=df_sim["date"], y=df_sim["valeur_portefeuille"],
        name=f"{ticker} (avec TER {ter_pct:.2f}%)",
        line=dict(color="#3b82f6", width=2.5),
        hovertemplate="%{x|%b %Y} — %{y:,.2f} €<extra></extra>"
    ))

    # ETF sans frais
    fig.add_trace(go.Scatter(
        x=df_sans_frais["date"], y=df_sans_frais["valeur_portefeuille"],
        name=f"{ticker} (sans frais)",
        line=dict(color="#94a3b8", width=1.5, dash="dot"),
        hovertemplate="%{x|%b %Y} — %{y:,.2f} €<extra></extra>"
    ))

    # Capital investi
    fig.add_trace(go.Scatter(
        x=df_sim["date"], y=df_sim["capital_investi"],
        name="Capital investi",
        line=dict(color="#e2e8f0", width=1.5),
        fill="tozeroy",
        fillcolor="rgba(226,232,240,0.3)",
        hovertemplate="%{x|%b %Y} — %{y:,.2f} €<extra></extra>"
    ))

    # Livret A
    dates_livret = df_sim["date"].values
    fig.add_trace(go.Scatter(
        x=dates_livret, y=livret_vals[:len(dates_livret)],
        name=f"Livret A ({taux_livret_a}%)",
        line=dict(color="#f59e0b", width=1.5, dash="dash"),
        hovertemplate="%{x|%b %Y} — %{y:,.2f} €<extra></extra>"
    ))

    fig.update_layout(
        height=480,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="DM Sans"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Valeur (€)",
        xaxis_title="Date",
        margin=dict(l=0, r=0, t=40, b=0)
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
    st.plotly_chart(fig, use_container_width=True)

    # ── Impact des frais ────────────────────────────────────────────────────
    st.markdown("### Impact des frais TER")

    val_avec = metriques['valeur_finale']
    val_sans = df_sans_frais["valeur_portefeuille"].iloc[-1]
    manque_a_gagner = val_sans - val_avec
    frais_totaux = metriques['frais_totaux']

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric("Valeur avec TER réel", f"{val_avec:,.2f} €")
    with col_f2:
        st.metric("Valeur sans TER", f"{val_sans:,.2f} €")
    with col_f3:
        st.metric("Coût total des frais", f"-{frais_totaux:,.2f} €",
                  delta=f"-{manque_a_gagner:,.2f} € manque à gagner", delta_color="inverse")

    st.markdown(f"""
    <div class="warning-box">
        <strong>📉 L'impact du TER sur {n_annees:.1f} ans</strong><br>
        Un TER de <strong>{ter_pct:.2f}%/an</strong> a prélevé <strong>{frais_totaux:,.2f} €</strong> au total sur la période,
        soit un manque à gagner de <strong>{manque_a_gagner:,.2f} €</strong> par rapport à un ETF sans frais.
        C'est pourquoi le choix d'un ETF à faibles frais est déterminant sur le long terme.
    </div>
    """, unsafe_allow_html=True)

    # ── Tableau détaillé ────────────────────────────────────────────────────
    with st.expander("📋 Voir le tableau détaillé mois par mois"):
        df_display = df_sim[["date", "prix", "parts_achetees", "parts_cumulees",
                              "valeur_portefeuille", "capital_investi", "frais_cumules"]].copy()
        df_display.columns = ["Date", "Prix (€)", "Parts achetées", "Parts cumulées",
                               "Valeur portefeuille (€)", "Capital investi (€)", "Frais cumulés (€)"]
        for col in ["Prix (€)", "Parts achetées", "Parts cumulées",
                    "Valeur portefeuille (€)", "Capital investi (€)", "Frais cumulés (€)"]:
            df_display[col] = df_display[col].round(2)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="warning-box" style="margin-top: 1rem;">
        <strong>⚠️ Limite du backtesting</strong><br>
        Ces résultats sont basés sur des données historiques réelles. Le fait qu'une stratégie ait bien 
        fonctionné dans le passé ne garantit <em>pas</em> ses performances futures. Le DCA est préférable 
        au market timing précisément parce qu'il ne prétend pas prévoir le marché.
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; color: #94a3b8;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">⚙️</div>
        <div style="font-size: 1.1rem; font-weight: 500; color: #64748b;">Configurez les paramètres dans le panneau latéral puis cliquez sur <strong>Lancer la simulation</strong>.</div>
    </div>
    """, unsafe_allow_html=True)
