import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
from utils.style import load_css, dark_layout, _BG, _PAPER, _GRID, _TICK

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.etf_data import get_etf_catalog, get_historical_data


load_css()

# Chargement catalogue
ETF_CATALOG = get_etf_catalog()
if not ETF_CATALOG:
    st.error("Impossible de charger les ETF depuis la base de données.")
    st.stop()
    
# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown("# Explorateur d'ETF")
st.caption("Module A — Analyse et comparaison d'ETF sur données historiques")
st.divider()

# ── Sélecteurs ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    ticker = st.selectbox(
        "Sélectionner un ETF",
        list(ETF_CATALOG.keys()),
        format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}"
    )
with col2:
    periode = st.selectbox("Période d'analyse", ["1 an", "3 ans", "5 ans", "10 ans"], index=1)

etf   = ETF_CATALOG[ticker]
jours = {"1 an": 365, "3 ans": 1095, "5 ans": 1825, "10 ans": 3650}[periode]
date_debut = (datetime.today() - timedelta(days=jours)).strftime("%Y-%m-%d")

# ── Fiche ETF + Graphique ─────────────────────────────────────────────────────
st.divider()
col_info, col_graph = st.columns([1, 2], gap="large")

with col_info:
    with st.container(border=True):
        st.markdown(f"### {ticker}")
        st.markdown(f"**{etf['nom']}**")
        st.divider()
        st.markdown(f"**Indice répliqué** — {etf['indice']}")
        st.markdown(f"**Gestionnaire** — {etf['gestionnaire']}")
        st.markdown(f"**TER annuel** — `{etf['ter']*100:.2f}%`")
        st.markdown(f"**TER mensuel** — `{etf['ter']/12*100:.4f}%`")
        pea = "✅ Éligible PEA" if etf["pea"] else "❌ Non éligible PEA"
        st.markdown(f"**{pea}**")
        st.divider()
        st.caption(etf["description"])

with col_graph:
    with st.spinner("Chargement des données…"):
        df = get_historical_data(etf["ticker_yf"], date_debut)

    if not df.empty:
        prix_debut = float(df["prix_cloture"].iloc[0])
        prix_fin   = float(df["prix_cloture"].iloc[-1])
        variation  = (prix_fin - prix_debut) / prix_debut * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df["prix_cloture"],
            mode="lines",
            line=dict(color="#3b82f6", width=2),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.06)",
            name="Prix de clôture",
            hovertemplate="%{y:.2f} €<extra></extra>",
        ))
        layout = dark_layout(title=f"{etf['nom']} — {periode}", height=360)
        layout["yaxis"]["title"] = dict(text="Prix (€)", font=dict(color=_TICK))
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Prix actuel",              f"{prix_fin:.2f} €")
        c2.metric("Prix de départ",           f"{prix_debut:.2f} €")
        c3.metric(f"Performance ({periode})", f"{variation:+.2f}%")
    else:
        st.warning("Données indisponibles pour cet ETF.")

# ── Comparaison deux ETF ──────────────────────────────────────────────────────
st.divider()
st.markdown("### Comparer deux ETF")

col_a, col_b, col_p = st.columns([2, 2, 1])
with col_a:
    etf_a = st.selectbox("ETF A", list(ETF_CATALOG.keys()), index=0, key="a",
                         format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}")
with col_b:
    etf_b = st.selectbox("ETF B", list(ETF_CATALOG.keys()), index=1, key="b",
                         format_func=lambda t: f"{t} — {ETF_CATALOG[t]['nom']}")
with col_p:
    periode_comp = st.selectbox("Période", ["1 an", "3 ans", "5 ans", "10 ans"], index=2, key="pc")

jours_comp = {"1 an": 365, "3 ans": 1095, "5 ans": 1825, "10 ans": 3650}[periode_comp]
date_comp  = (datetime.today() - timedelta(days=jours_comp)).strftime("%Y-%m-%d")

if st.button("Lancer la comparaison", type="primary"):
    df_a = get_historical_data(ETF_CATALOG[etf_a]["ticker_yf"], date_comp)
    df_b = get_historical_data(ETF_CATALOG[etf_b]["ticker_yf"], date_comp)

    if not df_a.empty and not df_b.empty:
        perf_a = df_a["prix_cloture"] / df_a["prix_cloture"].iloc[0] * 100
        perf_b = df_b["prix_cloture"] / df_b["prix_cloture"].iloc[0] * 100

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=perf_a.index, y=perf_a,
            name=f"{etf_a} — {ETF_CATALOG[etf_a]['nom']}",
            line=dict(color="#3b82f6", width=2.5),
            hovertemplate="%{y:.1f}<extra>" + etf_a + "</extra>",
        ))
        fig2.add_trace(go.Scatter(
            x=perf_b.index, y=perf_b,
            name=f"{etf_b} — {ETF_CATALOG[etf_b]['nom']}",
            line=dict(color="#f59e0b", width=2.5),
            hovertemplate="%{y:.1f}<extra>" + etf_b + "</extra>",
        ))
        fig2.add_hline(y=100, line_dash="dash", line_color="#1a2e48", line_width=1.5,
                       annotation_text="Base 100", annotation_font_color=_TICK)
        layout2 = dark_layout(title=f"Performance normalisée base 100 — {periode_comp}", height=420)
        layout2["yaxis"]["title"] = dict(text="Base 100", font=dict(color=_TICK))
        fig2.update_layout(**layout2)
        st.plotly_chart(fig2, use_container_width=True)

        def stats(df, info, t):
            perf = (df["prix_cloture"].iloc[-1] / df["prix_cloture"].iloc[0] - 1) * 100
            vol  = df["prix_cloture"].pct_change().std() * (252 ** 0.5) * 100
            return {
               "ticker": t,
               "nom": info["nom"],
               "perf": perf,
               "vol": vol,
               "ter": info["ter"] * 100,
               "pea": info["pea"],
           }

        s_a = stats(df_a, ETF_CATALOG[etf_a], etf_a)
        s_b = stats(df_b, ETF_CATALOG[etf_b], etf_b)
 
        rows_html = ""
        for s in [s_a, s_b]:
            perf_color = "#10b981" if s["perf"] >= 0 else "#ef4444"
            ter_class = "low" if s["ter"] < 0.20 else "mid" if s["ter"] < 0.40 else "high"
            pea_badge = '<span class="pea-yes">✓ PEA</span>' if s["pea"] else '<span class="pea-no">Non éligible</span>'
            rows_html += f'<tr><td><span class="etf-ticker">{s["ticker"]}</span></td><td><div class="etf-nom">{s["nom"]}</div></td><td style="color:{perf_color};font-weight:700;font-family:monospace;">{s["perf"]:+.2f}%</td><td style="color:#c5d4e8;font-family:monospace;">{s["vol"]:.2f}%</td><td><span class="etf-ter {ter_class}">{s["ter"]:.2f}%</span></td><td>{pea_badge}</td></tr>'

        st.markdown(f'<table class="etf-table"><thead><tr><th>Ticker</th><th>Nom</th><th>Performance</th><th>Volatilité ann.</th><th>TER annuel</th><th>Éligibilité</th></tr></thead><tbody>{rows_html}</tbody></table>', unsafe_allow_html=True)
    else:
        st.error("Impossible de charger les données pour un ou plusieurs ETF.")

# # Ajouter un nouvel ETF
# st.markdown("---")
# st.markdown("### :material/add_circle: Ajouter un nouvel ETF")

# with st.expander("Formulaire d'ajout"):
#     st.info("Le ticker Yahoo Finance est utilisé pour récupérer les données. Exemple : CW8.PA, IWDA.AS, SP5.PA")

#     col_f1, col_f2 = st.columns(2)
#     with col_f1:
#         new_code = st.text_input("Code (ex: IWDA)", max_chars=10).strip().upper()
#         new_nom = st.text_input("Nom complet (ex: iShares Core MSCI World)")
#         new_indice = st.text_input("Indice répliqué (ex: MSCI World)")
#         new_ticker_yf = st.text_input("Ticker Yahoo Finance (ex: IWDA.AS)")
#     with col_f2:
#         new_gestionnaire = st.text_input("Gestionnaire (ex: BlackRock)")
#         new_ter = st.number_input("TER annuel (%)", min_value=0.0, max_value=5.0,
#                                    value=0.20, step=0.01, format="%.2f")
#         new_pea = st.selectbox("Eligible PEA", ["Non", "Oui"]) == "Oui"
#         new_description = st.text_area("Description", height=80)

#     if st.button("Enregistrer l'ETF", type="primary"):
#         if not new_code or not new_nom or not new_ticker_yf:
#             st.error("Les champs Code, Nom et Ticker Yahoo Finance sont obligatoires.")
#         elif new_code in ETF_CATALOG:
#             st.error(f"L'ETF '{new_code}' existe déjà dans la base.")
#         else:
#             with st.spinner("Vérification du ticker Yahoo Finance..."):
#                 df_test = get_historical_data(
#                     new_ticker_yf,
#                     (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
#                 )
#             if df_test.empty:
#                 st.error(f"Le ticker '{new_ticker_yf}' est introuvable sur Yahoo Finance. Vérifiez et réessayez.")
#             else:
#                 try:
#                     conn = get_connection()
#                     cursor = conn.cursor()
#                     cursor.execute("""
#                         INSERT INTO etf (code, nom, indice, gestionnaire, ter, pea, ticker_yf, description)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                     """, (new_code, new_nom, new_indice, new_gestionnaire,
#                           new_ter / 100, new_pea, new_ticker_yf, new_description))
#                     conn.commit()
#                     get_etf_catalog.clear()
#                     conn.close()
#                     st.success(f"✅ ETF '{new_code} — {new_nom}' ajouté !")
#                     st.balloons()
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Erreur lors de l'insertion : {e}")