import streamlit as st

st.set_page_config(
    page_title="Portify",
    page_icon="images/logo_portify(2).png",
    layout="wide",
)

pg = st.navigation([
    st.Page("pages/app.py",                 title="Accueil",         icon=":material/home:"),
    st.Page("pages/explorateur_etf.py",     title="Explorateur ETF", icon=":material/candlestick_chart:"),
    st.Page("pages/simulateur_dca.py",      title="Simulateur DCA",  icon=":material/trending_up:"),
    st.Page("pages/regression_lineaire.py", title="Régression OLS",  icon=":material/query_stats:"),
])
pg.run()