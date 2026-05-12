import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth import login
from utils.style import load_css

load_css()

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    st.rerun()

_, col, _ = st.columns([1, 1.2, 1])

with col:
    st.markdown("""
    <div class="login-logo">
        <div class="login-title">Port<span>ify</span></div>
        <div class="login-subtitle">Investment Tracking & Simulation Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="login-divider">', unsafe_allow_html=True)

    st.markdown('<div style="color:#c5d4e8;font-weight:600;font-size:0.95rem;margin-bottom:1rem;">Connexion à votre espace</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Adresse email", placeholder="admin@portify.com")
        password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button(":material/login: Se connecter", type="secondary", use_container_width=True)

    if submit:
        if not email or not password:
            st.error("Veuillez remplir tous les champs.")
        else:
            user = login(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect.")

    st.markdown("""
    <div class="secure-badge">🔒 Connexion sécurisée · Données chiffrées</div>
    <div style="text-align:center;color:#1e3250;font-size:0.75rem;margin-top:0.8rem;">
        M2 MIAGE · Université Paris-Saclay · 2024–2025
    </div>
    """, unsafe_allow_html=True)