import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth import is_admin, get_all_users, create_user, delete_user
from utils.style import load_css, dark_layout
from data.etf_data import get_etf_catalog, get_connection
from datetime import datetime, timedelta

load_css()

# Vérification accès admin
if not is_admin():
    st.error("❌ Accès refusé — réservé aux administrateurs.")
    st.stop()

st.title(":material/admin_panel_settings: Panel Admin")
st.caption(f"Connecté en tant que **{st.session_state.user['email']}** — rôle : Admin")
st.divider()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    ":material/group: Utilisateurs",
    ":material/candlestick_chart: ETF",
    ":material/analytics: Statistiques"
])
# ══════════════════════════════════════════════════════════════
# TAB 1 — Gestion des utilisateurs
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Liste des utilisateurs")

    users = get_all_users()

    if not users:
        st.info("Aucun utilisateur en base.")
    else:
        # Stats rapides
        c1, c2, c3 = st.columns(3)
        c1.metric("Total utilisateurs", len(users))
        c2.metric("Admins", sum(1 for u in users if u["role"] == "admin"))
        c3.metric("Actifs", sum(1 for u in users if u["is_active"]))

        st.markdown("<br>", unsafe_allow_html=True)

        # Tableau utilisateurs
        rows_html = ""
        for user in users:
            role_badge = f'<span class="badge-admin">Admin</span>' if user["role"] == "admin" else f'<span class="badge-user">User</span>'
            active_badge = '<span class="badge-active">✓ Actif</span>' if user["is_active"] else '<span class="badge-inactive">✗ Inactif</span>'
            created = user["created_at"].strftime("%d/%m/%Y") if user["created_at"] else "-"
            rows_html += f'<tr><td class="table-email">{user["email"]}</td><td>{role_badge}</td><td>{active_badge}</td><td class="table-date">{created}</td></tr>'

        st.markdown(f'<table class="etf-table"><thead><tr><th>Email</th><th>Rôle</th><th>Statut</th><th>Créé le</th></tr></thead><tbody>{rows_html}</tbody></table>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Supprimer un utilisateur
        st.markdown("### Supprimer un utilisateur")
        emails = [u["email"] for u in users if u["email"] != st.session_state.user["email"]]
        if emails:
            email_to_delete = st.selectbox("Sélectionner l'utilisateur à supprimer", emails)
            if st.button("Supprimer", type="primary"):
                user_to_del = next(u for u in users if u["email"] == email_to_delete)
                if delete_user(user_to_del["id"]):
                    st.success(f"Utilisateur **{email_to_delete}** supprimé.")
                    st.rerun()
                else:
                    st.error("Erreur lors de la suppression.")
        else:
            st.info("Aucun autre utilisateur à supprimer.")

    st.divider()

    # Créer un utilisateur
    st.markdown("### Créer un utilisateur")
    with st.form("create_user"):
        col_a, col_b = st.columns(2)
        with col_a:
            new_email = st.text_input("Email")
            new_password = st.text_input("Mot de passe", type="password")
        with col_b:
            new_role = st.selectbox("Rôle", ["user", "admin"])
            st.markdown("<br>", unsafe_allow_html=True)

        if st.form_submit_button("Créer l'utilisateur", type="secondary"):
            if not new_email or not new_password:
                st.error("Email et mot de passe obligatoires.")
            elif create_user(new_email, new_password, new_role):
                st.success(f"Utilisateur **{new_email}** créé avec le rôle **{new_role}** !")
                st.rerun()
            else:
                st.error("Erreur — email déjà existant ?")

# ══════════════════════════════════════════════════════════════
# TAB 2 — Gestion des ETF
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Liste des ETF")

    ETF_CATALOG = get_etf_catalog()

    if not ETF_CATALOG:
        st.warning("Aucun ETF en base.")
    else:
        rows_html = ""
        for code, info in ETF_CATALOG.items():
            ter = info["ter"] * 100
            ter_class = "low" if ter < 0.20 else "mid" if ter < 0.40 else "high"
            pea_badge = '<span class="pea-yes">✓ PEA</span>' if info["pea"] else '<span class="pea-no">Non éligible</span>'
            rows_html += f'<tr><td><span class="etf-ticker">{code}</span></td><td><div class="etf-nom">{info["nom"]}</div><div class="etf-indice">{info["indice"]}</div></td><td>{info["gestionnaire"]}</td><td><span class="etf-ter {ter_class}">{ter:.2f}%</span></td><td>{pea_badge}</td></tr>'

        st.markdown(f'<table class="etf-table"><thead><tr><th>Ticker</th><th>Nom / Indice</th><th>Gestionnaire</th><th>TER</th><th>PEA</th></tr></thead><tbody>{rows_html}</tbody></table>', unsafe_allow_html=True)

    st.divider()

    # Ajouter un ETF
    st.markdown("### Ajouter un ETF")
    with st.form("add_etf"):
        col_a, col_b = st.columns(2)
        with col_a:
            new_code = st.text_input("Code (ex: IWDA)", max_chars=10).strip().upper()
            new_nom = st.text_input("Nom complet")
            new_indice = st.text_input("Indice répliqué")
            new_ticker_yf = st.text_input("Ticker Yahoo Finance (ex: IWDA.AS)")
        with col_b:
            new_gestionnaire = st.text_input("Gestionnaire")
            new_ter = st.number_input("TER annuel (%)", min_value=0.0, max_value=5.0, value=0.20, step=0.01, format="%.2f")
            new_pea = st.selectbox("Eligible PEA", ["Non", "Oui"]) == "Oui"
            new_description = st.text_area("Description", height=80)

        if st.form_submit_button("Ajouter l'ETF", type="secondary"):
            if not new_code or not new_nom or not new_ticker_yf:
                st.error("Code, Nom et Ticker sont obligatoires.")
            elif new_code in ETF_CATALOG:
                st.error(f"L'ETF '{new_code}' existe déjà.")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO etf (code, nom, indice, gestionnaire, ter, pea, ticker_yf, description)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (new_code, new_nom, new_indice, new_gestionnaire,
                          new_ter / 100, new_pea, new_ticker_yf, new_description))
                    conn.commit()
                    conn.close()
                    get_etf_catalog.clear()
                    st.success(f"ETF **{new_code}** ajouté !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

    st.divider()
    
    st.markdown("### :material/download: Importer depuis JustETF")

    with st.expander("Lancer l'import JustETF"):
        st.info("Récupère les ETFs éligibles depuis JustETF et les importe en base.")

        col_a, col_b = st.columns(2)
        with col_a:
            max_etfs = st.number_input("Nombre max d'ETFs à importer",
                                    min_value=10, max_value=200, value=50, step=10)
        with col_b:
            strategy = st.selectbox("Stratégie", [
                "epg-longOnly", "epg-short", "epg-leveraged"
            ], help="epg-longOnly = ETFs long uniquement (recommandé)")

        if st.button(":material/sync: Lancer l'import", type="primary"):
            with st.spinner("Scraping JustETF en cours..."):
                from utils.justetf_scraper import fetch_etfs_from_justetf
                df = fetch_etfs_from_justetf(strategy=strategy, max_etfs=max_etfs)

            if df.empty:
                st.error("Aucun ETF récupéré.")
            else:
                st.session_state.df_justetf = df
                st.success(f"✅ {len(df)} ETFs récupérés depuis JustETF")

        # Afficher aperçu + bouton confirmer si df disponible
        if "df_justetf" in st.session_state and st.session_state.df_justetf is not None:
            df = st.session_state.df_justetf

            st.dataframe(
                df[["ticker", "nom", "indice_replique", "gestionnaire", "ter", "eligible_pea"]],
                use_container_width=True, hide_index=True
            )

            if st.button(":material/save: Confirmer et sauvegarder en base", type="primary"):
                from utils.justetf_scraper import save_etfs_to_db
                with st.spinner("Insertion en base..."):
                    inseres, ignores = save_etfs_to_db(df)
                get_etf_catalog.clear()
                st.session_state.df_justetf = None
                st.success(f"✅ {inseres} ETFs insérés, {ignores} ignorés.")
                st.rerun()
                    
    st.divider()       
    
    st.markdown("### :material/auto_fix_high: Enrichir les ETFs depuis Yahoo Finance")
    st.caption("Résout le ticker Yahoo Finance et récupère nom, gestionnaire, indice, TER, description pour chaque ETF.")

    ETF_CATALOG = get_etf_catalog()
    tickers_sans_yf = [t for t, info in ETF_CATALOG.items() if not info.get("ticker_yf")]
    tickers_tous = list(ETF_CATALOG.keys())

    col_a, col_b = st.columns(2)
    with col_a:
        mode = st.radio("ETFs à enrichir", [
            f"Sans ticker YF ({len(tickers_sans_yf)})",
            f"Tous ({len(tickers_tous)})"
        ])

    tickers_a_enrichir = tickers_sans_yf if "Sans" in mode else tickers_tous
    st.info(f"{len(tickers_a_enrichir)} ETF(s) à enrichir — environ {len(tickers_a_enrichir) * 0.5:.0f} secondes")

    if st.button(":material/auto_fix_high: Lancer l'enrichissement", type="primary"):
        from utils.etf_enricher import enrich_all_etfs
        from data.etf_data import get_etf_catalog

        progress_bar = st.progress(0)
        status_text = st.empty()

        rapport = enrich_all_etfs(tickers_a_enrichir, progress_bar, status_text)

        get_etf_catalog.clear()
        progress_bar.progress(1.0)
        status_text.text("✅ Enrichissement terminé")

        st.success(f"✅ {rapport['succes']} enrichis, ❌ {rapport['echecs']} non trouvés")

        # Tableau résultat
        rows_html = ""
        for d in rapport["details"]:
            color = "#10b981" if "✅" in d["statut"] else "#ef4444"
            rows_html += f'<tr><td><span class="etf-ticker">{d["ticker"]}</span></td><td style="color:{color};font-family:monospace;">{d["ticker_yf"] or "—"}</td><td style="color:{color};">{d["statut"]}</td></tr>'

        st.markdown(
            f'<table class="etf-table"><thead><tr><th>Ticker</th><th>Ticker Yahoo Finance</th><th>Statut</th></tr></thead><tbody>{rows_html}</tbody></table>',
            unsafe_allow_html=True
        )
        st.rerun()   
        
    st.divider()          
    # Supprimer un ETF
    st.markdown("### Supprimer un ETF")
    ETF_CATALOG = get_etf_catalog()
    if ETF_CATALOG:
        code_to_delete = st.selectbox("Sélectionner l'ETF à supprimer", list(ETF_CATALOG.keys()),
                                       format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}")
        if st.button("Supprimer l'ETF", type="primary"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM etf WHERE code = %s", (code_to_delete,))
                conn.commit()
                conn.close()
                get_etf_catalog.clear()
                st.success(f"ETF **{code_to_delete}** supprimé.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

# ══════════════════════════════════════════════════════════════
# TAB 3 — Statistiques
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Vue d'ensemble")

    ETF_CATALOG = get_etf_catalog()
    users = get_all_users()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ETF en base", len(ETF_CATALOG))
    c2.metric("Utilisateurs", len(users))
    c3.metric("Admins", sum(1 for u in users if u["role"] == "admin"))
    c4.metric("Users actifs", sum(1 for u in users if u["is_active"]))

    st.divider()
    st.info("Les statistiques détaillées (simulations lancées, ETF les plus consultés...) seront disponibles quand la table simulation_history sera alimentée.")