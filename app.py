import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Passive Portfolio Simulator",
    page_icon="📈",
    layout="wide",
)

# ── Dark theme CSS (seul usage de unsafe_allow_html) ──────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp {
    background-color: #060e1c !important;
    font-family: 'Inter', sans-serif !important;
}
.main .block-container {
    padding-top: 2rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1400px !important;
}
[data-testid="stSidebar"] {
    background-color: #08111f !important;
    border-right: 1px solid #162035 !important;
}
[data-testid="stSidebar"] * { color: #7a90a8 !important; }
[data-testid="stSidebar"] a:hover { color: #3b82f6 !important; }

h1, h2, h3, h4 { color: #f1f5f9 !important; font-weight: 700 !important; }
p, li, .stMarkdown p { color: #94a3b8 !important; }
hr, [data-testid="stDivider"] { border-color: #162035 !important; }

/* Bordered containers = cartes */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, #0c1928, #0d2040) !important;
    border: 1px solid #1a2e48 !important;
    border-radius: 14px !important;
    padding: 8px !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #0c1928, #0e2038) !important;
    border: 1px solid #1a2e48 !important;
    border-radius: 12px !important;
    padding: 20px 24px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.45) !important;
}
[data-testid="stMetricValue"] {
    color: #f1f5f9 !important; font-weight: 700 !important; font-size: 24px !important;
}
[data-testid="stMetricLabel"] {
    color: #3f5470 !important; font-size: 10px !important;
    text-transform: uppercase !important; letter-spacing: 1px !important; font-weight: 600 !important;
}
[data-testid="stMetricDelta"] { font-size: 13px !important; font-weight: 600 !important; }

/* Boutons primaires */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border: 1px solid #3b82f6 !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 22px rgba(37,99,235,0.5) !important;
    transform: translateY(-1px) !important;
}

/* Tableaux */
.stDataFrame {
    border: 1px solid #1a2e48 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Alertes / info / warning */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid #1a2e48 !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #1a2e48 !important;
    border-radius: 10px !important;
    background-color: #0c1928 !important;
}

/* Inputs */
[data-testid="stSelectbox"] > div > div {
    background-color: #0c1928 !important;
    border-color: #1a2e48 !important;
    color: #c5d4e8 !important;
    border-radius: 8px !important;
}
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    background-color: #0c1928 !important;
    border-color: #1a2e48 !important;
    color: #c5d4e8 !important;
}
.stSlider > div > div > div { background-color: #1a2e48 !important; }
.stCheckbox label { color: #7a90a8 !important; }
</style>
""", unsafe_allow_html=True)

# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown("# 📈 Passive Portfolio Simulator")
st.caption("M2 MIAGE — Université Paris-Saclay  ·  Analyse et simulation de stratégies d'investissement passif")

st.divider()

# ── Cartes des modules ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    with st.container(border=True):
        st.markdown("### 🔍 Module A")
        st.markdown("**Explorateur d'ETF**")
        st.markdown(
            "Recherchez et analysez un ETF, visualisez son évolution sur 1 à 10 ans "
            "et comparez deux instruments côte à côte sur une base normalisée 100."
        )

with col2:
    with st.container(border=True):
        st.markdown("### 📊 Module B")
        st.markdown("**Simulateur DCA**")
        st.markdown(
            "Simulez une stratégie d'investissement programmé sur données historiques réelles. "
            "Mesurez l'impact du TER, comparez au Livret A et calculez le CAGR."
        )

with col3:
    with st.container(border=True):
        st.markdown("### 📉 Module C")
        st.markdown("**Régression Linéaire**")
        st.markdown(
            "Analysez la tendance long terme via régressions OLS, visualisez les résidus "
            "avec bandes ±2σ et comprenez les limites statistiques de la prédiction."
        )

st.divider()

# ── Tableau ETF de référence ──────────────────────────────────────────────────
st.markdown("### ETF de référence")

etf_data = {
    "Ticker": ["CW8", "PS20", "ESE", "OBLI"],
    "Nom": ["Amundi MSCI World", "Amundi S&P 500", "iShares MSCI Europe", "Lyxor Oblig. Etat Euro"],
    "Indice répliqué": ["MSCI World", "S&P 500", "MSCI Europe", "EuroMTS Govt Bond"],
    "TER (%)": [0.38, 0.15, 0.12, 0.17],
    "Éligible PEA": ["✅ Oui", "✅ Oui", "❌ Non", "❌ Non"],
}
st.dataframe(
    pd.DataFrame(etf_data),
    use_container_width=True,
    hide_index=True,
    column_config={"TER (%)": st.column_config.NumberColumn(format="%.2f %%")},
)

st.divider()

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.warning(
    "⚠️ Les performances passées ne préjugent pas des performances futures. "
    "Cette application est réalisée à des fins **pédagogiques uniquement** "
    "dans le cadre du M2 MIAGE — Université Paris-Saclay. "
    "Aucun élément présenté ne constitue un conseil en investissement."
)
