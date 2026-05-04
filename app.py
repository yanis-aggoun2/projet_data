import streamlit as st

st.set_page_config(
    page_title="Simulateur Portefeuille Passif",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif !important;
}

.main-header {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    padding: 2.5rem 2rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    color: white;
}

.main-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    margin: 0 0 0.4rem 0;
    color: white !important;
}

.main-header p {
    font-size: 1rem;
    opacity: 0.75;
    margin: 0;
    color: white;
}

.metric-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}

.metric-card .label {
    font-size: 0.78rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}

.metric-card .value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #0f172a;
    font-family: 'DM Serif Display', serif;
}

.metric-card .sub {
    font-size: 0.82rem;
    color: #94a3b8;
}

.etf-badge {
    display: inline-block;
    background: #dbeafe;
    color: #1d4ed8;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    margin: 0.1rem;
}

.pea-badge {
    display: inline-block;
    background: #dcfce7;
    color: #15803d;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
}

.warning-box {
    background: #fef3c7;
    border-left: 4px solid #f59e0b;
    padding: 1rem 1.2rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
    color: #78350f;
}

.info-box {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    padding: 1rem 1.2rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
    color: #1e3a8a;
}

.sidebar-nav-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
    font-weight: 600;
    padding: 0.5rem 0 0.2rem;
}

[data-testid="stSidebar"] {
    background: #0f172a;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

[data-testid="stSidebar"] .sidebar-nav-label {
    color: #475569 !important;
}

div[data-testid="stSidebarNav"] {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Sidebar branding
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 1.5rem;'>
        <div style='font-family: DM Serif Display, serif; font-size: 1.4rem; color: #f1f5f9;'>📈 Portefeuille Passif</div>
        <div style='font-size: 0.78rem; color: #64748b; margin-top: 0.3rem;'>M2 MIAGE — Université Paris-Saclay</div>
    </div>
    <hr style='border-color: #1e293b; margin-bottom: 1rem;'>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sidebar-nav-label">Navigation</div>', unsafe_allow_html=True)

# Home page content
st.markdown("""
<div class="main-header">
    <h1>Simulateur de Portefeuille Passif</h1>
    <p>Analysez, simulez et comprenez l'investissement passif avec des données réelles</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
        <div style="font-family: 'DM Serif Display', serif; font-size: 1.1rem; margin-bottom: 0.3rem;">Module A</div>
        <div style="font-weight: 600; font-size: 1rem; color: #0f172a; margin-bottom: 0.4rem;">Explorateur d'ETF</div>
        <div style="font-size: 0.85rem; color: #64748b;">Recherchez un ETF, comparez les frais et visualisez les performances historiques.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
        <div style="font-family: 'DM Serif Display', serif; font-size: 1.1rem; margin-bottom: 0.3rem;">Module B</div>
        <div style="font-weight: 600; font-size: 1rem; color: #0f172a; margin-bottom: 0.4rem;">Simulateur DCA</div>
        <div style="font-size: 0.85rem; color: #64748b;">Simulez une stratégie d'investissement programmé sur données historiques réelles.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📉</div>
        <div style="font-family: 'DM Serif Display', serif; font-size: 1.1rem; margin-bottom: 0.3rem;">Module C</div>
        <div style="font-weight: 600; font-size: 1rem; color: #0f172a; margin-bottom: 0.4rem;">Régression Linéaire</div>
        <div style="font-size: 0.85rem; color: #64748b;">Analysez la tendance long terme et les limites de la prédiction financière.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <strong>Comment utiliser cette application ?</strong><br>
    Naviguez entre les modules via le menu latéral à gauche. Commencez par l'<strong>Explorateur d'ETF</strong> 
    pour comprendre les actifs disponibles, puis simulez votre stratégie DCA, et enfin analysez les tendances 
    avec la régression linéaire.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ETF reference table
st.markdown("### ETF de référence")
st.markdown("Ces 4 ETF constituent la base de travail du projet :")

import pandas as pd
etf_data = {
    "Ticker": ["CW8", "PS20", "ESE", "OBLI"],
    "Nom complet": [
        "Amundi MSCI World",
        "Amundi S&P 500",
        "iShares MSCI Europe",
        "Lyxor Obligations d'État Euro"
    ],
    "Indice répliqué": ["MSCI World", "S&P 500", "MSCI Europe", "EuroMTS Govt Bond"],
    "TER (%)": [0.38, 0.15, 0.12, 0.17],
    "Éligible PEA": ["✅ Oui", "✅ Oui", "❌ Non", "❌ Non"],
    "Ticker Yahoo": ["CW8.PA", "500.PA", "ESEU.AS", "MTH.PA"]
}
df_etf = pd.DataFrame(etf_data)
st.dataframe(df_etf, use_container_width=True, hide_index=True)

st.markdown("""
<div class="warning-box" style="margin-top: 1.5rem;">
    <strong>⚠️ Avertissement</strong><br>
    Les performances passées ne préjugent pas des performances futures. Cette application est un outil 
    pédagogique. Le backtesting illustre ce qui s'est passé historiquement — ce n'est pas une recommandation d'investissement.
</div>
""", unsafe_allow_html=True)
