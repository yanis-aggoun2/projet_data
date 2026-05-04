import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Simulateur Portefeuille Passif",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Simulateur de Portefeuille Passif")
st.markdown("**M2 MIAGE — Université Paris-Saclay**")
st.markdown("---")

st.markdown("""
Bienvenue sur le simulateur de portefeuille passif. Naviguez entre les modules
via le **menu latéral à gauche**.
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("**🔍 Module A — Explorateur d'ETF**\n\nRecherchez un ETF, comparez les frais et visualisez les performances historiques.")

with col2:
    st.info("**📊 Module B — Simulateur DCA**\n\nSimulez une stratégie d'investissement programmé sur données historiques réelles.")

with col3:
    st.info("**📉 Module C — Régression Linéaire**\n\nAnalysez la tendance long terme et les limites de la prédiction financière.")

st.markdown("---")
st.markdown("### ETF de référence")

etf_data = {
    "Ticker": ["CW8", "PS20", "ESE", "OBLI"],
    "Nom": ["Amundi MSCI World", "Amundi S&P 500", "iShares MSCI Europe", "Lyxor Oblig. Etat Euro"],
    "Indice": ["MSCI World", "S&P 500", "MSCI Europe", "EuroMTS Govt Bond"],
    "TER (%)": [0.38, 0.15, 0.12, 0.17],
    "PEA": ["✅", "✅", "❌", "❌"],
}
st.dataframe(pd.DataFrame(etf_data), use_container_width=True, hide_index=True)

st.warning("⚠️ Les performances passées ne préjugent pas des performances futures. Application pédagogique uniquement.")
