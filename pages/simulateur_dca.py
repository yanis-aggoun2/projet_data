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

# ── Dark theme CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp { background-color: #060e1c !important; font-family: 'Inter', sans-serif !important; }
.main .block-container { padding-top: 2rem !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; max-width: 1400px !important; }
[data-testid="stSidebar"] { background-color: #08111f !important; border-right: 1px solid #162035 !important; }
[data-testid="stSidebar"] * { color: #7a90a8 !important; }
h1, h2, h3, h4 { color: #f1f5f9 !important; font-weight: 700 !important; }
p, li, .stMarkdown p { color: #94a3b8 !important; }
hr, [data-testid="stDivider"] { border-color: #162035 !important; }
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, #0c1928, #0d2040) !important;
    border: 1px solid #1a2e48 !important; border-radius: 14px !important;
}
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #0c1928, #0e2038) !important;
    border: 1px solid #1a2e48 !important; border-radius: 12px !important;
    padding: 20px 24px !important; box-shadow: 0 4px 24px rgba(0,0,0,0.45) !important;
}
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-weight: 700 !important; font-size: 24px !important; }
[data-testid="stMetricLabel"] { color: #3f5470 !important; font-size: 10px !important; text-transform: uppercase !important; letter-spacing: 1px !important; font-weight: 600 !important; }
[data-testid="stMetricDelta"] { font-size: 13px !important; font-weight: 600 !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border: 1px solid #3b82f6 !important; color: #fff !important;
    font-weight: 600 !important; border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.3) !important;
}
.stButton > button[kind="primary"]:hover { box-shadow: 0 6px 22px rgba(37,99,235,0.5) !important; transform: translateY(-1px) !important; }
.stDataFrame { border: 1px solid #1a2e48 !important; border-radius: 12px !important; overflow: hidden !important; }
[data-testid="stAlert"] { border-radius: 10px !important; }
[data-testid="stExpander"] { border: 1px solid #1a2e48 !important; border-radius: 10px !important; background-color: #0c1928 !important; }
[data-testid="stSelectbox"] > div > div { background-color: #0c1928 !important; border-color: #1a2e48 !important; color: #c5d4e8 !important; border-radius: 8px !important; }
.stNumberInput > div > div > input, .stDateInput > div > div > input { background-color: #0c1928 !important; border-color: #1a2e48 !important; color: #c5d4e8 !important; }
</style>
""", unsafe_allow_html=True)

# ── Constantes graphique sombre ───────────────────────────────────────────────
_BG    = "#0c1928"
_PAPER = "#060e1c"
_GRID  = "#162035"
_TICK  = "#3f5470"

def dark_layout(title="", height=450):
    return dict(
        title=dict(text=title, font=dict(color="#c5d4e8", size=14), x=0.01),
        plot_bgcolor=_BG, paper_bgcolor=_PAPER,
        font=dict(color=_TICK, family="Inter, sans-serif", size=12),
        xaxis=dict(gridcolor=_GRID, linecolor=_GRID, tickfont=dict(color=_TICK), zeroline=False),
        yaxis=dict(gridcolor=_GRID, linecolor=_GRID, tickfont=dict(color=_TICK), zeroline=False),
        legend=dict(bgcolor="rgba(12,25,40,0.95)", bordercolor=_GRID, borderwidth=1,
                    font=dict(color="#7a90a8", size=12)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0e2038", bordercolor=_GRID, font=dict(color="#f1f5f9")),
        height=height, margin=dict(l=0, r=0, t=44, b=0),
    )

# ── Sidebar ───────────────────────────────────────────────────────────────────
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

    lancer = st.button("🚀 Lancer la simulation", type="primary", use_container_width=True)

# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown("# 📊 Simulateur DCA")
st.caption("Module B — Investissement programmé sur données historiques réelles")
st.divider()

# ── Résultats ─────────────────────────────────────────────────────────────────
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
        st.dataframe(df_sim.round(2), use_container_width=True, hide_index=True)

else:
    with st.container(border=True):
        st.markdown("### 📊 Prêt à simuler")
        st.markdown(
            "Configurez vos paramètres dans le **panneau latéral gauche** "
            "puis cliquez sur **Lancer la simulation** pour visualiser l'évolution de votre portefeuille."
        )
