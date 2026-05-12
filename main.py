import streamlit as st

st.set_page_config(
    page_title="Portify",
    page_icon="images/logo_portify(2).png",
    layout="wide",
)

# Initialisation session
if "user" not in st.session_state:
    st.session_state.user = None

# Navigation conditionnelle
if st.session_state.user is None:
    pg = st.navigation([
        st.Page("pages/login.py", title="Connexion", icon=":material/login:"),
    ])
else:
    pages = [
        st.Page("pages/app.py",                  title="Accueil",         icon=":material/home:"),
        st.Page("pages/explorateur_etf.py",       title="Explorateur ETF", icon=":material/candlestick_chart:"),
        st.Page("pages/simulateur_dca.py",        title="Simulateur DCA",  icon=":material/trending_up:"),
        st.Page("pages/regression_lineaire.py",   title="Régression OLS",  icon=":material/query_stats:"),
    ]

    if st.session_state.user["role"] == "admin":
        pages.append(
            st.Page("pages/admin.py", title="Admin", icon=":material/admin_panel_settings:")
        )

    pg = st.navigation(pages)

    # Bouton déconnexion dans le sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"<div style='font-size:0.8rem;color:#475569;margin-bottom:0.5rem;'>Connecté : <strong style='color:#c5d4e8;'>{st.session_state.user['email']}</strong></div>", unsafe_allow_html=True)
        if st.button(":material/logout: Se déconnecter", use_container_width=True):
            st.session_state.user = None
            st.rerun()

pg.run()